import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Title and Introduction
st.title("OTR Baseball Metrics Analyzer")
st.write("Upload your Bat Speed and Exit Velocity CSV files to generate a comprehensive report.")

# File Uploads
bat_speed_file = st.file_uploader("Upload Bat Speed File", type="csv")
exit_velocity_file = st.file_uploader("Upload Exit Velocity File", type="csv")

# Ask for Player Level
player_level = st.selectbox("Select Player Level", ["Youth", "High School", "College", "Indy", "Affiliate"])

# Updated Benchmarks Based on Levels
benchmarks = {
    "Youth": {
        "Avg EV": 58.4, "Top 8th EV": 70.19, "Avg LA": 12.14, "HHB LA": 8.78,
        "Avg BatSpeed": 49.21, "90th% BatSpeed": 52.81, "Avg TimeToContact": 0.19, "Avg AttackAngle": 11.78
    },
    "High School": {
        "Avg EV": 74.54, "Top 8th EV": 86.75, "Avg LA": 16.51, "HHB LA": 11.47,
        "Avg BatSpeed": 62.4, "90th% BatSpeed": 67.02, "Avg TimeToContact": 0.163, "Avg AttackAngle": 9.8
    },
    "College": {
        "Avg EV": 81.57, "Top 8th EV": 94.44, "Avg LA": 17.57, "HHB LA": 12.86,
        "Avg BatSpeed": 67.53, "90th% BatSpeed": 72.54, "Avg TimeToContact": 0.154, "Avg AttackAngle": 10.52
    },
    "Indy": {
        "Avg EV": 85.99, "Top 8th EV": 98.12, "Avg LA": 18.68, "HHB LA": 14.74,
        "Avg BatSpeed": 69.2, "90th% BatSpeed": 74.04, "Avg TimeToContact": 0.154, "Avg AttackAngle": 10.62
    },
    "Affiliate": {
        "Avg EV": 85.49, "Top 8th EV": 98.71, "Avg LA": 18.77, "HHB LA": 15.55,
        "Avg BatSpeed": 70.17, "90th% BatSpeed": 75.14, "Avg TimeToContact": 0.147, "Avg AttackAngle": 11.09
    }
}

# Function to determine performance category
def evaluate_performance(metric, benchmark):
    if abs(metric - benchmark) <= 0.1 * benchmark:
        return "Above Average"
    elif abs(metric - benchmark) <= 0.2 * benchmark:
        return "Average"
    else:
        return "Below Average"

# Process Bat Speed File (Skip the first 8 rows)
bat_speed_metrics = ""
if bat_speed_file:
    df_bat_speed = pd.read_csv(bat_speed_file, skiprows=8)
    bat_speed_data = pd.to_numeric(df_bat_speed.iloc[:, 7], errors='coerce')  # Column H: "Bat Speed (mph)"
    attack_angle_data = pd.to_numeric(df_bat_speed.iloc[:, 10], errors='coerce')  # Column K: "Attack Angle (deg)"
    time_to_contact_data = pd.to_numeric(df_bat_speed.iloc[:, 15], errors='coerce')  # Column: "Time to Contact (sec)"

    # Calculate Bat Speed Metrics
    player_avg_bat_speed = bat_speed_data.mean()
    top_10_percent_bat_speed = bat_speed_data.quantile(0.90)
    top_10_percent_swings = df_bat_speed[bat_speed_data >= top_10_percent_bat_speed]
    avg_attack_angle_top_10 = attack_angle_data[top_10_percent_swings.index].mean()
    avg_time_to_contact = time_to_contact_data.mean()

    # Benchmarks for Bat Speed, Time to Contact, and Attack Angle
    bat_speed_benchmark = benchmarks[player_level]["Avg BatSpeed"]
    top_90_benchmark = benchmarks[player_level]["90th% BatSpeed"]
    time_to_contact_benchmark = benchmarks[player_level]["Avg TimeToContact"]
    attack_angle_benchmark = benchmarks[player_level]["Avg AttackAngle"]

    # Format Bat Speed Metrics
    bat_speed_metrics = (
        "### Bat Speed Metrics\n"
        f"- **Player Average Bat Speed:** {player_avg_bat_speed:.2f} mph (Benchmark: {bat_speed_benchmark} mph)\n"
        f"- **Top 10% Bat Speed:** {top_10_percent_bat_speed:.2f} mph (Benchmark: {top_90_benchmark} mph)\n"
        f"- **Average Attack Angle (Top 10% Bat Speed Swings):** {avg_attack_angle_top_10:.2f}° (Benchmark: {attack_angle_benchmark}°)\n"
        f"- **Average Time to Contact:** {avg_time_to_contact:.3f} sec (Benchmark: {time_to_contact_benchmark} sec)\n"
    )

