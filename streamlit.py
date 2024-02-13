import streamlit as st
import pandas as pd
import logging

from utils import read_yaml
from data_loading import data_loader
from data_filtering import filter_data
from tabs.tab_column_summary import tab_column_summary_content
from tabs.aggregate_summary import tab_aggregate_content


# Set page width
st.set_page_config(layout="wide")

# Get aliases from yaml
aliases_dict = read_yaml(file_path = 'aliases.yaml')

# Set colour scheme
color_discrete_map = read_yaml(file_path = 'color_discrete_map.yaml')


# Get data
df = data_loader()

# Grouping Columns
date_column = 'Period'
group_columns = ['ABN', 'Institution Name']
category_column = 'Institution Name'
group_by_columns = [date_column] + group_columns

# Set default selections
default_category = 'Macquarie Bank Limited'
default_column = 'Business Loans'


# Header
st.write("""
    # APRA - Monthly ADI Statistics (MADIS)
    """)
reporting_date = df['Period'].max()
reporting_date_str = reporting_date.strftime('%d %B %Y')
st.write(f"Reporting date: {reporting_date_str}") # Present the reporting_date in the format of '30th December 2023'


# Selection Section
st.write("# Data Filters")
st.write("Please make your filtering selections below:")
dfs_dict, selections_dict, details_dicts = filter_data(
        df=df,
        date_column=date_column,
        group_by_columns=group_by_columns,
        default_column=default_column,
        category_column=category_column,
        default_category=default_category,
        aliases_dict=aliases_dict,
)


# Insert containers separated into tabs:
tab1, tab2, tab3 = st.tabs(["Account Statistics", "Market Summaries", "How To Use"])

# Tab 1 content
with tab1:
    tab_column_summary_content(
        date_column=date_column,
        category_column=category_column,
        selected_category=selections_dict['selected_category'],
        alias=selections_dict['alias'],
        selected_date=selections_dict['selected_date'],
        selected_column=selections_dict['selected_column'],
        mom_dict=details_dicts['mom_dict'],
        yoy_dict=details_dicts['yoy_dict'],
        top_x_and_other_df=dfs_dict['top_x_and_other_df'],
        ordered_category_list=selections_dict['ordered_category_list'],
        color_discrete_map=color_discrete_map,
    )

# Tab 2 content
with tab2:
    # tab_aggregate_content(
    #     df=dfs_dict['original'],
    #     selected_date=selections_dict['selected_date'],
    # )
    st.write("Under construction.")

# Tab 3 content
with tab3:
    st.write("Under construction.")
    
