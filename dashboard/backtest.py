import pandas as pd
import numpy as np
from pandas.tseries.offsets import MonthEnd

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
    summary['flavour'] = result_incl[['OECD_CH','favour_mean']].groupby('OECD_CH')['favour_mean'].mean()
    summary['avoid'] = result_excl[['OECD_CH','avoid_mean']].groupby('OECD_CH')['avoid_mean'].mean()

    return summary

def plots(result_incl: pd.DataFrame, result_excl: pd.DataFrame, market: pd.DataFrame):
    row, col = 0, 0
    fig, axes = plt.subplots(1, 1, figsize=(15, 12))
    fig2, axes2 = plt.subplots(1, 1, figsize=(15, 12))
    # add plot
    sns.lineplot((result_incl.loc[result_incl.index >= '2005-11-01']['favour_mean']).cumsum(), ax=axes[0, 0], label="Favour")
    sns.lineplot((result_excl.loc[result_excl.index >= '2005-11-01']['avoid_mean']).cumsum(), ax=axes[0, 0], label="Avoid")
    sns.lineplot((market.loc[market.index >= '2005-11-01'].cumsum()), ax=axes[0, 0], label="Market")
    axes[0, 0].set_title(title)
    axes[0, 0].legend()
    axes[0, 0].set_ylabel("Cum Sum Return")

    # Apply background color based on OECD_CH value
    previous_oecd_value = None
    start_date = None
    for date in result_incl.index:
        oecd_value = result_incl.loc[date, 'OECD_CH']  # Get the OECD_CH value at each date
        if oecd_value != previous_oecd_value:
            if start_date is not None:
                # Use axvspan to fill the background color from start_date to current date
                bg_color = color_map.get(previous_oecd_value, 'white')
                axes[0, 0].axvspan(start_date, date, color=bg_color, alpha=0.3)
            start_date = date  # Update the start date for the new period
        previous_oecd_value = oecd_value

    # Ensure the last region gets colored
    if previous_oecd_value is not None:
        bg_color = color_map.get(previous_oecd_value, 'white')
        axes[0, 0].axvspan(start_date, result_incl.index[-1], color=bg_color, alpha=0.1)

    # Combine the original legend with the background color legend
    original_handles, original_labels = axes[0, 0].get_legend_handles_labels()
    axes[0, 0].legend(
    handles=original_handles + legend_patches, 
    labels=original_labels + [patch.get_label() for patch in legend_patches], 
    loc='upper left',
    bbox_to_anchor=(1.05, 1),  # Move the legend outside to the right
    fontsize=8,  # Optional: Adjust font size for readability
    borderaxespad=0.,  # Optional: Adjust the spacing between the plot and legend
    title_fontsize=8  # Optional: Adjust the title font size
)
    # add plot2
    sns.lineplot((result_incl_ex_stag.loc[result_incl_ex_stag.index >= '2005-11-01']['favour_mean']).cumsum(), ax=axes2[0, 0], label="Favour")
    sns.lineplot((result_excl_ex_stag.loc[result_excl_ex_stag.index >= '2005-11-01']['avoid_mean']).cumsum(), ax=axes2[0, 0], label="Avoid")
    sns.lineplot((market.loc[market.index >= '2005-11-01'].cumsum()), ax=axes2[0, 0], label="Market")
    axes2[0, 0].set_title(f'{title} (ex stagflation)')
    axes2[0, 0].legend()
    axes2[0, 0].set_ylabel("Cum Sum Return")

    # Apply background color dynamically based on the OECD_CH values over time for plot2
    previous_oecd_value2 = None
    start_date2 = None
    for date in result_incl_ex_stag.index:
        oecd_value2 = result_incl_ex_stag.loc[date, 'OECD_CH']  # Get the OECD_CH value at each date
        if oecd_value2 != previous_oecd_value2:
            if start_date2 is not None:
                # Use axvspan to fill the background color from start_date to current date
                bg_color2 = color_map.get(previous_oecd_value2, 'white')
                axes2[row, col].axvspan(start_date2, date, color=bg_color2, alpha=0.3)
            start_date2 = date  # Update the start date for the new period
        previous_oecd_value2 = oecd_value2

    # Ensure the last region gets colored
    if previous_oecd_value2 is not None:
        bg_color2 = color_map.get(previous_oecd_value2, 'white')
        axes2[row, col].axvspan(start_date2, result_incl_ex_stag.index[-1], color=bg_color2, alpha=0.1)

    # Add the background color legend to the second plot
    # Combine the original legend with the background color legend
    original_handles2, original_labels2 = axes2[row, col].get_legend_handles_labels()
    axes2[row, col].legend(
    handles=original_handles2 + legend_patches, 
    labels=original_labels2 + [patch.get_label() for patch in legend_patches], 
    loc='upper left', 
    bbox_to_anchor=(1.05, 1),  # Move the legend outside to the right
    fontsize=8,  # Optional: Adjust font size for readability
    borderaxespad=0.,  # Optional: Adjust the spacing between the plot and legend
    title_fontsize=8  # Optional: Adjust the title font size
)

    fig.tight_layout(pad=1.5)
    fig.subplots_adjust(hspace=0.5, wspace=0.3)

    return fig, fig2