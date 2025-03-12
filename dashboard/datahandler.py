import pandas as pd
import numpy as np
import streamlit as st

DATA_FOLDER = './dashboard/data/'
CONSTITUENTS_FILE = 'broad_china_consituents.csv'
REGIME_FILE_OPTION = ['CPI & OECD_CH (Month End)', 'CI & OECD_CH (Month End)', 'CI & OECD_CH (Monthly)']
INDUSTRY_GROUPS_OPTION = ['Ind Gp +1M-0-ALL',
'Ind Gp-0-ALL(raw)',
'Ind Gp +1M-1-NO',
'Ind Gp-1-NO(raw)',
'Ind Gp +1M-2-1Q',
'Ind Gp-2-1Q(raw)',
'Ind Gp +1M-3+1Q',
'Ind Gp-3+1Q(raw)',
'OECD Monthend x CI-ALL_ABCD',
'OECD Monthend x CI 2.0_ALL_ABC',
'OECD Monthend x CI-ALL_ABC',
'OECD Monthly x CI 2.0-ALL_ABC',
'OECD Monthly x CI-ALL_ABC',
'OECD Monthly_M x CI 2.0-ALL_ABC'
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
