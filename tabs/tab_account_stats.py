import streamlit as st
import pandas as pd
import numpy as np

from utils import rounded_dollars_md
from streamlit_utils import graph_selected_col

def tab_account_stats(
        dfs_dict,
        charts_dict,
        selected_column,
        selected_date,
        descriptions_dict,
        aliases_dict,
):
    # Tab header
    st.markdown(f"# {selected_column} as at {selected_date.strftime('%d %B %Y')}")

    # Key Points information
    st.markdown("## Key Points:")
    st.write(descriptions_dict['account_statistics_aggregate'])
    st.write(descriptions_dict['account_statistics_category'])

    # Provide Plot
    st.markdown("## Balance Charts")
    st.write(descriptions_dict['balance_movements_graph_text'])
    st.plotly_chart(charts_dict[selected_column], use_container_width=True)
    

    return 0