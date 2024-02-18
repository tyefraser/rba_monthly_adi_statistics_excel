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
        details_dicts,
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

    # Movement Charts
    st.markdown("## Movement Charts")
    for months_ago in details_dicts['months_ago_list']:
        title = details_dicts[f'date_{months_ago}_col_prefix']
        if title in dfs_dict.keys():
            st.write(f"### {title} Movments")
            st.plotly_chart(charts_dict[f'{selected_column} - {title} Movement ($)'], use_container_width=True)
            st.plotly_chart(charts_dict[f'{selected_column} - {title} Movement (%)'], use_container_width=True)

    return 0