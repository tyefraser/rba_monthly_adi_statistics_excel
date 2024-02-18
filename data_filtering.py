import pandas as pd
import numpy as np

from utils import period_ago, get_months_ago_list, period_ago_prefix

def market_positions(
        df,
        date_column,
        category_column,
        selected_column
):

    df_to_rank = df[[date_column, category_column, selected_column]]
    market_position_df = pd.DataFrame()
    for date in df_to_rank[date_column].unique():
        # Generate rankings df
        rankings_df = df_to_rank[df_to_rank[date_column] == date][[date_column, category_column, selected_column]].sort_values(by=selected_column, ascending=False)
        rankings_df['Rank'] = rankings_df[selected_column].rank(method='max', ascending=False).astype(int)
        rankings_df['Market Share'] = rankings_df[selected_column] / rankings_df[selected_column].sum()

        # Concatengate to the complete market_position_df
        if len(market_position_df) == 0:
            market_position_df = rankings_df.copy()
        else:
            market_position_df = pd.concat([market_position_df, rankings_df], ignore_index=True)
    return market_position_df

def calculate_movement_cols(
        df,
        date_column,
        category_column,
        selected_column,
        dollar_movements: str = None,
        percentage_movements: str = None,
        timing: str = '',
):
    """
    Calculate the movement in business loans for each bank over the periods.
    
    Parameters:
    - df: A pandas DataFrame with columns date_column, category_column, and selected_column.
    
    Returns:
    - A pandas DataFrame with an additional 'Movement' column showing the movement in the selected_column columns.
    """

    # Ensure date_column is a datetime column
    df[date_column] = pd.to_datetime(df[date_column])
    
    # Sort the DataFrame by category_column and date_column
    df_sorted = df.sort_values(by=[category_column, date_column])
    
    # Calculate the movement in selected_column for each bank - as dollars
    if dollar_movements is None:
        if timing != '':
            dollar_movements = f'{selected_column} - {timing} Movement ($)'
        else:
            dollar_movements = f'{selected_column} - Movement ($)'
    df_sorted[dollar_movements] = df_sorted.groupby(category_column)[selected_column].diff()

    # Calculate the movement in selected_column for each bank - as percentage
    if percentage_movements is None:
        if timing != '':
            percentage_movements = f'{selected_column} - {timing} Movement (%)'
        else:
            percentage_movements = f'{selected_column} - Movement (%)'
    df_sorted[percentage_movements] = df_sorted.groupby(category_column)[selected_column].pct_change()

    # Generate return values
    df_dict = {}
    df_dict['df'] = df_sorted
    df_dict['category_col'] = category_column
    df_dict['dollar_col'] = selected_column
    df_dict['dollar_movements_col'] = dollar_movements
    df_dict['percentage_movements_col'] = percentage_movements    
    
    return df_dict


def aggregate_sums(
        df,
        date_column,
        category_column
):
    # Ensure 'Period' is a datetime column
    df[date_column] = pd.to_datetime(df[date_column])

    # Drop the 'Institution Name' as it's not needed for aggregation
    df_dropped = df.drop(columns=[category_column])

    # Aggregate the account balances for each month
    monthly_aggregates = df_dropped.groupby(date_column).sum().reset_index()

    # Reshape the DataFrame to have accounts and their values in separate columns
    melted_df = monthly_aggregates.melt(id_vars=[date_column], var_name='Account', value_name='Value')

    df_dict = calculate_movement_cols(
        df = melted_df,
        date_column = date_column,
        category_column = 'Account',
        selected_column = 'Value',
        dollar_movements = 'Movement ($)',
        percentage_movements = 'Movement (%)',
        timing = 'MoM',
    )

    return df_dict

def ordered_category_list_fn(
        df,
        date_column,
        selected_date,
        selected_column,
        category_column,
        other_col = 'other',
        other_at_end = True,
):
    # Get data for current month only
    df_current = df[df[date_column] == selected_date]
    
    # Create ordered list
    ordered_category_list = df_current.sort_values(by=selected_column, ascending=False).copy()[category_column].tolist()

    # Move 'other' if required
    if other_at_end:
        # Remove 'other' from its current position
        ordered_category_list.remove(other_col)

        # Append 'other' to the end of the list
        ordered_category_list.append(other_col)
    
    return ordered_category_list

