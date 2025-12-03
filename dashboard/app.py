import streamlit as st
import numpy as np
import pandas as pd

st.title('AIG dashboard')

correlation = st.Page("pages/US/correlation.py", title="Correlation", icon=":material/analytics:", default=True)
correlation_download = st.Page("pages/US/correlation_download.py", title="Correlation download", icon=":material/download:")

compare_bt = st.Page("pages/HK/compare_backtest.py", title="Compare Backtest", icon=":material/finance_mode:")
regime_bt = st.Page("pages/HK/regime_backtest.py", title="Regime Backtest", icon=":material/chart_data:")
clock = st.Page("pages/HK/royal_clock.py", title="Royal Clock", icon=":material/alarm:")
sector_stats = st.Page("pages/HK/sector_stats.py", title="Sector Stats", icon=":material/pie_chart:")
universe_stats = st.Page("pages/HK/universe_stats.py", title="Universe Stats", icon=":material/dashboard:")

pg = st.navigation(
    {
        "US - 2025": [correlation, correlation_download],
        "HK - royal clock": [universe_stats, sector_stats, regime_bt, compare_bt, clock],
    }
)

pg.run()