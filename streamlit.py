import streamlit as st
import pandas as pd
import logging

from utils import read_yaml
from data_generator import read_and_process_data
from data_generator import data_generator
from tabs.tab1 import tab1_content
from tabs.tab_business_banking import tab_business_banking_content
from tabs.tab_column_summary import tab_column_summary_content

# Get data
df = data_generator()

# Get aliases from yaml
aliases_dict = read_yaml(file_path = 'aliases.yaml')

st.write("""
    # APRA - Monthly ADI Statistics (MADIS)
    """)


# Present the reporting_date in the format of '30th December 2023'
reporting_date = df['Period'].max()
reporting_date_str = reporting_date.strftime('%d %B %Y')
st.write(f"Reporting date: {reporting_date_str}")


# Insert containers separated into tabs:
tab1, tab2, tab3 = st.tabs(["Tab 1", "Business Banking", "Test"])

# Tab 1 content
with tab1:
    tab_column_summary_content(
        df=df,
        aliases_dict=aliases_dict['aliases'],
    )

# Tab 2 content
with tab2:
    st.write("This is tab 3 content")
    # tab_business_banking_content(
    #     bb_df=data_dict['bb_df'],
    #     aliases_dict=aliases_dict['aliases'],
    # )

# Tab 3 content
with tab3:
    st.write("This is tab 3 content")
    
