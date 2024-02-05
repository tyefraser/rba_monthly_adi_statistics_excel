import logging

from utils import absolute_path, read_yaml
from utils_dataframe_calcs import filter_dataframe_by_values_then_group, df_column_movements_multiple

logger = logging.getLogger(__name__)


def aggregate_bank_stats_fn(
        narrow_rba_monthly_stats_df,
):
    aggregate_bank_stats_yaml = read_yaml(absolute_path(dir='aggregate_bank_statistics/aggregate_stats.yaml'))

    aggregate_bank_stats_df=filter_dataframe_by_values_then_group(
        df = narrow_rba_monthly_stats_df,
        group_data_dict = aggregate_bank_stats_yaml['groupings_dict'],
    )

    # Get columns movements over time
    column_names_list=list(aggregate_bank_stats_df.columns)
    column_names_list.remove('Period')

    aggregate_bank_stats_df=df_column_movements_multiple(
        df=aggregate_bank_stats_df,
        column_names_list=column_names_list,
        new_col_suffix='MoM Movement ($)'
    )


    
    return aggregate_bank_stats_df