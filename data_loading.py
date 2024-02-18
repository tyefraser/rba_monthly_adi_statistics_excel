import pandas as pd
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from urllib.parse import quote
import requests

from utils import read_yaml
from data_processing.business_loans.business_loans import business_loans_fn
from pd_data_frame_checks import check_columns_existence, convert_columns_dict_type_allocation, column_adjustments
from utils_dataframe_calcs import new_calculated_column

logger = logging.getLogger(__name__)

def load_url_xlsx():
    base_url = 'https://www.apra.gov.au/sites/default/files/'
    last_month_eom = datetime.now().replace(day=1) - timedelta(days=1)
    last_month_yyyy_mm = last_month_eom.strftime('%Y-%m')
    file_path = '/Monthly%20authorised%20deposit-taking%20institution%20statistics%20back-series%20March%202019%20-%20'
    two_months_ago = last_month_eom - relativedelta(months=1)
    two_months_ago_mmm_yyyy = two_months_ago.strftime('%B %Y')
    file_extension = '.xlsx'

    # Concatenate the strings to form the full URL
    full_url = base_url + last_month_yyyy_mm + file_path + quote(two_months_ago_mmm_yyyy) + file_extension

    try:
        # Set xlsx path
        file_name = f"data/madis_{two_months_ago_mmm_yyyy}.xlsx".replace(' ', '_')

        # Attempt to load URL xlsx
        response = requests.get(full_url)
        response.raise_for_status()  # This will raise an exception if there is an error

        with open(file_name, 'wb') as f:
            f.write(response.content)

        logger.debug(f"File downloaded successfully! file_name:{file_name}")
    except Exception as e:
        logger.info(f"Failed to download the file: {e}")

        # Set xlsx path
        file_name = 'data/Monthly authorised deposit-taking institution statistics back-series March 2019 - December 2023.xlsx'
        logger.info(f"Using alternative file: {file_name}")
    
    return file_name

def read_and_process_data(
        config_dict,
        file_name,
        date_column,
):
    # Read the Excel file into a DataFrame
    df = pd.read_excel(
        io=file_name,
        sheet_name=config_dict['file_loading_details']['sheet_name'],
        skiprows=config_dict['file_loading_details']['skiprows'],
    )

    # Sort by date column
    df.sort_values(by=date_column, inplace=True)

    # Check expected columns exist
    check_columns_existence(
        df=df,
        target_columns=config_dict['file_loading_details']['expected_columns_list']
    )

    # Column Data Types
    df=convert_columns_dict_type_allocation(
        df=df.copy(),
        col_types_dict=config_dict['column_typing_dict'],
    )

    # Column Adjustments - convert to dollar amounts (not scalled)
    df=column_adjustments(df, config_dict)

    df[date_column] = pd.to_datetime(df[date_column])

    return df


def data_loader():
    logger.debug("Executing: data_loader")
     # to do: generate logs to see what columns are converted to what - datetime col issues

    # Read config
    config_dict = read_yaml(file_path = 'config.yaml')
    date_column = 'Period'

    # Load data
    file_name=load_url_xlsx()

    # Read and process data
    df = read_and_process_data(
        config_dict=config_dict,
        file_name=file_name,
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

    logger.debug("Executed: data_loader")
    return df, file_name
