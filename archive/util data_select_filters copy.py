import pandas as pd
import streamlit as st
import numpy as np

from utils_data_select_filters import date_filter_selection
from utils_data_select_filters import column_filter_selection
from utils_data_select_filters import category_filter_selection
from utils_data_select_filters import top_x_filter_selection

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

    # Create three columns to display the dropdowns
    col1, col2, col3 = st.columns(3)

    # Generate date list and default as max
    complete_dates_list, max_date = date_filter_selection(
        df=df,
        date_column=date_column,
    )

    # Create a dropdown widget with the unique values from the column
    with col1:
        selected_date = st.selectbox('Date', complete_dates_list, index=complete_dates_list.index(max_date))


    # Filter for the selected Column
    columns_list, default_column = column_filter_selection(
        df=df,
        group_by_columns=group_by_columns,
        default_column=default_column,
    )

    # Create a dropdown widget with the unique values from the column
    with col2:
        selected_column = st.selectbox('Select column', columns_list, index=columns_list.index(default_column))

    # Select Category
    categories_list, default_category = category_filter_selection(
        # only select categories from the relevant date selected
        df=df[df[date_column] == selected_date],
        category_column=category_column,
        default_category=default_category,
    )   
    # Create a dropdown widget with the unique values from the column
    with col3:
        selected_category = st.selectbox('Select ' + category_column, categories_list, index=categories_list.index(default_category))

    # Select top x
    (
        top_x_value,
        top_x_category_list,
    ) = top_x_filter_selection(
        df=df,
        date_column=date_column,
        selected_date=selected_date,
        category_column=category_column,
        selected_category=selected_category,
        selected_column=selected_column,
        default_x_value = 15,
    )

    return selected_date, selected_column, selected_category, top_x_value, top_x_category_list
