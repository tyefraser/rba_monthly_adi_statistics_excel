# from pandas import Timestamp
import logging
from dateutil.relativedelta import relativedelta

from utils import movement_values, rounded_dollars, rounded_dollars_md, escape_dollar_signs
from utils import percentage_to_string, period_ago, get_months_ago_list
from utils import ranking_position, position_s_movement

# Setup logging
logger = logging.getLogger(__name__)

def period_on_period_descriptions(
        txt,
        movement,
        cagr,
        prior_value,
        prior_date,
        period,
):
    # Generate MoM descriptions
    if movement > 0:
        txt = txt + f"\n     * Over the past {period} this has increased {rounded_dollars_md(movement)} (CAGR: {percentage_to_string(cagr)}, from {rounded_dollars_md(prior_value)} at {prior_date.strftime('%d %B %Y')})."
    elif movement < 0:
        txt = txt + f"\n     * Over the past {period} this has decreased {rounded_dollars_md(movement)} (CAGR: {percentage_to_string(cagr)}, from {rounded_dollars_md(prior_value)} at {prior_date.strftime('%d %B %Y')})."
    elif movement == 0:
        txt = txt + f"\n     * Over the past {period} this value has rermained stable at {rounded_dollars_md(prior_value)} at {prior_date.strftime('%d %B %Y')})."
    else:
        logger.info("ERROR: Movement cannot be determined")
    
    return txt

def movements_df_descriptions(
        df,
        date_column,
        selected_column,
        category_col,
        dollar_col,
        dollar_movements_col,
        percentage_movements_col,
        alias,
):
    # Current value
    current_value = df[dollar_col].iloc[-1]
    current_date = df[date_column].iloc[-1]    
    txt = f" - {alias}'s {selected_column} as at {current_date.strftime('%d %B %Y')} is {rounded_dollars_md(current_value)}. "

    # Points for eahc period
    months_list = get_months_ago_list(
        df = df,
        date_column = date_column,
    )
    for month in months_list:
        # MoM Values
        relative_month = month + 1
        prior_value = df[dollar_col].iloc[-relative_month]
        prior_date = df[date_column].iloc[-relative_month]
        movement, movement_perc = movement_values(start=prior_value, end=current_value)

        # Add point to txt
        txt = period_on_period_descriptions(
            txt = txt,
            movement = movement,
            cagr = ((1+float(movement_perc))**(12.0/month))-1,
            prior_value = prior_value,
            prior_date = prior_date,
            period = period_ago(months_ago=month),
        )
    
    return txt

def balance_movements_graph_text(
        alias,
        dfs_dict_ranked,
        date_column,
        category_column,
        selected_category,
        selected_column,
        details_dicts,
        
):
    # df details
    df = dfs_dict_ranked['df']
    dollar_movements_col = dfs_dict_ranked['dollar_movements_col']

    # Selected category
    df_selected_category = df[df[category_column] == selected_category]

    # Current balances
    current_ranking = df_selected_category['Rank'].iloc[-1]
    current_balance = df_selected_category[selected_column].iloc[-1]
    current_balance_str  = rounded_dollars_md(current_balance)
    balance_description = f" - {alias} is currently {ranking_position(current_ranking)} in the market with a total {selected_column} balance of {current_balance_str}"

    # Get number of months within data    
    months_ago_list = get_months_ago_list(
        df = df_selected_category,
        date_column = date_column,
    )

    # Prior months descriptions
    for months_ago in months_ago_list:
        # Prior date
        date = details_dicts[f'date_{months_ago}_months_ago'] # .strftime('%Y-%m-%d')
        period = details_dicts[f'date_{months_ago}_wording']

        # At as date descriptions
        if (df_selected_category[date_column] == date).any():
            # Prior movements            
            month_ref = months_ago + 1
            prior_month_ranking = df_selected_category['Rank'].iloc[-month_ref]
            prior_month_balance = df_selected_category[selected_column].iloc[-month_ref]
            movement = (current_balance - prior_month_balance)
            # prior_month_dollar_movement = df_selected_category[dollar_movements_col].iloc[-month_ref]
            # prior_month_dollar_movement_str  = rounded_dollars_md(prior_month_dollar_movement)

            # Balance Movements
            balance_movements_txt = f'Over the past {period} this balance has '
            if movement > 0:
                txt = f'increased by {rounded_dollars_md(movement)}'
            elif movement < 0:
                txt = f'decreased by {rounded_dollars_md(movement)}'
            else:
                txt = 'remained unchanged.'
            balance_movements_txt = balance_movements_txt + txt            

            # Ranking text
            position_movement = int(current_ranking-prior_month_ranking)
            position_movement_str = str(abs(position_movement))
            if (position_movement < 0):
                position_movement_txt = f'increased {position_movement_str} {position_s_movement(position_movement)} from {ranking_position(prior_month_ranking)}.'
            elif (position_movement > 0):
                position_movement_txt = f'decreased {position_movement_str} {position_s_movement(position_movement)} from {ranking_position(prior_month_ranking)}.'
            else:
                position_movement_txt = f'remained at {ranking_position(prior_month_ranking)} position'

            balance_description = f'{balance_description}\n    - {balance_movements_txt} and {position_movement_txt}'
    
    return balance_description

