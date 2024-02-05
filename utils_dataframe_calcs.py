import pandas as pd
import logging

# Create a logger variable
logger = logging.getLogger(__name__)

def filter_dataframe_by_values(df, df_column_filter_dict):
    """
    Filter a DataFrame based on specified values for multiple columns.

    Parameters:
    - df (pd.DataFrame): The input DataFrame.
    - column_filter_dict (dict): A dictionary where keys are column names and values are filter values.

    Returns:
    - pd.DataFrame: The filtered DataFrame.
    """
    logger.debug('\nRunning: filter_dataframe_by_values')

    for column, filter_values in df_column_filter_dict.items():
        logger.debug(f"Filtering by {column}: {filter_values}")
        df = df[df[column].isin(filter_values)]

    return df

def group_data(
        df,
        base_column,
        calculated_column,
        calculation,
        column_name,
):
    """
    Group data in a DataFrame based on a specified column and perform aggregation.

    Parameters:
    - df (pd.DataFrame): The input DataFrame.
    - base_column (str): The column to group by.
    - calculated_column (str): The column to perform the calculation on.
    - calculation (str): The type of aggregation ('count' for counting unique values, 'sum' for summing).
    - column_name (str): The name for the new calculated column.

    Returns:
    - pd.DataFrame: The resulting DataFrame with grouped and aggregated data.
    """
    logger.debug('\nRunning: group_data')

    if calculation == 'count':
        # Group by 'base_column' and count unique values in 'calculated_column'
        aggregated_df = df.groupby(base_column)[calculated_column].nunique().reset_index()

        # Rename the calculated column
        aggregated_df = aggregated_df.rename(columns={calculated_column: column_name})

    elif calculation == 'sum':
        # Group by 'base_column' and sum values in 'calculated_column'
        aggregated_df = df.groupby(base_column)[calculated_column].sum().reset_index()

        # Rename the calculated column
        aggregated_df = aggregated_df.rename(columns={calculated_column: column_name})

    else:
        raise ValueError("Invalid calculation type. Use 'count' or 'sum'.")

    return aggregated_df

def filter_dataframe_by_values_then_group(
        df,
        group_data_dict
):
    """
    Filter a DataFrame by values and then group it based on specified criteria.

    Parameters:
    - df (pd.DataFrame): The input DataFrame.
    - group_data_dict (dict): A dictionary containing grouping information. E.g.
        base_column: 'Period'
        column_groupings_dict:
            'ABN - count':
            'calculated_column': 'ABN'
            'calculation': 'count'
            'Cash - totals':
            df_column_filter_dict:
                'Variable': ['Cash and deposits with financial institutions']
                'ABN' : [94150148299]
            'calculated_column': 'Value'
            'calculation': 'sum'

    Returns:
    - pd.DataFrame: The resulting DataFrame after filtering and grouping.
    """
    logger.debug('Running: filter_dataframe_by_values_then_group')

    # Create dictionary to store all dfs into before combining them all
    grouped_data_dfs_dict = {}

    for column_grouping, group_settings in group_data_dict['column_groupings_dict'].items():
        logger.debug(f'\nProcessing column_grouping: {column_grouping}')

        # Create a copy of the DataFrame for the current grouping
        column_grouping_df = df.copy()

        # Filter on the required data if df_column_filter_dict is specified
        if 'df_column_filter_dict' in group_settings:
            column_grouping_df = filter_dataframe_by_values(column_grouping_df, group_settings['df_column_filter_dict'])

        # Group the DataFrame based on specified criteria
        column_grouping_df = group_data(
            df=column_grouping_df,
            base_column=group_data_dict['base_column'],
            calculated_column=group_settings['calculated_column'],
            calculation=group_settings['calculation'],
            column_name=column_grouping,
        )

        grouped_data_dfs_dict[column_grouping] = column_grouping_df
    
    # Combined all filters into a single DataFrame
    grouped_data_df = pd.DataFrame()
    for df_name, df in grouped_data_dfs_dict.items():
        if grouped_data_df.empty:
            grouped_data_df = df
        else:
            grouped_data_df = pd.merge(grouped_data_df, df, on='Period', how='left')

    return grouped_data_df

def df_column_movements(
        df,
        column_name,
        new_col_suffix,
):
    # Calculate row by row (downward) movements
    new_column_name=(column_name + ' - ' + new_col_suffix)
    df[new_column_name] = df[column_name].diff()

    return df

def df_column_movements_multiple(
        df,
        column_names_list,
        new_col_suffix,
):
    for column in column_names_list:
        df_column_movements(
            df=df,
            column_name=column,
            new_col_suffix=new_col_suffix
        )
    
    return df