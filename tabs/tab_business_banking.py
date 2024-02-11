import streamlit as st
import pandas as pd

from utils import rounded_dollars

def tab_business_banking_content(
        bb_df,
        aliases_dict,
):
    current_month = bb_df['Period'].max()
    prior_month = bb_df['Period'].iloc[-2]

    bb_df_current = bb_df[bb_df['Period'] == current_month]

    # Aggregated Stats

    st.write("""
        # Business Banking
        ## Aggregated Statistics - current month
    """)




    st.write("""
        ## Specific Bank Statistics
    """)
    
    category_column = 'Institution Name'

    # Extract unique values from the column for dropdown options
    categories = list(bb_df[category_column].unique())

    # Set a default selected value for the dropdown, if it exists
    default_category = 'Macquarie Bank Limited' if 'Macquarie Bank Limited' in categories else categories[0]

    # Create a dropdown widget with the unique values from the column
    selected_category = st.selectbox('Select Bank', categories, index=categories.index(default_category))

    # Create alias for the selected category
    alias = aliases_dict[selected_category] if selected_category in aliases_dict else selected_category

    
    # Group versus selected category
    top_x = st.slider('Select Top x Companies', 1, len(bb_df_current['Institution Name'].unique()), 10, 1)
    bb_category_agg_df = bb_df_current
    st.bar_chart(bb_category_agg_df.groupby('Institution Name')['Business Loans'].sum())

    # Filter the data based on the selected option
    filtered_data = bb_df[bb_df[category_column] == selected_category]

    # Generate Key Points
    # current_month = filtered_data['Period'].max()
    # prior_month = filtered_data['Period'].iloc[-2]
    filtered_data_current = filtered_data[filtered_data['Period'] == current_month]
    filtered_data_prior = filtered_data[filtered_data['Period'] == prior_month]
    point_movements = (
        alias + "'s Business Loans portfoliio " + filtered_data_current['Movement Direction'].values[0] +
        " by " + rounded_dollars(filtered_data_current['Business Loans - MoM ($)'].values[0]) +
        " from " + rounded_dollars(filtered_data_prior['Business Loans'].values[0]) + " at " + prior_month.strftime('%d %B %Y') +
        " to " + rounded_dollars(filtered_data_current['Business Loans'].values[0]) + " at " + current_month.strftime('%d %B %Y') +
        " in the previous month."
    )
    # point_movements
    

    # List key points about Business Banking    
    st.write("""
        Key statistics:
        - """ + point_movements + """
        - Business Banking is a key part of the banking sector
        - Business Banking is a key part of the banking sector
        - Business Banking is a key part of the banking sector
    """)


    # Update the graph and text based on the selected option
    st.write('Filtered Data:')
    st.write(filtered_data)
