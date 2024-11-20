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
def evaluate_performance(metric, benchmark, lower_is_better=False):
    if lower_is_better:
        if metric < benchmark:  # Lower values are better
            return "Above Average"
        elif metric <= benchmark * 1.1:  # Up to 10% higher is considered "Average"
            return "Average"
        else:  # More than 10% higher is "Below Average"
            return "Below Average"
    else:
        if metric > benchmark:  # Higher values are better
            return "Above Average"
        elif metric >= benchmark * 0.9:  # Up to 10% lower is considered "Average"
            return "Average"
        else:  # More than 10% lower is "Below Average"
            return "Below Average"

# Function to add Player Grade
def player_grade(metric, benchmark, lower_is_better=False):
    if lower_is_better:
        if metric < benchmark:  # Lower values are better
            return "Above Average"
        elif metric <= benchmark * 1.1:  # Up to 10% higher is considered "Average"
            return "Average"
        else:  # More than 10% higher is "Below Average"
            return "Below Average"
    else:
        if metric > benchmark:  # Higher values are better
            return "Above Average"
        elif metric >= benchmark * 0.9:  # Up to 10% lower is considered "Average"
            return "Average"
        else:  # More than 10% lower is "Below Average"
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
    avg_attack_angle_top_10 = attack_angle_data[bat_speed_data >= top_10_percent_bat_speed].mean()
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
        f"  - Player Grade: {player_grade(player_avg_bat_speed, bat_speed_benchmark)}\n"
        f"- **Top 10% Bat Speed:** {top_10_percent_bat_speed:.2f} mph (Benchmark: {top_90_benchmark} mph)\n"
        f"  - Player Grade: {player_grade(top_10_percent_bat_speed, top_90_benchmark)}\n"
        f"- **Average Attack Angle (Top 10% Bat Speed Swings):** {avg_attack_angle_top_10:.2f}° (Benchmark: {attack_angle_benchmark}°)\n"
        f"  - Player Grade: {player_grade(avg_attack_angle_top_10, attack_angle_benchmark)}\n"
        f"- **Average Time to Contact:** {avg_time_to_contact:.3f} sec (Benchmark: {time_to_contact_benchmark} sec)\n"
        f"  - Player Grade: {player_grade(avg_time_to_contact, time_to_contact_benchmark, lower_is_better=True)}\n"

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
    exit_velocity_avg = exit_velocity_data.mean()
    top_8_percent_exit_velocity = exit_velocity_data.quantile(0.92)
    avg_launch_angle_top_8 = launch_angle_data[exit_velocity_data >= top_8_percent_exit_velocity].mean()
    avg_distance_top_8 = distance_data[exit_velocity_data >= top_8_percent_exit_velocity].mean()
    total_avg_launch_angle = launch_angle_data[launch_angle_data > 0].mean()

    # Benchmarks for Exit Velocity, Avg LA, and HHB LA
    ev_benchmark = benchmarks[player_level]["Avg EV"]
    top_8_benchmark = benchmarks[player_level]["Top 8th EV"]
    la_benchmark = benchmarks[player_level]["Avg LA"]
    hhb_la_benchmark = benchmarks[player_level]["HHB LA"]

    # Format Exit Velocity Metrics
    exit_velocity_metrics = (
        "### Exit Velocity Metrics\n"
        f"- **Average Exit Velocity:** {exit_velocity_avg:.2f} mph (Benchmark: {ev_benchmark} mph)\n"
        f"  - Player Grade: {player_grade(exit_velocity_avg, ev_benchmark)}\n"
        f"- **Top 8% Exit Velocity:** {top_8_percent_exit_velocity:.2f} mph (Benchmark: {top_8_benchmark} mph)\n"
        f"  - Player Grade: {player_grade(top_8_percent_exit_velocity, top_8_benchmark)}\n"
        f"- **Average Launch Angle (On Top 8% Exit Velocity Swings):** {avg_launch_angle_top_8:.2f}° (Benchmark: {hhb_la_benchmark}°)\n"
        f"  - Player Grade: {player_grade(avg_launch_angle_top_8, hhb_la_benchmark)}\n"
        f"- **Total Average Launch Angle (Avg LA):** {total_avg_launch_angle:.2f}° (Benchmark: {la_benchmark}°)\n"
        f"  - Player Grade: {player_grade(total_avg_launch_angle, la_benchmark)}\n"
        f"- **Average Distance (8% swings):** {avg_distance_top_8:.2f} ft\n"
    )

