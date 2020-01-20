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

DATA_URI_QOE = '../logs/test.csv'
FEATURES = ['Time',
            'SocketID',
            'pktFlowWindow',
            'pktCongestionWindow',
            'pktFlightSize',
            'msRTT','mbpsBandwidth','mbpsMaxBW','pktSent','pktSndLoss','pktSndDrop','pktRetrans','byteSent','byteSndDrop','mbpsSendRate',
            'usPktSndPeriod','pktRecv','pktRcvLoss','pktRcvDrop','pktRcvRetrans','pktRcvBelated','byteRecv','byteRcvLoss','byteRcvDrop',
            'mbpsRecvRate','RCVLATENCYms','pktSndFilterExtra','pktRcvFilterExtra','pktRcvFilterSupply','pktRcvFilterLoss'
]
def load_data(data_uri, nrows):
    """
    Function to retrieve data from a given file or URL
    in a Pandas DataFrame suitable for model training.
    nrows limits the amount of data displayed for optimization
    """
    data_df = pd.read_csv(data_uri, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data_df.rename(lowercase, axis='columns', inplace=True)

    return data_df

def plot_3D(title, z_metric, z_axis, color_metric, df_aggregated):
    """
    Function to plot and format a 3D scatterplot from the aggregated dataframe
    """

    fig = go.Figure(data=go.Scatter3d(x=df_aggregated['dimension_y'],
                                      y=df_aggregated['size'],
                                      z=df_aggregated[z_metric],
                                      mode='markers',
                                      marker=dict(size=1,
                                                  color=df_aggregated[color_metric],
                                                  opacity=0.8
                                                 )
                                      ))
    fig.update_layout(title=title,
                      scene = dict(xaxis_title="Vertical Resolution",
                                   yaxis_title="File Size",
                                   zaxis_title=z_axis),
                      font=dict(size=15),
                      legend=go.layout.Legend(x=0,
                                              y=1,
                                              traceorder="normal",
                                              font=dict(family="sans-serif",
                                                        size=12,
                                                        color="black"
                                                        ),
                                              bgcolor="LightSteelBlue",
                                              bordercolor="Black",
                                              borderwidth=2
                                            )
                     )
    st.plotly_chart(fig, width=1000, height=1000)

def plot_scatter(title, x_metric, y_metrics, x_axis_title, y_axis_title, df_aggregated, line=False):
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

    # if line:
    #     trace_line = go.Scatter(x=np.arange(0, 1.1, 0.1),
    #                             y=np.arange(0, 1.1, 0.1),
    #                             mode='lines',
    #                             name='y=x')
    #     data.append(trace_line)
    # else:
    #     shapes.append({'type': 'line',
    #                 'xref': 'x',
    #                 'yref': 'y',
    #                 'x0': 0,
    #                 'y0': 0,
    #                 'x1': 0,
    #                 'y1': 1000})

    fig = go.Figure(data=data)
    fig.update_layout(title=title,
                      xaxis_title=x_axis_title,
                      yaxis_title=y_axis_title,
                      legend=go.layout.Legend(x=0,
                                              y=1,
                                            traceorder="normal",
                                            font=dict(family="sans-serif",
                                                    size=12,
                                                    color="black"
                                                    ),
                                            bgcolor="LightSteelBlue",
                                            bordercolor="Black",
                                            borderwidth=2
                                             ),
                                             shapes=shapes
                    )
    st.plotly_chart(fig, width=1000, height=1000)

def plot_histogram(metric, x_title, df_aggregated):
    """
    Function to plot and format a histogram from the aggregated dataframe
    """
    resolutions = list(df_aggregated['dimension_y'].unique())
    resolutions.sort()
    data = []
    for res in resolutions:
        data.append(go.Histogram(x=df_aggregated[metric][df_aggregated['dimension_y'] == res],
                                 name='{}p'.format(res),
                                 autobinx=False,
                                 nbinsx=500,
                                 opacity=0.75))
    shapes = list()
    # shapes.append({'type': 'line',
    #             'xref': 'x',
    #             'yref': 'y',
    #             'x0': 0,
    #             'y0': 0,
    #             'x1': 0,
    #             'y1': 1000})

    fig = go.Figure(data=data)
    fig.layout.update(barmode='overlay',
                      title='Histogram of legit assets',
                      xaxis_title_text=x_title,
                      yaxis_title_text='Count',
                      legend=go.layout.Legend(x=1,
                            y=1,
                            traceorder="normal",
                            font=dict(family="sans-serif",
                                    size=12,
                                    color="black"
                                                        )
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
 
    st.plotly_chart(fig, width=1000, height=1000)

def main():
    """
    Main function to train and evaluate tamper and QoE models
    """
    # Get QoE pristine dataset (no attacks)
    df_qoe = load_data(DATA_URI_QOE, 50000)

    df_qoe = df_qoe.loc[:, (df_qoe != 0).any(axis=0)]
    # # Display datasets
    st.subheader('Raw QoE data')
    st.write(df_qoe.head(100), df_qoe.shape)

    st.subheader('Describe QoE data')
    st.write(df_qoe.describe())
    # # Display correlation between measured distance to decision function, resolution and size.
    # plot_3D('OC-SVM Classifier', 'ocsvm_dist', 'Distance to Decision Function', 'tamper', df_plots_aggregated)
    # # Display histogram of non-tampered assets
    # plot_histogram('ocsvm_dist', 'Distance to decision function', df_aggregated)
    # # Display difference between predicted ssim and measured ssim
    # # according to their tamper classification
    plot_scatter('MSRTT time series',
                 'time',
                 df_qoe.columns,
                 'Time',
                 'MSRTT',
                 df_qoe,
                 line=True)
    # # Display correlation matrix
    plot_correlation_matrix(df_qoe)

if __name__ == '__main__':

    main()