import streamlit as st
import pandas as pd
import plotly.express as px

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
        group_by_columns,
        default_column,
):
    # Extract unique values from the column for dropdown options    
    columns_list = [col for col in list(df.columns) if col not in group_by_columns]

    # Create a dropdown widget with the unique values from the column
    selected_column = st.selectbox('Select column', columns_list, index=columns_list.index(default_column))

    df_column = df[group_by_columns + [selected_column]]

    return df_column, selected_column

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
        df,
        group_by_columns,
        default_column,
    )

    # Select Category

    # Extract unique values from the column for dropdown options
    categories = list(df[category_column].unique())

    # Set a default selected value for the dropdown, if it exists
    default_category = default_category if default_category in categories else categories[0]

    # Create a dropdown widget with the unique values from the column
    selected_category = st.selectbox('Select ' + category_column, categories, index=categories.index(default_category))

    # Create alias for the selected category
    alias = aliases_dict[selected_category] if selected_category in aliases_dict else selected_category



    # Select top x

    # Create a slider widget with the unique values from the column
    top_x = st.slider('Select Top x', 1, df_column['rank'].max(), 15, 1)

    # Get Selected Month Data
    current_month_df = df_column[df_column[date_column] == selected_date]

    # Filter the data based on the selected option
    top_x_category_df = current_month_df[current_month_df['rank'] <= top_x]

    # List of the top x categories
    top_x_category_list = top_x_category_df[category_column].tolist()

    # add selected category to the list
    top_x_category_list.append(selected_category)

    # make sure the list is unique
    top_x_category_list = list(set(top_x_category_list))

    # Assuming df is your DataFrame with columns: date_column, category_column, and selected_category
    # and categories of interest are in the list: top_x_category_list

    # Filter DataFrame to include only categories of interest
    top_x_filtered_df = df[df[category_column].isin(top_x_category_list)][[date_column, category_column, selected_column]]

    # Group by month and category, summing the values
    grouped_df = top_x_filtered_df.groupby([top_x_filtered_df[date_column], category_column]).sum().reset_index()

    # Create a DataFrame with all unique months
    # to do: ensures there are no missing months (typing issue)
    # to do: all_months = pd.period_range(start=df[date_column].min(), end=df[date_column].max())
    # to do: all_months_df = pd.DataFrame({date_column: all_months})

    all_months_df = pd.DataFrame({date_column: df[date_column].unique()})

    # Cartesian product to get all combinations of months and categories of interest
    all_combinations_df = all_months_df.assign(key=1).merge(pd.DataFrame({category_column: top_x_category_list, 'key': 1}), on='key').drop('key', axis=1)


    # Merge with grouped DataFrame to fill missing combinations with zeros
    merged_df = pd.merge(all_combinations_df, grouped_df, on=[date_column, category_column], how='left').fillna(0)

    # Calculate sum of values for 'other' category for each month
    other_values = df[~df[category_column].isin(top_x_category_list)].groupby(df[date_column])[selected_column].sum().reset_index()
    other_values[category_column] = 'other'

    # Append 'other' values to merged DataFrame
    final_df = pd.concat([merged_df, other_values], ignore_index=True)

    # Sort DataFrame by date and category
    final_df = final_df.sort_values(by=[date_column, category_column])

    # Reset index
    final_df.reset_index(drop=True, inplace=True)

    # stacked_area_100_perc(
    #     df=final_df,
    #     date_column=date_column,
    #     category_column=category_column,
    #     selected_column=selected_column,
    # )

    streamlit_column_graph(
        df=final_df,
        date_column=date_column,
        category_column=category_column,
        selected_column=selected_column,
        display_data = False
    )


    # # Insert containers separated into tabs:
    # market, individual = st.tabs(["Market", "Individual Bank"])
    # # Tab 1 content
    # with market:
    #     streamlit_column_graph(
    #         df=final_df,
    #         date_column=date_column,
    #         category_column=category_column,
    #         selected_column=selected_column,
    #         display_data = True
    #     )
    # with individual:
    #     streamlit_column_graph(
    #         df=final_df,
    #         date_column=date_column,
    #         category_column=category_column,
    #         selected_column=selected_column,
    #         display_data = True
    #     )

    # Generate Key Points
    st.write(current_month)
    st.write(prior_month)
    filtered_data_current = df_column[(df_column['Period'] == current_month) & (df_column[category_column] == selected_category)]
    filtered_data_prior = df_column[(df_column['Period'] == prior_month) & (df_column[category_column] == selected_category)]
    st.write(filtered_data_current)
    st.write(filtered_data_prior)

    movement_txt = str(rounded_dollars(filtered_data_current[selected_column + ' - MoM ($)'].values[0]))
    sign, number, scale =rounded_number(filtered_data_current[selected_column + ' - MoM ($)'].values[0])
    point_tst_1 = (
        f"{alias}'s {selected_column} portfoliio {filtered_data_current[selected_column + ' - MoM Movement Direction'].values[0]}d " +
        f" by {sign}${number} {scale} "
    )
    st.write(point_tst_1)
    st.write(f"Test Latex issue \$ issue? \$ point_tst_1")

    sign, number, scale = rounded_number(filtered_data_prior[selected_column].values[0])
    point_tst_2 = (
        f"from {rounded_dollars(filtered_data_prior[selected_column].values[0])} at {prior_month.strftime('%d %B %Y')}"
        # f" from {sign}${number} {scale} at {prior_month.strftime('%d %B %Y')}"
    )
    st.write(point_tst_2)

    point_tst_3 = (
        f" to {rounded_dollars(filtered_data_current[selected_column].values[0])} at {current_month.strftime('%d %B %Y')} in the previous month."
    )
    st.write(point_tst_3)

    st.text(str(point_tst_1) + str(point_tst_2) + str(point_tst_3))
    st.markdown(str(point_tst_1) + str(point_tst_2) + str(point_tst_3))

    

            # f"from {rounded_dollars(filtered_data_prior[selected_column].values[0])} at {prior_month.strftime('%d %B %Y')}" +
        # f" to {rounded_dollars(filtered_data_current[selected_column].values[0])} at {current_month.strftime('%d %B %Y')} in the previous month."


    # direction_txt = str(filtered_data_current[selected_column + ' - MoM Movement Direction'].values[0])
    prior_amount_txt = str(rounded_dollars(filtered_data_prior[selected_column].values[0]))
    current_amount_txt = str(rounded_dollars(filtered_data_current[selected_column].values[0]))


    st.write(" by ", rounded_dollars(filtered_data_current[selected_column + ' - MoM ($)'].values[0]))

    st.write("HERE")
    st.write(
        alias, "'s ", selected_column, " portfoliio ", filtered_data_current[selected_column + ' - MoM Movement Direction'].values[0], "d ",
        " by ", rounded_dollars_md(filtered_data_current[selected_column + ' - MoM ($)'].values[0]),
        " from ", rounded_dollars_md(filtered_data_prior[selected_column].values[0]), " at ", prior_month.strftime('%d %B %Y'),
        " to ", rounded_dollars_md(filtered_data_current[selected_column].values[0]), " at ", current_month.strftime('%d %B %Y'),
        " in the previous month."
    )

    
    st.write(f'movement_txt:{movement_txt}')
    st.write(f'direction_txt: {direction_txt}')
    st.write(f'prior_amount_txt:{prior_amount_txt}')
    st.write(f'current_amount_txt:{current_amount_txt}')

    point_movements = (
        alias + "'s " + selected_column + " portfoliio " + direction_txt + "d " +
        " by " + str(movement_txt) +
        " from " + prior_amount_txt + " at " + prior_month.strftime('%d %B %Y') +
        " to " + current_amount_txt + " at " + current_month.strftime('%d %B %Y') +
        " in the previous month."
    )
    st.write(point_movements)
    st.markdown(point_movements, unsafe_allow_html=True)
    st.markdown(point_movements)


    point_movements = (
        alias + "'s " + selected_column + " portfoliio " + filtered_data_current[selected_column + ' - MoM Movement Direction'].values[0] + "d " +
        " by " + rounded_dollars(filtered_data_current[selected_column + ' - MoM ($)'].values[0]) +
        " from " + rounded_dollars(filtered_data_prior[selected_column].values[0]) + " at " + prior_month.strftime('%d %B %Y') +
        " to " + rounded_dollars(filtered_data_current[selected_column].values[0]) + " at " + current_month.strftime('%d %B %Y') +
        " in the previous month."
    )

    # Display the string using st.write()
    st.write("""
        Key statistics:
        - """ + point_movements + """
        - Business Banking is a key part of the banking sector
        - Business Banking is a key part of the banking sector
        - Business Banking is a key part of the banking sector
    """)
    
    

    return final_df
    
    

    


    # Update the graph and text based on the selected option
    st.write('Filtered Data:')
    st.write(filtered_data)
