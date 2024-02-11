import streamlit as st
import pandas as pd
import plotly.express as px
# import plotly as pt
import numpy as np
from datetime import datetime

from utils import rounded_dollars, rounded_number, rounded_dollars_md
from single_column_stats import single_column_stats_fn
from streamlit_utils import stacked_area_100_perc, streamlit_column_graph

def date_selection(
        df,
        date_column
):
    # Extract unique values from the column for dropdown options
    complete_dates_list = sorted(list(df[date_column].unique()))
    
    # max date from df
    max_date = complete_dates_list[-1]

    # Create a dropdown widget with the unique values from the column
    selected_date = st.selectbox('Date', complete_dates_list, index=complete_dates_list.index(max_date))

    # Only keep data to the selected date or before
    df_dated = df[df[date_column] <= selected_date]

    # Extract dates from the dated df
    filtered_dates_list = sorted(list(df_dated[date_column].unique()))

    # Get prior month and yoy dates
    prior_month = filtered_dates_list[-2]
    yoy_month = filtered_dates_list[-13]

    return df_dated, selected_date, prior_month, yoy_month

def column_selection(
        df,
        date_column,
        group_by_columns,
        default_column,
        
):
    # Extract unique values from the column for dropdown options    
    columns_list = [col for col in list(df.columns) if col not in group_by_columns]

    # Create a dropdown widget with the unique values from the column
    selected_column = st.selectbox('Select column', columns_list, index=columns_list.index(default_column))

    df_column = df[group_by_columns + [selected_column]]

    return df_column, selected_column

def category_selection(
        df,
        category_column,
        default_category,
        aliases_dict,
):
    # Extract unique values from the column for dropdown options
    categories = list(df[category_column].unique())

    # Set a default selected value for the dropdown, if it exists
    default_category = default_category if default_category in categories else categories[0]

    # Create a dropdown widget with the unique values from the column
    selected_category = st.selectbox('Select ' + category_column, categories, index=categories.index(default_category))

    # Create alias for the selected category
    alias = aliases_dict[selected_category] if selected_category in aliases_dict else selected_category

    return selected_category, alias

def top_x_selection(
        df,
        date_column,
        selected_date,
        category_column,
        selected_category,
        selected_column,
        default_x_value = None,
):
    current_df = df[df[date_column] == selected_date][[category_column, selected_column]].sort_values(by=selected_column, ascending=False)

    # Define default_x_value if not set
    if default_x_value == None:
        default_x_value=int(len(current_df)/5)

    # Create a slider widget with the unique values from the column
    top_x_value = st.slider('Select Top x', 1, len(current_df), default_x_value, 1)

    # Get Selected Month Data
    # current_month_df = df_ranked[df_ranked[date_column] == selected_date]

    # Filter the data based on the selected option
    top_x_category_list = current_df.iloc[1:(top_x_value+1) , :][category_column].tolist()

    # Add selected category to list incase it isnt present
    top_x_category_list.append(selected_category)

    # Ensure list has only unique values
    top_x_category_list = list(set(top_x_category_list))

    return top_x_value, top_x_category_list
        
def create_top_x_and_other_df(
        df,
        date_column,
        category_column,
        top_x_category_list,
        selected_column,
):
    # Assuming df is your DataFrame with columns: date_column, category_column, and selected_category
    # and categories of interest are in the list: top_x_category_list

    # Generate top x df

    # Filter DataFrame to include only categories of interest
    top_x_filtered_df = df[df[category_column].isin(top_x_category_list)][[date_column, category_column, selected_column]]

    # Group by month and category, summing the values
    top_x_grouped_df = top_x_filtered_df.groupby([top_x_filtered_df[date_column], category_column]).sum().reset_index()


    # 'Other' rows generator

    # Create a DataFrame with all unique months
    # to do: ensures there are no missing months (typing issue)
    # to do: all_months = pd.period_range(start=df[date_column].min(), end=df[date_column].max())
    # to do: all_months_df = pd.DataFrame({date_column: all_months})

    all_months_df = pd.DataFrame({date_column: df[date_column].unique()})

    # Cartesian product to get all combinations of months and categories of interest
    all_combinations_df = all_months_df.assign(key=1).merge(pd.DataFrame({category_column: top_x_category_list, 'key': 1}), on='key').drop('key', axis=1)


    # Merge with grouped DataFrame to fill missing combinations with zeros
    merged_df = pd.merge(all_combinations_df, top_x_grouped_df, on=[date_column, category_column], how='left').fillna(0)

    # Calculate sum of values for 'other' category for each month
    other_values = df[~df[category_column].isin(top_x_category_list)].groupby(df[date_column])[selected_column].sum().reset_index()
    other_values[category_column] = 'other'

    # Append 'other' values to merged DataFrame
    top_x_and_other_df = pd.concat([merged_df, other_values], ignore_index=True)

    # Sort DataFrame by date and category
    top_x_and_other_df = top_x_and_other_df.sort_values(by=[date_column, category_column])

    # Reset index
    top_x_and_other_df.reset_index(drop=True, inplace=True)

    return top_x_and_other_df

