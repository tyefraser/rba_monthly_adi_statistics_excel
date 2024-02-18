import pandas as pd
import plotly.express as px
import plotly as pt
import altair as alt
import plotly.graph_objects as go

from utils import rounded_dollars

def chart_selected_col_bar(
        df,
        category_column,
        reference_col,
        title = None,
        ordered_category_list=None,
        show_xaxis_labels = True,
        x_tickformat = None,
        x_gridcolor = None,
        color_discrete_map=None,
):
    if title == None:
        title = reference_col
    
    if ordered_category_list == None:
        ordered_category_list = df[category_column].tolist()

    if (color_discrete_map==None) or ('default_color' not in color_discrete_map.keys()):
        color_discrete_map = {'default_color': '#83C9FF'}

    # Create empty text if none exists
    if 'chart_txt' not in df.columns:
        df['chart_txt'] = ''

    # Plot with Plotly Express
    fig = px.bar(
        df,
        x=reference_col,
        y=category_column,
        orientation='h',
        title=title,
        color=category_column,
        text=df['chart_txt'],
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

def growth_over_time(
        category_df,
        date_column,
        chart_column,
):
    # category_df = dfs_dict['top_x_df'][dfs_dict['top_x_df'][category_column] == selected_category].copy()
    # category_df

    # Preparing the DataFrame
    category_df['Year'] = category_df[date_column].dt.year
    category_df['Month'] = category_df[date_column].dt.strftime('%B')  # Full month name
    category_df['MonthIndex'] = category_df[date_column].dt.month  # To ensure correct month sorting

    pivot_df = category_df.pivot_table(index=['Month', 'MonthIndex'], columns='Year', values=chart_column, aggfunc='sum').reset_index().sort_values('MonthIndex')
    pivot_df

    # Plotly graph
    fig = go.Figure()

    # Add a bar trace for each year
    for year in pivot_df.columns[2:]:  # Skipping 'Month' and 'MonthIndex' columns
        fig.add_trace(go.Bar(
            x=pivot_df['Month'],
            y=pivot_df[year],
            name=str(year),
        ))

    # Customize layout
    fig.update_layout(
        title='Monthly Values Over Years',
        xaxis_title='Month',
        yaxis_title='Value',
        barmode='group',  # Grouped bar chart
        xaxis={'categoryorder':'array', 'categoryarray':pivot_df['Month']}  # Ensure correct month order
    )

    return fig

def generate_charts(
    dfs_dict,
    details_dicts,
    date_column,
    selected_date,
    category_column,
    selected_category,
    selected_column,
    top_x_category_list,
    color_discrete_map,
):
    charts_dict = {}


    # Balance chart    
    top_x_df = dfs_dict['top_x_df_dict']['df']
    top_x_df_current = top_x_df[top_x_df[date_column] == selected_date]
    formatted_dollars  = top_x_df_current[selected_column].apply(rounded_dollars)
    formatted_percentages = top_x_df_current['Market Share'].apply(lambda x: f"({x * 100:.1f} %)")
    top_x_df_current.loc[:, 'chart_txt'] = formatted_dollars + ' ' + formatted_percentages
    charts_dict[selected_column] = chart_selected_col_bar(
        df = top_x_df_current,
        category_column = category_column,
        reference_col = f'{selected_column}',
        title = f'{selected_column}',
        ordered_category_list= details_dicts['ordered_category_list'],
        show_xaxis_labels = True,
        x_tickformat = None,
        x_gridcolor='Grey',
        color_discrete_map= color_discrete_map,
    )

    # Movements charts
    for months_ago in details_dicts['months_ago_list']:
        title = details_dicts[f'date_{months_ago}_col_prefix']
        if title in dfs_dict.keys():
            # get df
            movements_df = dfs_dict[title]['df']
            
            # Dollar Movements
            dollar_movements_col = dfs_dict[title]['dollar_movements_col_name']
            movements_df.loc[:, 'chart_txt'] = movements_df[dollar_movements_col].apply(rounded_dollars)
            charts_dict[dollar_movements_col] = chart_selected_col_bar(
                df = movements_df,
                category_column = category_column,
                reference_col = dollar_movements_col,
                ordered_category_list= details_dicts['ordered_category_list'],
                show_xaxis_labels = True,
                x_tickformat = None,
                x_gridcolor='Grey',
                color_discrete_map= color_discrete_map,
            )

            # Percentage Movements
            percentage_movements_col = dfs_dict[title]['percentage_movements_col_name']
            movements_df.loc[:, 'chart_txt'] = movements_df[percentage_movements_col].apply(lambda x: f"{x * 100:.1f} %")
            charts_dict[percentage_movements_col] = chart_selected_col_bar(
                df = movements_df,
                category_column = category_column,
                reference_col = percentage_movements_col,
                ordered_category_list= details_dicts['ordered_category_list'],
                show_xaxis_labels = True,
                x_tickformat = None,
                x_gridcolor='Grey',
                color_discrete_map= color_discrete_map,
            )

    return charts_dict



# px bar chart
##fig = px.bar(
##        data_frame=None,
##        x=None,
##        y=None,
##        color=None,
##        pattern_shape=None,
##        facet_row=None,
##        facet_col=None,
##        facet_col_wrap=0,
##        facet_row_spacing=None,
##        facet_col_spacing=None,
##        hover_name=None,
##        hover_data=None,
##        custom_data=None,
##        text=None,
##        base=None,
##        error_x=None,
##        error_x_minus=None,
##        error_y=None,
##        error_y_minus=None,
##        animation_frame=None,
##        animation_group=None,
##        category_orders=None,
##        labels=None,
##        color_discrete_sequence=None,
##        color_discrete_map=None,
##        color_continuous_scale=None,
##        pattern_shape_sequence=None,
##        pattern_shape_map=None,
##        range_color=None,
##        color_continuous_midpoint=None,
##        opacity=None,
##        orientation=None,
##        barmode='relative',
##        log_x=False,
##        log_y=False,
##        range_x=None,
##        range_y=None,
##        text_auto=False,
##        title=None,
##        template=None,
##        width=None,
##        height=None)


## def selected_col_chart(
##         top_x_df_as_at,
##         category_column,
##         selected_column,
##         ordered_category_list=None,        
##         color_discrete_map=None,
## ):
##     if ordered_category_list == None:
##         ordered_category_list = top_x_df_as_at[category_column].tolist()
## 
##     if (color_discrete_map==None) or ('default_color' not in color_discrete_map.keys()):
##         color_discrete_map = {'default_color': '#83C9FF'}
## 
##     # Get text to display
##     formatted_dollars  = top_x_df_as_at[selected_column].apply(rounded_dollars)
##     formatted_percentages = top_x_df_as_at['Market Share'].apply(lambda x: f"({x * 100:.1f} %)")
##     top_x_df_as_at['txt'] = formatted_dollars + ' ' + formatted_percentages
## 
##     # Plot with Plotly Express
##     fig = px.bar(
##         data_frame=top_x_df_as_at,
##         x=selected_column,
##         y=category_column,
##         color=category_column,
##         text=top_x_df_as_at['txt'],
##         category_orders={category_column: ordered_category_list},  # Ensure custom order is applied
##         color_discrete_sequence=[color_discrete_map['default_color']],
##         color_discrete_map=color_discrete_map,
##         orientation='h',
##         title=f"{selected_column}",
##         height=800
##     )
##     
##     # Update grid
##     fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='grey')
## 
##     
## 
##     # Optionally customize the layout
##     fig.update_layout(
##         xaxis_title=selected_column,
##         yaxis_title=category_column,
##         legend_title=category_column,
##         legend=dict(
##             orientation="h",
##             yanchor="bottom",
##             y=1.02,
##             xanchor="right",
##             x=1
##         ),
##         showlegend=False,
##     )
## 
##     # if not show_xaxis_labels:
##     #     fig.update_xaxes(tickangle=45, tickmode='array', tickvals=[])
##     
##     return fig

    # Selected column balances as at date chart
    ## top_x_df = dfs_dict['top_x_df_dict']['df']
    ## top_x_df_as_at = top_x_df[top_x_df[date_column] == selected_date]
    ## charts_dict['fig_balance_as_at'] = selected_col_chart(
    ##     top_x_df_as_at = top_x_df_as_at,
    ##     category_column = category_column,
    ##     selected_column = selected_column,
    ##     ordered_category_list = details_dicts['ordered_category_list'],        
    ##     color_discrete_map = color_discrete_map,
    ## )
