import streamlit as st
import pandas as pd
import numpy as np

from utils import rounded_dollars_md
from streamlit_utils import graph_selected_col, date_selection



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
    top_x_category_list = current_df.iloc[0:(top_x_value+1) , :][category_column].tolist()    

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
    df_two_dates.loc[df_two_dates[date_column] == selected_date, date_column] = selected_column
    df_two_dates.loc[df_two_dates[date_column] == comparison_date, date_column] = 'comparison'

    # Pivot the DataFrame
    pivot_df = df_two_dates.pivot_table(index=category_column, columns=date_column, values=selected_column, aggfunc='first')

    # Reset the index to make 'category' a column again
    pivot_df.reset_index(inplace=True)
    
    # Dollar Movements
    dollar_movements_col_name = f"{selected_column} -{prefix_padded}Movement ($)"
    pivot_df[dollar_movements_col_name] = pivot_df[selected_column] - pivot_df['comparison']

    # Dollar Direction
    movement_direction_col_name = f"{selected_column} -{prefix_padded}Movement Direction"
    pivot_df[movement_direction_col_name] = np.where(pivot_df[dollar_movements_col_name] >= 0, 'increase', 'decrease')

    # Percentage Movements
    percentage_movements_col_name = f"{selected_column} -{prefix_padded}Movement (%)"
    pivot_df[percentage_movements_col_name] = (pivot_df[dollar_movements_col_name] / pivot_df['comparison']) # * 100

    # Percentage of market Movements
    percentage_of_market_movements_col_name = f"{selected_column} -{prefix_padded}Movement as Percentage of Market(%)"
    pivot_df[percentage_of_market_movements_col_name] = (pivot_df[dollar_movements_col_name] / pivot_df['comparison'].sum()) # * 100

    date_to_date_comparison_dict = {
        'prefix': prefix,
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
        df,
        aliases_dict,
        date_column = 'Period',
        group_columns = ['ABN', 'Institution Name'],
        category_column = 'Institution Name',
        default_category = 'Macquarie Bank Limited',
        default_column = 'Business Loans',
        color_discrete_map = None,
):
    # Set the columns to group by
    group_by_columns = [date_column] + group_columns

    # Selection Section
    st.write("# Data Selection")
    st.write("""
             In this section you can select filters to apply to the data. For example you can:
              - Select the 'as at' date you want to analyse
              - Select the specific data point to analyse
              - Specify the bank of interest
              - Indicate how many top banks to include within the graphs (including the bank of interest)
             
             Please make your selections below:
             """)

    # Filter for the selected date
    complete_dates_list, selected_date, df_dated, filtered_dates_list = date_selection(
        df=df,
        date_column=date_column,
    )
    # Get prior month and yoy dates
    prior_month = filtered_dates_list[-2]
    yoy_month = filtered_dates_list[-13]

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
    st.markdown("___")
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

    return 0