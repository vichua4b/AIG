import streamlit as st
import pandas as pd
import datahandler as dh
import plotly.graph_objects as go
import numpy as np

st.header('Royal clock')

region_options = ['CN', 'US']
region = st.radio('Region', region_options, horizontal=True)

col1, col2, col3, col4 = st.columns(4)
frequency_options = ['monthly', 'quarterly']
cpi_options = ['CPI', 'Core CPI']
lookback_options = [12, 24, 36]
zscore_options = [True, False]

with col1:
    freq = st.radio('Frequency', frequency_options)
with col2:
    cpi = st.radio('CPI', cpi_options)
with col3:
    lookback = st.radio('MA / zscore lookback', lookback_options)
with col4:
    zscore = st.radio('zscore', zscore_options)

points = st.slider('Points show', 1, 10) - 1 # -1 to include current

df = pd.read_csv(dh.DATA_FOLDER + region + '_econ_data.csv')
df['date_idx'] = pd.to_datetime(df['date'])
df.set_index('date_idx', inplace=True)
df.sort_index(ascending=True, inplace=True)
df['CPI_MA'] = df[cpi].rolling(window=lookback).mean()
df['OECD_MA'] = df['OECD'].rolling(window=lookback).mean()
df['dist_CPI'] = df[cpi] - df['CPI_MA']
df['dist_OECD'] = df['OECD'] - df['OECD_MA']

if freq == 'quarterly':
    df = df.resample('QE').last()

def zscore_func(value):
    return (value[-1] - np.mean(value)) / np.std(value)

if zscore:
    df['dist_CPI'] = df['dist_CPI'].rolling(window=lookback).apply(zscore_func)
    df['dist_OECD'] = df['dist_OECD'].rolling(window=lookback).apply(zscore_func)

to_plot = df.dropna()
time_points = to_plot['date']
x_values = to_plot['dist_CPI'] 
y_values = to_plot['dist_OECD'] 

# Create the frames for the animation with the lookback window
frames = [
    go.Frame(
        data=[
            go.Scatter(
                x=x_values[max(0, k - points):k+1],  # Adjust x values to show a window of `lookback`
                y=y_values[max(0, k - points):k+1],  # Adjust y values to show a window of `lookback`
                mode='lines+markers',
                marker=dict(
                    size=10,
                    color=['red' if i == len(x_values[max(0, k - points):k+1]) - 1 else 'lightblue' for i in range(len(x_values[max(0, k - points):k+1]))]
                )
            )
        ],
        name=str(k)
    ) for k in range(len(time_points))
]

# Create the initial scatter plot with no points
scatter = go.Scatter(
    x=[], y=[], mode='lines+markers', marker=dict(size=10)
)

# Layout with play button and a slider to control the lookback
layout = go.Layout(
    title='Clock history',
    yaxis=dict(range=[to_plot['dist_OECD'].min(), to_plot['dist_OECD'].max() + 5]),
    xaxis=dict(range=[to_plot['dist_CPI'].min(), to_plot['dist_CPI'].max()]),
    updatemenus=[{
        'buttons': [
            {
                'args': [None, {'frame': {'duration': 300, 'redraw': True}, 'fromcurrent': True}],
                'label': 'Play',
                'method': 'animate'
            },
            {
                'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}],
                'label': 'Pause',
                'method': 'animate'
            }
        ],
        'direction': 'left',
        'pad': {'r': 0, 't': 90},
        'showactive': False,
        'type': 'buttons',
        'x': 0.1,
        'xanchor': 'right',
        'y': 0,
        'yanchor': 'top'
    }],
    sliders=[{
        'active': 0,
        'yanchor': 'top',
        'xanchor': 'left',
        'currentvalue': {
            'font': {'size': 15},
            'visible': True,
            'xanchor': 'center',
            'prefix': 'Period: ',
            'visible': True
        },
        'transition': {'duration': 300, 'easing': 'cubic-in-out'},
        'pad': {'r': 50, 't': 30},
        'len': 0.9,
        'x': 0.1,
        'y': 0.0,
        'steps': [{
            'args': [
                [str(k)],
                {
                    'frame': {'duration': 0, 'redraw': True},
                    'mode': 'immediate',
                    'transition': {'duration': 0}
                }
            ],
            'label': f"{str(time_points[max(0, k-points)])} - {str(time_points[k])}",
            'method': 'animate'
        } for k in range(len(time_points))]
    }]
)

# Create the figure
fig = go.Figure(
    data=[scatter],
    layout=layout,
    frames=frames
)

fig.add_shape(
    type="line",
    x0=to_plot['dist_CPI'].min(), x1=to_plot['dist_CPI'].max() + 5,  # Extend across the entire x-axis
    y0=0, y1=0,
    line=dict(color="grey", width=2)
)

fig.add_shape(
    type="line",
    x0=0, x1=0,  # Extend from the bottom to the top of the y-axis
    y0=to_plot['dist_OECD'].min(), y1=to_plot['dist_OECD'].max() + 5,
    line=dict(color="grey", width=2)
)

fig.update_layout(
    annotations=[
        # Top-left corner
        dict(
            x=to_plot['dist_CPI'].min()/2, y=to_plot['dist_OECD'].max() + 5,
            xref="x", yref="y",
            text="Recovery",
            showarrow=False,
            # font=dict(size=12, color="black"),
            align="right"
        ),
        # Top-right corner
        dict(
            x=to_plot['dist_CPI'].max()/2, y=to_plot['dist_OECD'].max() + 5,
            xref="x", yref="y",
            text="Overheat",
            showarrow=False,
            # font=dict(size=12, color="black"),
            align="left"
        ),
        # Bottom-left corner
        dict(
            x=to_plot['dist_CPI'].min()/2, y=to_plot['dist_OECD'].min(),
            xref="x", yref="y",
            text="Reflation",
            showarrow=False,
            # font=dict(size=12, color="black"),
            align="right"
        ),
        # Bottom-right corner
        dict(
            x=to_plot['dist_CPI'].max()/2, y=to_plot['dist_OECD'].min(),
            xref="x", yref="y",
            text="Stagflation",
            showarrow=False,
            # font=dict(size=12, color="black"),
            align="left"
        )
    ]
)

st.plotly_chart(fig)

st.write('')
st.write('Underlying data')
st.dataframe(df[[cpi, 'OECD', 'CPI_MA', 'OECD_MA', 'dist_CPI', 'dist_OECD']])