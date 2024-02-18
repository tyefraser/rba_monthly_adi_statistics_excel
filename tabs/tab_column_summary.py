import streamlit as st
import pandas as pd
import numpy as np

from utils import rounded_dollars_md
from streamlit_utils import graph_selected_col


def point_txt(
        alias,
        category_column,
        selected_category,
        selected_column,
        period_dict,
        end = ".",
):
    period_category_df = period_dict['df'][period_dict['df'][category_column] == selected_category]
    
    # Month on Month Movements
    st.write(
        " - " +
        alias, "'s ", selected_column, " portfoliio ", f"{period_category_df[period_dict['movements_direction_col_name']].values[0]}d ",
        " by ",   rounded_dollars_md(period_category_df[period_dict['dollar_movements_col_name']].values[0]),
        " from ", rounded_dollars_md(period_category_df['comparison'].values[0]), " at ", period_dict['comparison_date'].strftime('%d %B %Y'),
        " to ",   rounded_dollars_md(period_category_df[selected_column].values[0]), " at ", period_dict['selected_date'].strftime('%d %B %Y'),
        end
    )

def escape_dollar_signs(text):
    # Escaping all dollar signs for Markdown and avoiding HTML entities
    return text.replace("$", "\\$").replace("\\\\$", "\\$")

def colum_details_dollars(
        df,
        reference_col
):
    # Provide details
    st.markdown(escape_dollar_signs(
        f" - The Net Total for {reference_col} is {rounded_dollars_md(df[reference_col].sum())}"
    ))
    movements_txt = (
        f" - The Total Positive {reference_col} values are {rounded_dollars_md(df[df[reference_col] >= 0][reference_col].sum())}" +
        f" (Negative:{rounded_dollars_md(df[df[reference_col] < 0][reference_col].sum())})"
    )
    st.markdown(escape_dollar_signs(movements_txt))    

def graph_movements(
        movement_dict,
        category_column,
        ordered_category_list,
        color_discrete_map,
):
    
    # Dollars
    st.write("## Dollar Movements")
    st.write("Total Dollar Movements over the period")
    graph_selected_col(
        df=movement_dict['df'],
        category_column=category_column,
        reference_col = movement_dict['dollar_movements_col_name'],
        ordered_category_list=ordered_category_list,
        show_xaxis_labels = True,
        x_gridcolor='Grey',
        color_discrete_map=color_discrete_map,
    )

    # Period on Period Movements
    st.write("## Period on Period Movements (%)")
    st.write("Movements over the period as a percentage of prior total")
    graph_selected_col(
        df=movement_dict['df'],
        category_column=category_column,
        reference_col = movement_dict['percentage_movements_col_name'],
        ordered_category_list=ordered_category_list,
        show_xaxis_labels = True,
        x_tickformat = ".1%",
        x_gridcolor='Grey',
        color_discrete_map=color_discrete_map,
    )

    st.write("## Movement / Market movement (%)")
    st.write("Movements as a percentage of the total market movement")
    graph_selected_col(
        df=movement_dict['df'],
        category_column=category_column,
        reference_col = movement_dict['percentage_of_market_movements_col_name'],
        ordered_category_list=ordered_category_list,
        show_xaxis_labels = True,
        x_tickformat = ".1%",
        x_gridcolor='Grey',
        color_discrete_map=color_discrete_map,
    )

def tab_column_summary_content(
        date_column,
        category_column,
        selected_category,
        alias,
        selected_date,
        selected_column,
        mom_dict,
        yoy_dict,
        top_x_and_other_df,
        ordered_category_list,
        color_discrete_map,
):

    # Key Points information
    st.markdown("# Key Points:")
    if alias == selected_category:
        st.write(f'Key Points for {selected_category}:')
    else:
        st.write(f"Key Points for {selected_category} ({alias}) as at {selected_date.strftime('%d %B %Y')}:")
    point_txt(
        alias=alias,
        category_column=category_column,
        selected_category=selected_category,
        selected_column=selected_column,
        period_dict=mom_dict,
        end = " in the previous month.",
    )
    point_txt(
        alias=alias,
        category_column=category_column,
        selected_category=selected_category,
        selected_column=selected_column,
        period_dict=yoy_dict,
        end = " in the previous year.",
    )
    

    # Graph current month balances
    st.markdown("___")
    st.markdown(f"# {selected_column} as at {selected_date.strftime('%d %B %Y')}")  
    df_selected_date_to_graph = top_x_and_other_df[top_x_and_other_df[date_column] == selected_date]
    graph_selected_col(
        df=df_selected_date_to_graph,
        category_column=category_column,
        reference_col = selected_column,
        ordered_category_list=ordered_category_list,
        show_xaxis_labels = True,
        x_gridcolor='Grey',
        color_discrete_map=color_discrete_map,
    )
    colum_details_dollars(
        df=df_selected_date_to_graph,
        reference_col=selected_column,
    )
    

    # Graph Month on Month data comparisons
    st.markdown("___")
    st.markdown(f"# {selected_column} Month on Month Movements")
    colum_details_dollars(
        df=mom_dict['df'],
        reference_col=mom_dict['dollar_movements_col_name'],
    )
    graph_movements(
        movement_dict=mom_dict,
        category_column=category_column,
        ordered_category_list=ordered_category_list,
        color_discrete_map=color_discrete_map,
    )

    # Graph Year on Year data comparisons
    st.markdown("___")
    st.markdown(f"# {selected_column} Year on Year Movements")
    colum_details_dollars(
        df=yoy_dict['df'],
        reference_col=yoy_dict['dollar_movements_col_name'],
    )
    graph_movements(
        movement_dict=yoy_dict,
        category_column=category_column,
        ordered_category_list=ordered_category_list,
        color_discrete_map=color_discrete_map,
    )

    # MoM mobements
    options = st.multiselect(
        f'Select {category_column} to include',
        top_x_and_other_df[category_column],
        selected_category,
    )
    st.write(options)

    return 0