import streamlit as st
import pandas as pd
import datahandler as dh
import backtest as bt
import plotly.express as px
import quantstats as qs
import numpy as np

df = dh.get_constituents()
df['date'] = pd.to_datetime(df['date']).dt.date

selected_regime = st.selectbox('Regime config', ['Core CPI + OECD', 'CPI + OECD'])
regime = dh.get_regime('core_cpi' if selected_regime == 'Core CPI + OECD' else 'cpi')

selected_bt = st.multiselect('Backtest config', dh.INDUSTRY_GROUPS_OPTION, default='Ind Gp +1M-0-ALL')
industry_return = dh.industry_return(df)

bt_data = pd.DataFrame()
summary_data = pd.DataFrame()
stats_data = pd.DataFrame()
stats_a_data = pd.DataFrame()
for i in selected_bt:
    selected_industry = dh.industry_group_selection(i)
    result_incl, result_excl, result_incl_ex_stag, result_excl_ex_stag, market = bt.run_backtest(selected_industry, regime, industry_return)

    tmp = pd.DataFrame()
    tmp['favour'] = (result_incl.loc[result_incl.index >= '2005-11-01']['favour_mean']).cumsum()
    tmp['avoid'] = (result_excl.loc[result_excl.index >= '2005-11-01']['avoid_mean']).cumsum()
    tmp['market'] = (market.loc[market.index >= '2005-11-01'].cumsum()) if i == selected_bt[0] else None
    tmp['date'] = tmp.index
    tmp['BT'] = i

    tmp2 = bt.summary_table(result_incl, result_excl, market)
    tmp2['BT'] = i

    stats = {'cagr': qs.stats.cagr(result_incl.loc[result_incl.index >= '2000-11-01']['favour_mean'], compounded=False),
             'volatility': qs.stats.volatility(result_incl.loc[result_incl.index >= '2000-11-01']['favour_mean']),
             'sharpe': qs.stats.sharpe(result_incl.loc[result_incl.index >= '2000-11-01']['favour_mean']),
             'mdd': qs.stats.max_drawdown(result_incl.loc[result_incl.index >= '2000-11-01']['favour_mean'])
            }
    stats_a = {'cagr': qs.stats.cagr(result_excl.loc[result_excl.index >= '2000-11-01']['avoid_mean'], compounded=False),
             'volatility': qs.stats.volatility(result_excl.loc[result_excl.index >= '2000-11-01']['avoid_mean']),
             'sharpe': qs.stats.sharpe(result_excl.loc[result_excl.index >= '2000-11-01']['avoid_mean']),
             'mdd': qs.stats.max_drawdown(result_excl.loc[result_excl.index >= '2000-11-01']['avoid_mean'])
            }
    stats_data = pd.concat([stats_data, pd.DataFrame(stats, index=[i])])
    stats_a_data = pd.concat([stats_a_data, pd.DataFrame(stats_a, index=[i])])

    bt_data = pd.concat([bt_data, tmp])
    summary_data = pd.concat([summary_data, tmp2])

to_plot = bt_data.melt(id_vars = ['date', 'BT'], value_vars= ['favour', 'avoid', 'market'])
to_plot['label'] = np.where(to_plot['variable'] != 'market', to_plot['BT'] + "-" + to_plot['variable'], 'market')

fig = px.line(to_plot, x='date' , y='value', color='label')
fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))

st.subheader('Cumulative return')
st.plotly_chart(fig, use_container_width=True, theme="streamlit", key=None, on_select="ignore")

summary_data = summary_data.reset_index().set_index(['BT', 'OECD_CH']).unstack('BT')
summary_data = summary_data.iloc[:, (len(selected_bt) - 1):]
st.subheader('Average return in each period')
st.dataframe(((summary_data*100).transpose().style.format('{:.2f}%')), use_container_width=True)

st.subheader('Backtest stats (favour)')
# Add in market
stats = {'cagr': qs.stats.cagr(market.loc[market.index >= '2005-11-01'], compounded=False),
             'volatility': qs.stats.volatility(market.loc[market.index >= '2005-11-01']),
             'sharpe': qs.stats.sharpe(market.loc[market.index >= '2005-11-01']),
             'mdd': qs.stats.max_drawdown(market.loc[market.index >= '2005-11-01'])
            }
stats_data = pd.concat([stats_data, pd.DataFrame(stats, index=['market'])])
st.dataframe(stats_data, use_container_width=True)