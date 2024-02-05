import plotly.express as px

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_column_graph(date_column, value_column, title='Column Graph', xlabel='Date', ylabel='Value'):
    """
    Plot a column graph from a Pandas DataFrame with a date column and a value column.

    Parameters:
    - date_column (pd.Series): The date column.
    - value_column (pd.Series): The value column (floats).
    - title (str): Title of the plot.
    - xlabel (str): Label for the x-axis.
    - ylabel (str): Label for the y-axis.

    Returns:
    - None: Displays the plot.
    """
    plt.figure(figsize=(10, 6))  # Adjust the figure size as needed
    plt.bar(date_column, value_column, color='skyblue')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  # Format date on x-axis

    plt.tight_layout()
    plt.show()



def plot_column_graph_plotly(date_column, value_column, title='Column Graph', xlabel='Date', ylabel='Value'):
    """
    Plot an interactive column graph using plotly.express from a Pandas DataFrame with a date column and a value column.

    Parameters:
    - date_column (pd.Series): The date column.
    - value_column (pd.Series): The value column (floats).
    - title (str): Title of the plot.
    - xlabel (str): Label for the x-axis.
    - ylabel (str): Label for the y-axis.

    Returns:
    - None: Displays the plot.
    """
    df = pd.DataFrame({'Date': date_column, 'Value': value_column})
    fig = px.bar(df, x='Date', y='Value', title=title, labels={'Value': ylabel, 'Date': xlabel})
    fig.update_xaxes(type='category')  # Set the x-axis type to category for date handling
    fig.update_layout(xaxis=dict(tickmode='linear'))  # Adjust x-axis ticks for better spacing
    fig.show()
