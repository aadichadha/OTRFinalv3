import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage  # Import MIMEImage for embedding images
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io

# ------------------------------
# 1. Define Zone Layout
# ------------------------------

# Define zone boundaries based on your setup
zone_definitions = {
    # Main Grid Zones
    1: {'x': [2, 3], 'y': [3, 4]},   # Top Right
    2: {'x': [1, 2], 'y': [3, 4]},   # Top Center
    3: {'x': [0, 1], 'y': [3, 4]},   # Top Left
    4: {'x': [2, 3], 'y': [2, 3]},   # Middle Right
    5: {'x': [1, 2], 'y': [2, 3]},   # Middle Center
    6: {'x': [0, 1], 'y': [2, 3]},   # Middle Left
    7: {'x': [2, 3], 'y': [1, 2]},   # Bottom Right
    8: {'x': [1, 2], 'y': [1, 2]},   # Bottom Center
    9: {'x': [0, 1], 'y': [1, 2]},   # Bottom Left
    # Additional Zones
    10: {'x': [3, 4], 'y': [3, 4]},  # Top Right Extra
    11: {'x': [-1, 0], 'y': [3, 4]}, # Top Left Extra
    12: {'x': [-1, 0], 'y': [0, 1]}, # Bottom Left Extra
    13: {'x': [3, 4], 'y': [0, 1]},  # Bottom Right Extra
}

# ------------------------------
# 2. Title and Introduction
# ------------------------------

st.title("OTR Baseball Metrics Analyzer")
st.write("Upload your Bat Speed and Exit Velocity CSV files to generate a comprehensive report.")

# ------------------------------
# 3. File Uploads
# ------------------------------

bat_speed_file = st.file_uploader("Upload Bat Speed File", type="csv")
exit_velocity_file = st.file_uploader("Upload Exit Velocity File", type="csv")

# ------------------------------
# 4. Dropdowns for Player Levels
# ------------------------------

bat_speed_level = st.selectbox(
    "Select Player Level for Bat Speed", 
    ["Youth", "High School", "College", "Indy", "Affiliate"]
)

exit_velocity_level = st.selectbox(
    "Select Player Level for Exit Velocity", 
    ["10u", "12u", "14u", "JV/16u", "Var/18u", "College", "Indy", "Affiliate"]
)

# Debugging: Ensure levels are selected correctly
st.write(f"Selected Bat Speed Level: {bat_speed_level}")
st.write(f"Selected Exit Velocity Level: {exit_velocity_level}")

# ------------------------------
# 5. Benchmarks Based on Levels
# ------------------------------

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
        "Avg EV": 72.65, "Top 8th EV": 85,  # New 16u benchmarks for Exit Velocity
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

# ------------------------------
# 6. Performance Evaluation Function
# ------------------------------

def evaluate_performance(metric, benchmark, lower_is_better=False, special_metric=False):
    if special_metric:  # Special handling for Exit Velocity and Top 8% Exit Velocity
        if benchmark - 3 <= metric <= benchmark:  # Within 3 mph below the benchmark
            return "Average"
        elif metric < benchmark - 3:  # More than 3 mph below the benchmark
            return "Below Average"
        else:  # Anything above the benchmark
            return "Above Average"
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

# ------------------------------
# 7. Process Bat Speed File (Skip the first 8 rows)
# ------------------------------

bat_speed_metrics = None  # Initialize as None
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
    bat_speed_benchmark = benchmarks[bat_speed_level]["Avg BatSpeed"]
    top_90_benchmark = benchmarks[bat_speed_level]["90th% BatSpeed"]
    time_to_contact_benchmark = benchmarks[bat_speed_level]["Avg TimeToContact"]
    attack_angle_benchmark = benchmarks[bat_speed_level]["Avg AttackAngle"]

    # Format Bat Speed Metrics
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

# ------------------------------
# 8. Process Exit Velocity File (No rows skipped)
# ------------------------------

exit_velocity_metrics = None  # Initialize as None
zone_data_top_8 = None        # Initialize to store Zone data for top 8% swings

