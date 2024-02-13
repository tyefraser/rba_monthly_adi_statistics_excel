import pandas as pd
import streamlit as st
import numpy as np

def date_selection(
        df,
        date_column,
        col1,
):
    # Extract unique values from the column for dropdown options
    complete_dates_list = sorted(list(df[date_column].unique()), reverse=True)
    
    # max date from df
    max_date = complete_dates_list[0]

    # Create a dropdown widget with the unique values from the column
    # Place a selectbox in each column
    with col1:
        selected_date = st.selectbox('Date', complete_dates_list, index=complete_dates_list.index(max_date))

    # Only keep data to the selected date or before
    df_dated = df[df[date_column] <= selected_date]

    # Extract dates from the dated df
    filtered_dates_list = sorted(list(df_dated[date_column].unique()), reverse=True)

    # Get prior month and yoy dates
    prior_month = filtered_dates_list[1]
    yoy_month = filtered_dates_list[12]    

    return complete_dates_list, selected_date, df_dated, filtered_dates_list, prior_month, yoy_month

def column_selection(
        df,
        date_column,
        group_by_columns,
        default_column,
        col2,
):

    # Extract unique values from the column for dropdown options    
    columns_list = [col for col in list(df.columns) if col not in group_by_columns]

    # Create a dropdown widget with the unique values from the column
    with col2:
        selected_column = st.selectbox('Select column', columns_list, index=columns_list.index(default_column))

    df_column = df[group_by_columns + [selected_column]]

    return df_column, selected_column

def category_selection(
        df,
        category_column,
        default_category,
        aliases_dict,
        col3,
):
    # Extract unique values from the column for dropdown options
    categories = list(df[category_column].unique())

    # Set a default selected value for the dropdown, if it exists
    default_category = default_category if default_category in categories else categories[0]

    # Create a dropdown widget with the unique values from the column
    with col3:
        selected_category = st.selectbox('Select ' + category_column, categories, index=categories.index(default_category))

    # Create alias for the selected category
    alias = aliases_dict[selected_category] if selected_category in aliases_dict else selected_category

    return selected_category, alias

def top_x_selection(
        df,
        date_column,
        selected_date,
        category_column,
        selected_category,
        selected_column,
        default_x_value = None,
):
    current_df = df[df[date_column] == selected_date][[category_column, selected_column]].sort_values(by=selected_column, ascending=False)

    # Define default_x_value if not set
    if default_x_value == None:
        default_x_value=int(len(current_df)/5)

    # Create a slider widget with the unique values from the column
    top_x_value = st.slider('Select Top x', 1, len(current_df), default_x_value, 1)

    # Get Selected Month Data
    # current_month_df = df_ranked[df_ranked[date_column] == selected_date]

    # Filter the data based on the selected option
    top_x_category_list = current_df.iloc[0:(top_x_value+1) , :][category_column].tolist()    

    # Add selected category to list incase it isnt present
    top_x_category_list.append(selected_category)

    # Ensure list has only unique values
    top_x_category_list = list(set(top_x_category_list))

    return top_x_value, top_x_category_list
        
