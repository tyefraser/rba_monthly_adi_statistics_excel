from utils import read_yaml
import logging

# Create a logger variable
logger = logging.getLogger(__name__)

def business_loans_fn(
        narrow_rba_monthly_stats_df,
):
    logger.debug('\nRunning: business_loans_fn')

    # Read config
    business_banking_config_dict = read_yaml(file_path = 'business_loans/business_loans_config.yaml')
    alias_dict = read_yaml(file_path = 'alias.yaml')

    # Maintain only the business loan data
    narrow_rba_monthly_stats_df[narrow_rba_monthly_stats_df['Variable'].isin(business_banking_config_dict['account_groupings']['Business Loans'])]

    return business_banking_config_dict