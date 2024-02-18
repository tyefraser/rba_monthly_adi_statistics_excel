import streamlit as st
import pandas as pd
import plotly.express as px
import plotly as pt
import altair as alt


def graph_selected_col(
        df,
        category_column,
        reference_col,
        ordered_category_list=None,
        show_xaxis_labels = True,
        x_tickformat = None,
        x_gridcolor = None,
        color_discrete_map=None,
):
    if ordered_category_list == None:
        ordered_category_list = df[category_column].tolist()

    if (color_discrete_map==None) or ('default_color' not in color_discrete_map.keys()):
        color_discrete_map = {'default_color': '#83C9FF'}

    # Plot with Plotly Express
    fig = px.bar(
        df,
        x=reference_col,
        y=category_column,
        orientation='h',
        title=f"{reference_col}",
        color=category_column,
        category_orders={category_column: ordered_category_list},  # Ensure custom order is applied
        color_discrete_map=color_discrete_map,
        color_discrete_sequence=[color_discrete_map['default_color']],
        height=800
    )

    # Format the x-axis
    if x_tickformat != None:
        fig.update_xaxes(tickformat=x_tickformat)  # ".0%" for no decimal places
        # fig.update_xaxes(tickformat=x_tickformat, tickmode='linear')  # ".0%" for no decimal places

    if x_gridcolor != None:
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=x_gridcolor)

    # Optionally customize the layout
    fig.update_layout(
        xaxis_title=reference_col,
        yaxis_title=category_column,
        legend_title=category_column,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        showlegend=False,
    )

    if not show_xaxis_labels:
        fig.update_xaxes(tickangle=45, tickmode='array', tickvals=[])

    # Provide Plot
    st.plotly_chart(fig, use_container_width=True)

def stacked_area_100_perc(
        df,
        date_column,
        category_column,
        selected_column,
):
    fig = px.area(df, x=date_column, y=selected_column, color=category_column, 
                    title='100% Stacked Area Graph of Total Revenue by Company',
                    labels={date_column: 'Date', selected_column: selected_column, category_column: 'Company'},
                    category_orders={category_column: sorted(df[category_column].unique())}, # Ensure consistent color mapping
                    color_discrete_sequence=px.colors.qualitative.Set1) # Set color scheme

    fig.update_layout(yaxis=dict(tickformat=".0%"))  # Format y-axis as percentage

    # Display the plot using Streamlit
    st.plotly_chart(fig)



def streamlit_column_graph(
        df,
        date_column,
        category_column,
        selected_column,
        selected_date=None,
        display_data=False,
):

    if selected_date is None:
        selected_date = df[date_column].max()

    chart_data_df = df[df[date_column] == selected_date][[category_column, selected_column]]

    # Sort the DataFrame by the desired column
    sorted_chart_data_df = chart_data_df.sort_values(by=selected_column, ascending=False).reset_index(drop=True).copy()

    # Create an Altair chart
    bars = alt.Chart(sorted_chart_data_df).mark_bar().encode(
        x=alt.X(category_column, axis=alt.Axis(title=category_column, labels=False)),  # Remove x-axis labels
        y=alt.Y(selected_column, axis=alt.Axis(title=selected_column)),
        color=alt.Color(
            category_column,
            legend=alt.Legend(
                orient='bottom',
                title=category_column,
                titleFontSize=12,
                labelFontSize=10,
                labelOverlap='parity',
                columns=2,
                rowPadding=5,
                symbolType='square'
            ))
    ).properties(
        width=600,
        height=400
    )

    # Display the Altair chart using st.altair_chart()
    st.altair_chart(bars)

    # Display the sorted DataFrame if required
    if display_data:
        st.write(sorted_chart_data_df)


    # Create an Altair chart
    bars = alt.Chart(sorted_chart_data_df).mark_bar().encode(
        x=alt.X(category_column, axis=alt.Axis(title=category_column, labels=False)),
        y=alt.Y(selected_column, axis=alt.Axis(title=selected_column)),
        color=alt.Color(
            category_column,
            legend=alt.Legend(
                orient='bottom',
                title=category_column,
                titleFontSize=12,
                labelFontSize=10,
                labelOverlap='parity',
                columns=2,
                rowPadding=5,
                symbolType='square'
            ))
    ).properties(
        width=600,
        height=400
    )

    # Display the Altair chart using st.altair_chart()
    st.altair_chart(bars)

    # Display the sorted DataFrame if required
    if display_data:
        st.write(sorted_chart_data_df)

# Example usage
# streamlit_column_graph(df, 'date', 'category', 'total_revenue', display_data=True)
