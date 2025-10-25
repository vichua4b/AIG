import streamlit as st
import pandas as pd
import datahandler as dh
import plotly.express as px
import numpy as np

etf_prices, etf_returns = dh.load_etf_prices()
indicator_prices, indicator_returns, freq = dh.load_indicator_prices()
name_ref = dh.load_name_ref()
name_map = dict(zip(name_ref['Ticker'], name_ref['Name']))

bull_bear = dh.load_us_bull_bear_data()
def get_bull_bear_color(comment):
    if '牛' in comment:
        return 'rgba(0,200,0,0.15)'  # light green for bull
    elif '熊' in comment:
        return 'rgba(200,0,0,0.15)'  # light red for bear
    else:
        return 'rgba(128,128,128,0.08)'  # default gray

# drop those columns in indicator_prices that are in etf_prices except date
indicator_prices = indicator_prices.drop(columns=[col for col in indicator_prices.columns if col in etf_prices.columns and col != 'date'])
indicator_returns = indicator_returns.drop(columns=[col for col in indicator_returns.columns if col in etf_prices.columns and col != 'date'])

etf_list = etf_prices.columns.tolist()
indicator_list = indicator_prices.columns.tolist()

etf_display = [f"{etf} - {name_map.get(etf, '')}" for etf in etf_list]
etf_display = [e.rstrip(' - ') for e in etf_display]  # in case name_map returns empty string
etf_display_map = dict(zip(etf_display, etf_list))
indicator_display = [f"{indicator} - {name_map.get(indicator, '')}" for indicator in indicator_list]
indicator_display = [i.rstrip(' - ') for i in indicator_display]  # in case name_map returns empty string
indicator_display_map = dict(zip(indicator_display, indicator_list))

# combine etf and indicator prices
df = pd.merge(etf_prices, indicator_prices, left_index=True, right_index=True, how='inner')
# returns
df_ret = pd.merge(etf_returns, indicator_returns, left_index=True, right_index=True, how='inner')
df_ret.reset_index(inplace=True)

st.header('Correlation matrix')
st.markdown("""
<div style='font-size:16px; line-height:1.7'>
<b><span>Data Frequency Handling:</span></b> Returns are calculated based on <i>each column's native frequency</i> (e.g. quarterly / monthly), then <span style='color:#388e3c'><b>forward-filled</b></span> to match the lower frequency (quarterly → monthly).
<br><br>
<i style='color:#616161'>Ideally, we should align to the lower frequency (monthly → quarterly) instead of forward fill, but for simplicity and initial analysis:</i>
<ul>
  <li><b>Full correlation matrix:</b> <span style='color:#388e3c'>forward fill</span></li>
  <li><b>Individual pairs in rolling correlation:</b> <span style='color:#388e3c'>option to change frequency</span></li>
</ul>
</div>
""", unsafe_allow_html=True)

# select months lag
indicator_months_lag = st.slider('Indicator Months lag', 0, 12, 0)
for indicator in indicator_list:
    df_ret[indicator] = df_ret[indicator].shift(indicator_months_lag)

# select start and end date
col1, col2 = st.columns(2)
with col1:
    sdate = st.date_input('Start date', min_value=df_ret['date'].min(), max_value=df_ret['date'].max(), value=df_ret['date'].min())

    multiSelect_etf_display = st.multiselect('Select ETF', etf_display, default=etf_display)
    multiSelect_etf = [etf_display_map[etf] for etf in multiSelect_etf_display]
with col2:
    edate = st.date_input('End date', min_value=df_ret['date'].min(), max_value=df_ret['date'].max(), value=df_ret['date'].max())

    multiSelect_indicator_display = st.multiselect('Select Indicator', indicator_display, default=indicator_display)
    multiSelect_indicator = [indicator_display_map[indicator] for indicator in multiSelect_indicator_display]

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
horizon = st.slider('Rolling window (month)', 6, 36, 6, 6)

# select etf and indicator to show
show_bg = st.checkbox('Show background 牛熊', value=False)
r_col1, r_col2 = st.columns(2)
with r_col1:
    selected_etf_display = st.selectbox('Select ETF', etf_display, index=0)
    selected_etf = etf_display_map[selected_etf_display]
with r_col2:
    selected_indicator_display = st.selectbox('Select Indicator', indicator_display, index=0)
    selected_indicator = indicator_display_map[selected_indicator_display]

# frequency info
st.markdown(f"""
<div style='font-size:16px; line-height:1.7'>
<b>Indicator months lag (selected above):</b> <span style='color:red'>{indicator_months_lag}</span><br>
<b>ETF data frequency:</b> <span style='color:red'>{freq[selected_etf]}</span><br>
<b>Indicator data frequency:</b> <span style='color:red'>{freq[selected_indicator]}</span>
</div><br/>
""", unsafe_allow_html=True)
# refined frequency selection based on the lower frequency between etf and indicator
if freq[selected_etf] == 'yearly' or freq[selected_indicator] == 'yearly':
    refined_freq = 'Y'
elif freq[selected_etf] == 'quarterly' or freq[selected_indicator] == 'quarterly':
    refined_freq = 'Q'
else:
    refined_freq = 'M'
freq_options = ['M', 'Q', 'Y']
selected_freq = st.selectbox('Data Frequency', options=freq_options, index=freq_options.index(refined_freq), disabled=False)

