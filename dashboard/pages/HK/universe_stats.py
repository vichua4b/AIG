import streamlit as st
import pandas as pd
import datahandler as dh
import plotly.express as px

SECTOR = ['Communication Services','Consumer Discretionary','Consumer Staples','Energy','Financials','Health Care','Industrials','Information Technology','Materials','Real Estate','Utilities']
INDUSTRY = ['Automobiles & Components', 'Banks', 'Capital Goods', 'Commercial & Professional Services', 'Consumer Discretionary Distribution & Retail', 'Consumer Durables & Apparel', 'Consumer Services', 'Consumer Staples Distribution & Retail', 'Energy', 'Equity Real Estate Investment Trusts (REITs)', 'Financial Services', 'Food Beverage & Tobacco', 'Health Care Equipment & Services', 'Household & Personal Products', 'Insurance', 'Materials', 'Media', 'Pharmaceuticals, Biotechnology & Life Sciences', 'Semiconductors & Semiconductor Equipment', 'Software & Services', 'Technology Hardware & Equipment', 'Telecommunication Services', 'Transportation', 'Utilities', ]

df = dh.get_constituents()
df['date'] = pd.to_datetime(df['date']).dt.date

universe_returns = dh.universe_return(df)
cum_ret = (1 + universe_returns['cap_weighted_ret']).cumprod()
fig = px.line(cum_ret)
fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))

st.header('Universe return')
st.plotly_chart(fig, use_container_width=True, theme="streamlit", key=None, on_select="ignore")

country_returns = dh.universe_return_by_country(df)
cum_ret_ctry = (1 + country_returns['cap_weighted_ret'].unstack('country')).cumprod()
fig_ctry = px.line(cum_ret_ctry)
fig_ctry.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))

st.header('Country return')
st.plotly_chart(fig_ctry, use_container_width=True, theme="streamlit", key=None, on_select="ignore")

stock_count = df.groupby(['date', 'country'])['country'].count().unstack('country')
fig_count = px.bar(stock_count)
st.header('No of stock')
st.plotly_chart(fig_count, use_container_width=True, theme="streamlit", key=None, on_select="ignore")

df = df[['date', 'home_code', 'sector', 'industry_adj', 'MCAP_LOCAL']]
df.rename(columns={'date': 'Date', 'home_code': 'Ticker', 'sector': 'Sector', 'industry_adj': 'Industry', 'MCAP_LOCAL': 'Market Cap (local $)'}, inplace = True)

col1, col2 = st.columns(2)
with col1:
    sdate = st.date_input('Start date', min_value=df['Date'].min(), max_value=df['Date'].max())
with col2:
    edate = st.date_input('End date', min_value=df['Date'].min(), max_value=df['Date'].max())

selected_sector = st.multiselect('Sector', SECTOR, default=SECTOR)
selected_industry = st.multiselect('Industry', INDUSTRY, default=INDUSTRY)

filtered_df = df[(df['Date'] >= sdate) & (df['Date'] <= edate) & ((df['Sector'].isin(selected_sector)) | (df['Industry'].isin(selected_industry)))]

st.dataframe(filtered_df, hide_index=True, use_container_width=True)
