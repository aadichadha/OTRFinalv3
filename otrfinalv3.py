import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Title and Introductio
st.title("OTR Baseball Metrics Analyzer")
st.write("Upload your Bat Speed and Exit Velocity CSV files to generate a comprehensive report.")

# File Uploads
bat_speed_file = st.file_uploader("Upload Bat Speed File", type="csv")
exit_velocity_file = st.file_uploader("Upload Exit Velocity File", type="csv")

# Ask for Player Level for Bat Speed and Exit Velocity
bat_speed_level = st.selectbox("Select Player Level for Bat Speed", ["Youth", "High School", "College", "Indy", "Affiliate"])
exit_velocity_level = st.selectbox("Select Player Level for Exit Velocity", ["10u", "12u", "14u", "JV/16u", "Var/18u", "College", "Indy", "Affiliate"])

# Updated Benchmarks Based on Levels
# Updated Benchmarks Based on Levels
benchmarks = {
    "10u": {
        "Avg EV": 50, "Top 8th EV": 61,
        "Avg LA": 12.14, "HHB LA": 8.78  # Youth benchmarks for launch angles
    },
    "12u": {
        "Avg EV": 59, "Top 8th EV": 72,
        "Avg LA": 12.14, "HHB LA": 8.78  # Youth benchmarks for launch angles
    },
    "14u": {
        "Avg EV": 68, "Top 8th EV": 80,
        "Avg LA": 12.14, "HHB LA": 8.78  # Youth benchmarks for launch angles
    },
    "JV/16u": {  # Match the dropdown value
        "Avg EV": 72.65, "Top 8th EV": 85.0,  # New 16u benchmarks for Exit Velocity
        "Avg LA": 16.51, "HHB LA": 11.47  # Keeping existing High School benchmarks for launch angles
    },
    "Var/18u": {  # Match the dropdown value
        "Avg EV": 78.0, "Top 8th EV": 91.5,  # New 18u benchmarks for Exit Velocity
        "Avg LA": 16.51, "HHB LA": 11.47  # Keeping existing High School benchmarks for launch angles
    },
    "Youth": {
        "Avg EV": 58.4, "Top 8th EV": 70.19, "Avg LA": 12.14, "HHB LA": 8.78,
        "Avg BatSpeed": 49.21, "90th% BatSpeed": 52.81, "Avg TimeToContact": 0.19, "Avg AttackAngle": 11.78
    },
    "High School": {  # High School remains for Bat Speed only
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
def evaluate_performance(metric, benchmark, lower_is_better=False, special_metric=False):
    if special_metric:  # Special handling for Exit Velocity and Top 8% Exit Velocity
        if abs(metric - benchmark) <= 3:  # Within ±3 mph of the benchmark
            return "Average"
        elif metric > benchmark + 3:  # More than 3 mph above the benchmark
            return "Above Average"
        else:  # More than 3 mph below the benchmark
            return "Below Average"
    else:  # Standard evaluation
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
def player_grade(metric, benchmark, lower_is_better=False, special_metric=False):
    if special_metric:  # Special handling for Exit Velocity and Top 8% Exit Velocity
        if abs(metric - benchmark) <= 3:  # Within ±3 mph of the benchmark
            return "Average"
        elif metric > benchmark + 3:  # More than 3 mph above the benchmark
            return "Above Average"
        else:  # More than 3 mph below the benchmark
            return "Below Average"
    else:  # Standard evaluation
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

# Calculate Exit Velocity Metrics
exit_velocity_avg = exit_velocity_data.mean()
top_8_percent_exit_velocity = exit_velocity_data.quantile(0.92)
avg_launch_angle_top_8 = launch_angle_data[exit_velocity_data >= top_8_percent_exit_velocity].mean()
avg_distance_top_8 = distance_data[exit_velocity_data >= top_8_percent_exit_velocity].mean()
total_avg_launch_angle = launch_angle_data[launch_angle_data > 0].mean()

# Benchmarks for Exit Velocity
ev_benchmark = benchmarks[exit_velocity_level]["Avg EV"]
top_8_benchmark = benchmarks[exit_velocity_level]["Top 8th EV"]
la_benchmark = benchmarks[exit_velocity_level]["Avg LA"]
hhb_la_benchmark = benchmarks[exit_velocity_level]["HHB LA"]

# Format Exit Velocity Metrics
# Format Exit Velocity Metrics
exit_velocity_metrics = (
    "### Exit Velocity Metrics\n"
    f"- **Average Exit Velocity:** {exit_velocity_avg:.2f} mph (Benchmark: {ev_benchmark} mph)\n"
    f"  - Player Grade: {player_grade(exit_velocity_avg, ev_benchmark, special_metric=True)}\n"  # Use special_metric
    f"- **Top 8% Exit Velocity:** {top_8_percent_exit_velocity:.2f} mph (Benchmark: {top_8_benchmark} mph)\n"
    f"  - Player Grade: {player_grade(top_8_percent_exit_velocity, top_8_benchmark, special_metric=True)}\n"  # Use special_metric
    f"- **Average Launch Angle (On Top 8% Exit Velocity Swings):** {avg_launch_angle_top_8:.2f}° (Benchmark: {hhb_la_benchmark}°)\n"
    f"  - Player Grade: {player_grade(avg_launch_angle_top_8, hhb_la_benchmark)}\n"
    f"- **Total Average Launch Angle (Avg LA):** {total_avg_launch_angle:.2f}° (Benchmark: {la_benchmark}°)\n"
    f"  - Player Grade: {player_grade(total_avg_launch_angle, la_benchmark)}\n"
    f"- **Average Distance (8% swings):** {avg_distance_top_8:.2f} ft\n"
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

    # Benchmarks for Exit Velocity
    ev_benchmark = benchmarks[exit_velocity_level]["Avg EV"]
    top_8_benchmark = benchmarks[exit_velocity_level]["Top 8th EV"]
    la_benchmark = benchmarks[exit_velocity_level]["Avg LA"]
    hhb_la_benchmark = benchmarks[exit_velocity_level]["HHB LA"]

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

# Player Name and Date Range Input
player_name = st.text_input("Enter Player Name")
date_range = st.text_input("Enter Date Range")

# Email Configuration
email_address = "otrdatatrack@gmail.com"  # Your email address
email_password = "pslp fuab dmub cggo"  # Your app-specific password
smtp_server = "smtp.gmail.com"
smtp_port = 587
# Function to Send Email
def send_email_report(recipient_email, bat_speed_metrics, exit_velocity_metrics, player_name, date_range):
    # Create the email content
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = recipient_email
    msg['Subject'] = "OTR Baseball Metrics and Grade Report"

    # Start the email body with the general introduction, player name, and date range
    email_body = f"""
    <html>
    <body style="color: black; background-color: white;">
        <h2 style="color: black;">OTR Metrics Report</h2>
        <p style="color: black;"><strong>Player Name:</strong> {player_name}</p>
        <p style="color: black;"><strong>Date Range:</strong> {date_range}</p>
        <p style="color: black;">The following data is constructed with benchmarks for each level.</p>
    """

    # Check if Bat Speed Metrics are available
    if bat_speed_metrics:
        email_body += """
        <h3 style="color: black;">Bat Speed Metrics</h3>
        <ul>
            <li style="color: {color1};"><strong>Player Average Bat Speed:</strong> {:.2f} mph (Benchmark: {:.2f} mph)
                <br>Player Grade: {}</li>
            <li style="color: {color2};"><strong>Top 10% Bat Speed:</strong> {:.2f} mph (Benchmark: {:.2f} mph)
                <br>Player Grade: {}</li>
            <li style="color: {color3};"><strong>Average Attack Angle (Top 10% Bat Speed Swings):</strong> {:.2f}° (Benchmark: {:.2f}°)
                <br>Player Grade: {}</li>
            <li style="color: {color4};"><strong>Average Time to Contact:</strong> {:.3f} sec (Benchmark: {:.3f} sec)
                <br>Player Grade: {}</li>
        </ul>
        """.format(
            player_avg_bat_speed, bat_speed_benchmark, evaluate_performance(player_avg_bat_speed, bat_speed_benchmark),
            top_10_percent_bat_speed, top_90_benchmark, evaluate_performance(top_10_percent_bat_speed, top_90_benchmark),
            avg_attack_angle_top_10, attack_angle_benchmark, evaluate_performance(avg_attack_angle_top_10, attack_angle_benchmark),
            avg_time_to_contact, time_to_contact_benchmark, evaluate_performance(avg_time_to_contact, time_to_contact_benchmark, lower_is_better=True),
            color1="red" if evaluate_performance(player_avg_bat_speed, bat_speed_benchmark) == "Below Average" else "black",
            color2="red" if evaluate_performance(top_10_percent_bat_speed, top_90_benchmark) == "Below Average" else "black",
            color3="red" if evaluate_performance(avg_attack_angle_top_10, attack_angle_benchmark) == "Below Average" else "black",
            color4="red" if evaluate_performance(avg_time_to_contact, time_to_contact_benchmark, lower_is_better=True) == "Below Average" else "black"
        )
    # Check if Exit Velocity Metrics are available
    if exit_velocity_metrics:
        email_body += """
        <h3 style="color: black;">Exit Velocity Metrics</h3>
        <ul>
            <li style="color: {color5};"><strong>Average Exit Velocity:</strong> {:.2f} mph (Benchmark: {:.2f} mph)
                <br>Player Grade: {}</li>
            <li style="color: {color6};"><strong>Top 8% Exit Velocity:</strong> {:.2f} mph (Benchmark: {:.2f} mph)
                <br>Player Grade: {}</li>
            <li style="color: {color7};"><strong>Average Launch Angle (On Top 8% Exit Velocity Swings):</strong> {:.2f}° (Benchmark: {:.2f}°)
                <br>Player Grade: {}</li>
            <li style="color: {color8};"><strong>Total Average Launch Angle (Avg LA):</strong> {:.2f}° (Benchmark: {:.2f}°)
                <br>Player Grade: {}</li>
            <li style="color: black;"><strong>Average Distance (8% swings):</strong> {:.2f} ft</li>
        </ul>
        """.format(
            exit_velocity_avg, ev_benchmark, evaluate_performance(exit_velocity_avg, ev_benchmark),
            top_8_percent_exit_velocity, top_8_benchmark, evaluate_performance(top_8_percent_exit_velocity, top_8_benchmark),
            avg_launch_angle_top_8, hhb_la_benchmark, evaluate_performance(avg_launch_angle_top_8, hhb_la_benchmark),
            total_avg_launch_angle, la_benchmark, evaluate_performance(total_avg_launch_angle, la_benchmark),
            avg_distance_top_8,
            color5="red" if evaluate_performance(exit_velocity_avg, ev_benchmark) == "Below Average" else "black",
            color6="red" if evaluate_performance(top_8_percent_exit_velocity, top_8_benchmark) == "Below Average" else "black",
            color7="red" if evaluate_performance(avg_launch_angle_top_8, hhb_la_benchmark) == "Below Average" else "black",
            color8="red" if evaluate_performance(total_avg_launch_angle, la_benchmark) == "Below Average" else "black"
        )

    # Close the HTML body
    email_body += "<p style='color: black;'>Best Regards,<br>OTR Baseball</p></body></html>"

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
        # Send the email report with the player's name and date range
        send_email_report(recipient_email, bat_speed_metrics, exit_velocity_metrics, player_name, date_range)
    else:
        st.error("Please enter a valid email address.")

