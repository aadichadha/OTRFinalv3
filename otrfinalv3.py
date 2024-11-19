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
email_address = "aadichadha@gmail.com"  # Your email address
email_password = "eeoi odag olix nnfc"  # Your app-specific password
smtp_server = "smtp.gmail.com"
smtp_port = 587

# Function to Send Email
def send_email_report(recipient_email, bat_speed_metrics, exit_velocity_metrics):
    # Create the email content
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = recipient_email
    msg['Subject'] = "Baseball Metrics Report"

    # Construct the email body with organized layout
    email_body = """
    <html>
    <body>
        <h2>Baseball Metrics Report</h2>
        <p>Please find the detailed analysis of the uploaded baseball metrics below:</p>
        
        <h3>Bat Speed Metrics</h3>
        <ul>
            <li><strong>Player Average Bat Speed:</strong> {}</li>
            <li><strong>Top 10% Bat Speed:</strong> {}</li>
            <li><strong>Average Attack Angle (Top 10% Bat Speed Swings):</strong> {}</li>
            <li><strong>Average Time to Contact:</strong> {}</li>
        </ul>
        
        <h3>Exit Velocity Metrics</h3>
        <ul>
            <li><strong>Average Exit Velocity:</strong> {}</li>
            <li><strong>Top 8% Exit Velocity:</strong> {}</li>
            <li><strong>Average Launch Angle (On Top 8% Exit Velocity Swings):</strong> {}</li>
            <li><strong>Total Average Launch Angle (Avg LA):</strong> {}</li>
            <li><strong>Average Distance (8% swings):</strong> {}</li>
        </ul>
        
        <p>Best Regards,<br>Your Baseball Metrics Analyzer</p>
    </body>
    </html>
    """.format(
        bat_speed_metrics.replace('### ', '').split("- ")[1],
        bat_speed_metrics.replace('### ', '').split("- ")[2],
        bat_speed_metrics.replace('### ', '').split("- ")[3],
        bat_speed_metrics.replace('### ', '').split("- ")[4],
        exit_velocity_metrics.replace('### ', '').split("- ")[1],
        exit_velocity_metrics.replace('### ', '').split("- ")[2],
        exit_velocity_metrics.replace('### ', '').split("- ")[3],
        exit_velocity_metrics.replace('### ', '').split("- ")[4],
        exit_velocity_metrics.replace('### ', '').split("- ")[5]
    )

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
        send_email_report(recipient_email, bat_speed_metrics, exit_velocity_metrics)
    else:
        st.error("Please enter a valid email address.")