# calculate rolling correlation
if selected_freq == 'M':
    tmp_ret = df_ret[['date', selected_etf, selected_indicator]].copy()
elif selected_freq == 'Q':
    tmp_ret = df_ret[['date', selected_etf, selected_indicator]].copy()
    tmp_ret.set_index('date', inplace=True)
    tmp_ret = tmp_ret.resample('QE').last().reset_index()
elif selected_freq == 'Y':
    tmp_ret = df_ret[['date', selected_etf, selected_indicator]].copy()
    tmp_ret.set_index('date', inplace=True)
    tmp_ret = tmp_ret.resample('YE').last().reset_index()
rolling_corr = tmp_ret.copy()
rolling_corr['correlation'] = tmp_ret[selected_etf].rolling(window=horizon).corr(tmp_ret[selected_indicator])
rolling_corr = rolling_corr.drop(columns=[selected_etf, selected_indicator])
rolling_corr = rolling_corr.dropna()

# show rolling_corr to check
# st.dataframe(rolling_corr, hide_index=True, use_container_width=True)

fig2 = px.line(rolling_corr, x='date', y='correlation')
fig2.update_layout(title=f'Rolling correlation between {selected_etf} and {selected_indicator}', xaxis_title='Date', yaxis_title='Correlation')

if show_bg:
    for _, row in bull_bear[(bull_bear['start date'] >= rolling_corr['date'].min()) | (bull_bear['end date'] >= rolling_corr['date'].min())].iterrows():
        fig2.add_vrect(
            x0=pd.to_datetime(row.iloc[1]),
            x1=pd.to_datetime(row.iloc[2]),
            fillcolor=get_bull_bear_color(str(row.iloc[3])),
            opacity=0.3,
            layer="below",
            line_width=0,
            annotation_text=str(row.iloc[3]),
            annotation_position="top left",
            annotation=dict(font_size=10, font_color='black')
        )
st.plotly_chart(fig2, use_container_width=True, theme="streamlit", key=None, on_select="ignore")


# Price history
import plotly.graph_objects as go
import numpy as np
st.header('Price history (log scale)')
prices = df[[selected_etf, selected_indicator]].copy()
prices_ln = np.log(prices)
returns = df_ret[[selected_etf, selected_indicator]].copy()
returns.index = df_ret['date']

fig3 = go.Figure()

# ETF price on primary y-axis
fig3.add_trace(go.Scatter(
    x=prices_ln.index,
    y=prices_ln[selected_etf],
    name=selected_etf,
    yaxis='y1'
))

# Indicator level on secondary y-axis
fig3.add_trace(go.Scatter(
    x=prices_ln.index,
    y=prices_ln[selected_indicator],
    name=selected_indicator,
    yaxis='y2'
))

fig3.update_layout(
    title=f'Price history of {selected_etf} and {selected_indicator}',
    xaxis_title='Date',
    yaxis=dict(
        title=f'{selected_etf} Price'
    ),
    yaxis2=dict(
        title=f'{selected_indicator} Level',
        overlaying='y',
        side='right'
    ),
    legend=dict(x=0.01, y=0.99)
)

if show_bg:
    for _, row in bull_bear[(bull_bear['start date'] >= prices.index.min()) | (bull_bear['end date'] >= prices.index.min())].iterrows():
        fig3.add_vrect(
            x0=pd.to_datetime(row.iloc[1]),
            x1=pd.to_datetime(row.iloc[2]),
            fillcolor=get_bull_bear_color(str(row.iloc[3])),
            opacity=0.3,
            layer="below",
            line_width=0,
            annotation_text=str(row.iloc[3]),
            annotation_position="top left",
            annotation=dict(font_size=10, font_color='black')
        )


st.plotly_chart(fig3, use_container_width=True, theme="streamlit", key=None, on_select="ignore")

st.header('zscore of returns')

z_etf = (returns[selected_etf] - returns[selected_etf].mean()) / returns[selected_etf].std()
z_etf = z_etf.clip(-3, 3)
z_indicator = (returns[selected_indicator] - returns[selected_indicator].mean()) / returns[selected_indicator].std()
z_indicator = z_indicator.clip(-3, 3)
fig_z = go.Figure()
fig_z.add_trace(go.Bar(
    x=returns.index,
    y=z_etf,
    name=f"{selected_etf} Return z-score"
))
fig_z.add_trace(go.Bar(
    x=returns.index,
    y=z_indicator,
    name=f"{selected_indicator} Return z-score"
))
fig_z.update_layout(
    title=f'Z-score of Returns of {selected_etf} and {selected_indicator}',
    xaxis_title='Date',
    yaxis=dict(
        title=f'Return z-score'
    ),
    legend=dict(x=0.01, y=0.99)
)
st.plotly_chart(fig_z, use_container_width=True, theme="streamlit", key=None, on_select="ignore")

st.header('Data Check')
# show raw table to check
st.dataframe(pd.merge(prices, returns, left_index=True, right_index=True, how='inner', suffixes=('_price', '_return')), hide_index=False, width='stretch')
# congress = dh.load_us_congress_data()
# st.dataframe(congress, hide_index=True, width='stretch')

st.dataframe(bull_bear, hide_index=True, width='stretch')
