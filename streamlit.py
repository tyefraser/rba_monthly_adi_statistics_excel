import streamlit as st
import pandas as pd
import logging

from utils import read_yaml
from rba_monthly_adi_statistics import read_and_process_data


logger = logging.getLogger(__name__)

# Arguments
file_name: str = 'data/Monthly authorised deposit-taking institution statistics back-series March 2019 - December 2023.xlsx'
sheet_name: str = 'Table 1'
skiprows: int = 1
processes_to_run: list = ['all']
specific_bank_names_list: str = ['Macquarie Bank Limited']
date_column: str = 'Period'


# Read config
config_dict = read_yaml(file_path = 'config.yaml')

# Read and process data
rba_monthly_stats_df = read_and_process_data(
    config_dict=config_dict,
    file_name=file_name,
    sheet_name=sheet_name,
    skiprows=skiprows,
    date_column=date_column,        
)

# Melt the DataFrame to convert from wide to long format
id_cols = ['Period', 'ABN', 'Institution Name']
narrow_rba_monthly_stats_df = pd.melt(rba_monthly_stats_df, id_vars=id_cols, var_name='Variable', value_name='Value')


df = narrow_rba_monthly_stats_df[
    (narrow_rba_monthly_stats_df['Variable'] == 'Cash and deposits with financial institutions') &
    (narrow_rba_monthly_stats_df['Institution Name'] == 'Woori Bank')
][['Period', 'Value']]

# st.write
st.write("""
# My first app
Hello *world!*
""")

#st.line_chart(df)
#st.line_chart(df)

# Create a line chart with dates on the x-axis and values on the y-axis
st.line_chart(df.set_index('Period'))

# # Assuming df is your DataFrame containing the data
# 
# # Select x and y axis columns
# x_column = st.selectbox('Select x-axis column', df.columns)
# y_column = st.selectbox('Select y-axis column', df.columns)
# 
# # Plot line chart
# if x_column and y_column:
#     st.line_chart(df[[x_column, y_column]])