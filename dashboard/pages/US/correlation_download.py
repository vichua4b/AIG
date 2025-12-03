import streamlit as st
import pandas as pd
import datahandler as dh
import plotly.express as px
import numpy as np

if 'generate_excel' not in st.session_state:
    st.session_state['generate_excel'] = False

etf_prices, etf_returns = dh.load_etf_prices()
indicator_prices, indicator_returns, freq = dh.load_indicator_prices()
name_ref = dh.load_name_ref()
name_map = dict(zip(name_ref['Ticker'], name_ref['Name']))
bull_bear = dh.load_us_bull_bear_data()

if st.button("Refresh cached data"):
    st.cache_data.clear()
    st.rerun()

# drop those columns in indicator_prices that are in etf_prices except date
indicator_prices = indicator_prices.drop(columns=[col for col in indicator_prices.columns if col in etf_prices.columns and col != 'date'])
indicator_returns = indicator_returns.drop(columns=[col for col in indicator_returns.columns if col in etf_prices.columns and col != 'date'])

etf_list = etf_prices.columns.tolist()
indicator_list = indicator_prices.columns.tolist()

indicator_display = [f"{name_map.get(indicator, indicator)}" for indicator in indicator_list]
indicator_display_map = dict(zip(indicator_display, indicator_list))
indicator_map = dict(zip(indicator_list, indicator_display))

# combine etf and indicator prices
df = pd.merge(etf_prices, indicator_prices, left_index=True, right_index=True, how='inner')
# returns
df_ret = pd.merge(etf_returns, indicator_returns, left_index=True, right_index=True, how='inner')
df_ret.reset_index(inplace=True)

# select start and end date
col1, col2 = st.columns(2)
with col1:
    sdate = st.date_input('Start date', min_value=df_ret['date'].min(), max_value=df_ret['date'].max(), value=df_ret['date'].min())
with col2:
    edate = st.date_input('End date', min_value=df_ret['date'].min(), max_value=df_ret['date'].max(), value=df_ret['date'].max())

if st.button("Generate ALL correlation matrix Excel file"):
    st.session_state['generate_excel'] = True

import io
if st.session_state['generate_excel']:
    with st.spinner("Generating Excel file..."):
        df_ret_filtered = df_ret[(df_ret['date'] >= pd.to_datetime(sdate)) & (df_ret['date'] <= pd.to_datetime(edate))]
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for i in range(0, 48+1, 3):
                all_data = df_ret_filtered.copy()
                for indicator in indicator_list:
                    all_data[indicator] = all_data[indicator].shift(i)
                all_correlation = all_data.corr()
                all_correlation = all_correlation.drop(columns=['date'], index=['date'])
                all_correlation = all_correlation.loc[etf_list, indicator_list]

                # map column to indicator_display_map
                all_correlation.columns = [indicator_map.get(col, "col") for col in all_correlation.columns]
                # sort index and columns
                all_correlation = all_correlation.sort_index().sort_index(axis=1)
                all_correlation = all_correlation.reset_index().melt(id_vars='index')
                all_correlation.columns = ['ETF', 'Indicator', 'Correlation']
                # drop NaN rows
                all_correlation = all_correlation.dropna()
                # Add sdate and edate and month lag info to the csv file
                all_correlation['sdate'] = sdate.strftime('%Y-%m-%d')
                all_correlation['edate'] = edate.strftime('%Y-%m-%d')
                # rearrange columns
                all_correlation = all_correlation[['sdate', 'edate', 'ETF', 'Indicator', 'Correlation']]
                all_correlation.to_excel(writer, sheet_name=f'lag_{i}m', index=False)
        output.seek(0)
    st.download_button(
        label="Download ALL correlation matrix as Excel",
        data=output.getvalue(),
        file_name=f'correlation_{sdate}_{edate}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    st.session_state['generate_excel'] = False