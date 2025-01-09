import streamlit as st
import pandas as pd
import smtplib
import base64
from io import BytesIO

# Email libraries
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------
# STREAMLIT UI: Title and Introduction
# ---------------------------------------------------------
st.title("OTR Baseball Metrics Analyzer (CID Approach)")
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

# ---------------------------------------------------------
# BENCHMARKS
# ---------------------------------------------------------
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
        "Avg BatSpeed": 49.21, "90th% BatSpeed": 52.81,
        "Avg TimeToContact": 0.19, "Avg AttackAngle": 11.78
    },
    "High School": {
        "Avg EV": 74.54, "Top 8th EV": 86.75, "Avg LA": 16.51, "HHB LA": 11.47,
        "Avg BatSpeed": 62.4, "90th% BatSpeed": 67.02,
        "Avg TimeToContact": 0.163, "Avg AttackAngle": 9.8
    },
    "College": {
        "Avg EV": 81.57, "Top 8th EV": 94.44, "Avg LA": 17.57, "HHB LA": 12.86,
        "Avg BatSpeed": 67.53, "90th% BatSpeed": 72.54,
        "Avg TimeToContact": 0.154, "Avg AttackAngle": 10.52
    },
    "Indy": {
        "Avg EV": 85.99, "Top 8th EV": 98.12, "Avg LA": 18.68, "HHB LA": 14.74,
        "Avg BatSpeed": 69.2, "90th% BatSpeed": 74.04,
        "Avg TimeToContact": 0.154, "Avg AttackAngle": 10.62
    },
    "Affiliate": {
        "Avg EV": 85.49, "Top 8th EV": 98.71, "Avg LA": 18.77, "HHB LA": 15.55,
        "Avg BatSpeed": 70.17, "90th% BatSpeed": 75.14,
        "Avg TimeToContact": 0.147, "Avg AttackAngle": 11.09
    }
}

def evaluate_performance(metric, benchmark, lower_is_better=False, special_metric=False):
    """
    Grades the metric against a benchmark.
    special_metric=True means we allow a small range around the benchmark
    for "Average" (useful for exit velocity).
    """
    if special_metric:
        # For EV: "Average" if within 3 mph below the benchmark
        if benchmark - 3 <= metric <= benchmark:
            return "Average"
        elif metric < benchmark - 3:
            return "Below Average"
        else:
            return "Above Average"
    else:
        if lower_is_better:
            # For Time to Contact: smaller is better
            if metric < benchmark:
                return "Above Average"
            elif metric <= benchmark * 1.1:
                return "Average"
            else:
                return "Below Average"
        else:
            # For speeds, angles, etc.: bigger is better
            if metric > benchmark:
                return "Above Average"
            elif metric >= benchmark * 0.9:
                return "Average"
            else:
                return "Below Average"

# ---------------------------------------------------------
# GLOBALS for storing final metrics & image data
# ---------------------------------------------------------
bat_speed_metrics = None
exit_velocity_metrics = None
strike_zone_img_data = None  # We'll store Base64 for the heatmap here

# ---------------------------------------------------------
# PROCESS BAT SPEED FILE (Skip the first 8 rows)
# ---------------------------------------------------------
if bat_speed_file:
    df_bat_speed = pd.read_csv(bat_speed_file, skiprows=8)
    bat_speed_data = pd.to_numeric(df_bat_speed.iloc[:, 7], errors='coerce')  # Column H: Bat Speed
    attack_angle_data = pd.to_numeric(df_bat_speed.iloc[:, 10], errors='coerce')  # Column K: Attack Angle
    time_to_contact_data = pd.to_numeric(df_bat_speed.iloc[:, 15], errors='coerce')  # Column P (check your CSV)

    player_avg_bat_speed = bat_speed_data.mean()
    top_10_percent_bat_speed = bat_speed_data.quantile(0.90)
    avg_attack_angle_top_10 = attack_angle_data[bat_speed_data >= top_10_percent_bat_speed].mean()
    avg_time_to_contact = time_to_contact_data.mean()

    # Fetch benchmarks
    bat_speed_benchmark = benchmarks[bat_speed_level]["Avg BatSpeed"]
    top_90_benchmark = benchmarks[bat_speed_level]["90th% BatSpeed"]
    time_to_contact_benchmark = benchmarks[bat_speed_level]["Avg TimeToContact"]
    attack_angle_benchmark = benchmarks[bat_speed_level]["Avg AttackAngle"]

    # Build a markdown text chunk for the final report
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

