import streamlit as st
import pandas as pd
import datahandler as dh
import backtest as bt
import numpy as np
import plots as pt

df = dh.get_constituents()
df['date'] = pd.to_datetime(df['date']).dt.date

selected_regime = st.selectbox('Regime config', dh.REGIME_FILE_OPTION)
regime = dh.get_regime(selected_regime)

selected_bt = st.multiselect('Backtest config', dh.INDUSTRY_GROUPS_OPTION, default='Ind Gp +1M-0-ALL')
industry_return = dh.industry_return(df)

bt_data = pd.DataFrame()
summary_data = pd.DataFrame()
summary_data_p1 = pd.DataFrame()
summary_data_p2 = pd.DataFrame()
stats_data = pd.DataFrame()
stats_data_p1 = pd.DataFrame()
stats_data_p2 = pd.DataFrame()
for i in selected_bt:
    selected_industry = dh.industry_group_selection(i)
    result_incl, result_excl, result_incl_ex_stag, result_excl_ex_stag, market = bt.run_backtest(selected_industry, regime, industry_return)

    tmp = pd.DataFrame()
    tmp['favour'] = (result_incl.loc[result_incl.index >= '2005-11-01']['favour_mean']).cumsum()
    tmp['avoid'] = (result_excl.loc[result_excl.index >= '2005-11-01']['avoid_mean']).cumsum()
    tmp['market'] = (market.loc[market.index >= '2005-11-01'].cumsum()) if i == selected_bt[0] else None
    tmp['date'] = tmp.index
    tmp['OECD_CH'] = result_incl.loc[result_incl.index >= '2005-11-01']['OECD_CH']
    tmp['BT'] = i
    bt_data = pd.concat([bt_data, tmp])

    tmp2 = bt.summary_table(result_incl.loc[result_incl.index >= '2005-11-01'], 
                            result_excl.loc[result_excl.index >= '2005-11-01'], 
                            market.loc[market.index >= '2005-11-01'])
    tmp2['BT'] = i
    summary_data = pd.concat([summary_data, tmp2])

    tmp2 = bt.summary_table(result_incl.loc[(result_incl.index >= '2005-11-01') & (result_incl.index < '2023-01-01')], 
                            result_excl.loc[(result_excl.index >= '2005-11-01') & (result_excl.index < '2023-01-01')], 
                            market.loc[(market.index >= '2005-11-01') & (market.index < '2023-01-01')])
    tmp2['BT'] = i
    summary_data_p1 = pd.concat([summary_data_p1, tmp2])

    tmp2 = bt.summary_table(result_incl.loc[result_incl.index >= '2023-01-01'], 
                            result_excl.loc[result_excl.index >= '2023-01-01'], 
                            market.loc[market.index >= '2023-01-01'])
    tmp2['BT'] = i
    summary_data_p2 = pd.concat([summary_data_p2, tmp2])

    tmp_stats = bt.bt_stats(result_incl.loc[result_incl.index >= '2005-11-01'],
                            result_excl.loc[result_excl.index >= '2005-11-01'],
                            market.loc[market.index >= '2005-11-01'])
    tmp_stats['BT'] = i
    stats_data = pd.concat([stats_data, tmp_stats])

    tmp_stats = bt.bt_stats(result_incl.loc[(result_incl.index >= '2005-11-01') & (result_incl.index < '2023-01-01')],
                            result_excl.loc[(result_excl.index >= '2005-11-01') & (result_excl.index < '2023-01-01')],
                            market.loc[(market.index >= '2005-11-01') & (market.index < '2023-01-01')])
    tmp_stats['BT'] = i
    stats_data_p1 = pd.concat([stats_data_p1, tmp_stats])

    tmp_stats = bt.bt_stats(result_incl.loc[result_incl.index >= '2023-01-01'],
                            result_excl.loc[result_excl.index >= '2023-01-01'],
                            market.loc[market.index >= '2023-01-01'])
    tmp_stats['BT'] = i
    stats_data_p2 = pd.concat([stats_data_p2, tmp_stats])

