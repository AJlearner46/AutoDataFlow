import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sys import prefix
import datetime, pytz
import glob, os

# -----------------------------------------[streamlit page]--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

st.set_page_config(
    page_title = "Data Analysis Web App",
    page_icon = "🧊",
    layout = "wide",
    initial_sidebar_state = "expanded",
    menu_items = {
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

st.sidebar.title("Data Analysis Web App")

# -------------------------------------------[web app features]------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

file_format_type = ["csv"]
functions = ["Overview", "Drop Columns", "Drop Categorical Rows", "Rename Columns", "Display Plot", "Handling Missing Data"]

# -------------------------------------[Helper Functions]------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def data(data, file_type, seperator=None):
    if file_type == "csv":
        data = pd.read_csv(data)
    return data

def describe(data):
    global num_category, str_category
    num_category = [feature for feature in data.columns if data[feature].dtype != 'object']
    str_category = [feature for feature in data.columns if data[feature].dtype == 'object']
    column_with_null_values = data.columns[data.isnull().any()]
    return data.describe(), data.shape, data.columns, num_category, str_category, data.isnull().sum(), data.dtypes.astype("str"), data.nunique(), str_category, column_with_null_values 

def drop_items(data, selected_name):
    droped = data.drop(selected_name, axis = 1)
    return droped

def filter_data(data, selected_cloumn, selected_name):
    if selected_name == []:
        filtered_data = data
    else:
        filtered_data = data[~ data[selected_cloumn].isin(selected_name)]
    return filtered_data

def download_data(data, label):
    current_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
    current_time = "{}.{}-{}-{}".format(current_time.date(), current_time.hour, current_time.minute, current_time.second)
    export_data = st.download_button(
                        label="Download {} data as CSV".format(label),
                        data=data.to_csv(),
                        file_name='{}{}.csv'.format(label, current_time),
                        mime='text/csv',
                        help = "When You Click On Download Button You can download your {} CSV File".format(label)
                    )
    return export_data

def rename_columns(data, column_names):
    rename_column = data.rename(columns=column_names)
    return rename_column

def handling_missing_values(data, option_type, dict_value=None):
    if option_type == "Drop all null value rows":
        data = data.dropna()

    elif option_type == "Only Drop Rows that contanines all null values":
        data = data.dropna(how="all")
    
    elif option_type == "Filling in Missing Values":
        data = data.fillna(dict_value)
    
    return data

# --------------------------------------------------[upload data]-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

uploaded_file = st.sidebar.file_uploader("Upload Your File", type = file_format_type)

if uploaded_file is not None:

    file_type = uploaded_file.type.split("/")[1]

    
    data = data(uploaded_file, file_type)

    describe, shape, columns, num_category, str_category, null_values, dtypes, unique, str_category, column_with_null_values = describe(data)

    multi_function_selector = st.sidebar.multiselect("Enter Name or Select the Column which you want To Plot: ",functions, default=["Overview"])

    st.subheader("Dataset Preview")
    st.dataframe(data)

    st.text(" ")
    st.text(" ")
    st.text(" ")

# -------------------------------------------------[handle all features]------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    if "Overview" in multi_function_selector:
        st.subheader("Dataset Description")
        st.write(describe)

        st.text(" ")
        st.text(" ")
        st.text(" ")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.text("Basic Information")
            st.write("Dataset Name")
            st.text(uploaded_file.name)

            st.write("Dataset Size(MB)")
            number = round((uploaded_file.size*0.000977)*0.000977,2)
            st.write(number)

            st.write("Dataset Shape")
            st.write(shape)
            
        with col2:
            st.text("Dataset Columns")
            st.write(columns)
        
        with col3:
            st.text("Numeric Columns")
            st.dataframe(num_category)
        
        with col4:
            st.text("String Columns")
            st.dataframe(str_category)
            
        col5, col6, col7, col8= st.columns(4)

        with col6:
            st.text("Columns Data-Type")
            st.dataframe(dtypes)
        
        with col7:
            st.text("Counted Unique Values")
            st.write(unique)
        
        with col5:
            st.write("Counted Null Values")
            st.dataframe(null_values)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
   
    if "Drop Categorical Rows" in multi_function_selector:

        filter_cloumn_selection = st.selectbox("Please Select or Enter a Cloumn Name: ", options=data.columns )
        filtered_value_selection = st.multiselect("Enter Name or Select the value which you don't want in your {} cloumn(you can choose multiple value): " .format(filter_cloumn_selection), data[filter_cloumn_selection].unique())
        filtered_data = filter_data(data, filter_cloumn_selection, filtered_value_selection)

        st.write(filtered_data)

        filtered_export = download_data(filtered_data, label="filtered")

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    if "Drop Columns" in multi_function_selector:

        multiselected_drop = st.multiselect("Please Type or select one or Multipe Columns you want to drop: ", data.columns)
        
        droped = drop_items(data, multiselected_drop)
        st.write(droped)
        
        drop_export = download_data(droped, label="Droped(edited)")

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    if "Rename Columns" in multi_function_selector:
         
         if 'rename_dict' not in st.session_state:
            st.session_state.rename_dict = {}
         
         rename_dict = {}
         rename_column_selector = st.selectbox("Please Select or Enter a column Name you watn to rename: ", options=data.columns)
         rename_text_data = st.text_input("Enter the Name for the {} Column".format(rename_column_selector), max_chars=20)

         if st.button("Draft Changes", help="when you want to rename multiple columns/single column so first you have to click Save Draft button this updates the data and then press Rename Columns Button."):
             st.session_state.rename_dict[rename_column_selector] = rename_text_data

         st.code(st.session_state.rename_dict)

         if st.button("Apply Changes", help="Takes your data and rename the column as your wish."):
            rename_column = rename_columns(data, st.session_state.rename_dict)
            st.write(rename_column)
            export_rename_column = download_data(rename_column, label="rename_column")
            st.session_state.rename_dict = {}

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 
    if "Display Plot" in multi_function_selector:

        multi_bar_plotting = st.multiselect("Enter Name or Select the Column which you Want To Plot: ", str_category)
        
        for i in range(len(multi_bar_plotting)):
            column = multi_bar_plotting[i]
            st.markdown("#### Bar Plot for {} column".format(column))
            bar_plot = data[column].value_counts().reset_index().sort_values(by=column, ascending=False)
            st.bar_chart(bar_plot)

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    if "Handling Missing Data" in multi_function_selector:
        handling_missing_value_option = st.radio("Select What you want to do", ("Drop Null Values", "Filling in Missing Values"))

        if handling_missing_value_option == "Drop Null Values":

            drop_null_values_option = st.radio("Choose your option as suted: ", ("Drop all null value rows", "Only Drop Rows that contanines all null values"))
            droped_null_value = handling_missing_values(data, drop_null_values_option)
            st.write(droped_null_value)
            export_rename_column = download_data(droped_null_value, label="fillna_column")
        
        elif handling_missing_value_option == "Filling in Missing Values":
            
            if 'missing_dict' not in st.session_state:
                st.session_state.missing_dict = {}
            
            fillna_column_selector = st.selectbox("Please Select or Enter a column Name you want to fill the NaN Values: ", options=column_with_null_values)
            fillna_option = st.radio("Select a method for filling missing values:", ("Enter a specific value", "Mean", "Mode", "Median"))

            if fillna_option == "Enter a specific value":
                fillna_text_data = st.text_input("Enter the New Value for the {} Column NaN Value".format(fillna_column_selector),max_chars=20)
                st.session_state.missing_dict[fillna_column_selector] = fillna_text_data
            else:
                if data[fillna_column_selector].dtype.kind in 'bifc':
                    if fillna_option == "Mean":
                        fill_value = data[fillna_column_selector].mean()
                    elif fillna_option == "Mode":
                        fill_value = data[fillna_column_selector].mode().iloc[0]  # Get the first mode value
                    elif fillna_option == "Median":
                        fill_value = data[fillna_column_selector].median()
                else:
                    st.warning(f"Cannot calculate statistical measures for non-numeric column: {fillna_column_selector}")
                    fill_value = None

                st.session_state.missing_dict[fillna_column_selector] = fill_value
               
            st.code(st.session_state.missing_dict)

            if st.button("Apply Changes", help="Takes your data and Fill NaN Values for columns as your wish."):

                fillna_column = handling_missing_values(data,handling_missing_value_option, st.session_state.missing_dict)
                st.write(fillna_column)
                export_rename_column = download_data(fillna_column, label="fillna_column")
                st.session_state.missing_dict = {}

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

