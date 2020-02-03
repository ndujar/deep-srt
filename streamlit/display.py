"""
Module to generate an interactive app to visualize and train a QoE predictive model
from data retrieved out of srt-live-transmit protocol stats
It relies of Streamlite library for the visualization and display of widgets
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# TODO: Change filepaths back
TRANSMITTER_LOGS = 'logs/transmitter.csv'
RECEIVER_LOGS = 'logs/receiver.csv'
# TRANSMITTER_LOGS = '/Users/msharabayko/_data/mac_eunorth/local/4-srt-xtransmit-stats-snd.csv'
# RECEIVER_LOGS = '/Users/msharabayko/_data/mac_eunorth/msharabayko@40.69.89.21/3-srt-xtransmit-stats-rcv.csv'


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
    df_transmitter = load_data(TRANSMITTER_LOGS, 50000)
    df_receiver = load_data(RECEIVER_LOGS, 50000)

    # Preprocess the datasets to align time series and remove spurious data
    # Filter out zero values
    df_transmitter = df_transmitter.loc[:, (df_transmitter != 0).any(axis=0)]
    df_receiver = df_receiver.loc[:, (df_receiver != 0).any(axis=0)]
    # Remove NANs
    df_transmitter = df_transmitter.dropna(axis=1)
    df_receiver = df_receiver.dropna(axis=1)
    # Align time series
    df_transmitter = df_transmitter[df_transmitter['Time'] > df_receiver['Time'].min()]
    df_receiver = df_receiver[df_receiver['Time'] < df_transmitter['Time'].max()]

    df_transmitter.set_index('Time', inplace=True)
    df_receiver.set_index('Time', inplace=True)
   
    df_synchronized = df_transmitter.join(df_receiver, how='outer', lsuffix='_transmit', rsuffix='_receive')
    df_synchronized = df_synchronized.interpolate()
    df_synchronized['Rate'] = df_synchronized['mbpsSendRate'] / (df_synchronized['mbpsRecvRate'])

    # Display datasets
    st.subheader('Processed TRANSMITTER data')
    st.write(df_transmitter, df_transmitter.shape)

    st.subheader('Processed RECEIVER data')
    st.write(df_receiver, df_receiver.shape)

    st.subheader('SYNCHRONIZED data')
    st.write(df_synchronized, df_synchronized.shape)

    st.subheader('Summary, SYNCHRONIZED data')
    st.write(df_synchronized.describe())

    plot_scatter(
        'TRANSMITTER Time series',
        'Time',
        df_transmitter.columns,
        'Time',
        'TRANSMITTER',
        df_transmitter
    )

    plot_scatter(
        'RECEIVER Time series',
        'Time',
        df_receiver.columns,
        'Time',
        'RECEIVER',
        df_receiver
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
    plot_correlation_matrix(df_receiver)
    plot_correlation_matrix(df_transmitter)
    plot_correlation_matrix(df_synchronized)


if __name__ == '__main__':
    main()