# Display Results
st.write("## Calculated Metrics")
if bat_speed_metrics:
    st.markdown(bat_speed_metrics)
if exit_velocity_metrics:
    st.markdown(exit_velocity_metrics)

# Email Configuration
email_address = "otrdatatrack@gmail.com"  # Your email address
email_password = "pslp fuab dmub cggo"  # Your app-specific password
smtp_server = "smtp.gmail.com"
smtp_port = 587

# Function to Send Email
def send_email_report(recipient_email, bat_speed_metrics, exit_velocity_metrics):
    # Create the email content
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = recipient_email
    msg['Subject'] = "OTR Baseball Metrics and Grade Report"

    # Construct the email body with your formatted layout
    email_body = """
    <html>
    <body>
        <h2>OTR Metrics Report</h2>
        <p>The following data is constructed with benchmarks for each level. </p>
    """

    # Include Bat Speed Metrics if available
    if bat_speed_metrics:
        email_body += """
        <h3>Bat Speed Metrics</h3>
        <ul>
            <li><strong>Player Average Bat Speed:</strong> {:.2f} mph (Benchmark: {:.2f} mph)
                <br><strong>Player Grade:</strong> <strong>{}</strong></li>
            <li><strong>Top 10% Bat Speed:</strong> {:.2f} mph (Benchmark: {:.2f} mph)
                <br><strong>Player Grade:</strong> <strong>{}</strong></li>
            <li><strong>Average Attack Angle (Top 10% Bat Speed Swings):</strong> {:.2f}° (Benchmark: {:.2f}°)
                <br><strong>Player Grade:</strong> <strong>{}</strong></li>
            <li><strong>Average Time to Contact:</strong> {:.3f} sec (Benchmark: {:.3f} sec)
                <br><strong>Player Grade:</strong> <strong>{}</strong></li>
        </ul>
        """.format(
            player_avg_bat_speed, bat_speed_benchmark, evaluate_performance(player_avg_bat_speed, bat_speed_benchmark),
            top_10_percent_bat_speed, top_90_benchmark, evaluate_performance(top_10_percent_bat_speed, top_90_benchmark),
            avg_attack_angle_top_10, attack_angle_benchmark, evaluate_performance(avg_attack_angle_top_10, attack_angle_benchmark),
            avg_time_to_contact, time_to_contact_benchmark, evaluate_performance(avg_time_to_contact, time_to_contact_benchmark)
        )

    # Include Exit Velocity Metrics if available
    if exit_velocity_metrics:
        email_body += """
        <h3>Exit Velocity Metrics</h3>
        <ul>
            <li><strong>Average Exit Velocity:</strong> {:.2f} mph (Benchmark: {:.2f} mph)
                <br><strong>Player Grade:</strong> <strong>{}</strong></li>
            <li><strong>Top 8% Exit Velocity:</strong> {:.2f} mph (Benchmark: {:.2f} mph)
                <br><strong>Player Grade:</strong> <strong>{}</strong></li>
            <li><strong>Average Launch Angle (On Top 8% Exit Velocity Swings):</strong> {:.2f}° (Benchmark: {:.2f}°)
                <br><strong>Player Grade:</strong> <strong>{}</strong></li>
            <li><strong>Total Average Launch Angle (Avg LA):</strong> {:.2f}° (Benchmark: {:.2f}°)
                <br><strong>Player Grade:</strong> <strong>{}</strong></li>
            <li><strong>Average Distance (8% swings):</strong> {:.2f} ft</li>
        </ul>
        """.format(
            exit_velocity_avg, ev_benchmark, evaluate_performance(exit_velocity_avg, ev_benchmark),
            top_8_percent_exit_velocity, top_8_benchmark, evaluate_performance(top_8_percent_exit_velocity, top_8_benchmark),
            avg_launch_angle_top_8, hhb_la_benchmark, evaluate_performance(avg_launch_angle_top_8, hhb_la_benchmark),
            total_avg_launch_angle, la_benchmark, evaluate_performance(total_avg_launch_angle, la_benchmark),
            avg_distance_top_8
        )

    email_body += "<p>Best Regards,<br>OTR Baseball</p></body></html>"

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

# Streamlit Email Input and Button
st.write("## Email the Report")
recipient_email = st.text_input("Enter Email Address")

if st.button("Send Report"):
    if recipient_email:
        # Send the email report
        send_email_report(recipient_email, bat_speed_metrics, exit_velocity_metrics)
    else:
        st.error("Please enter a valid email address.")
