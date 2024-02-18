import streamlit as st
import pandas as pd
import numpy as np
import io

import streamlit as st

def get_file_content_as_string(path):
    """Read a file and return its content as a string."""
    with open(path, "rb") as file:
        return file.read()

def download_file(
        file_path,
        label,
        mime: str = "text/plain",
):
    # Path to your log file within your repo/app structure
    # file_path

    # Read the content of the file
    file_content = get_file_content_as_string(file_path)

    # Provide a button to download the log file
    st.download_button(
        label=label,
        data=file_content,
        file_name=file_path,
        mime = mime,
    )

def tab_about(
        dfs_dict,
        file_name,
):
    st.title("About the APRA Monthly ADI Statistics Dashboard")

    st.markdown("""
        **Welcome to the APRA Monthly ADI Statistics Dashboard**

        This interactive dashboard provides insights into the latest trends and analyses of the Australian financial sector, focusing on Authorised Deposit-taking Institutions (ADIs). Powered by data from the Australian Prudential Regulation Authority (APRA), our tool is designed to assist analysts, investors, policymakers, and the general public in understanding the financial health and performance of ADIs.

        **Features of the Dashboard:**

        - **Interactive Charts:** Explore a range of visualizations that highlight key metrics such as business loans, deposits, and other financial indicators across various ADIs.
        - **Current and Historical Data:** Access up-to-date statistics and historical trends to gauge performance over time.
        - **Insightful Analysis:** Gain valuable insights through our curated analysis, helping you to decipher the complexities of the banking sector.
                
        **Tips:**
        - **Open Multiple Browsers**: If you are looking to perform comparisons, it may be best to open two instances of the app side by side.
                
        """)
    
    # DO 
    left_co, cent_co,last_co = st.columns([1,100,1])
    with cent_co:
        st.image('assets/side_by_side.png', caption='Side-by-side Comparisons', use_column_width="auto")
    
    st.markdown("""
        **Data Source:**

        All data presented in this dashboard is sourced directly from the APRA Monthly ADI Statistics report, ensuring accuracy and reliability. For more detailed information and access to the raw data, please visit [APRA's official website](https://www.apra.gov.au/).

        **How to Use This Dashboard:**

        - Navigate through different tabs to explore various data visualizations.
        - Hover over charts to see specific data points and metrics.
        - Use filters to customize the data display according to your interests.

        **Disclaimer:**

        This dashboard is for informational purposes only and should not be considered as financial advice. While we strive to ensure the accuracy of the information, users are advised to consult with financial experts before making any investment decisions.

    """, unsafe_allow_html=True)

    # Gloassary
    # 'total market' represents all companies within the APRA dataset, not necessarily the full Australian market
    
    ## **Contact Us:**
    ## 
    ##     For feedback, questions, or more information, please contact us at [info@example.com](mailto:info@example.com).

    # Centered Image
    left_co, cent_co,last_co = st.columns([1,10,1])
    with cent_co:
        st.image('assets/graphic.webp', caption='Financial Data Analytics Dashboard', use_column_width="auto")
    


    # Key Points information
    st.markdown("# Downloads:")

    # Data
    download_file(
        file_path = file_name,
        label = 'Download data',
        mime = "text/plain",
    )

    # INFO Logs
    download_file(
        file_path = "logs/info.log",
        label = 'Download INFO logs',
        mime = "text/plain",
    )

    # Details Logs
    download_file(
        file_path = "logs/detailed.log",
        label = 'Download DEBUG logs',
        mime = "text/plain",
    )

    return 0