"""
Module to generate an interactive app to visualize and train a QoE predictive model
from data retrieved out of srt-live-transmit protocol stats
It relies of Streamlite library for the visualization and display of widgets
"""

import os.path

from catboost import Pool, CatBoostRegressor, CatBoostClassifier

import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.metrics import fbeta_score, roc_curve, auc
from sklearn.preprocessing import StandardScaler
from sklearn import svm

st.title('QoE model predictor')

TRANSMITTER_LOGS = '../logs/transmitter.csv'
RECEIVER_LOGS = '../logs/receiver.csv'
FEATURES = ['Time',
            'pktFlowWindow',
            'pktCongestionWindow',
            'pktFlightSize',
            'msRTT',
            'mbpsBandwidth',
            'pktSent',
            'pktSndLoss',
            'pktSndDrop',
            'pktRetrans',
            'byteSent',
            'byteSndDrop',
            'mbpsSendRate',
            'usPktSndPeriod',
            'pktRecv',
            'pktRcvLoss',
            'pktRcvDrop',
            'pktRcvRetrans',
            'pktRcvBelated',
            'byteRecv',
            'byteRcvLoss',
            'byteRcvDrop',
            'mbpsRecvRate',
            'pktSndFilterExtra',
            'pktRcvFilterExtra',
            'pktRcvFilterSupply',
            'pktRcvFilterLoss'
            ]
def load_data(data_uri, nrows):
    """
    Function to retrieve data from a given file or URL
    in a Pandas DataFrame suitable for model training.
    nrows limits the amount of data displayed for optimization
    """
    data_df = pd.read_csv(data_uri, nrows=nrows)
    # lowercase = lambda x: str(x).lower()
    # data_df.rename(lowercase, axis='columns', inplace=True)
    data_df = data_df[FEATURES]
    return data_df

def plot_scatter(title, x_metric, y_metrics, x_axis_title, y_axis_title, df_aggregated):
    """
    Function to plot and format a scatterplot from the aggregated dataframe
    """
    data = []
    shapes = list()
    for y_metric in y_metrics:
        data.append(go.Scatter(x=df_aggregated[x_metric],
                            y=df_aggregated[y_metric],
                            mode='lines',
                            marker=dict(
                                    opacity=0.8,
                                    line=dict(width=0)
                                    ),
                            name=y_metric
                            
                            )
                        )

    fig = go.Figure(data=data)
    fig.update_layout(title=title,
                      xaxis_title=x_axis_title,
                      yaxis_title=y_axis_title,
                      legend=go.layout.Legend(x=0,
                                              y=1,
                                            traceorder="normal",
                                            font=dict(family="sans-serif",
                                                    size=8,
                                                    color="black"
                                                    ),
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
    fig = go.Figure(data=go.Heatmap(x=FEATURES,
                                    y=FEATURES,
                                    z=corr
                                    ))
 
    st.plotly_chart(fig)

def main():
    """
    Main function to train and evaluate tamper and QoE models
    """
    # Get QoE pristine dataset (no attacks)
    df_transmitter = load_data(TRANSMITTER_LOGS, 50000)
    df_receiver = load_data(RECEIVER_LOGS, 50000)
    
    st.subheader('Raw features')
    st.write(FEATURES)

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

    st.write('Mean transmitter delta Time:', np.diff(df_transmitter['Time']).mean())
    st.write('Mean receiver delta Time:', np.diff(df_receiver['Time']).mean())

    # Display datasets
    st.subheader('Raw TRANSMITTER data')
    st.write(df_transmitter, df_transmitter.shape)

    st.subheader('Raw RECEIVER data')
    st.write(df_receiver, df_receiver.shape)

    plot_scatter('TRANSMITTER Time series',
                 'Time',
                 df_transmitter.columns,
                 'Time',
                 'TRANSMITTER',
                 df_transmitter)

    plot_scatter('RECEIVER Time series',
                 'Time',
                 df_receiver.columns,
                 'Time',
                 'RECEIVER',
                 df_receiver)
    
    # Display correlation matrix
    plot_correlation_matrix(df_receiver)
    # Display correlation matrix
    plot_correlation_matrix(df_transmitter)
if __name__ == '__main__':

    main()