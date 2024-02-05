from utils import read_yaml
import logging

# Create a logger variable
logger = logging.getLogger(__name__)

def specific_bank_calculations(
        rba_monthly_stats_df,
        specific_bank_names_list,

):
    logger.debug('\nRunning: specific_bank_calculations')
    # Read config
    specific_bank_config_dict = read_yaml(file_path = 'process_specific_bank/single_bank_analysis.yaml')
    alias_dict = read_yaml(file_path = 'alias.yaml')

    for specific_bank_name in specific_bank_names_list:
        # Use alias if available
        try:
            alias=alias['alias'][specific_bank_name]
        except:
            alias=specific_bank_name
        
        # Retrive data for the specific bank
        specific_bank_df=rba_monthly_stats_df[
                rba_monthly_stats_df['Institution Name'] == specific_bank_name   
            ]
    

    
    return specific_bank_config_dict