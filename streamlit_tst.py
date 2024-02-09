import streamlit as st
import pandas as pd
import logging

from utils import read_yaml
from rba_monthly_adi_statistics import read_and_process_data
from data_generator import data_generator
from tabs.tab1 import tab1_content
from tabs.tab_business_banking import tab_business_banking_content

# Get data
data_dict = data_generator()
# data_dict['rba_monthly_stats_df']
# data_dict['narrow_rba_monthly_stats_df']
# data_dict['bb_df']


st.write("""
    # APRA - Monthly ADI Statistics (MADIS)
    """)


# Present the reporting_date in the format of '30th December 2023'
reporting_date = data_dict['rba_monthly_stats_df']['Period'].max()
reporting_date_str = reporting_date.strftime('%d %B %Y')
st.write(f"Reporting date: {reporting_date_str}")


# Insert containers separated into tabs:
tab1, tab2, tab3 = st.tabs(["Tab 1", "Business Banking", "Test"])

# Tab 1 content
with tab1:
    tab1_content()

# Tab 2 content
with tab2:
    tab_business_banking_content(
        bb_df=data_dict['bb_df']
    )

# Tab 3 content
with tab3:
    tab_business_banking_content(
        bb_df=data_dict['bb_df']
    )
    st.write("This is tab 3 content")
    


#st.line_chart(df)
#st.line_chart(df)

# Create a line chart with dates on the x-axis and values on the y-axis


# # Assuming df is your DataFrame containing the data
# 
# # Select x and y axis columns
# x_column = st.selectbox('Select x-axis column', df.columns)
# y_column = st.selectbox('Select y-axis column', df.columns)
# 
# # Plot line chart
# if x_column and y_column:
#     st.line_chart(df[[x_column, y_column]])