if exit_velocity_file:
    df_exit_velocity = pd.read_csv(exit_velocity_file)  # No rows are skipped here

    try:
        # Ensure the file has enough columns for the required calculations
        if len(df_exit_velocity.columns) > 9:  # Ensure at least 10 columns for "Velo", "LA", "Dist", "Zone"
            exit_velocity_data = pd.to_numeric(df_exit_velocity.iloc[:, 7], errors='coerce')  # Column H: "Velo"
            launch_angle_data = pd.to_numeric(df_exit_velocity.iloc[:, 8], errors='coerce')  # Column I: "LA"
            distance_data = pd.to_numeric(df_exit_velocity.iloc[:, 9], errors='coerce')  # Column J: "Dist"
            zone_data = pd.to_numeric(df_exit_velocity.iloc[:, 10], errors='coerce')      # Column K: "Zone"

            # Filter out rows where Exit Velocity is zero or NaN
            non_zero_ev_rows = exit_velocity_data[exit_velocity_data > 0]
            zone_data = zone_data[exit_velocity_data > 0]

            # Only proceed if there is valid data
            if not non_zero_ev_rows.empty:
                # Calculate Exit Velocity Metrics
                exit_velocity_avg = non_zero_ev_rows.mean()
                top_8_percent_exit_velocity = non_zero_ev_rows.quantile(0.92)
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
                    f"  - Player Grade: {evaluate_performance(exit_velocity_avg, ev_benchmark, special_metric=True)}\n"
                    f"- **Top 8% Exit Velocity:** {top_8_percent_exit_velocity:.2f} mph (Benchmark: {top_8_benchmark} mph)\n"
                    f"  - Player Grade: {evaluate_performance(top_8_percent_exit_velocity, top_8_benchmark, special_metric=True)}\n"
                    f"- **Average Launch Angle (On Top 8% Exit Velocity Swings):** {avg_launch_angle_top_8:.2f}° (Benchmark: {hhb_la_benchmark}°)\n"
                    f"  - Player Grade: {evaluate_performance(avg_launch_angle_top_8, hhb_la_benchmark)}\n"
                    f"- **Total Average Launch Angle (Avg LA):** {total_avg_launch_angle:.2f}° (Benchmark: {la_benchmark}°)\n"
                    f"  - Player Grade: {evaluate_performance(total_avg_launch_angle, la_benchmark)}\n"
                    f"- **Average Distance (8% swings):** {avg_distance_top_8:.2f} ft\n"
                )

                # Extract Zone data for top 8% swings
                zone_data_top_8 = zone_data[exit_velocity_data >= top_8_percent_exit_velocity].dropna().astype(int)
            else:
                st.error("No valid Exit Velocity data found in the file. Please check the data.")
        else:
            st.error("The uploaded Exit Velocity file does not have the required columns (at least 11 columns expected).")
    except Exception as e:
        st.error(f"An error occurred while processing the Exit Velocity file: {e}")

# ------------------------------
# 9. Display Calculated Metrics
# ------------------------------

st.write("## Calculated Metrics")
if bat_speed_metrics:
    st.markdown(bat_speed_metrics)
if exit_velocity_metrics:
    st.markdown(exit_velocity_metrics)

# ------------------------------
# 10. Player Name and Date Range Input
# ------------------------------

player_name = st.text_input("Enter Player Name")
date_range = st.text_input("Enter Date Range")

# ------------------------------
# 11. Email Configuration
# ------------------------------

# **Security Notice:** It's not secure to hardcode your email password.
# Consider using Streamlit Secrets or environment variables for sensitive information.
email_address = "otrdatatrack@gmail.com"  # Your email address
email_password = "pslp fuab dmub cggo"  # Your app-specific password
smtp_server = "smtp.gmail.com"
smtp_port = 587

# ------------------------------
# 12. Function to Create Strike Zone Graphic
# ------------------------------

