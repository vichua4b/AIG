import pandas as pd
import numpy as np
from pandas.tseries.offsets import MonthEnd
import quantstats as qs

def run_backtest(selection: pd.DataFrame, periods: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    indgp = returns.copy()
    indgp.reset_index(inplace=True)
    indgp['date'] = pd.to_datetime(indgp['date']) + MonthEnd(0)
    indgp['industry_adj'] = indgp['industry_adj'].str.strip()
    indgp.set_index(['date','industry_adj'], inplace=True)
    indgp = indgp[['cap_weighted_ret']].unstack('industry_adj')
    indgp = indgp.droplevel(0, axis=1)

    # market return
    market = indgp.mean(axis=1)

    # Merge with cycle data
    all_ds = periods.merge(selection, how='left', left_on='OECD_CH', right_index=True)
    all_ds = all_ds.reset_index()
    monthly_index = pd.date_range(start=all_ds['date'].min(), end=all_ds['date'].max(), freq='ME')
    # Reindex with the monthly date range and forward-fill values
    all_ds.set_index('date', inplace=True)
    all_ds_monthly = all_ds.reindex(monthly_index, method='ffill')
    
    # calc return series
    combine = all_ds_monthly.join(indgp, rsuffix='_r')
    columns = indgp.columns
    result_incl = combine[['OECD_CH']]
    result_incl_ex_stag = result_incl.copy()
    result_excl = combine[['OECD_CH']]
    result_excl_ex_stag = result_excl.copy()

    for c in columns:
        result_incl[c] = np.where(((combine[c.strip()] == 1)), (combine[c.strip()] * combine[c.strip() + '_r']), np.nan)
        result_excl[c] = np.where(((combine[c.strip()] == -1)), (combine[c.strip()] * combine[c.strip() + '_r']), np.nan)
        result_incl_ex_stag[c] = np.where(((combine[c.strip()] == 1) & (combine['OECD_CH'] != 'Stagflation')), (combine[c.strip()] * combine[c.strip() + '_r']), np.nan)
        result_excl_ex_stag[c] = np.where(((combine[c.strip()] == -1) & (combine['OECD_CH'] != 'Stagflation')), (combine[c.strip()] * combine[c.strip() + '_r']), np.nan)

    result_incl.reset_index().set_index(['index','OECD_CH'], inplace=True)
    result_excl.reset_index().set_index(['index','OECD_CH'], inplace=True)
    result_incl_ex_stag.reset_index().set_index(['index','OECD_CH'], inplace=True)
    result_excl_ex_stag.reset_index().set_index(['index','OECD_CH'], inplace=True)

    result_incl['favour_mean'] = result_incl.iloc[:, 1:].mean(axis=1)
    result_excl['avoid_mean'] = result_excl.iloc[:, 1:].mean(axis=1)
    result_incl_ex_stag['favour_mean'] = result_incl_ex_stag.iloc[:, 1:].mean(axis=1)
    result_excl_ex_stag['avoid_mean'] = result_excl_ex_stag.iloc[:, 1:].mean(axis=1)

    result_incl['favour_mean'] = result_incl['favour_mean'].fillna(0)
    result_excl['avoid_mean'] = result_excl['avoid_mean'].fillna(0)
    result_incl_ex_stag['favour_mean'] = result_incl_ex_stag['favour_mean'].fillna(0)
    result_excl_ex_stag['avoid_mean'] = result_excl_ex_stag['avoid_mean'].fillna(0)

    return result_incl, result_excl, result_incl_ex_stag, result_excl_ex_stag, market

def summary_table(result_incl: pd.DataFrame, result_excl: pd.DataFrame, market: pd.DataFrame) -> pd.DataFrame:
    market.rename('market', inplace=True)
    result_incl = result_incl.join(market, how='left')
    # summary table
    summary = pd.DataFrame()
    summary['market'] = result_incl[['OECD_CH','market']].groupby('OECD_CH')['market'].mean()
    summary['favour'] = result_incl[['OECD_CH','favour_mean']].groupby('OECD_CH')['favour_mean'].mean()
    summary['avoid'] = result_excl[['OECD_CH','avoid_mean']].groupby('OECD_CH')['avoid_mean'].mean()

    return summary

def bt_stats(result_incl: pd.DataFrame, result_excl: pd.DataFrame, market: pd.DataFrame) -> pd.DataFrame:
    stats = {'cagr': qs.stats.cagr(result_incl['favour_mean'], compounded=False),
             'volatility': qs.stats.volatility(result_incl['favour_mean']),
             'sharpe': qs.stats.sharpe(result_incl['favour_mean']),
             'mdd': qs.stats.max_drawdown(result_incl['favour_mean'])
            }
    stats_a = {'cagr': qs.stats.cagr(result_excl['avoid_mean'], compounded=False),
             'volatility': qs.stats.volatility(result_excl['avoid_mean']),
             'sharpe': qs.stats.sharpe(result_excl['avoid_mean']),
             'mdd': qs.stats.max_drawdown(result_excl['avoid_mean'])
            }
    # Add in market
    stats_m = {'cagr': qs.stats.cagr(market, compounded=False),
                'volatility': qs.stats.volatility(market),
                'sharpe': qs.stats.sharpe(market),
                'mdd': qs.stats.max_drawdown(market)
                }
    return pd.DataFrame([stats_m, stats, stats_a], index=['Market', 'Favour', 'Avoid']).transpose()