def generate_descriptions(
        dfs_dict,
        date_column,
        selected_column,
        category_column,
        selected_category,
        aliases_dict,
        details_dicts, 
):
    descriptions_dict = {}

    # Alias
    if selected_category in aliases_dict.keys():
        alias = aliases_dict[selected_category]
    else:
        alias = selected_category

    # Aggregates data
    aggregates_df = dfs_dict['aggregates_df_dict']['df']
    aggregates_df_category_col = dfs_dict['aggregates_df_dict']['category_col']
    aggregates_df_dollar_col = dfs_dict['aggregates_df_dict']['dollar_col']
    aggregates_df_dollar_movements_col = dfs_dict['aggregates_df_dict']['dollar_movements_col']
    aggregates_df_percentage_movements_col = dfs_dict['aggregates_df_dict']['percentage_movements_col']

    # Top x data
    topx_x_df = dfs_dict['top_x_df_dict']['df']
    topx_x_df_category_col = dfs_dict['top_x_df_dict']['category_col']
    topx_x_df_dollar_col = dfs_dict['top_x_df_dict']['dollar_col']
    topx_x_df_dollar_movements_col = dfs_dict['top_x_df_dict']['dollar_movements_col']
    topx_x_df_percentage_movements_col = dfs_dict['top_x_df_dict']['percentage_movements_col']


    # Account Statistics - Aggregate
    aggregates_df_selected_col = aggregates_df[aggregates_df[aggregates_df_category_col] == selected_column]
    descriptions_dict['account_statistics_aggregate'] = movements_df_descriptions(
        df = aggregates_df_selected_col,
        date_column = date_column,
        selected_column = selected_column,
        category_col = aggregates_df_category_col,
        dollar_col = aggregates_df_dollar_col,
        dollar_movements_col = aggregates_df_dollar_movements_col,
        percentage_movements_col = aggregates_df_percentage_movements_col,
        alias = 'The total market'
    )

    # Account Statistics - selected category
    topx_x_df_selected_category = topx_x_df[topx_x_df[topx_x_df_category_col] == selected_category]
    descriptions_dict['account_statistics_category'] = movements_df_descriptions(
        df = topx_x_df_selected_category,
        date_column = date_column,
        selected_column = selected_column,
        category_col = topx_x_df_category_col,
        dollar_col = topx_x_df_dollar_col,
        dollar_movements_col = topx_x_df_dollar_movements_col,
        percentage_movements_col = topx_x_df_percentage_movements_col,
        alias = alias,
    )

    # Columns Movements Chart
    descriptions_dict['balance_movements_graph_text'] = balance_movements_graph_text(
        alias = alias,
        dfs_dict_ranked = dfs_dict['top_x_df_dict'],
        date_column = date_column,
        category_column = category_column,
        selected_category = selected_category,
        selected_column = selected_column,
        details_dicts = details_dicts,
    )

    


    return descriptions_dict