def create_top_x_and_other_df(
        df,
        date_column,
        category_column,
        top_x_category_list,
        selected_column,
):
    # Assuming df is your DataFrame with columns: date_column, category_column, and selected_category
    # and categories of interest are in the list: top_x_category_list

    # Generate top x df

    # Filter DataFrame to include only categories of interest
    top_x_filtered_df = df[df[category_column].isin(top_x_category_list)][[date_column, category_column, selected_column]]

    # Group by month and category, summing the values
    top_x_grouped_df = top_x_filtered_df.groupby([top_x_filtered_df[date_column], category_column]).sum().reset_index()


    # 'Other' rows generator

    # Create a DataFrame with all unique months
    # to do: ensures there are no missing months (typing issue)
    # to do: all_months = pd.period_range(start=df[date_column].min(), end=df[date_column].max())
    # to do: all_months_df = pd.DataFrame({date_column: all_months})

    all_months_df = pd.DataFrame({date_column: df[date_column].unique()})

    # Cartesian product to get all combinations of months and categories of interest
    all_combinations_df = all_months_df.assign(key=1).merge(pd.DataFrame({category_column: top_x_category_list, 'key': 1}), on='key').drop('key', axis=1)


    # Merge with grouped DataFrame to fill missing combinations with zeros
    merged_df = pd.merge(all_combinations_df, top_x_grouped_df, on=[date_column, category_column], how='left').fillna(0)

    # Calculate sum of values for 'other' category for each month
    other_values = df[~df[category_column].isin(top_x_category_list)].groupby(df[date_column])[selected_column].sum().reset_index()
    other_values[category_column] = 'other'

    # Append 'other' values to merged DataFrame
    top_x_and_other_df = pd.concat([merged_df, other_values], ignore_index=True)

    # Sort DataFrame by date and category
    top_x_and_other_df = top_x_and_other_df.sort_values(by=[date_column, category_column])

    # Reset index
    top_x_and_other_df.reset_index(drop=True, inplace=True)

    return top_x_and_other_df

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
    df = df[df[date_column] == selected_date]
    
    # Create ordered list
    ordered_category_list = df.sort_values(by=selected_column, ascending=False).copy()[category_column].tolist()

    # Move 'other' if required
    if other_at_end:
        # Remove 'other' from its current position
        ordered_category_list.remove(other_col)

        # Append 'other' to the end of the list
        ordered_category_list.append(other_col)
    
    return ordered_category_list

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

    # df for teh selected dates
    df_two_dates = df[df[date_column].isin([selected_date, comparison_date])]
    df_two_dates.loc[df_two_dates[date_column] == selected_date, date_column] = selected_column
    df_two_dates.loc[df_two_dates[date_column] == comparison_date, date_column] = 'comparison'

    # Pivot the DataFrame
    pivot_df = df_two_dates.pivot_table(index=category_column, columns=date_column, values=selected_column, aggfunc='first')

    # Reset the index to make 'category' a column again
    pivot_df.reset_index(inplace=True)
    
    # Dollar Movements
    dollar_movements_col_name = f"{selected_column} -{prefix_padded}Movement ($)"
    pivot_df[dollar_movements_col_name] = pivot_df[selected_column] - pivot_df['comparison']

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
        group_by_columns,
        default_column,
        category_column,
        default_category,
        aliases_dict,
):
    dfs_dict = {}
    selections_dict = {}
    details_dicts = {}

    dfs_dict['original'] = df

    # Create three columns to display the dropdowns
    col1, col2, col3 = st.columns(3)

    # Place a selectbox in each column
    

    


    # Filter for the selected date
    (
        selections_dict['complete_dates_list'],
        selections_dict['selected_date'],
        dfs_dict['df_dated'],
        selections_dict['filtered_dates_list'],
        selections_dict['prior_month'],
        selections_dict['yoy_month'],
    ) = date_selection(
        df=dfs_dict['original'],
        date_column=date_column,
        col1=col1,
    )

    # Filter for the selected Column
    (
        dfs_dict['df_column'],
        selections_dict['selected_column'],
    ) = column_selection(
        df=dfs_dict['df_dated'],
        date_column=date_column,
        group_by_columns=group_by_columns,
        default_column=default_column,
        col2=col2,
    )

    # Select Category
    (
        selections_dict['selected_category'],
        selections_dict['alias'],
    ) = category_selection(
        df=dfs_dict['df_column'],
        category_column=category_column,
        default_category=default_category,
        aliases_dict=aliases_dict,
        col3=col3,
    )

    # Select top x
    selections_dict['top_x_value'], selections_dict['top_x_category_list'] = top_x_selection(
        df=dfs_dict['original'],
        date_column=date_column,
        selected_date=selections_dict['selected_date'],
        category_column=category_column,
        selected_category=selections_dict['selected_column'],
        selected_column=selections_dict['selected_column'],
        default_x_value = 15,
    )

    # Create df with top_x and other rows
    dfs_dict['top_x_and_other_df'] = create_top_x_and_other_df(
        df = df,
        date_column = date_column,
        category_column = category_column,
        top_x_category_list = selections_dict['top_x_category_list'],
        selected_column = selections_dict['selected_column'],
    )

    # Create default cetegory order - ordered list of category values including 'other' row
    selections_dict['ordered_category_list'] = ordered_category_list_fn(
        df = dfs_dict['top_x_and_other_df'],
        date_column=date_column,
        selected_date=selections_dict['selected_date'],
        selected_column=selections_dict['selected_column'],
        category_column=category_column,
        other_col = 'other',
        other_at_end = True,
    )
        
    # Month on Month data comparisons
    details_dicts['mom_dict'] = date_to_date_comparison(
        df=dfs_dict['top_x_and_other_df'],
        date_column=date_column,
        selected_date=selections_dict['selected_date'],
        comparison_date=selections_dict['prior_month'],
        selected_column=selections_dict['selected_column'],
        category_column=category_column,
        prefix = "MoM",
    )

    # Year on Year data comparisons
    details_dicts['yoy_dict'] = date_to_date_comparison(
        df=dfs_dict['top_x_and_other_df'],
        date_column=date_column,
        selected_date=selections_dict['selected_date'],
        comparison_date=selections_dict['yoy_month'],
        selected_column=selections_dict['selected_column'],
        category_column=category_column,
        prefix = "YoY",
    )

    return dfs_dict, selections_dict, details_dicts
