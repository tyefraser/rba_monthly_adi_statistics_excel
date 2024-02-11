import logging
import numpy as np
import pandas as pd

# Create a logger variable
logger = logging.getLogger(__name__)

def apply_current_ranking(
        df,
        date_column,
        column_to_rank,
        ranking_column,
        group_concatenated: str = 'group_concatenated',
):
    # Get the most recent date
    current_period=df[date_column].max()

    # Get unique values of group_concatenated column
    group_concatenated_unique = df[group_concatenated].unique()

    # Create a DataFrame to store the rankings
    ranking_df = pd.DataFrame({
        group_concatenated: group_concatenated_unique,
    })
    
    # Get current df
    current_period_df = df[df[date_column] == current_period][[group_concatenated, column_to_rank]]

    ranking_df = pd.merge(ranking_df, current_period_df, on=group_concatenated, how='left')

    # sort ranking_df by column_to_rank
    ranking_df = ranking_df.sort_values(by=column_to_rank, ascending=False)

    # Add ranking column
    ranking_df[ranking_column] = range(1, len(ranking_df) + 1)

    # drop the column_to_rank column
    ranking_df = ranking_df.drop(columns=[column_to_rank])

    # Merge the ranking DataFrame with the original DataFrame
    df = pd.merge(df, ranking_df, on=group_concatenated, how='left')
    
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
        mom_direction_col = movement_column + ' - MoM Movement Direction'
        df.loc[unique_id_mask, mom_direction_col] = movement_direction

    return df

def single_column_stats_fn(
        df,
        date_column,
        selected_column,
        group_columns,
        ranking_column='rank',
):
    logger.debug('\nRunning: single_column_stats_fn')

    # Make a single group column for joining data

    # Initialize an empty column to store the concatenated values
    df['group_concatenated'] = ''

    # Concatenate the values in each column specified in group_columns
    for col in group_columns:
        df['group_concatenated'] += df[col].astype(str)


    df = apply_current_ranking(
        df=df,
        date_column=date_column,
        column_to_rank=selected_column,
        ranking_column=ranking_column,
        group_concatenated = 'group_concatenated',
    )

    df=movement_fn(
        df=df,
        unique_id_col='ABN',
        movement_column=selected_column,
    )

    # drop the group_concatenated column
    df = df.drop(columns=['group_concatenated'])

    return df