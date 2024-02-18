import pandas as pd
import plotly.express as px
import plotly as pt
import altair as alt


def chart_selected_col_bar(
        df,
        category_column,
        reference_col,
        ordered_category_list=None,
        show_xaxis_labels = True,
        x_tickformat = None,
        x_gridcolor = None,
        color_discrete_map=None,
):
    if ordered_category_list == None:
        ordered_category_list = df[category_column].tolist()

    if (color_discrete_map==None) or ('default_color' not in color_discrete_map.keys()):
        color_discrete_map = {'default_color': '#83C9FF'}

    # Plot with Plotly Express
    fig = px.bar(
        df,
        x=reference_col,
        y=category_column,
        orientation='h',
        title=f"{reference_col}",
        color=category_column,
        category_orders={category_column: ordered_category_list},  # Ensure custom order is applied
        color_discrete_map=color_discrete_map,
        color_discrete_sequence=[color_discrete_map['default_color']],
        height=800
    )

    # Format the x-axis
    if x_tickformat != None:
        fig.update_xaxes(tickformat=x_tickformat)  # ".0%" for no decimal places
        # fig.update_xaxes(tickformat=x_tickformat, tickmode='linear')  # ".0%" for no decimal places

    if x_gridcolor != None:
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=x_gridcolor)

    # Optionally customize the layout
    fig.update_layout(
        xaxis_title=reference_col,
        yaxis_title=category_column,
        legend_title=category_column,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        showlegend=False,
    )

    if not show_xaxis_labels:
        fig.update_xaxes(tickangle=45, tickmode='array', tickvals=[])

    return fig

def chart_selected_col_line(
        df,
        category_column,
        reference_col,
        ordered_category_list=None,
        show_xaxis_labels = True,
        x_tickformat = None,
        x_gridcolor = None,
        color_discrete_map=None,
):
    if ordered_category_list == None:
        ordered_category_list = df[category_column].tolist()

    if (color_discrete_map==None) or ('default_color' not in color_discrete_map.keys()):
        color_discrete_map = {'default_color': '#83C9FF'}

    # Plot with Plotly Express
    fig = px.line(
        df,
        x=reference_col,
        y=category_column,
        orientation='h',
        title=f"{reference_col}",
        color=category_column,
        category_orders={category_column: ordered_category_list},  # Ensure custom order is applied
        color_discrete_map=color_discrete_map,
        color_discrete_sequence=[color_discrete_map['default_color']],
        height=800
    )

    # Format the x-axis
    if x_tickformat != None:
        fig.update_xaxes(tickformat=x_tickformat)  # ".0%" for no decimal places
        # fig.update_xaxes(tickformat=x_tickformat, tickmode='linear')  # ".0%" for no decimal places

    if x_gridcolor != None:
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=x_gridcolor)

    # Optionally customize the layout
    fig.update_layout(
        xaxis_title=reference_col,
        yaxis_title=category_column,
        legend_title=category_column,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        showlegend=False,
    )

    if not show_xaxis_labels:
        fig.update_xaxes(tickangle=45, tickmode='array', tickvals=[])

    return fig