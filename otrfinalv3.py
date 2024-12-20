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

# Dropdown for Bat Speed Level
bat_speed_level = st.selectbox(
    "Select Player Level for Bat Speed", 
    ["Youth", "High School", "College", "Indy", "Affiliate"]
)

# Dropdown for Exit Velocity Level
exit_velocity_level = st.selectbox(
    "Select Player Level for Exit Velocity", 
    ["10u", "12u", "14u", "JV/16u", "Var/18u", "College", "Indy", "Affiliate"]
)

# Debugging: Ensure levels are selected correctly
st.write(f"Selected Bat Speed Level: {bat_speed_level}")
st.write(f"Selected Exit Velocity Level: {exit_velocity_level}")

# Benchmarks
benchmarks = {
    "10u": {
        "Avg EV": 50, "Top 8th EV": 61,
        "Avg LA": 12.14, "HHB LA": 8.78
    },
    "12u": {
        "Avg EV": 59, "Top 8th EV": 72,
        "Avg LA": 12.14, "HHB LA": 8.78
    },
    "14u": {
        "Avg EV": 68, "Top 8th EV": 80,
        "Avg LA": 12.14, "HHB LA": 8.78
    },
    "JV/16u": {
        "Avg EV": 72.65, "Top 8th EV": 85,
        "Avg LA": 16.51, "HHB LA": 11.47
    },
    "Var/18u": {
        "Avg EV": 78.0, "Top 8th EV": 91.5,
        "Avg LA": 16.51, "HHB LA": 11.47
    },
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

def evaluate_performance(metric, benchmark, lower_is_better=False, special_metric=False):
    if special_metric:
        # Special handling for Exit Velocity
        if benchmark - 3 <= metric <= benchmark:
            return "Average"
        elif metric < benchmark - 3:
            return "Below Average"
        else:
            return "Above Average"
    else:
        if lower_is_better:
            if metric < benchmark:
                return "Above Average"
            elif metric <= benchmark * 1.1:
                return "Average"
            else:
                return "Below Average"
        else:
            if metric > benchmark:
                return "Above Average"
            elif metric >= benchmark * 0.9:
                return "Average"
            else:
                return "Below Average"

# Process Bat Speed File (Skip the first 8 rows)
bat_speed_metrics = None
if bat_speed_file:
    df_bat_speed = pd.read_csv(bat_speed_file, skiprows=8)
    bat_speed_data = pd.to_numeric(df_bat_speed.iloc[:, 7], errors='coerce')  # Column H: Bat Speed
    attack_angle_data = pd.to_numeric(df_bat_speed.iloc[:, 10], errors='coerce')  # Column K: Attack Angle
    time_to_contact_data = pd.to_numeric(df_bat_speed.iloc[:, 15], errors='coerce')  # Time to Contact

    player_avg_bat_speed = bat_speed_data.mean()
    top_10_percent_bat_speed = bat_speed_data.quantile(0.90)
    avg_attack_angle_top_10 = attack_angle_data[bat_speed_data >= top_10_percent_bat_speed].mean()
    avg_time_to_contact = time_to_contact_data.mean()

    bat_speed_benchmark = benchmarks[bat_speed_level]["Avg BatSpeed"]
    top_90_benchmark = benchmarks[bat_speed_level]["90th% BatSpeed"]
    time_to_contact_benchmark = benchmarks[bat_speed_level]["Avg TimeToContact"]
    attack_angle_benchmark = benchmarks[bat_speed_level]["Avg AttackAngle"]

    bat_speed_metrics = (
        "### Bat Speed Metrics\n"
        f"- **Player Average Bat Speed:** {player_avg_bat_speed:.2f} mph (Benchmark: {bat_speed_benchmark} mph)\n"
        f"  - Player Grade: {evaluate_performance(player_avg_bat_speed, bat_speed_benchmark)}\n"
        f"- **Top 10% Bat Speed:** {top_10_percent_bat_speed:.2f} mph (Benchmark: {top_90_benchmark} mph)\n"
        f"  - Player Grade: {evaluate_performance(top_10_percent_bat_speed, top_90_benchmark)}\n"
        f"- **Average Attack Angle (Top 10% Bat Speed Swings):** {avg_attack_angle_top_10:.2f}° (Benchmark: {attack_angle_benchmark}°)\n"
        f"  - Player Grade: {evaluate_performance(avg_attack_angle_top_10, attack_angle_benchmark)}\n"
        f"- **Average Time to Contact:** {avg_time_to_contact:.3f} sec (Benchmark: {time_to_contact_benchmark} sec)\n"
        f"  - Player Grade: {evaluate_performance(avg_time_to_contact, time_to_contact_benchmark, lower_is_better=True)}\n"
    )

# Process Exit Velocity File
exit_velocity_metrics = None
strike_zone_html = ""
if exit_velocity_file:
    df_exit_velocity = pd.read_csv(exit_velocity_file)
    try:
        required_columns = ["Velo", "LA", "Dist", "Strike Zone"]
        if all(col in df_exit_velocity.columns for col in required_columns):
            exit_velocity_data = pd.to_numeric(df_exit_velocity["Velo"], errors='coerce')
            launch_angle_data = pd.to_numeric(df_exit_velocity["LA"], errors='coerce')
            distance_data = pd.to_numeric(df_exit_velocity["Dist"], errors='coerce')
            # Strike Zone data as is
            strike_zone_data = df_exit_velocity["Strike Zone"]

            # Filter out rows where Exit Velocity is zero or NaN
            non_zero_ev_rows = exit_velocity_data[exit_velocity_data > 0]

            if not non_zero_ev_rows.empty:
                # Calculate Exit Velocity Metrics
                exit_velocity_avg = non_zero_ev_rows.mean()
                top_8_percent_exit_velocity = non_zero_ev_rows.quantile(0.92)

                avg_launch_angle_top_8 = launch_angle_data[exit_velocity_data >= top_8_percent_exit_velocity].mean()
                avg_distance_top_8 = distance_data[exit_velocity_data >= top_8_percent_exit_velocity].mean()
                total_avg_launch_angle = launch_angle_data[launch_angle_data > 0].mean()

                ev_benchmark = benchmarks[exit_velocity_level]["Avg EV"]
                top_8_benchmark = benchmarks[exit_velocity_level]["Top 8th EV"]
                la_benchmark = benchmarks[exit_velocity_level]["Avg LA"]
                hhb_la_benchmark = benchmarks[exit_velocity_level]["HHB LA"]

                exit_velocity_metrics = (
                    "### Exit Velocity Metrics\n"
                    f"- **Average Exit Velocity:** {exit_velocity_avg:.2f} mph (Benchmark: {ev_benchmark} mph)\n"
                    f"  - Player Grade: {evaluate_performance(exit_velocity_avg, ev_benchmark, special_metric=True)}\n"
                    f"- **Top 8% Exit Velocity:** {top_8_percent_exit_velocity:.2f} mph (Benchmark: {top_8_benchmark} mph)\n"
                    f"  - Player Grade: {evaluate_performance(top_8_percent_exit_velocity, top_8_benchmark, special_metric=True)}\n"
                    f"- **Average Launch Angle (On Top 8% Exit Velocity Swings):** {avg_launch_angle_top_8:.2f}° (Benchmark: {hhb_la_benchmark}°)\n"
                    f"  - Player Grade: {evaluate_performance(avg_launch_angle_top_8, hhb_la_benchmark)}\n"
                    f"- **Total Average Launch Angle (Avg LA):** {total_avg_launch_angle:.2f}° (Benchmark: {la_benchmark}°)\n"
                    f"  - Player Grade: {evaluate_performance(total_avg_launch_angle, la_benchmark)}\n"
                    f"- **Average Distance (8% swings):** {avg_distance_top_8:.2f} ft\n"
                )

                # Compute top 8% EV per zone
                zone_stats = df_exit_velocity.groupby("Strike Zone")["Velo"].quantile(0.92)

                # Extract each zone value
                z1 = zone_stats.get(1, None)
                z2 = zone_stats.get(2, None)
                z3 = zone_stats.get(3, None)
                z4 = zone_stats.get(4, None)
                z5 = zone_stats.get(5, None)
                z6 = zone_stats.get(6, None)
                z7 = zone_stats.get(7, None)
                z8 = zone_stats.get(8, None)
                z9 = zone_stats.get(9, None)
                z10 = zone_stats.get(10, None)
                z11 = zone_stats.get(11, None)
                z12 = zone_stats.get(12, None)
                z13 = zone_stats.get(13, None)

                # Construct HTML for strike zone graphic
                strike_zone_html = f"""
                <h3>Strike Zone Top 8% Exit Velocities</h3>
                <table style="border-collapse: collapse; margin: 20px 0; text-align:center;">
                  <tr>
                    <td></td><td>{z11 if z11 else ''}</td><td></td><td>{z10 if z10 else ''}</td><td></td>
                  </tr>
                  <tr>
                    <td></td><td>{z3 if z3 else ''}</td><td>{z2 if z2 else ''}</td><td>{z1 if z1 else ''}</td><td></td>
                  </tr>
                  <tr>
                    <td></td><td>{z6 if z6 else ''}</td><td>{z5 if z5 else ''}</td><td>{z4 if z4 else ''}</td><td></td>
                  </tr>
                  <tr>
                    <td></td><td>{z9 if z9 else ''}</td><td>{z8 if z8 else ''}</td><td>{z7 if z7 else ''}</td><td></td>
                  </tr>
                  <tr>
                    <td></td><td>{z13 if z13 else ''}</td><td></td><td>{z12 if z12 else ''}</td><td></td>
                  </tr>
                </table>
                """
            else:
                st.error("No valid Exit Velocity data found in the file. Please check the data.")
        else:
            st.error("The uploaded file does not have the required columns (Velo, LA, Dist, Strike Zone).")
    except Exception as e:
        st.error(f"An error occurred while processing the Exit Velocity file: {e}")

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

def send_email_report(recipient_email, bat_speed_metrics, exit_velocity_metrics, player_name, date_range, bat_speed_level, exit_velocity_level, strike_zone_html):
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = recipient_email
    msg['Subject'] = "OTR Baseball Metrics and Grade Report"

    email_body = f"""
    <html>
    <body style="color: black; background-color: white;">
        <h2 style="color: black;">OTR Metrics Report</h2>
        <p style="color: black;"><strong>Player Name:</strong> {player_name}</p>
        <p style="color: black;"><strong>Date Range:</strong> {date_range}</p>
    """

    if bat_speed_metrics:
        email_body += f"<p style='color: black;'><strong>Bat Speed Level:</strong> {bat_speed_level}</p>"

    if exit_velocity_metrics:
        email_body += f"<p style='color: black;'><strong>Exit Velocity Level:</strong> {exit_velocity_level}</p>"

    email_body += "<p style='color: black;'>The following data is constructed with benchmarks for each level.</p>"

    if bat_speed_metrics:
        # Use the already computed metrics variables (player_avg_bat_speed, etc.) from the bat speed section
        # We'll need to access them here or recalculate if needed. Because they're only defined above,
        # we can just trust that this code runs after processing. If needed, store them as global or pass them.
        # For brevity, we reuse the variables directly here as they are defined above.
        email_body += f"""
        <h3 style="color: black;">Bat Speed Metrics</h3>
        <p><strong>Player Average Bat Speed:</strong> {player_avg_bat_speed:.2f} mph (Benchmark: {bat_speed_benchmark} mph)
        <br>Player Grade: {evaluate_performance(player_avg_bat_speed, bat_speed_benchmark)}</p>

        <p><strong>Top 10% Bat Speed:</strong> {top_10_percent_bat_speed:.2f} mph (Benchmark: {top_90_benchmark} mph)
        <br>Player Grade: {evaluate_performance(top_10_percent_bat_speed, top_90_benchmark)}</p>

        <p><strong>Average Attack Angle (Top 10% Bat Speed Swings):</strong> {avg_attack_angle_top_10:.2f}° (Benchmark: {attack_angle_benchmark}°)
        <br>Player Grade: {evaluate_performance(avg_attack_angle_top_10, attack_angle_benchmark)}</p>

        <p><strong>Average Time to Contact:</strong> {avg_time_to_contact:.3f} sec (Benchmark: {time_to_contact_benchmark} sec)
        <br>Player Grade: {evaluate_performance(avg_time_to_contact, time_to_contact_benchmark, lower_is_better=True)}</p>
        """

    if exit_velocity_metrics:
        # Same assumption as above: the variables computed for EV are still in scope.
        email_body += f"""
        <h3 style="color: black;">Exit Velocity Metrics</h3>
        <p><strong>Average Exit Velocity:</strong> {exit_velocity_avg:.2f} mph (Benchmark: {ev_benchmark} mph)
        <br>Player Grade: {evaluate_performance(exit_velocity_avg, ev_benchmark, special_metric=True)}</p>

        <p><strong>Top 8% Exit Velocity:</strong> {top_8_percent_exit_velocity:.2f} mph (Benchmark: {top_8_benchmark} mph)
        <br>Player Grade: {evaluate_performance(top_8_percent_exit_velocity, top_8_benchmark, special_metric=True)}</p>

        <p><strong>Average Launch Angle (On Top 8% Exit Velocity Swings):</strong> {avg_launch_angle_top_8:.2f}° (Benchmark: {hhb_la_benchmark}°)
        <br>Player Grade: {evaluate_performance(avg_launch_angle_top_8, hhb_la_benchmark)}</p>

        <p><strong>Total Average Launch Angle (Avg LA):</strong> {total_avg_launch_angle:.2f}° (Benchmark: {la_benchmark}°)
        <br>Player Grade: {evaluate_performance(total_avg_launch_angle, la_benchmark)}</p>

        <p><strong>Average Distance (8% swings):</strong> {avg_distance_top_8:.2f} ft</p>
        """

        # Add the strike zone graphic HTML
        email_body += strike_zone_html

    email_body += "<p style='color: black;'>Best Regards,<br>OTR Baseball</p></body></html>"

    msg.attach(MIMEText(email_body, 'html'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg)
        st.success("Report sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

st.write("## Email the Report")
recipient_email = st.text_input("Enter Email Address")

if st.button("Send Report"):
    if recipient_email:
        send_email_report(
            recipient_email, 
            bat_speed_metrics, 
            exit_velocity_metrics, 
            player_name, 
            date_range, 
            bat_speed_level,  
            exit_velocity_level,
            strike_zone_html
        )
    else:
        st.error("Please enter a valid email address.")
