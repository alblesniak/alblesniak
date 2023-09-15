import streamlit as st
import pandas as pd
import numpy as np
from streamlit_pagination import pagination_component

# Initialize Streamlit UI and session state
st.set_page_config(layout='wide')
# Add custom style for pagination
st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)

# Data Loading and Manipulation Functions
def load_data():
    df_ll = pd.read_excel('log_likelihood_results.xlsx', sheet_name='All Data 1', nrows=10000)
    df_sorted = pd.read_excel('sorted_average_occurrences_per_year.xlsx')
    df_sorted.columns = df_sorted.columns.astype(str)
    merged_df = pd.merge(df_ll, df_sorted, how='inner', on='keyword')

    def generate_occurrences_over_time(row):
        if row['corpus'] == 'A':
            return row.loc['2005':'2023'].tolist()
        elif row['corpus'] == 'B':
            return row.loc['1989':'2022'].tolist()
        else:
            return []

    merged_df['occurrences_over_time'] = merged_df.apply(generate_occurrences_over_time, axis=1)
    columns_to_drop = [str(year) for year in range(1989, 2024)]
    merged_df = merged_df.drop(columns=columns_to_drop)
    
    return merged_df

def data_chunk_choice():
    if 'foo' not in st.session_state or st.session_state['foo'] is None:
        return 0
    return st.session_state['foo']


# Load data
merged_df = load_data()

# UI
# Add a column sorting selector
sort_column = st.selectbox('Sort By:', ['keyword', 'log_likelihood', 'occurrences_A', 
                                        'occurrences_per_1000_A', 'occurrences_B', 
                                        'occurrences_per_1000_B', 'corpus'])
sort_order = st.selectbox('Order:', ['Ascending', 'Descending'])
if sort_order == 'Descending':
    merged_df = merged_df.sort_values(by=sort_column, ascending=False)
else:
    merged_df = merged_df.sort_values(by=sort_column, ascending=True)

# Break the dataframe into chunks for pagination
n = 100  # Batch size (number of rows per page)
list_df = [merged_df[i:i+n] for i in range(0, merged_df.shape[0], n)] 

# Get the current data chunk choice from pagination
current_data_chunk = list_df[data_chunk_choice()]

st.dataframe(
    current_data_chunk,
    column_config={
        "keyword": st.column_config.TextColumn("Słowo kluczowe", width="medium"),
        "log_likelihood": st.column_config.NumberColumn("Log Likelihood"),
        "occurrences_A": st.column_config.NumberColumn("Wystąpienia w korpusie A"),
        "occurrences_per_1000_A": st.column_config.NumberColumn("Wystąpienia na 1000 słów (A)"),
        "occurrences_B": st.column_config.NumberColumn("Wystąpienia w korpusie B"),
        "occurrences_per_1000_B": st.column_config.NumberColumn("Wystąpienia na 1000 słów (A)"),
        "corpus": st.column_config.TextColumn('Korpus'),
        "occurrences_over_time": st.column_config.LineChartColumn(
            "Occurrences Over Time", y_min=0, y_max=1
        ),
    },
    hide_index=True,
    height=2024,
)

# Setup layout for pagination
layout = {
    'color': "secondary",
    'style': {'margin-top': '10px'}
}

# Add the pagination component
pagination_component(len(list_df), layout=layout, key="foo")