# ---------------------------------------------------------
# PROCESS EXIT VELOCITY FILE (No rows skipped)
# ---------------------------------------------------------
if exit_velocity_file:
    df_exit_velocity = pd.read_csv(exit_velocity_file)
    try:
        # According to instructions:
        # Column F (Index 5) = Strike Zone
        # Column H (Index 7) = EV
        # Column I (Index 8) = LA
        # Column J (Index 9) = Dist

        if len(df_exit_velocity.columns) > 9:
            strike_zone_data = df_exit_velocity.iloc[:, 5]
            exit_velocity_data = pd.to_numeric(df_exit_velocity.iloc[:, 7], errors='coerce')
            launch_angle_data = pd.to_numeric(df_exit_velocity.iloc[:, 8], errors='coerce')
            distance_data = pd.to_numeric(df_exit_velocity.iloc[:, 9], errors='coerce')

            # Filter out zero or invalid EV rows
            non_zero_ev_rows = exit_velocity_data[exit_velocity_data > 0]
            if not non_zero_ev_rows.empty:
                # Calculate metrics
                exit_velocity_avg = non_zero_ev_rows.mean()
                top_8_percent_exit_velocity = non_zero_ev_rows.quantile(0.92)

                top_8_mask = exit_velocity_data >= top_8_percent_exit_velocity
                avg_launch_angle_top_8 = launch_angle_data[top_8_mask].mean()
                avg_distance_top_8 = distance_data[top_8_mask].mean()
                total_avg_launch_angle = launch_angle_data[launch_angle_data > 0].mean()

                # Benchmarks
                ev_benchmark = benchmarks[exit_velocity_level]["Avg EV"]
                top_8_benchmark = benchmarks[exit_velocity_level]["Top 8th EV"]
                la_benchmark = benchmarks[exit_velocity_level]["Avg LA"]
                hhb_la_benchmark = benchmarks[exit_velocity_level]["HHB LA"]

                # Build text for the final metrics
                exit_velocity_metrics = (
                    "### Exit Velocity Metrics\n"
                    f"- **Average Exit Velocity (Non-zero EV):** {exit_velocity_avg:.2f} mph (Benchmark: {ev_benchmark} mph)\n"
                    f"  - Player Grade: {evaluate_performance(exit_velocity_avg, ev_benchmark, special_metric=True)}\n"
                    f"- **Top 8% Exit Velocity:** {top_8_percent_exit_velocity:.2f} mph (Benchmark: {top_8_benchmark} mph)\n"
                    f"  - Player Grade: {evaluate_performance(top_8_percent_exit_velocity, top_8_benchmark, special_metric=True)}\n"
                    f"- **Average Launch Angle (On Top 8% EV Swings):** {avg_launch_angle_top_8:.2f}° (Benchmark: {hhb_la_benchmark}°)\n"
                    f"  - Player Grade: {evaluate_performance(avg_launch_angle_top_8, hhb_la_benchmark)}\n"
                    f"- **Total Average Launch Angle (Avg LA):** {total_avg_launch_angle:.2f}° (Benchmark: {la_benchmark}°)\n"
                    f"  - Player Grade: {evaluate_performance(total_avg_launch_angle, la_benchmark)}\n"
                    f"- **Average Distance (8% swings):** {avg_distance_top_8:.2f} ft\n"
                )

                # -------- Create Strike-Zone Heatmap ----------
                top_8_df = df_exit_velocity[top_8_mask].copy()
                top_8_df["StrikeZone"] = top_8_df.iloc[:, 5]  # Column F
                zone_counts = top_8_df["StrikeZone"].value_counts()

                # Layout
                zone_layout = [
                    [10, None, 11],
                    [1,   2,    3],
                    [4,   5,    6],
                    [7,   8,    9],
                    [12, None, 13]
                ]
                max_count = zone_counts.max() if not zone_counts.empty else 0

                # Plot with matplotlib
                fig, ax = plt.subplots(figsize=(3,5))
                ax.axis('off')
                cmap = plt.get_cmap('Reds')
                cell_width = 1.0
                cell_height = 1.0

                for r, row_zones in enumerate(zone_layout):
                    for c, z in enumerate(row_zones):
                        x = c * cell_width
                        y = (len(zone_layout)-1 - r) * cell_height
                        if z is not None:
                            count = zone_counts.get(z, 0)
                            norm_val = (count / max_count) if max_count > 0 else 0
                            color = cmap(norm_val * 0.8 + 0.2) if norm_val > 0 else (1,1,1,1)
                            rect = plt.Rectangle((x, y), cell_width, cell_height,
                                                 facecolor=color, edgecolor='black')
                            ax.add_patch(rect)
                            ax.text(x + 0.5*cell_width, y + 0.5*cell_height, str(z),
                                    ha='center', va='center', fontsize=10, color='black')
                        else:
                            # blank cell
                            rect = plt.Rectangle((x, y), cell_width, cell_height,
                                                 facecolor='white', edgecolor='black')
                            ax.add_patch(rect)

                ax.set_xlim(0, 3*cell_width)
                ax.set_ylim(0, 5*cell_height)

                # Save plot to buffer, then base64-encode
                buf = BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight')
                buf.seek(0)
                strike_zone_img_data = base64.b64encode(buf.read()).decode('utf-8')
                plt.close(fig)
            else:
                st.error("No valid Exit Velocity data found in the file. Please check the data.")
        else:
            st.error("The uploaded file does not have the required columns for Exit Velocity.")
    except Exception as e:
        st.error(f"An error occurred while processing the Exit Velocity file: {e}")

