import pandas as pd
import numpy as np
import streamlit as st

# Google sheet constants
GOOGLE_SHEET_URL = 'https://docs.google.com/spreadsheets/d/1wvq1dhhVmtaoqMLLZwNrtv8dUSk8t5LHJHZJ5wcFUi0/export?format=csv&gid='
GOOGLE_ETF_SHEET_GRID = '403272206'
GOOGLE_MASTER_SHEET_GRID = '905030353'
GOOGLE_NAME_REF_SHEET_GRID = '1267495009'

GOOGLE_US_ECON_SHEET_URL = 'https://docs.google.com/spreadsheets/d/1nRI_r4qAkUdGc1L750AHeXULnYwPeAvYli4bbpeB7AM/export?format=csv&gid='
GOOGLE_US_NEWS_SHEET_GRID = '1020638433'
GOOGLE_US_CONGRESS_SHEET_GRID = '598725487'
GOOGLE_US_BULL_BEAR_SHEET_GRID = '731885871'

DATA_FOLDER = './dashboard/data/'
# local path
# DATA_FOLDER = './data/'
CONSTITUENTS_FILE = 'broad_china_consituents.csv'
REGIME_FILE_OPTION = ['CPI & OECD_CH (Month End)', 'CI & OECD_CH (Month End)', 'CI & OECD_CH (Monthly)']
INDUSTRY_GROUPS_OPTION = [
    # OECD CLI-based Quadrants (Ind Gp)
    'Ind Gp-0-ALL(raw)',
    'Ind Gp-1-NO(raw)',
    'Ind Gp-2-1Q(raw)',
    'Ind Gp-3+1Q(raw)',
    # OECD CLI-based Quadrants (Ind Gp +1M)
    'Ind Gp +1M-0-ALL',
    'Ind Gp +1M-1-NO',
    'Ind Gp +1M-2-1Q',
    'Ind Gp +1M-3+1Q',
    # OECD Monthend x CI
    'OECD Monthend x CI-ALL_ABC',
    'OECD Monthend x CI-ALL_ABCD',
    # OECD Monthly x CI
    'OECD Monthly x CI-ALL_ABC',
    # OECD Monthend x CI 2.0
    'OECD Monthend x CI 2.0_ALL_ABC',
    # OECD Monthly x CI 2.0
    'OECD Monthly x CI 2.0-ALL_ABC',
    'OECD Monthly x CI 2.0-3+1Q_ABC',
    # OECD Monthly_M x CI 2.0
    'OECD Monthly_M x CI 2.0-ALL_ABC',
    'OECD Monthly_M x CI 2.0-ALL_ABCD',
    'OECD Monthly_M x CI 2.0-1-NO_ABC',
    'OECD Monthly_M x CI 2.0-2-1Q_ABC',
    'OECD Monthly_M x CI 2.0-3+1Q_ABC',
    # OECD Monthend_M x CI
    'OECD Monthend_M x CI 2.0-ALL_ABCD',
    'OECD Monthend_M x CI 2.0-ALL_ABC',
    'OECD Monthend_M x CI 2.0-1-NO_ABC',
    'OECD Monthend_M x CI 2.0-2-1Q_ABC',
    'OECD Monthend_M x CI 2.0-3+1Q_ABC',
    # OECD-MEND_M_CI-PosRetOnly
    'OECD-MEND_M_CI-PosRetOnly-1-NO',
    'OECD-MEND_M_CI-PosRetOnly-1-NO-2022',
    # OECD-MEND_M_CI-PosNegRet
    'OECD-MEND_M_CI-PosNegRet-1-NO',
    'OECD-MEND_M_CI-PosNegRet-1-NO-2022',
    'OECD-MEND_M_CI-PosNegRetNoStag-1-NO-2022',
    'royal_clock'
]

@st.cache_data
def get_constituents() -> pd.DataFrame:
    df = pd.read_csv(DATA_FOLDER + CONSTITUENTS_FILE)
    df = df.dropna()
    # adjust industry
    df['industry_adj'] = np.where(df['industry'] == 'Media & Entertainment', 'Media', df['industry'])
    df['industry_adj'] = np.where(df['industry_adj'] == 'Real Estate Management & Development', 'Equity Real Estate Investment Trusts (REITs) ', df['industry_adj'])
    df['country'] = df['home_code'].str[-2:]
    df['country'] = np.where(df['country'].isin(['HK', 'CN']), df['country'], 'CN')
    return df

