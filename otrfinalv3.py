import streamlit as st
import pandas as pd

# Title and Introduction
st.title("Baseball Metrics Analyzer")
st.write("Upload your Bat Speed and Exit Velocity CSV files to generate a comprehensive report.")

# File Uploads
bat_speed_file = st.file_uploader("Upload Bat Speed (mph) File", type="csv")
exit_velocity_file = st.file_uploader("Upload Exit Velocity File", type="csv")

# Process Bat Speed File
if bat_speed_file:
    # Load the file with the specific structure in mind
    df_bat_speed = pd.read_csv(bat_speed_file, skiprows=20)
    df_bat_speed.columns = df_bat_speed.columns.str.strip()  # Remove any extra spaces from column names

    # Extract Bat Speed data from the specific column
    try:
        bat_speed_data = df_bat_speed.iloc[:, 7]  # Column H is the 8th column (0-indexed)
        player_avg_bat_speed = bat_speed_data.mean()
        top_10_percent_bat_speed = bat_speed_data.quantile(0.90)
    except IndexError:
        st.error("The file format is incorrect or the column 'Bat Speed (mph)' was not found.")
        st.stop()

    # Display Bat Speed Metrics
    st.write("### Bat Speed Metrics")
    st.write(f"- **Player Average Bat Speed:** {player_avg_bat_speed:.2f} mph")
    st.write(f"- **Top 10% Bat Speed:** {top_10_percent_bat_speed:.2f} mph")

# Process Exit Velocity File
if exit_velocity_file:
    # Load the file with the specific structure in mind
    df_exit_velocity = pd.read_csv(exit_velocity_file, skiprows=20)
    df_exit_velocity.columns = df_exit_velocity.columns.str.strip()  # Remove any extra spaces from column names

    # Extract Exit Velocity data from the specific column
    try:
        exit_velocity_data = df_exit_velocity.iloc[:, 7]  # Column H is the 8th column (0-indexed)
        exit_velocity_avg = exit_velocity_data[exit_velocity_data > 0].mean()  # Ignore zero values
        top_8_percent_exit_velocity = exit_velocity_data.quantile(0.92)
    except IndexError:
        st.error("The file format is incorrect or the column 'Velo' was not found.")
        st.stop()

    # Display Exit Velocity Metrics
    st.write("### Exit Velocity Metrics")
    st.write(f"- **Average Exit Velocity:** {exit_velocity_avg:.2f} mph")
    st.write(f"- **Top 8% Exit Velocity:** {top_8_percent_exit_velocity:.2f} mph")