def attach_market_info(
        df,
        date_column,
        category_column,
        selected_column,
        market_position_df,
):
    # Ensure only required columns are included
    market_position_df = market_position_df[[date_column , category_column, selected_column, 'Rank', 'Market Share']].copy()

    # Create return df
    df_ranked = pd.DataFrame()

    # Loop through all dates
    for date in df[date_column].unique():
        # Get data for the current date
        df_at_date = df[df[date_column] == date]

        # Add rankings and market share
        df_at_date_ranked = pd.merge(
            df_at_date,
            market_position_df,
            on=[date_column, category_column, selected_column], how='left'
        )

        # Calculate 'other' values
        df_at_date_ranked.loc[df_at_date_ranked[category_column] == 'other', 'Rank'] = len(df_at_date_ranked)
        df_at_date_ranked.loc[df_at_date_ranked[category_column] == 'other', 'Market Share'] = (1 - df_at_date_ranked['Market Share'].sum())

        # Update the df_ranked df
        if len(df_ranked) == 0:
            df_ranked = df_at_date_ranked.copy()
        else:
            df_ranked = pd.concat([df_ranked, df_at_date_ranked], ignore_index=True)

    return df_ranked

def create_top_x_and_other_df(
        df_dated,
        date_column,
        selected_date,
        category_column,
        selected_column,
        top_x_category_list,
        market_position_df,
):
    # Assuming df_dated is your DataFrame with columns: date_column, category_column, and selected_category
    # and categories of interest are in the list: top_x_category_list

    # Generate top x df_dated

    # Filter DataFrame to include only categories of interest
    top_x_filtered_df = df_dated[df_dated[category_column].isin(top_x_category_list)][[date_column, category_column, selected_column]]

    # Group by month and category, summing the values
    top_x_grouped_df = top_x_filtered_df.groupby([top_x_filtered_df[date_column], category_column]).sum().reset_index()

    # 'Other' rows generator

    # Create a DataFrame with all unique months
    # to do: ensures there are no missing months (typing issue)
    # to do: all_months = pd.period_range(start=df_dated[date_column].min(), end=df_dated[date_column].max())
    # to do: all_months_df = pd.DataFrame({date_column: all_months})

    all_months_df = pd.DataFrame({date_column: df_dated[date_column].unique()})

    # Cartesian product to get all combinations of months and categories of interest
    all_combinations_df = all_months_df.assign(key=1).merge(pd.DataFrame({category_column: top_x_category_list, 'key': 1}), on='key').drop('key', axis=1)


    # Merge with grouped DataFrame to fill missing combinations with zeros
    merged_df = pd.merge(all_combinations_df, top_x_grouped_df, on=[date_column, category_column], how='left').fillna(0)

    # Calculate sum of values for 'other' category for each month
    other_values = df_dated[~df_dated[category_column].isin(top_x_category_list)].groupby(df_dated[date_column])[selected_column].sum().reset_index()
    other_values[category_column] = 'other'

    # Append 'other' values to merged DataFrame
    top_x_and_other_df = pd.concat([merged_df, other_values], ignore_index=True)

    # Sort DataFrame by date and category
    top_x_and_other_df = top_x_and_other_df.sort_values(by=[date_column, category_column])

    # Reset index
    top_x_and_other_df.reset_index(drop=True, inplace=True)

    ordered_category_list = ordered_category_list_fn(
        df = top_x_and_other_df,
        date_column = date_column,
        selected_date = selected_date,
        selected_column = selected_column,
        category_column = category_column,
        other_col = 'other',
        other_at_end = True,
    )

    top_x_and_other_df_dict = calculate_movement_cols(
        df=top_x_and_other_df,
        date_column=date_column,
        category_column=category_column,
        selected_column=selected_column,
        timing = 'MoM',
    )

    # Update df to include market share info
    top_x_and_other_df_dict['df'] = attach_market_info(
        df = top_x_and_other_df_dict['df'],
        date_column = date_column,
        category_column = category_column,
        selected_column = selected_column,
        market_position_df = market_position_df,
    )

    return top_x_and_other_df_dict, ordered_category_list

def get_date_details(
        date_col_df,
        date_column,
):
    date_details = {}
    date_details['mom_dates_list'] = sorted(list(date_col_df[date_column].unique()), reverse=True)    
    date_details['yoy_dates_list'] = date_details['mom_dates_list'][0::12]
    date_details['months_ago_list'] = get_months_ago_list(
        df = date_col_df,
        date_column = date_column,
    )
    no_months = len(date_details['mom_dates_list'])
    for months_ago in [0, 1, 12, 48, 60]:
        if no_months >= (months_ago+1):
            date_details.update({f'date_{months_ago}_months_ago': date_details['mom_dates_list'][months_ago]})
            date_details.update({f'date_{months_ago}_wording': period_ago(months_ago)})
            date_details.update({f'date_{months_ago}_col_prefix': period_ago_prefix(months_ago)})

    return date_details