def create_strike_zone_graphic(zones, zone_definitions):
    if zones is None or zones.empty:
        return None  # No data to plot

    fig, ax = plt.subplots(figsize=(8, 8))  # Adjust figure size as needed

    # Draw each zone
    for zone_num, bounds in zone_definitions.items():
        rect = patches.Rectangle(
            (bounds['x'][0], bounds['y'][0]),
            bounds['x'][1] - bounds['x'][0],
            bounds['y'][1] - bounds['y'][0],
            linewidth=2,
            edgecolor='black',
            facecolor='lightgray',
            alpha=0.5
        )
        ax.add_patch(rect)
        
        # Annotate zone number at the center
        center_x = (bounds['x'][0] + bounds['x'][1]) / 2
        center_y = (bounds['y'][0] + bounds['y'][1]) / 2
        ax.text(
            center_x, center_y, str(zone_num),
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=12,
            fontweight='bold'
        )

    # Count the number of swings per zone
    zone_counts = zones.value_counts().to_dict()

    # Plot swing locations
    for zone_num, count in zone_counts.items():
        bounds = zone_definitions.get(zone_num)
        if bounds:
            x_center = (bounds['x'][0] + bounds['x'][1]) / 2
            y_center = (bounds['y'][0] + bounds['y'][1]) / 2
            ax.plot(x_center, y_center, 'ro', markersize=8, alpha=0.7)
            ax.text(
                x_center, y_center + 0.1, f"x{count}",
                horizontalalignment='center',
                verticalalignment='bottom',
                fontsize=10,
                color='blue'
            )
        else:
            st.warning(f"Zone {zone_num} is not defined in zone_definitions.")

    # Set plot limits
    all_x = [bounds['x'][1] for bounds in zone_definitions.values()]
    all_y = [bounds['y'][1] for bounds in zone_definitions.values()]
    min_x = min(bounds['x'][0] for bounds in zone_definitions.values()) - 0.5
    max_x = max(all_x) + 0.5
    min_y = min(bounds['y'][0] for bounds in zone_definitions.values()) - 0.5
    max_y = max(all_y) + 0.5

    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)
    ax.set_xlabel('Horizontal Location')
    ax.set_ylabel('Vertical Location')
    ax.set_title('Strike Zone - Top 8% Exit Velocity Swings')
    ax.set_aspect('equal')
    plt.grid(True)
    plt.tight_layout()

    # Save the plot to a BytesIO object
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    plt.close(fig)
    img_buffer.seek(0)
    return img_buffer

# ------------------------------
# 13. Function to Send Email with Embedded Graphic
# ------------------------------

def send_email_report(recipient_email, bat_speed_metrics, exit_velocity_metrics, player_name, date_range, bat_speed_level, exit_velocity_level, strike_zone_image):
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
    """

    # Dynamically add Bat Speed Level if Bat Speed Metrics are available
    if bat_speed_metrics:
        email_body += f"<p style='color: black;'><strong>Bat Speed Level:</strong> {bat_speed_level}</p>"
    
    # Dynamically add Exit Velocity Level if Exit Velocity Metrics are available
    if exit_velocity_metrics:
        email_body += f"<p style='color: black;'><strong>Exit Velocity Level:</strong> {exit_velocity_level}</p>"

    # Add a general statement about benchmarks
    email_body += "<p style='color: black;'>The following data is constructed with benchmarks for each level.</p>"

    # Check if Bat Speed Metrics are available
    if bat_speed_metrics:
        email_body += f"""
        <h3 style="color: black;">Bat Speed Metrics</h3>
        {bat_speed_metrics.replace('\n', '<br>')}
        """

    # Check if Exit Velocity Metrics are available
    if exit_velocity_metrics:
        email_body += f"""
        <h3 style="color: black;">Exit Velocity Metrics</h3>
        {exit_velocity_metrics.replace('\n', '<br>')}
        """

    # Embed Strike Zone Graphic if available
    if strike_zone_image:
        # Attach the image
        image = MIMEImage(strike_zone_image.read(), _subtype='png')
        image.add_header('Content-ID', '<strike_zone>')
        msg.attach(image)

        # Add HTML to display the image
        email_body += """
        <h3 style="color: black;">Strike Zone Analysis</h3>
        <p style="color: black;">The following graphic illustrates the distribution of the top 8% exit velocity swings across different zones:</p>
        <img src="cid:strike_zone" alt="Strike Zone Graphic" style="width:600px;height:auto;">
        """

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

# ------------------------------
# 14. Streamlit Email Input and Button
# ------------------------------

st.write("## Email the Report")
recipient_email = st.text_input("Enter Email Address")

if st.button("Send Report"):
    if recipient_email and player_name and date_range:
        # Create Strike Zone Graphic
        strike_zone_image = create_strike_zone_graphic(zone_data_top_8, zone_definitions)
        
        # Send the email report with the player's name, date range, and levels
        send_email_report(
            recipient_email, 
            bat_speed_metrics, 
            exit_velocity_metrics, 
            player_name, 
            date_range, 
            bat_speed_level,  # Pass bat speed level
            exit_velocity_level,  # Pass exit velocity level
            strike_zone_image  # Pass the strike zone image
        )
    else:
        st.error("Please enter all required information: Email Address, Player Name, and Date Range.")
