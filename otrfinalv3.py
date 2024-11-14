import streamlit as st
import pandas as pd

# Title and Introduction
st.title("Debugging Column Names")
st.write("Upload your Bat Speed and Exit Velocity CSV files to inspect column names.")

# File Uploads
bat_speed_file = st.file_uploader("Upload Bat Speed File", type="csv")
exit_velocity_file = st.file_uploader("Upload Exit Velocity File", type="csv")

# Process Bat Speed File
if bat_speed_file:
    df_bat_speed = pd.read_csv(bat_speed_file, skiprows=20)
    st.write("Columns in Bat Speed File:", df_bat_speed.columns.tolist())  # Print all column names

# Process Exit Velocity File
if exit_velocity_file:
    df_exit_velocity = pd.read_csv(exit_velocity_file, skiprows=20)
    st.write("Columns in Exit Velocity File:", df_exit_velocity.columns.tolist())  # Print all column names