# ---------------------------------------------------------
# DISPLAY RESULTS IN STREAMLIT
# ---------------------------------------------------------
st.write("## Calculated Metrics")
if bat_speed_metrics:
    st.markdown(bat_speed_metrics)

if exit_velocity_metrics:
    st.markdown(exit_velocity_metrics)

    if strike_zone_img_data:
        # Show the chart in Streamlit using data URI
        chart_html = f"<h3>Strike Zone Average Exit Velocity</h3><img src='data:image/png;base64,{strike_zone_img_data}'/>"
        st.markdown(chart_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# COLLECT EMAIL FIELDS
# ---------------------------------------------------------
player_name = st.text_input("Enter Player Name")
date_range = st.text_input("Enter Date Range")

email_address = "otrdatatrack@gmail.com"  # Sender email
email_password = "pslp fuab dmub cggo"    # App-specific or SMTP password
smtp_server = "smtp.gmail.com"
smtp_port = 587

# ---------------------------------------------------------
# SEND EMAIL USING CID
# ---------------------------------------------------------
def send_email_report_cid(
    recipient_email,
    bat_speed_metrics,
    exit_velocity_metrics,
    player_name,
    date_range,
    bat_speed_level,
    exit_velocity_level,
    strike_zone_img_data
):
    """
    Send an HTML email with the strike-zone image attached as a 'cid' inline image.
    """
    # 1) Create a MIMEMultipart 'related' container for HTML + image
    msg_root = MIMEMultipart('related')
    msg_root['From'] = email_address
    msg_root['To'] = recipient_email
    msg_root['Subject'] = "OTR Baseball Metrics and Grade Report (CID)"

    # 2) Build the HTML with a reference to 'cid:strike_zone_image'
    email_html = f"""
    <html>
    <body style="color: black; background-color: white;">
        <h2 style="color: black;">OTR Metrics Report</h2>
        <p><strong>Player Name:</strong> {player_name}</p>
        <p><strong>Date Range:</strong> {date_range}</p>
    """

    if bat_speed_metrics:
        email_html += f"<p><strong>Bat Speed Level:</strong> {bat_speed_level}</p>"
    if exit_velocity_metrics:
        email_html += f"<p><strong>Exit Velocity Level:</strong> {exit_velocity_level}</p>"

    email_html += "<p>The following data is constructed with benchmarks for each level.</p>"

    # Insert bat speed and exit velocity sections
    if bat_speed_metrics:
        # Convert the Markdown metrics to HTML, or just inline them as text
        email_html += f"<div>{bat_speed_metrics}</div>"
    if exit_velocity_metrics:
        email_html += f"<div>{exit_velocity_metrics}</div>"

    # Add the heatmap if available
    if strike_zone_img_data:
        email_html += """
        <h3>Strike Zone Average Exit Velocity</h3>
        <img src="cid:strike_zone_image" alt="Strike Zone Heatmap" />
        """

    email_html += """
    <p>Best Regards,<br>OTR Baseball</p>
    </body>
    </html>
    """

    # 3) Create a MIMEMultipart('alternative') to hold the HTML
    msg_alternative = MIMEMultipart('alternative')
    msg_root.attach(msg_alternative)

    # 4) Attach HTML into the alternative part
    msg_text = MIMEText(email_html, 'html')
    msg_alternative.attach(msg_text)

    # 5) If we have the strike zone image, attach it with Content-ID = 'strike_zone_image'
    if strike_zone_img_data:
        img_data_content = base64.b64decode(strike_zone_img_data)  # decode from base64
        msg_image = MIMEImage(img_data_content, _subtype='png')
        msg_image.add_header('Content-ID', '<strike_zone_image>')
        msg_image.add_header('Content-Disposition', 'inline', filename='strike_zone.png')
        msg_root.attach(msg_image)

    # 6) Send
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg_root)
        st.success("Report sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# ---------------------------------------------------------
# STREAMLIT: SEND EMAIL BUTTON
# ---------------------------------------------------------
st.write("## Email the Report")
recipient_email = st.text_input("Enter Recipient Email")

if st.button("Send Report"):
    if recipient_email:
        send_email_report_cid(
            recipient_email,
            bat_speed_metrics,
            exit_velocity_metrics,
            player_name,
            date_range,
            bat_speed_level,
            exit_velocity_level,
            strike_zone_img_data
        )
    else:
        st.error("Please enter a valid email address.")
