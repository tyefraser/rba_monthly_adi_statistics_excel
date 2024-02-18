def date_filter_selection(
        df,
        date_column,
):
    # Extract unique values from the column for dropdown options
    complete_dates_list = sorted(list(df[date_column].unique()), reverse=True)
    
    # max date from df
    max_date = complete_dates_list[0]

    return complete_dates_list, max_date

def column_filter_selection(
        df,
        group_by_columns,
        default_column,
):

    # Extract unique values from the column for dropdown options    
    columns_list = [col for col in list(df.columns) if col not in group_by_columns]

    # Update default value if required
    if default_column not in columns_list:
        default_column = columns_list[0]

    return columns_list, default_column

def category_filter_selection(
        df,
        category_column,
        default_category,
):
    # Extract unique values from the column for dropdown options
    categories_list = list(df[category_column].unique())

    # Set a default selected value for the dropdown, if it exists
    default_category = default_category if default_category in categories_list else categories_list[0]
    
    return categories_list, default_category

def top_x_filter_selection(
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

    # Filter the data based on the selected option
    top_x_category_list = current_df.iloc[0:(top_x_value+1) , :][category_column].tolist()

    # Add selected category to list incase it isnt present
    top_x_category_list.append(selected_category)

    # Ensure list has only unique values
    top_x_category_list = list(set(top_x_category_list))

    return top_x_value, top_x_category_list
