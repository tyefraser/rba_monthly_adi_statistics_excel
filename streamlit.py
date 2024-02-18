import streamlit as st
import pandas as pd
import logging

from utils import read_yaml
from utils_logging import setup_logging
from utils_logging import close_log_handlers
from data_loading import data_loader
from data_filtering import filter_data
from tabs.tab_column_summary import tab_column_summary_content
from tabs.aggregate_summary import tab_aggregate_content
from tabs.tab_account_stats import tab_account_stats
from tabs.tab_about_page import tab_about
from data_select_filters import select_data_filters
from chart_generator import generate_charts
from descriptions import generate_descriptions

# Setup logging
close_log_handlers()
setup_logging()
logger = logging.getLogger(__name__)
logger.info("This is an info message from main.")

# Set page width
st.set_page_config(layout="wide")

# Get aliases from yaml
aliases_dict = read_yaml(file_path = 'aliases.yaml')

# Set colour scheme
color_discrete_map = read_yaml(file_path = 'color_discrete_map.yaml')

# Get data
df, file_name = data_loader()

# Grouping Columns
date_column = 'Period'
category_column = 'Institution Name'
exclude_columns = ['ABN']
df = df.drop(columns=exclude_columns)
group_by_columns = [date_column] + [category_column]

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


# Select Data filters
st.write("# Select Data Filters")
st.write("Please make your filtering selections below:")
(
    selected_date,
    selected_column,
    selected_category,
    top_x_value,
    top_x_category_list,
) = select_data_filters(
    df=df,
    date_column=date_column,
    group_by_columns=group_by_columns,
    default_column=default_column,
    category_column=category_column,
    default_category=default_category,
)

# Filter data
dfs_dict, details_dicts = filter_data(
        df = df,
        date_column = date_column,
        selected_date = selected_date,
        group_by_columns=group_by_columns,
        selected_column = selected_column,
        category_column = category_column,
        selected_category = selected_category,
        top_x_category_list = top_x_category_list,
)

# Generate graphs
charts_dict = generate_charts(
    dfs_dict = dfs_dict,
    details_dicts = details_dicts,
    date_column = date_column,
    selected_date = selected_date,
    category_column = category_column,
    selected_category = selected_category,
    selected_column = selected_column,
    top_x_category_list = top_x_category_list,
    color_discrete_map = color_discrete_map,
)

# Generate Descriptions
descriptions_dict = generate_descriptions(
    dfs_dict = dfs_dict,
    date_column = date_column,
    selected_column = selected_column,
    category_column = category_column,
    selected_category = selected_category,
    aliases_dict = aliases_dict,
    details_dicts = details_dicts,
)

# Insert containers separated into tabs:
tab1, tab2, tab3 = st.tabs(["Account Statistics", "Market Summaries", "About"])

# Tab 1 content
with tab1:
    tab_account_stats(
        dfs_dict = dfs_dict,
        charts_dict = charts_dict,
        selected_column = selected_column,
        selected_date = selected_date,
        descriptions_dict = descriptions_dict,
        aliases_dict = aliases_dict,
    )

# Tab 2 content
with tab2:
    st.write("Under construction.")
##     # tab_aggregate_content(
##     #     df=dfs_dict['original'],
##     #     selected_date=selections_dict['selected_date'],
##     # )
     
## 
# Tab 3 content
with tab3:
    tab_about(
        dfs_dict,
        file_name,
    )

close_log_handlers()