def ordered_category_list_fn(
        df,
        date_column,
        selected_date,
        selected_column,
        category_column,
        other_col = 'other',
        other_at_end = True,
):
    # Get data for current month only
    df = df[df[date_column] == selected_date]
    
    # Create ordered list
    ordered_category_list = df.sort_values(by=selected_column, ascending=False).copy()[category_column].tolist()

    # Move 'other' if required
    if other_at_end:
        # Remove 'other' from its current position
        ordered_category_list.remove(other_col)

        # Append 'other' to the end of the list
        ordered_category_list.append(other_col)
    
    return ordered_category_list

def graph_selected_month(
    df,
    date_column,
    selected_date,
    selected_column,
    category_column,
    ordered_category_list=None,
    show_xaxis_labels = True,
):

    if ordered_category_list == None:
        ordered_category_list = ordered_category_list_fn(
            df = df,
            date_column=date_column,
            selected_date=selected_date,
            selected_column=selected_column,
            category_column=category_column,
            other_col = 'other',
            other_at_end = True,
        )
    
    # Graph current month df
    df_selected_date = df[df[date_column] == selected_date]

    # Plot with Plotly Express
    fig = px.bar(
        df_selected_date,
        x=category_column,
        y=selected_column,
        title=f"{selected_column} Month End Balances",
        color=category_column,
        category_orders={category_column: ordered_category_list},  # Ensure custom order is applied
        # color_discrete_map=colors,
        height=800
    )

    # Optionally customize the layout
    fig.update_layout(
        xaxis_title=category_column,
        yaxis_title=selected_column,
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

    st.plotly_chart(fig, use_container_width=True)

def graph_selected_col(
        df,
        category_column,
        col_to_chart,
        ordered_category_list=None,
        show_xaxis_labels = True,
):
    if ordered_category_list == None:
        ordered_category_list = df[category_column].tolist()

    # Plot with Plotly Express
    fig = px.bar(
        df,
        x=category_column,
        y=col_to_chart,
        title=f"{col_to_chart}",
        color=category_column,
        category_orders={category_column: ordered_category_list},  # Ensure custom order is applied
        # color_discrete_map=colors,
        height=800
    )

    # Optionally customize the layout
    fig.update_layout(
        xaxis_title=category_column,
        yaxis_title=col_to_chart,
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

    st.plotly_chart(fig, use_container_width=True)



def date_to_date_comparison(
        df,
        date_column,
        selected_date,
        comparison_date,
        selected_column,
        category_column,
        prefix = '',
):
    # Created padded varsiion of the prefix value
    if prefix == '':
        prefix_padded = ' '
    else:
        prefix_padded = ' ' + prefix + ' '

    # df for teh selected dates
    df_two_dates = df[df[date_column].isin([selected_date, comparison_date])]
    df_two_dates.loc[df_two_dates[date_column] == selected_date, date_column] = 'selected'
    df_two_dates.loc[df_two_dates[date_column] == comparison_date, date_column] = 'comparison'

    # Pivot the DataFrame
    pivot_df = df_two_dates.pivot_table(index=category_column, columns=date_column, values=selected_column, aggfunc='first')

    # Reset the index to make 'category' a column again
    pivot_df.reset_index(inplace=True)
    
    # Dollar Movements
    dollar_movements_col_name = f"{selected_column} -{prefix_padded}Movement ($)"
    pivot_df[dollar_movements_col_name] = pivot_df['selected'] - pivot_df['comparison']

    # Dollar Direction
    movement_direction_col_name = f"{selected_column} -{prefix_padded}Movement Direction"
    pivot_df[movement_direction_col_name] = np.where(pivot_df[dollar_movements_col_name] >= 0, 'increase', 'decrease')

    # Percentage Movements
    percentage_movements_col_name = f"{selected_column} -{prefix_padded}Movement (%)"
    pivot_df[percentage_movements_col_name] = (pivot_df[dollar_movements_col_name] / pivot_df['comparison']) * 100

    # Percentage of market Movements
    percentage_of_market_movements_col_name = f"{selected_column} -{prefix_padded}Movement as Percentage of Market(%)"
    pivot_df[percentage_of_market_movements_col_name] = (pivot_df[dollar_movements_col_name] / pivot_df['comparison'].sum()) * 100

    date_to_date_comparison_dict = {
        'df': pivot_df,
        'dollar_movements_col_name': dollar_movements_col_name,
        'movements_direction_col_name': movement_direction_col_name,
        'percentage_movements_col_name': percentage_movements_col_name,
        'percentage_of_market_movements_col_name': percentage_of_market_movements_col_name,
        'selected_date': selected_date,
        'comparison_date': comparison_date,
    }

    return date_to_date_comparison_dict

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
        " to ",   rounded_dollars_md(period_category_df['selected'].values[0]), " at ", period_dict['selected_date'].strftime('%d %B %Y'),
        end
    )



def tab_column_summary_content(
        df,
        aliases_dict,
        date_column = 'Period',
        group_columns = ['ABN', 'Institution Name'],
        category_column = 'Institution Name',
        default_category = 'Macquarie Bank Limited',
        default_column = 'Business Loans'
):
    # Set the columns to group by
    group_by_columns = [date_column] + group_columns

    # Filter for the selected date
    df_dated, selected_date, prior_month, yoy_month = date_selection(
        df=df,
        date_column=date_column,
    )

    # Filter for the selected Column
    df_column, selected_column = column_selection(
        df=df_dated,
        date_column=date_column,
        group_by_columns=group_by_columns,
        default_column=default_column,
    )

    # Select Category
    selected_category, alias = category_selection(
        df=df_column,
        category_column=category_column,
        default_category=default_category,
        aliases_dict=aliases_dict,
    )

    # Select top x
    top_x_value, top_x_category_list = top_x_selection(
        df,
        date_column,
        selected_date,
        category_column,
        selected_category,
        selected_column,
        default_x_value = 15,
    )

    # Create df with top_x and other rows
    top_x_and_other_df = create_top_x_and_other_df(
        df = df,
        date_column = date_column,
        category_column = category_column,
        top_x_category_list = top_x_category_list,
        selected_column = selected_column,
    )

    # Create default cetegory order - ordered list of category values including 'other' row
    ordered_category_list = ordered_category_list_fn(
        df = top_x_and_other_df,
        date_column=date_column,
        selected_date=selected_date,
        selected_column=selected_column,
        category_column=category_column,
        other_col = 'other',
        other_at_end = True,
    )

    # Define colors for specific categories
    # colors = {'YourCategory1': 'color1', 'YourCategory2': 'color2'}  # Define your color mapping

    # Month on Month data comparisons
    mom_dict = date_to_date_comparison(
        df=top_x_and_other_df,
        date_column=date_column,
        selected_date=selected_date,
        comparison_date=prior_month,
        selected_column=selected_column,
        category_column=category_column,
        prefix = "MoM",
    )

    # Year on Year data comparisons
    yoy_dict = date_to_date_comparison(
        df=top_x_and_other_df,
        date_column=date_column,
        selected_date=selected_date,
        comparison_date=yoy_month,
        selected_column=selected_column,
        category_column=category_column,
        prefix = "YoY",
    )

    # Key Points information
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
    graph_selected_month(
        df=top_x_and_other_df,
        date_column=date_column,
        selected_date=selected_date,
        selected_column=selected_column,
        category_column=category_column,
        ordered_category_list=ordered_category_list,
        show_xaxis_labels = True,
    )

    # Graph Month on Month data comparisons
    graph_selected_col(
        df=mom_dict['df'],
        category_column=category_column,
        col_to_chart = mom_dict['percentage_of_market_movements_col_name'],
        ordered_category_list=ordered_category_list,
        show_xaxis_labels = True,
    )

    # Graph Year on Year data comparisons
    graph_selected_col(
        df=yoy_dict['df'],
        category_column=category_column,
        col_to_chart = yoy_dict['percentage_of_market_movements_col_name'],
        ordered_category_list=ordered_category_list,
        show_xaxis_labels = True,
    )

    return 0