def universe_return(df: pd.DataFrame) -> pd.DataFrame:
    returns = pd.DataFrame()
    returns['cap_weighted_ret'] = df.groupby(['date']).apply(lambda x: np.average(x['FWD_RET_1M'], weights=x['MCAP_USD']))
    returns['eq_weighted_ret'] = df.groupby(['date']).apply(lambda x: np.average(x['FWD_RET_1M']))
    returns['count'] = df.groupby(['date'])['MCAP_USD'].count()
    return returns

def universe_return_by_country(df: pd.DataFrame) -> pd.DataFrame:
    df['country'] = df['home_code'].str[-2:]
    df['country'] = np.where(df['country'].isin(['HK', 'CN']), df['country'], 'CN')
    returns = pd.DataFrame()
    returns['cap_weighted_ret'] = df.groupby(['date', 'country']).apply(lambda x: np.average(x['FWD_RET_1M'], weights=x['MCAP_USD']))
    returns['eq_weighted_ret'] = df.groupby(['date', 'country']).apply(lambda x: np.average(x['FWD_RET_1M']))
    returns['count'] = df.groupby(['date', 'country'])['country'].count()
    return returns

def sector_return(df: pd.DataFrame) -> pd.DataFrame:
    # return by sector
    sector_returns = pd.DataFrame()
    sector_returns['cap_weighted_ret'] = df.groupby(['date', 'sector']).apply(lambda x: np.average(x['FWD_RET_1M'], weights=x['MCAP_USD']))
    sector_returns['eq_weighted_ret'] = df.groupby(['date', 'sector']).apply(lambda x: np.average(x['FWD_RET_1M']))
    sector_returns['count'] = df.groupby(['date', 'sector'])['sector'].count()
    return sector_returns


def industry_return(df: pd.DataFrame) -> pd.DataFrame:
    # return by industry
    industry_returns = pd.DataFrame()
    industry_returns['cap_weighted_ret'] = df.groupby(['date', 'industry_adj']).apply(lambda x: np.average(x['FWD_RET_1M'], weights=x['MCAP_USD']))
    industry_returns['eq_weighted_ret'] = df.groupby(['date', 'industry_adj']).apply(lambda x: np.average(x['FWD_RET_1M']))
    industry_returns['count'] = df.groupby(['date', 'industry_adj'])['industry_adj'].count()
    return industry_returns

@st.cache_data
def get_regime(type: str) -> pd.DataFrame:
    file = DATA_FOLDER + type + '.csv'
    periods = pd.read_csv(file)
    periods.Period = pd.to_datetime(periods.Period)
    periods.rename(columns={'Period': 'date'}, inplace=True)
    periods.set_index('date', inplace=True)
    
    return periods

@st.cache_data
def industry_group_selection(select: str) -> pd.DataFrame:
    selection = pd.read_csv(f"{DATA_FOLDER}{select}.csv")
    selection.set_index('indgp', inplace=True)
    selection = selection.transpose()

    return selection

@st.cache_data
def load_etf_prices() -> pd.DataFrame:
    df = pd.read_csv(f"{GOOGLE_SHEET_URL}{GOOGLE_ETF_SHEET_GRID}")
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df.set_index('date', inplace=True)
    # resample to monthend
    df = df.ffill()  # Forward fill all columns globally
    df = df.resample('ME').last()
    ret_df = df.pct_change()
    return df, ret_df

def detect_column_frequency(df):
    freq_dict = {}
    for col in df.columns:
        # Get the index (dates) where the column is not NA
        non_na_dates = df.index[df[col].notna()]
        if len(non_na_dates) < 5:
            freq_dict[col] = 'unknown'
            continue
        # Calculate the most common difference in months
        diffs = non_na_dates.to_series().diff().dropna().dt.days
        avg_diff = diffs.mean()
        if 25 < avg_diff < 35:
            freq_dict[col] = 'monthly'
        elif 80 < avg_diff < 100:
            freq_dict[col] = 'quarterly'
        else:
            # assume yearly
            freq_dict[col] = 'yearly'
    return freq_dict

