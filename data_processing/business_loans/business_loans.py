from utils import read_yaml
import logging
import numpy as np
from math import isnan
import pandas as pd

# Create a logger variable
logger = logging.getLogger(__name__)

def apply_current_ranking(
        df,
        date_col,
        column_to_rank,
        joining_column,
        ranking_column,
):
    # Get the most recent date
    current_period=df[date_col].max()

    # Order the current month by the column to be ranked
    sorted_df=df[df[date_col] == current_period].sort_values(by=column_to_rank, ascending=False)

    # Create a DataFrame to store the rankings
    ranking_df = pd.DataFrame({
        joining_column: sorted_df[joining_column],
        ranking_column: range(1, len(sorted_df) + 1)
    })

    # Merge the ranking DataFrame with the original DataFrame
    df = pd.merge(df, ranking_df, on=joining_column, how='left')

    # Now you can use the ranking column for all periods
    # If you want to fill NaN values in ranking for periods other than the current month,
    # you can use forward fill (ffill) or any other appropriate method.
    df[ranking_column] = df[ranking_column].ffill()


    return df



def movement_fn(
        df,
        unique_id_col,
        movement_column,
):
    for abn in df[unique_id_col].unique():
        # Create mask for the unique id
        unique_id_mask = df[unique_id_col] == abn

        # Get dollar movements
        mom_dollar_col = movement_column + ' - MoM ($)'
        df.loc[unique_id_mask, mom_dollar_col] = df.loc[unique_id_mask, movement_column].diff()
        # Set NaN for the first row since there's no previous month
        df.loc[unique_id_mask & df.index.isin([df.loc[unique_id_mask].index[0]]), mom_dollar_col] = None

        # Get percentage movements
        mom_percentage_col = movement_column + ' - MoM (%)'
        df.loc[unique_id_mask, mom_percentage_col] = (df.loc[unique_id_mask, mom_dollar_col] / df.loc[unique_id_mask, movement_column].shift(1))
         
        # Get direction of movement
        movement_direction = np.where(df.loc[unique_id_mask, mom_dollar_col] < 0, 'decrease', np.where(df.loc[unique_id_mask, mom_dollar_col] > 0, 'increase', 'none'))
        df.loc[unique_id_mask, 'Movement Direction'] = movement_direction

    return df

def business_loans_fn(
        rba_monthly_stats_df,
):
    logger.debug('\nRunning: business_loans_fn')

    # Create the bb_df DataFrame
    bb_df=rba_monthly_stats_df[['Period', 'ABN', 'Institution Name', 'Loans to non-financial businesses', 'Loans to financial institutions']].copy()

    # Create the 'Business Loans' column
    bb_df.loc[:, 'Business Loans'] = bb_df['Loans to non-financial businesses'] + bb_df['Loans to financial institutions']

    bb_df=apply_current_ranking(
        df=bb_df,
        date_col = 'Period',
        column_to_rank = 'Business Loans',
        joining_column = 'Institution Name',
        ranking_column = 'ranking',
    )

    bb_df=movement_fn(
        df=bb_df,
        unique_id_col='ABN',
        movement_column='Business Loans',
    )

    # bb_df['Business Loans - dollars text'] = bb_df['Business Loans'].apply(rounded_dollars)
    # bb_df['Business Loans - MoM ($) - dollars text'] = bb_df['Business Loans - MoM ($)'].apply(rounded_dollars)

    return bb_df