import streamlit as st
import pandas as pd
import datahandler as dh
import backtest as bt
import quantstats as qs
import plots as pt

df = dh.get_constituents()
df['date'] = pd.to_datetime(df['date']).dt.date

selected_regime = st.selectbox('Regime config', dh.REGIME_FILE_OPTION)
regime = dh.get_regime(selected_regime)

selected_bt = st.selectbox('Backtest config', dh.INDUSTRY_GROUPS_OPTION)
selected_industry = dh.industry_group_selection(selected_bt)
industry_return = dh.industry_return(df)

st.subheader('Selection: ' + selected_bt)
# selected_industry_style = selected_industry.style.map(lambda x: f"background-color: {'green' if x > 0 else 'red' if x < 0 else None}")
st.dataframe(selected_industry.style.format('{:.1f}'))
result_incl, result_excl, result_incl_ex_stag, result_excl_ex_stag, market = bt.run_backtest(selected_industry, regime, industry_return)

st.subheader('Cumulative return')
st.plotly_chart(pt.plot(result_incl.loc[result_incl.index >= '2005-11-01'], 
                        result_excl.loc[result_excl.index >= '2005-11-01'], 
                        market.loc[market.index >= '2005-11-01']), 
                use_container_width=True, theme="streamlit", key=None, on_select="ignore")

st.subheader('Cumulative return (ex Stagflation)')
st.plotly_chart(pt.plot(result_incl_ex_stag.loc[result_incl_ex_stag.index >= '2005-11-01'], 
                        result_excl_ex_stag.loc[result_excl_ex_stag.index >= '2005-11-01'], 
                        market.loc[market.index >= '2005-11-01']), 
                use_container_width=True, theme="streamlit", key=None, on_select="ignore")

col1, col2, col3 = st.columns(3)

with col1:
    st.write('Average return in each period')
    summary = bt.summary_table(result_incl, result_excl, market)
    st.dataframe((summary*100).style.format('{:.2f}%'))

with col2:
    st.write('Backtest stats')
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
    # Add in market
    stats_m = {'cagr': qs.stats.cagr(market.loc[market.index >= '2005-11-01'], compounded=False),
                'volatility': qs.stats.volatility(market.loc[market.index >= '2005-11-01']),
                'sharpe': qs.stats.sharpe(market.loc[market.index >= '2005-11-01']),
                'mdd': qs.stats.max_drawdown(market.loc[market.index >= '2005-11-01'])
                }
    st.dataframe(pd.DataFrame([stats_m, stats, stats_a], index=['Market', 'Favour', 'Avoid']).transpose())

with col3:
    st.write('Backtest stats (ex Stag)')
    stats = {'cagr': qs.stats.cagr(result_incl_ex_stag.loc[result_incl_ex_stag.index >= '2000-11-01']['favour_mean'], compounded=False),
             'volatility': qs.stats.volatility(result_incl_ex_stag.loc[result_incl_ex_stag.index >= '2000-11-01']['favour_mean']),
             'sharpe': qs.stats.sharpe(result_incl_ex_stag.loc[result_incl_ex_stag.index >= '2000-11-01']['favour_mean']),
             'mdd': qs.stats.max_drawdown(result_incl_ex_stag.loc[result_incl_ex_stag.index >= '2000-11-01']['favour_mean'])
            }
    stats_a = {'cagr': qs.stats.cagr(result_excl_ex_stag.loc[result_excl_ex_stag.index >= '2000-11-01']['avoid_mean'], compounded=False),
             'volatility': qs.stats.volatility(result_excl_ex_stag.loc[result_excl_ex_stag.index >= '2000-11-01']['avoid_mean']),
             'sharpe': qs.stats.sharpe(result_excl_ex_stag.loc[result_excl_ex_stag.index >= '2000-11-01']['avoid_mean']),
             'mdd': qs.stats.max_drawdown(result_excl_ex_stag.loc[result_excl_ex_stag.index >= '2000-11-01']['avoid_mean'])
            }
    # Add in market
    stats_m = {'cagr': qs.stats.cagr(market.loc[market.index >= '2005-11-01'], compounded=False),
                'volatility': qs.stats.volatility(market.loc[market.index >= '2005-11-01']),
                'sharpe': qs.stats.sharpe(market.loc[market.index >= '2005-11-01']),
                'mdd': qs.stats.max_drawdown(market.loc[market.index >= '2005-11-01'])
                }
    st.dataframe(pd.DataFrame([stats_m, stats, stats_a], index=['Market', 'Favour', 'Avoid']).transpose())

st.subheader('Favour monthly return')
fig = qs.plots.monthly_returns(result_incl.loc[result_incl.index >= '2000-11-01']['favour_mean'], compounded=False, show=False)
st.pyplot(fig)

st.subheader('Avoid monthly return')
fig_avoid = qs.plots.monthly_returns(result_excl.loc[result_excl.index >= '2000-11-01']['avoid_mean'], compounded=False, show=False)
st.pyplot(fig_avoid)
