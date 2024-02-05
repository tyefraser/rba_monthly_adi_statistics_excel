import pandas as pd
from pd_data_frame_checks import check_columns_existence

from utils import read_yaml
from pd_data_frame_checks import convert_columns_dict_type_allocation
from process_specific_bank.process_specific_bank import specific_bank_calculations

def read_and_process_data(
        config_dict,
        file_name: str = 'data/Monthly authorised deposit-taking institution statistics back-series March 2019 - December 2023.xlsx',
        sheet_name: str = 'Table 1',
        skiprows: int = 1,
        date_column: str = 'Period',
):
    # Read the Excel file into a DataFrame
    rba_monthly_stats_df = pd.read_excel(
        io=file_name,
        sheet_name=sheet_name,
        skiprows=skiprows,
    )

    # Sort by date column
    rba_monthly_stats_df.sort_values(by=date_column, inplace=True)

    # Check expected columns exist
    check_columns_existence(
        df=rba_monthly_stats_df,
        target_columns=config_dict['expected_columns_list']
    )

    # Column Data Types    
    convert_columns_dict_type_allocation(
        df=rba_monthly_stats_df.copy(),
        col_types_dict=config_dict['column_typing_dict'],
    )


    return rba_monthly_stats_df

def main(
        file_name: str = 'data/Monthly authorised deposit-taking institution statistics back-series March 2019 - December 2023.xlsx',
        sheet_name: str = 'Table 1',
        skiprows: int = 1,
        specific_bank_names_list: str = ['Macquarie Bank Limited'],
        processes_to_run: list = ['all'],
        date_column: str = 'Period',
):
    
    # Read config
    config_dict = read_yaml(file_path = 'config.yaml')

    # Read and process data
    rba_monthly_stats_df = read_and_process_data(
        config_dict=config_dict,
        file_name=file_name,
        sheet_name=sheet_name,
        skiprows=skiprows,
        date_column=date_column,        
    )

    print("hi")
    
    return rba_monthly_stats_df

    # Analysis using wide table format

    # Run code for specific bank
    if 'all' in processes_to_run or 'specific_bank' in processes_to_run:
        print('Running: specific_bank')
        ret = specific_bank_calculations(
            rba_monthly_stats_df=rba_monthly_stats_df,
            specific_bank_names_list=specific_bank_names_list,
        )
        return ret

    ## Analysis Requiring long table format
#
    ## Melt the DataFrame to convert from wide to long format
    #id_cols = ['Period', 'ABN', 'Institution Name']
    #narrow_rba_monthly_stats_df = pd.melt(rba_monthly_stats_df, id_vars=id_cols, var_name='Variable', value_name='Value')
#
    #
    ## Run code for complete set of banks at aggregated level
    #if 'all' in processes_to_run or 'banks_at_aggregate' in processes_to_run:
    #    None
    #
    ## Run code for top # set of banks from the current month
    #if 'all' in processes_to_run or 'top_x' in processes_to_run:
    #    None


    return 0 

if __name__ == "__main__":
    main()