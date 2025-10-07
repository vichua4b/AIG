import streamlit as st
import pandas as pd
import datahandler as dh
import plotly.express as px
import numpy as np

etf_prices = dh.load_etf_prices()
indicator_prices = dh.load_indicator_prices()
name_ref = dh.load_name_ref()
name_map = dict(zip(name_ref['Ticker'], name_ref['Name']))

# drop those columns in indicator_prices that are in etf_prices except date
indicator_prices = indicator_prices.drop(columns=[col for col in indicator_prices.columns if col in etf_prices.columns and col != 'date'])

etf_list = etf_prices.columns.tolist()
indicator_list = indicator_prices.columns.tolist()

etf_display = [f"{etf} - {name_map.get(etf, '')}" for etf in etf_list]
etf_display_map = dict(zip(etf_display, etf_list))
indicator_display = [f"{indicator} - {name_map.get(indicator, '')}" for indicator in indicator_list]
indicator_display_map = dict(zip(indicator_display, indicator_list))

# combine etf and indicator prices
df = pd.merge(etf_prices, indicator_prices, left_index=True, right_index=True, how='inner')
# returns
df_ret = df.pct_change(fill_method=None).pct_change().reset_index()

st.header('Correlation matrix')
# select months lag
indicator_months_lag = st.slider('Indicator Months lag', 0, 12, 0)
for indicator in indicator_list:
    df_ret[indicator] = df_ret[indicator].shift(indicator_months_lag)

# select start and end date
col1, col2 = st.columns(2)
with col1:
    sdate = st.date_input('Start date', min_value=df_ret['date'].min(), max_value=df_ret['date'].max(), value=df_ret['date'].min())
    multiSelect_etf_display = st.multiselect('Select ETF', etf_display, default=etf_display[:5])
    multiSelect_etf = [etf_display_map[etf] for etf in multiSelect_etf_display]
with col2:
    edate = st.date_input('End date', min_value=df_ret['date'].min(), max_value=df_ret['date'].max(), value=df_ret['date'].max())
    multiSelect_indicator_display = st.multiselect('Select Indicator', indicator_display, default=indicator_display[:5])
    multiSelect_indicator = [indicator_display_map[indicator] for indicator in multiSelect_indicator_display]

# show raw table to check
# st.dataframe(df, hide_index=True, use_container_width=True)

filtered_df = df_ret[(df_ret['date'] >= pd.to_datetime(sdate)) & (df_ret['date'] <= pd.to_datetime(edate))]
correlation = filtered_df.corr()
# drop date
correlation = correlation.drop(columns=['date'], index=['date'])
# correlation number format
correlation = correlation.round(2)
# only include combination of etf and indicator
correlation = correlation.loc[multiSelect_etf, multiSelect_indicator]

# correlation heatmap
# mask the upper triangle
# mask = np.triu(np.ones_like(correlation, dtype=bool))
# correlation = correlation.mask(mask)
fig = px.imshow(correlation, text_auto=True, aspect="auto", color_continuous_scale='RdBu', zmin=-1, zmax=1)
fig.update_layout(title='Correlation matrix', xaxis_title='Indicator', yaxis_title='ETF')

st.plotly_chart(fig, use_container_width=True, theme="streamlit", key=None, on_select="ignore")

# Rolling correlation
st.header('Rolling correlation')
st.write('Indicator months lag (selected above): ', indicator_months_lag)
horizon = st.slider('Rolling window (month)', 6, 36, 6, 6)

# select etf and indicator to show
r_col1, r_col2 = st.columns(2)
with r_col1:
    selected_etf_display = st.selectbox('Select ETF', etf_display, index=0)
    selected_etf = etf_display_map[selected_etf_display]
with r_col2:
    selected_indicator_display = st.selectbox('Select Indicator', indicator_display, index=0)
    selected_indicator = indicator_display_map[selected_indicator_display]
rolling_corr = df_ret[['date', selected_etf, selected_indicator]].copy()
rolling_corr['correlation'] = rolling_corr[selected_etf].rolling(window=horizon).corr(rolling_corr[selected_indicator])
rolling_corr = rolling_corr.drop(columns=[selected_etf, selected_indicator])
rolling_corr = rolling_corr.dropna()

# show rolling_corr to check
# st.dataframe(rolling_corr, hide_index=True, use_container_width=True)

fig2 = px.line(rolling_corr, x='date', y='correlation')
fig2.update_layout(title=f'Rolling correlation between {selected_etf} and {selected_indicator}', xaxis_title='Date', yaxis_title='Correlation')
st.plotly_chart(fig2, use_container_width=True, theme="streamlit", key=None, on_select="ignore")


# Price history
st.header('Price history')
prices = df[[selected_etf, selected_indicator]].copy()
fig3 = px.line(prices, x=df.index, y=[selected_etf, selected_indicator])
fig3.update_layout(title=f'Price history of {selected_etf} and {selected_indicator}', xaxis_title='Date', yaxis_title='Price')
st.plotly_chart(fig3, use_container_width=True, theme="streamlit", key=None, on_select="ignore")