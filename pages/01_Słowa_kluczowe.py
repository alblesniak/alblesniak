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

# User Selection for 'corpus' filtering
options = {'wszystkie': None, 'pentekostalny': 'B', 'katolicki': 'A'}
selected_option = st.selectbox('Wybierz korpus:', list(options.keys()))

if options[selected_option] is not None:
    merged_df = merged_df[merged_df['corpus'] == options[selected_option]]

# Always sort dataframe by 'log_likelihood' - descending
merged_df = merged_df.sort_values(by='log_likelihood', ascending=False)

# Resetting index to have an index column in displayed dataframe, starting from 1
merged_df = merged_df.reset_index(drop=True).reset_index(drop=False)
merged_df['index'] = merged_df['index'] + 1

# Break the dataframe into chunks for pagination
n = 100  # Batch size (number of rows per page)
list_df = [merged_df[i:i+n] for i in range(0, merged_df.shape[0], n)] 

# Get the current data chunk choice from pagination
current_data_chunk = list_df[data_chunk_choice()]

# Display Dataframe
st.dataframe(
    current_data_chunk,
    column_config={
        "index": st.column_config.NumberColumn("#", width="tiny"),
        "keyword": st.column_config.TextColumn("Słowo kluczowe", width="medium"),
        "log_likelihood": st.column_config.NumberColumn("Log Likelihood"),
        "occurrences_A": st.column_config.NumberColumn("Wystąpienia w korpusie A"),
        "occurrences_per_1000_A": st.column_config.NumberColumn("Wystąpienia na 1000 słów (A)"),
        "occurrences_B": st.column_config.NumberColumn("Wystąpienia w korpusie B"),
        "occurrences_per_1000_B": st.column_config.NumberColumn("Wystąpienia na 1000 słów (A)"),
        "corpus": st.column_config.TextColumn('Korpus'),
        "occurrences_over_time": st.column_config.LineChartColumn(
            "Wystąpienia w czasie", y_min=0, y_max=1
        ),
    },
    hide_index=True,
    width=1500,  # Adjusting the width same as selectbox
)

# Setup layout for pagination
layout = {
    'color': "secondary",
    'style': {'margin-top': '10px'}
}

# Add the pagination component
pagination_component(len(list_df), layout=layout, key="foo")