def calc_exact_period_return(df, freq_dict):
    df_ret = pd.DataFrame(index=df.index)
    for col, freq in freq_dict.items():
        if (freq == 'monthly'):
            # Shift by 1 calendar month
            tmp = df[col].ffill().resample('ME').last()
            tmp_ret = tmp.pct_change()
            # Reindex back to original index, forward fill so all dates in the year get the same return
            df_ret[col] = tmp_ret.reindex(df.index)
        elif freq == 'quarterly':
            # Shift by 1 calendar quarter
            tmp = df[col].ffill().resample('QE').last()
            tmp_ret = tmp.pct_change()
            # Reindex back to original index, forward fill so all dates in the year get the same return
            df_ret[col] = tmp_ret.reindex(df.index)
        else:
            # Resample to year-end, then calculate returns
            yearly = df[col].ffill().resample('YE').last()
            yearly_ret = yearly.pct_change()
            # Reindex back to original index, forward fill so all dates in the year get the same return
            df_ret[col] = yearly_ret.reindex(df.index)
    return df_ret

@st.cache_data
def load_indicator_prices() -> pd.DataFrame:
    df = pd.read_csv(f"{GOOGLE_SHEET_URL}{GOOGLE_MASTER_SHEET_GRID}")
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    # filter from 1990 onwards as frequency is weekly before that
    df = df[df['date'] >= pd.to_datetime('1990-01-01')]
    df.set_index('date', inplace=True)
    df = df.resample('ME').last()
    # detect frequency of each column
    freq_dict = detect_column_frequency(df)
    # calculate return based on frequency (df is daily price data)
    return_df = calc_exact_period_return(df, freq_dict)
    # resample to monthend
    df = df.ffill()  # Forward fill all columns globally
    df = df.resample('ME').last()
    return_df = return_df.ffill().resample('ME').last()
    return df, return_df, freq_dict

def calc_correlation_monthly_quarterly(s_monthly: pd.Series, s_quarterly: pd.Series) -> float:
    # Resample monthly series to quarterly by taking last value of each quarter
    s_monthly_q = s_monthly.resample('Q').last()  # or .mean(), depending on your use case
    # Align both series on their dates and drop NA values
    aligned = pd.concat([s_monthly_q, s_quarterly], axis=1).dropna()
    # Calculate correlation
    corr = aligned.corr().iloc[0, 1]
    return corr

@st.cache_data
def load_name_ref() -> pd.DataFrame:
    df = pd.read_csv(f"{GOOGLE_SHEET_URL}{GOOGLE_NAME_REF_SHEET_GRID}")
    return df

@st.cache_data
def load_us_news_data() -> pd.DataFrame:
    df = pd.read_csv(f"{GOOGLE_US_ECON_SHEET_URL}{GOOGLE_US_NEWS_SHEET_GRID}")
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    return df

@st.cache_data
def load_us_congress_data() -> pd.DataFrame:
    df = pd.read_csv(f"{GOOGLE_US_ECON_SHEET_URL}{GOOGLE_US_CONGRESS_SHEET_GRID}")
    # Parse Congress column to get start_date and end_date
    df[['Congress_num', 'years']] = df['Congress'].str.extract(r'(\d+[a-z]{2}) \(([\d–]+)\)')
    df[['start_year', 'end_year']] = df['years'].str.split('–', expand=True)
    df['start_date'] = pd.to_datetime(df['start_year'], format='%Y')
    df['end_date'] = pd.to_datetime(df['end_year'], format='%Y') + pd.DateOffset(years=1) - pd.DateOffset(days=1)

    # Reshape to long format
    long_df = df.melt(
        id_vars=['Congress', 'start_date', 'end_date', 'Party Government'],
        value_vars=['House Majority', 'Senate Majority', 'Presidency'],
        var_name='category',
        value_name='desc'
    )
    long_df['comment'] = long_df['Party Government']

    # Select relevant columns
    long_df = long_df[['start_date', 'end_date', 'category', 'desc', 'comment']]

    return long_df

@st.cache_data
def load_us_bull_bear_data() -> pd.DataFrame:
    df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/1wvq1dhhVmtaoqMLLZwNrtv8dUSk8t5LHJHZJ5wcFUi0/export?format=csv&gid=374464057")
    df.dropna(inplace=True)
    df['start date'] = pd.to_datetime(df['start date'], format='%Y-%m-%d')
    df['end date'] = pd.to_datetime(df['end date'], format='%Y-%m-%d')
    return df