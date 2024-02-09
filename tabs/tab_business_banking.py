import streamlit as st

def tab_business_banking_content(bb_df):
    # List key points about Business Banking    
    st.write("""
        ## Business Banking
        
        Key statistics:
        - Business Banking is a key part of the banking sector
        - Business Banking is a key part of the banking sector
        - Business Banking is a key part of the banking sector
    """)
    
    
    st.line_chart(bb_df.set_index('Period'))
