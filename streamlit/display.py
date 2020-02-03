"""
Module to generate an interactive app to visualize and train a QoE predictive model
from data retrieved out of srt-live-transmit protocol stats
It relies of Streamlite library for the visualization and display of widgets
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# TODO: Change filepaths back
SND_LOGS = 'logs/transmitter.csv'
RCV_LOGS = 'logs/receiver.csv'
# SND_LOGS = '/Users/msharabayko/_data/mac_eunorth/local/4-srt-xtransmit-stats-snd.csv'
# RCV_LOGS = '/Users/msharabayko/_data/mac_eunorth/msharabayko@40.69.89.21/3-srt-xtransmit-stats-rcv.csv'


# TODO: Uncomment features back
FEATURES = [
    'Time',
    # 'pktFlowWindow',
    # 'pktCongestionWindow',
    # 'pktFlightSize',
    'msRTT',
    'mbpsBandwidth',
    'pktSent',
    'pktSndLoss',
    'pktSndDrop',
    'pktRetrans',
    # 'byteSent',
    # 'byteSndDrop',
    'mbpsSendRate',
    # 'usPktSndPeriod',
    'pktRecv',
    'pktRcvLoss',
    'pktRcvDrop',
    'pktRcvRetrans',
    'pktRcvBelated',
    # 'byteRecv',
    # 'byteRcvLoss',
    # 'byteRcvDrop',
    'mbpsRecvRate',
    # 'pktSndFilterExtra',
    # 'pktRcvFilterExtra',
    # 'pktRcvFilterSupply',
    # 'pktRcvFilterLoss'
]


def load_data(data_uri, nrows):
    """
    Function to retrieve data from a given file or URL
    in a Pandas DataFrame suitable for model training.
    nrows limits the amount of data displayed for optimization
    """
    data_df = pd.read_csv(data_uri, nrows=nrows)
    data_df = data_df[FEATURES]
    return data_df


def plot_scatter(
    title,
    x_metric,
    y_metrics,
    x_axis_title,
    y_axis_title,
    df_aggregated
):
    """
    Function to plot and format a scatterplot from the aggregated dataframe
    """
    data = []
    shapes = list()
    for y_metric in y_metrics:
        data.append(
            go.Scatter(
                x=df_aggregated.index,
                y=df_aggregated[y_metric],
                mode='lines',
                marker=dict(opacity=0.8, line=dict(width=0)),
                name=y_metric
            )
        )

    fig = go.Figure(data=data)
    fig.update_layout(
        title=title,
        xaxis_title=x_axis_title,
        yaxis_title=y_axis_title,
        legend=go.layout.Legend(
            x=0,
            y=1,
            traceorder="normal",
            font=dict(family="sans-serif", size=8, color="black"),
            bgcolor="LightSteelBlue",
            bordercolor="Black",
            borderwidth=2
        ),
        shapes=shapes
    )
    st.plotly_chart(fig)


def plot_correlation_matrix(df_aggregated):
    """
    Display correlation matrix for features
    """
    FEATURES = df_aggregated.columns
    df_features = pd.DataFrame(df_aggregated[FEATURES])
    corr = df_features.corr()
    corr.style.background_gradient(cmap='coolwarm')
    fig = go.Figure(data=go.Heatmap(x=FEATURES, y=FEATURES, z=corr))
    st.plotly_chart(fig)


def main():
    """
    Main function to train and evaluate tamper and QoE models
    """
    st.title('QoE model predictor')

    st.subheader('Raw features')
    st.write(FEATURES)

    # Get QoE pristine dataset (no attacks)
    df_snd = load_data(SND_LOGS, 50000)
    df_rcv = load_data(RCV_LOGS, 50000)

    # Preprocess the datasets to align time series and remove spurious data
    # Filter out zero values
    df_snd = df_snd.loc[:, (df_snd != 0).any(axis=0)]
    df_rcv = df_rcv.loc[:, (df_rcv != 0).any(axis=0)]
    # Remove NANs
    df_snd = df_snd.dropna(axis=1)
    df_rcv = df_rcv.dropna(axis=1)
    # Align time series
    df_snd = df_snd[df_snd['Time'] > df_rcv['Time'].min()]
    df_rcv = df_rcv[df_rcv['Time'] < df_snd['Time'].max()]

    df_snd.set_index('Time', inplace=True)
    df_rcv.set_index('Time', inplace=True)
   
    df_synchronized = df_snd.join(df_rcv, how='outer', lsuffix='_transmit', rsuffix='_receive')
    df_synchronized = df_synchronized.interpolate()
    df_synchronized['Rate'] = df_synchronized['mbpsSendRate'] / (df_synchronized['mbpsRecvRate'])

    # Display datasets
    st.subheader('Processed SENDER data')
    st.write(df_snd, df_snd.shape)

    st.subheader('Processed RECEIVER data')
    st.write(df_rcv, df_rcv.shape)

    st.subheader('SYNCHRONIZED data')
    st.write(df_synchronized, df_synchronized.shape)

    st.subheader('Summary, SYNCHRONIZED data')
    st.write(df_synchronized.describe())

    plot_scatter(
        'SENDER Time series',
        'Time',
        df_snd.columns,
        'Time',
        'SENDER',
        df_snd
    )

    plot_scatter(
        'RECEIVER Time series',
        'Time',
        df_rcv.columns,
        'Time',
        'RECEIVER',
        df_rcv
    )

    plot_scatter(
        'SYNCHRONIZED Time series',
        'Time',
        df_synchronized.columns,
        'Time',
        'SYNCHRONIZED',
        df_synchronized
    )

    # Display correlation matrixs
    plot_correlation_matrix(df_rcv)
    plot_correlation_matrix(df_snd)
    plot_correlation_matrix(df_synchronized)


if __name__ == '__main__':
    main()