to_plot = bt_data.melt(id_vars = ['date', 'BT', 'OECD_CH'], value_vars= ['favour', 'avoid', 'market'])
to_plot['label'] = np.where(to_plot['variable'] != 'market', to_plot['BT'] + "-" + to_plot['variable'], 'market')
to_plot = to_plot[to_plot['value'].notna()]

st.subheader('Cumulative return')
st.plotly_chart(pt.plot_multi(to_plot), use_container_width=True, theme="streamlit", key=None, on_select="ignore")

st.subheader('Average return in each period')
summary_data = summary_data.reset_index().set_index(['BT', 'OECD_CH']).unstack('BT')
summary_data = summary_data.iloc[:, (len(selected_bt) - 1):]
summary_data = ((summary_data*100).transpose())
st.dataframe(summary_data.style.format('{:.2f}%'), use_container_width=True)

picks = ['favour', 'avoid']
pick = st.radio('Type', picks, horizontal=True)
st.plotly_chart(pt.plot_summary(summary_data, pick))

st.subheader('Average return in each period (prior 2023)')
summary_data_p1 = summary_data_p1.reset_index().set_index(['BT', 'OECD_CH']).unstack('BT')
summary_data_p1 = summary_data_p1.iloc[:, (len(selected_bt) - 1):]
summary_data_p1 = ((summary_data_p1*100).transpose())
st.dataframe(summary_data_p1.style.format('{:.2f}%'), use_container_width=True)

pick_p1 = st.radio('Type 1', picks, horizontal=True)
st.plotly_chart(pt.plot_summary(summary_data_p1, pick_p1))

st.subheader('Average return in each period (2023 onwards)')
summary_data_p2 = summary_data_p2.reset_index().set_index(['BT', 'OECD_CH']).unstack('BT')
summary_data_p2 = summary_data_p2.iloc[:, (len(selected_bt) - 1):]
summary_data_p2 = ((summary_data_p2*100).transpose())
st.dataframe(summary_data_p2.style.format('{:.2f}%'), use_container_width=True)

pick_p2 = st.radio('Type 2', picks, horizontal=True)
st.plotly_chart(pt.plot_summary(summary_data_p2, pick_p2))

stats_data.reset_index(inplace=True, names=['metrics'])
stats_data.set_index(['BT','metrics'], inplace=True)
stats_data_p1.reset_index(inplace=True, names=['metrics'])
stats_data_p1.set_index(['BT','metrics'], inplace=True)
stats_data_p2.reset_index(inplace=True, names=['metrics'])
stats_data_p2.set_index(['BT','metrics'], inplace=True)

st.subheader('Backtest stats (favour)')
col1, col2 = st.columns(2)
with col1:
    st.write('Prior 2023')
    f = stats_data_p1[['Favour']].unstack('metrics')
    f = f.droplevel(0, axis=1)
    mkt = stats_data_p1[['Market']].loc[selected_bt[0]].T
    st.dataframe(pd.concat([f, mkt]))

with col2:
    st.write('2023 onwards')
    f2 = stats_data_p2[['Favour']].unstack('metrics')
    f2 = f2.droplevel(0, axis=1)
    mkt2 = stats_data_p2[['Market']].loc[selected_bt[0]].T
    st.dataframe(pd.concat([f2, mkt2]))

st.subheader('Backtest stats (avoid)')
col1_a, col2_a = st.columns(2)
with col1_a:
    st.write('Prior 2023')
    f = stats_data_p1[['Avoid']].unstack('metrics')
    f = f.droplevel(0, axis=1)
    mkt = stats_data_p1[['Market']].loc[selected_bt[0]].T
    st.dataframe(pd.concat([f, mkt]))

with col2_a:
    st.write('2023 onwards')
    f2 = stats_data_p2[['Avoid']].unstack('metrics')
    f2 = f2.droplevel(0, axis=1)
    mkt2 = stats_data_p2[['Market']].loc[selected_bt[0]].T
    st.dataframe(pd.concat([f2, mkt2]))