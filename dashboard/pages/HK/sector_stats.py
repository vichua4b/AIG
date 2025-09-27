import streamlit as st
import pandas as pd
import datahandler as dh
import plotly.express as px

SECTOR = ['Communication Services','Consumer Discretionary','Consumer Staples','Energy','Financials','Health Care','Industrials','Information Technology','Materials','Real Estate','Utilities']
INDUSTRY = ['Automobiles & Components', 'Banks', 'Capital Goods', 'Commercial & Professional Services', 'Consumer Discretionary Distribution & Retail', 'Consumer Durables & Apparel', 'Consumer Services', 'Consumer Staples Distribution & Retail', 'Energy', 'Equity Real Estate Investment Trusts (REITs)', 'Financial Services', 'Food Beverage & Tobacco', 'Health Care Equipment & Services', 'Household & Personal Products', 'Insurance', 'Materials', 'Media', 'Pharmaceuticals, Biotechnology & Life Sciences', 'Semiconductors & Semiconductor Equipment', 'Software & Services', 'Technology Hardware & Equipment', 'Telecommunication Services', 'Transportation', 'Utilities', ]

df = dh.get_constituents()
df['date'] = pd.to_datetime(df['date']).dt.date

sector_return = dh.sector_return(df)
industry_return = dh.industry_return(df)

cum_ret = (1 + sector_return['cap_weighted_ret'].unstack('sector')).cumprod()
fig = px.line(cum_ret)
fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))

st.header('Sector return')
st.plotly_chart(fig, use_container_width=True, theme="streamlit", key=None, on_select="ignore")

cum_ret_ind = (1 + industry_return['cap_weighted_ret'].unstack('industry_adj')).cumprod()
fig_ind = px.line(cum_ret_ind)
fig_ind.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))

st.header('Industry return')
st.plotly_chart(fig_ind, use_container_width=True, theme="streamlit", key=None, on_select="ignore")

st.header('Stock counts in each group')
col1, col2 = st.columns(2)

with col1:
    st.subheader('By sector')
    st.dataframe(sector_return['count'].unstack('sector').mean(), use_container_width=True)
with col2:
    st.subheader('By industry')
    st.dataframe(industry_return['count'].unstack('industry_adj').mean(), use_container_width=True)
