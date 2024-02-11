import streamlit as st
import pandas as pd
import plotly.express as px
import plotly as pt
import altair as alt


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
