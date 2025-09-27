import streamlit as st
import pandas as pd
import datahandler as dh
import plotly.express as px
import numpy as np

etf_prices = dh.load_etf_prices()
indicator_prices = dh.load_indicator_prices()

etf_list = etf_prices.columns.tolist()
indicator_list = indicator_prices.columns.tolist()

# combine etf and indicator prices
df = pd.merge(etf_prices, indicator_prices, left_index=True, right_index=True, how='inner')
# returns
df = df.pct_change().dropna().reset_index()

st.header('Correlation matrix')
# select months lag
indicator_months_lag = st.slider('Indicator Months lag', 0, 12, 0)
for indicator in indicator_list:
    df[indicator] = df[indicator].shift(indicator_months_lag)

# select start and end date
col1, col2 = st.columns(2)
with col1:
    sdate = st.date_input('Start date', min_value=df['date'].min(), max_value=df['date'].max(), value=df['date'].min())
with col2:
    edate = st.date_input('End date', min_value=df['date'].min(), max_value=df['date'].max(), value=df['date'].max())

# show raw table to check
# st.dataframe(df, hide_index=True, use_container_width=True)

filtered_df = df[(df['date'] >= pd.to_datetime(sdate)) & (df['date'] <= pd.to_datetime(edate))]
correlation = filtered_df.corr()
# drop date
correlation = correlation.drop(columns=['date'], index=['date'])
# correlation number format
correlation = correlation.round(2)

# correlation heatmap
# mask the upper triangle
mask = np.triu(np.ones_like(correlation, dtype=bool))
correlation = correlation.mask(mask)
fig = px.imshow(correlation, text_auto=True, aspect="auto", color_continuous_scale='RdBu', zmin=-1, zmax=1)
fig.update_layout(title='Correlation matrix', xaxis_title='Assets', yaxis_title='Assets')

st.plotly_chart(fig, use_container_width=True, theme="streamlit", key=None, on_select="ignore")

# Rolling correlation
st.header('Rolling correlation')
st.write('Indicator months lag (selected above): ', indicator_months_lag)
horizon = st.slider('Rolling window (month)', 6, 36, 6)

# select etf and indicator to show
r_col1, r_col2 = st.columns(2)
with r_col1:
    selected_etf = st.selectbox('Select ETF', etf_list, index=0)
with r_col2:
    selected_indicator = st.selectbox('Select Indicator', indicator_list, index=0)
rolling_corr = df[['date', selected_etf, selected_indicator]].copy()
rolling_corr['correlation'] = rolling_corr[selected_etf].rolling(window=horizon).corr(rolling_corr[selected_indicator])
rolling_corr = rolling_corr.drop(columns=[selected_etf, selected_indicator])
rolling_corr = rolling_corr.dropna()

# show rolling_corr to check
# st.dataframe(rolling_corr, hide_index=True, use_container_width=True)

fig2 = px.line(rolling_corr, x='date', y='correlation')
fig2.update_layout(title=f'Rolling correlation between {selected_etf} and {selected_indicator}', xaxis_title='Date', yaxis_title='Correlation')
st.plotly_chart(fig2, use_container_width=True, theme="streamlit", key=None, on_select="ignore")