def date_to_date_comparison(
        df,
        date_column,
        selected_date,
        comparison_date,
        selected_column,
        category_column,
        prefix = '',
):
    # Created padded varsiion of the prefix value
    if prefix == '':
        prefix_padded = ' '
    else:
        prefix_padded = ' ' + prefix + ' '

    # df for the selected dates
    df[date_column] = pd.to_datetime(df[date_column])
    df_two_dates = df[df[date_column].isin([selected_date, comparison_date])]
    df_two_dates.loc[df_two_dates[date_column] == selected_date, 'date_column_str'] = 'current'
    df_two_dates.loc[df_two_dates[date_column] == comparison_date, 'date_column_str'] = 'comparison'
    df_two_dates = df_two_dates.drop(date_column, axis=1).copy()
    df_two_dates.loc[:, date_column] = df_two_dates['date_column_str']
    df_two_dates = df_two_dates.drop('date_column_str', axis=1).copy()
    df_two_dates = df_two_dates[[date_column, category_column, selected_column]]

    # Pivot the DataFrame
    pivot_df = df_two_dates.pivot_table(index=category_column, columns=date_column, values=selected_column, aggfunc='first')

    # Reset the index to make 'category' a column again
    pivot_df.reset_index(inplace=True)
    
    # Dollar Movements
    dollar_movements_col_name = f"{selected_column} -{prefix_padded}Movement ($)"
    pivot_df[dollar_movements_col_name] = pivot_df['current'] - pivot_df['comparison']

    # Dollar Direction
    movement_direction_col_name = f"{selected_column} -{prefix_padded}Movement Direction"
    pivot_df[movement_direction_col_name] = np.where(pivot_df[dollar_movements_col_name] >= 0, 'increase', 'decrease')

    # Percentage Movements
    percentage_movements_col_name = f"{selected_column} -{prefix_padded}Movement (%)"
    pivot_df[percentage_movements_col_name] = (pivot_df[dollar_movements_col_name] / pivot_df['comparison']) # * 100

    # Percentage of market Movements
    percentage_of_market_movements_col_name = f"{selected_column} -{prefix_padded}Movement as Percentage of Market(%)"
    pivot_df[percentage_of_market_movements_col_name] = (pivot_df[dollar_movements_col_name] / pivot_df['comparison'].sum()) # * 100

    date_to_date_comparison_dict = {
        'prefix': prefix,
        'df': pivot_df,
        'dollar_movements_col_name': dollar_movements_col_name,
        'movements_direction_col_name': movement_direction_col_name,
        'percentage_movements_col_name': percentage_movements_col_name,
        'percentage_of_market_movements_col_name': percentage_of_market_movements_col_name,
        'selected_date': selected_date,
        'comparison_date': comparison_date,
    }

    return date_to_date_comparison_dict

def filter_data(
        df,
        date_column,
        selected_date,
        selected_column,
        category_column,
        selected_category,
        top_x_category_list,
        group_by_columns,
):
    # Generate return dictionaries
    dfs_dict = {}
    details_dicts = {}

    # Add original df to dfs dictionary
    dfs_dict['original_df'] = df.copy()

    # Filter on the selected data filters
    dfs_dict['dated_df'] = df.query(
        f"`{date_column}` <= '{selected_date}'"
    )

    # Market Positioning df
    dfs_dict['market_position_df'] = market_positions(
        df = dfs_dict['dated_df'],
        date_column = date_column,
        category_column = category_column,
        selected_column = selected_column
    )

    # Get relevant dates
    details_dicts.update(
        get_date_details(
            date_col_df = dfs_dict['dated_df'],
            date_column = date_column
        )
    )

    # Aggregate Data
    dfs_dict['aggregates_df_dict'] = aggregate_sums(
        df = dfs_dict['dated_df'],
        date_column = date_column,
        category_column = category_column,
    )

    # Top x data
    (
        dfs_dict['top_x_df_dict'],
        details_dicts['ordered_category_list']
    ) = create_top_x_and_other_df(
        df_dated = dfs_dict['dated_df'],
        date_column = date_column,
        selected_date = selected_date,
        category_column = category_column,
        selected_column = selected_column,
        top_x_category_list = top_x_category_list,
        market_position_df = dfs_dict['market_position_df'],
    )

    # Create period on period dfs
    top_x_df = dfs_dict['top_x_df_dict']['df']
    for months_ago in details_dicts['months_ago_list']:

        # Get reference date
        current_date = details_dicts['mom_dates_list'][0]
        reference_date = details_dicts['mom_dates_list'][months_ago]

        # Generate Chart
        dfs_dict[details_dicts[f'date_{months_ago}_col_prefix']] = date_to_date_comparison(
            df=top_x_df,
            date_column=date_column,
            selected_date=current_date,
            comparison_date=reference_date,
            selected_column=selected_column,
            category_column=category_column,
            prefix = details_dicts[f'date_{months_ago}_col_prefix'],
        )

    return dfs_dict, details_dicts