# Process Exit Velocity File (No rows skipped)
exit_velocity_metrics = ""
if exit_velocity_file:
    df_exit_velocity = pd.read_csv(exit_velocity_file)  # No rows are skipped here
    exit_velocity_data = pd.to_numeric(df_exit_velocity.iloc[:, 7], errors='coerce')  # Column H: "Velo"
    launch_angle_data = pd.to_numeric(df_exit_velocity.iloc[:, 8], errors='coerce')  # Column I: "LA"
    distance_data = pd.to_numeric(df_exit_velocity.iloc[:, 9], errors='coerce')  # Column J: "Dist"

    # Filter out rows where Exit Velocity is zero or NaN
    non_zero_ev_rows = df_exit_velocity[exit_velocity_data > 0]
    exit_velocity_data = pd.to_numeric(non_zero_ev_rows.iloc[:, 7], errors='coerce')  # Filtered "Velo"
    launch_angle_data = pd.to_numeric(non_zero_ev_rows.iloc[:, 8], errors='coerce')  # Filtered "LA"
    distance_data = pd.to_numeric(non_zero_ev_rows.iloc[:, 9], errors='coerce')  # Filtered "Dist"

    # Calculate Exit Velocity Metrics
    exit_velocity_avg = exit_velocity_data.mean()  # Use filtered data
    top_8_percent_exit_velocity = exit_velocity_data.quantile(0.92)
    top_8_percent_swings = non_zero_ev_rows[exit_velocity_data >= top_8_percent_exit_velocity]
    avg_launch_angle_top_8 = launch_angle_data[top_8_percent_swings.index].mean()
    avg_distance_top_8 = distance_data[top_8_percent_swings.index].mean()
    total_avg_launch_angle = launch_angle_data[launch_angle_data > 0].mean()  # Total average launch angle ignoring zeros

    # Benchmarks for Exit Velocity, Avg LA, and HHB LA
    ev_benchmark = benchmarks[player_level]["Avg EV"]
    top_8_benchmark = benchmarks[player_level]["Top 8th EV"]
    la_benchmark = benchmarks[player_level]["Avg LA"]
    hhb_la_benchmark = benchmarks[player_level]["HHB LA"]

    # Format Exit Velocity Metrics
    exit_velocity_metrics = (
        "### Exit Velocity Metrics\n"
        f"- **Average Exit Velocity:** {exit_velocity_avg:.2f} mph (Benchmark: {ev_benchmark} mph)\n"
        f"- **Top 8% Exit Velocity:** {top_8_percent_exit_velocity:.2f} mph (Benchmark: {top_8_benchmark} mph)\n"
        f"- **Average Launch Angle (On Top 8% Exit Velocity Swings):** {avg_launch_angle_top_8:.2f}° (Benchmark: {hhb_la_benchmark}°)\n"
        f"- **Total Average Launch Angle (Avg LA):** {total_avg_launch_angle:.2f}° (Benchmark: {la_benchmark}°)\n"
        f"- **Average Distance (8% swings):** {avg_distance_top_8:.2f} ft\n"
    )

# Display Results
st.write("## Calculated Metrics")
if bat_speed_metrics:
    st.markdown(bat_speed_metrics)
if exit_velocity_metrics:
    st.markdown(exit_velocity_metrics)

# Email Configuration
email_address = "aadichadha@gmail.com"
email_password = "eeoi odag olix nnfc"
smtp_server = "smtp.gmail.com"
smtp_port = 587

# Streamlit Email Input and Button
st.write("## Email the Report")
recipient_email = st.text_input("Enter Email Address")

if st.button("Send Report"):
    if recipient_email:
        # Prepare email content based on available metrics
        email_body = "<html><body><h2>Baseball Metrics Report</h2><p>Please find the detailed analysis of the uploaded baseball metrics below:</p>"

        if bat_speed_metrics:
            email_body += f"<h3>Bat Speed Metrics</h3><p>{bat_speed_metrics.replace('### ', '').replace('\\n', '<br>')}</p>"

            # Evaluate Bat Speed performance
            bat_speed_eval = evaluate_performance(player_avg_bat_speed, bat_speed_benchmark)
            top_10_bat_speed_eval = evaluate_performance(top_10_percent_bat_speed, top_90_benchmark)
            attack_angle_eval = evaluate_performance(avg_attack_angle_top_10, attack_angle_benchmark)
            time_to_contact_eval = evaluate_performance(avg_time_to_contact, time_to_contact_benchmark)

            email_body += (
                f"<h4>Today's Results:</h4>"
                f"<p>Player Average Bat Speed: {bat_speed_eval}<br>"
                f"Top 10% Bat Speed: {top_10_bat_speed_eval}<br>"
                f"Average Attack Angle (Top 10% Swings): {attack_angle_eval}<br>"
                f"Average Time to Contact: {time_to_contact_eval}</p>"
            )

        if exit_velocity_metrics:
            email_body += f"<h3>Exit Velocity Metrics</h3><p>{exit_velocity_metrics.replace('### ', '').replace('\\n', '<br>')}</p>"

            # Evaluate Exit Velocity performance
            ev_eval = evaluate_performance(exit_velocity_avg, ev_benchmark)
            top_8_ev_eval = evaluate_performance(top_8_percent_exit_velocity, top_8_benchmark)
            avg_la_eval = evaluate_performance(total_avg_launch_angle, la_benchmark)
            hhb_la_eval = evaluate_performance(avg_launch_angle_top_8, hhb_la_benchmark)

            email_body += (
                f"<h4>Today's Results:</h4>"
                f"<p>Average Exit Velocity: {ev_eval}<br>"
                f"Top 8% Exit Velocity: {top_8_ev_eval}<br>"
                f"Total Average Launch Angle: {avg_la_eval}<br>"
                f"Average Launch Angle (Top 8% Swings): {hhb_la_eval}</p>"
            )

        email_body += "<p>Best Regards,<br>Your Baseball Metrics Analyzer</p></body></html>"
        # Function to Send Email
def send_email_report(recipient_email, email_body):
    # Create the email content
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = recipient_email
    msg['Subject'] = "Baseball Metrics Report"
    msg.attach(MIMEText(email_body, 'html'))

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg)
        st.success("Report sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

