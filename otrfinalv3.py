import streamlit as st
import pandas as pd

# Title and Introduction
st.title("Baseball Metrics Analyzer")
st.write("Upload your Bat Speed and Exit Velocity CSV files to generate a comprehensive report.")

# File Uploads
bat_speed_file = st.file_uploader("Upload Bat Speed File", type="csv")
exit_velocity_file = st.file_uploader("Upload Exit Velocity File", type="csv")

# Ask for Player Level
player_level = st.selectbox("Select Player Level", ["Youth", "High School", "College", "Indy", "Affiliate", "Professional"])

# Benchmarks Based on Level
benchmarks = {
    "Youth": {"Avg EV": 58.4, "Top 8th EV": 70.19, "Avg BatSpeed": 49.21, "90th% BatSpeed": 52.81},
    "High School": {"Avg EV": 74.54, "Top 8th EV": 86.75, "Avg BatSpeed": 62.64, "90th% BatSpeed": 67.02},
    "College": {"Avg EV": 81.57, "Top 8th EV": 94.44, "Avg BatSpeed": 67.53, "90th% BatSpeed": 72.54},
    "Indy": {"Avg EV": 85.99, "Top 8th EV": 98.12, "Avg BatSpeed": 69.2, "90th% BatSpeed": 74.04},
    "Affiliate": {"Avg EV": 85.49, "Top 8th EV": 98.71, "Avg BatSpeed": 70.17, "90th% BatSpeed": 75.14},
    "Professional": {"Avg EV": 94.3, "Top 8th EV": 104.5, "Avg BatSpeed": 78.2, "90th% BatSpeed": 82.3}
}

# Function to Extract Metrics from Bat Speed File
def process_bat_speed_file(file):
    try:
        df = pd.read_csv(file, skiprows=20)
        df.columns = df.columns.str.strip()
        if "Bat Speed (mph)" in df.columns:
            bat_speed_data = df["Bat Speed (mph)"]
            player_avg_bat_speed = bat_speed_data.mean()
            top_10_percent_bat_speed = bat_speed_data.quantile(0.90)
            top_10_percent_swings = df[bat_speed_data >= top_10_percent_bat_speed]
            
            # Average Attack Angle for Top 10% Bat Speed Swings
            avg_attack_angle_top_10 = top_10_percent_swings["Attack Angle (deg)"].mean() if "Attack Angle (deg)" in df.columns else None
            avg_time_to_contact = df["Time to Contact (sec)"].mean() if "Time to Contact (sec)" in df.columns else None

            return player_avg_bat_speed, top_10_percent_bat_speed, avg_attack_angle_top_10, avg_time_to_contact
        else:
            st.error("The 'Bat Speed (mph)' column was not found in the uploaded Bat Speed file.")
            return None, None, None, None
    except Exception as e:
        st.error(f"Error processing Bat Speed file: {e}")
        return None, None, None, None

# Function to Extract Metrics from Exit Velocity File
def process_exit_velocity_file(file):
    try:
        df = pd.read_csv(file, skiprows=20)
        df.columns = df.columns.str.strip()
        if "Velo" in df.columns:
            exit_velocity_data = df["Velo"]
            exit_velocity_avg = exit_velocity_data[exit_velocity_data > 0].mean()  # Ignore zero values
            top_8_percent_exit_velocity = exit_velocity_data.quantile(0.92)
            top_8_percent_swings = df[exit_velocity_data >= top_8_percent_exit_velocity]

            # Average Launch Angle and Distance for Top 8% Exit Velocity Swings
            avg_launch_angle_top_8 = top_8_percent_swings["LA"].mean() if "LA" in df.columns else None
            avg_distance_top_8 = top_8_percent_swings["Distance"].mean() if "Distance" in df.columns else None

            return exit_velocity_avg, top_8_percent_exit_velocity, avg_launch_angle_top_8, avg_distance_top_8
        else:
            st.error("The 'Velo' column was not found in the uploaded Exit Velocity file.")
            return None, None, None, None
    except Exception as e:
        st.error(f"Error processing Exit Velocity file: {e}")
        return None, None, None, None

# Process and Display Metrics
if bat_speed_file:
    player_avg_bat_speed, top_10_percent_bat_speed, avg_attack_angle_top_10, avg_time_to_contact = process_bat_speed_file(bat_speed_file)
    if player_avg_bat_speed is not None:
        bat_speed_benchmark = benchmarks[player_level]["Avg BatSpeed"]
        top_90_benchmark = benchmarks[player_level]["90th% BatSpeed"]
        st.write("### Bat Speed Metrics")
        st.write(f"- **Player Average Bat Speed:** {player_avg_bat_speed:.2f} mph (Benchmark: {bat_speed_benchmark} mph)")
        st.write(f"- **Top 10% Bat Speed:** {top_10_percent_bat_speed:.2f} mph (Benchmark: {top_90_benchmark} mph)")
        if avg_attack_angle_top_10 is not None:
            st.write(f"- **Average Attack Angle (Top 10% Bat Speed Swings):** {avg_attack_angle_top_10:.2f}°")
        if avg_time_to_contact is not None:
            st.write(f"- **Average Time to Contact:** {avg_time_to_contact:.2f} seconds")

if exit_velocity_file:
    exit_velocity_avg, top_8_percent_exit_velocity, avg_launch_angle_top_8, avg_distance_top_8 = process_exit_velocity_file(exit_velocity_file)
    if exit_velocity_avg is not None:
        ev_benchmark = benchmarks[player_level]["Avg EV"]
        top_8_benchmark = benchmarks[player_level]["Top 8th EV"]
        st.write("### Exit Velocity Metrics")
        st.write(f"- **Average Exit Velocity:** {exit_velocity_avg:.2f} mph (Benchmark: {ev_benchmark} mph)")
        st.write(f"- **Top 8% Exit Velocity:** {top_8_percent_exit_velocity:.2f} mph (Benchmark: {top_8_benchmark} mph)")
        if avg_launch_angle_top_8 is not None:
            st.write(f"- **Average Launch Angle (Top 8% Exit Velocity Swings):** {avg_launch_angle_top_8:.2f}°")
        if avg_distance_top_8 is not None:
            st.write(f"- **Average Distance (Top 8% Exit Velocity Swings):** {avg_distance_top_8:.2f} ft")
