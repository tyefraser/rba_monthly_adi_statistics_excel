import pandas as pd
import logging

from utils import read_yaml
from data_processing.business_loans.business_loans import business_loans_fn
from pd_data_frame_checks import check_columns_existence, convert_columns_dict_type_allocation, column_adjustments
from utils_dataframe_calcs import new_calculated_column

logger = logging.getLogger(__name__)

def read_and_process_data(
        config_dict,
        file_name,
        sheet_name,
        skiprows,
        date_column,
):
    # Read the Excel file into a DataFrame
    df = pd.read_excel(
        io=file_name,
        sheet_name=sheet_name,
        skiprows=skiprows,
    )

    # Sort by date column
    df.sort_values(by=date_column, inplace=True)

    # Check expected columns exist
    check_columns_existence(
        df=df,
        target_columns=config_dict['expected_columns_list']
    )

    # Column Data Types
    df=convert_columns_dict_type_allocation(
        df=df.copy(),
        col_types_dict=config_dict['column_typing_dict'],
    )

    # Column Adjustments - convert to dollar amounts (not scalled)
    df=column_adjustments(df, config_dict)

    return df


def data_generator(
        file_name: str = 'data/Monthly authorised deposit-taking institution statistics back-series March 2019 - December 2023.xlsx',
        sheet_name: str = 'Table 1',
        skiprows: int = 1,
        date_column: str = 'Period',
):
    # Read config
    config_dict = read_yaml(file_path = 'config.yaml')

    # Read and process data
    df = read_and_process_data(
        config_dict=config_dict,
        file_name=file_name,
        sheet_name=sheet_name,
        skiprows=skiprows,
        date_column=date_column,        
    )

    # Create calculated columns
    for new_column_name, calculations in config_dict['calculated_columns'].items():
        df[new_column_name] = 0
        for column_calculation in calculations:
            calculation = column_calculation[0]
            column = column_calculation[1]
            df = new_calculated_column(
                df=df,
                new_column_name=new_column_name,
                calculation=calculation,
                column=column,
            )

    return df
