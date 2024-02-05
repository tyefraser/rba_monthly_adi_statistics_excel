import pandas as pd

def convert_columns_by_type(df, cols_list, cols_type):
    """
    Convert specified columns in a DataFrame to the specified data type.

    Parameters:
        df (pd.DataFrame): The DataFrame to perform column conversions on.
        cols_list (list): List of column names to convert.
        cols_type (str): Desired data type for the specified columns ('date', 'str', 'float').

    Raises:
        ValueError: If an unexpected data type is provided.

    Returns:
        None: The function modifies the DataFrame in place.
    """
    if cols_type == 'date':
        df[cols_list] = df[cols_list].apply(pd.to_datetime, errors='coerce').apply(lambda x: x.dt.date)
    elif cols_type == 'str':
        df[cols_list] = df[cols_list].astype(str)
    elif cols_type == 'float':
        df[cols_list] = df[cols_list].astype(float)
    else:
        raise ValueError('Unexpected data type. Supported types are: "date", "str", "float".')

def convert_columns_dict_type_allocation(df, col_types_dict):
    """
    Convert specified columns in a DataFrame to their respective data types based on a dictionary.

    Parameters:
        df (pd.DataFrame): The DataFrame to perform column conversions on.
        col_types_dict (dict): Dictionary associating data types with lists of column names.

    Returns:
        pd.DataFrame: The modified DataFrame with converted columns.
    """

    # Generate else columns list
    not_else_cols_list = []
    for key in col_types_dict.keys():
        if key not in ['skip_cols', 'else_cols_as_type']:
            not_else_cols_list = not_else_cols_list + col_types_dict[key]
    else_cols_list = [col for col in df.columns if col not in not_else_cols_list]

    # Convert columns to correct types
    for key, cols in col_types_dict.items():
        # Skipped Columns
        if key == 'skip_cols':
            continue
        # Columns to be converted with a common type
        elif key == 'else_cols_as_type':
            convert_columns_by_type(
                df=df,
                cols_list=else_cols_list,
                cols_type=cols  # assuming else_cols_as_type contains only one data type
            )
        else:
            convert_columns_by_type(
                df=df,
                cols_list=cols,
                cols_type=key
            )

    return df

def check_columns_existence(df, target_columns):
    """
    Check if all specified columns exist in a DataFrame.

    Parameters:
        df (pd.DataFrame): The DataFrame to check.
        target_columns (list): List of column names to check for existence.

    Raises:
        ValueError: If any specified columns are missing.

    Returns:
        None: If all columns exist, no exceptions are raised.
    """
    existing_columns = df.columns
    missing_columns = [col for col in target_columns if col not in existing_columns]

    if missing_columns:
        raise ValueError(f"Error: Columns not found in DataFrame: {missing_columns}")
