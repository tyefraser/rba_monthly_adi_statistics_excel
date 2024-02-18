import logging
import pandas as pd
import streamlit as st
import numpy as np
import datetime as dt

logger = logging.getLogger(__name__)

def date_selection(
        df,
        date_column,
        col1,
):
    # Extract unique values from the column for dropdown options
    complete_dates_list = sorted(list(df[date_column].unique()), reverse=True)

    # Convert to datetime.datetime object
    complete_dates_list = pd.to_datetime(complete_dates_list).to_pydatetime()

    # Convet list to strings to present in list
    complete_dates_list_str = [
        timestamp.strftime('%Y %B %d') for timestamp in complete_dates_list]
        
    # max date from df
    max_date = complete_dates_list_str[0]

    # Create a dropdown widget with the unique values from the column
    # Place a selectbox in each column
    with col1:
        selected_date_picked = st.selectbox('Date', complete_dates_list_str, index=complete_dates_list_str.index(max_date))

    selected_date = complete_dates_list[complete_dates_list_str.index(selected_date_picked)]

    return selected_date

def column_selection(
        df,
        group_by_columns,
        default_column,
        col2,
):

    # Extract unique values from the column for dropdown options    
    columns_list = [col for col in list(df.columns) if col not in group_by_columns]

    # Update default value if required
    if default_column not in columns_list:
        default_column = columns_list[0]

    # Create a dropdown widget with the unique values from the column
    with col2:
        selected_column = st.selectbox('Select column', columns_list, index=columns_list.index(default_column))

    return selected_column

def category_selection(
        df,
        category_column,
        default_category,
        col3,
):
    # Extract unique values from the column for dropdown options
    categories = list(df[category_column].unique())

    # Set a default selected value for the dropdown, if it exists
    default_category = default_category if default_category in categories else categories[0]

    # Create a dropdown widget with the unique values from the column
    with col3:
        selected_category = st.selectbox('Select ' + category_column, categories, index=categories.index(default_category))
    
    return selected_category

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

    # Filter the data based on the selected option
    top_x_category_list = current_df.iloc[0:(top_x_value+1) , :][category_column].tolist()

    # Add selected category to list incase it isnt present
    top_x_category_list.append(selected_category)

    # Ensure list has only unique values
    top_x_category_list = list(set(top_x_category_list))

    return top_x_value, top_x_category_list

def select_data_filters(
        df,
        date_column,
        group_by_columns,
        default_column,
        category_column,
        default_category
):
    """
    This returns the filter selections made to apply to the data.
    Note: The filtering could be, but isnt, performed here for a number of reasons.
    """
    logger.debug("Executing: select_data_filters")

    # Create three columns to display the dropdowns
    col1, col2, col3 = st.columns(3)

    # Filter for the selected date
    selected_date = date_selection(
        df=df,
        date_column=date_column,
        col1=col1,
    )

    # Filter for the selected Column
    selected_column = column_selection(
        df=df,
        group_by_columns=group_by_columns,
        default_column=default_column,
        col2=col2,
    )

    # Select Category
    selected_category = category_selection(
        # only select categories from the relevant date selected
        df=df[df[date_column] == selected_date],
        category_column=category_column,
        default_category=default_category,
        col3=col3,
    )    

    # Select top x
    (
        top_x_value,
        top_x_category_list,
    ) = top_x_selection(
        df=df,
        date_column=date_column,
        selected_date=selected_date,
        category_column=category_column,
        selected_category=selected_category,
        selected_column=selected_column,
        default_x_value = 15,
    )

    logger.debug("Executed: select_data_filters")
    return selected_date, selected_column, selected_category, top_x_value, top_x_category_list
