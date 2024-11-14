import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email Configuration
email_address = "aadichadha@gmail.com"
email_password = "eeoi odag olix nnfc"  # Your app-specific password
smtp_server = "smtp.gmail.com"
smtp_port = 587

# Title and File Upload
st.title("Baseball Metrics Analyzer")
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

# Function to send an email
def send_email(recipient_email, subject, body):
    try:
        # Set up the email
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(email_address, email_password)
            server.send_message(msg)
            st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Function to get the date range from the data
def get_date_range(df):
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")  # Convert to datetime
        min_date = df["Date"].min().strftime("%Y-%m-%d")
        max_date = df["Date"].max().strftime("%Y-%m-%d")
        return min_date, max_date
    else:
        return None, None

if uploaded_file:
    # Read the CSV into a DataFrame
    df = pd.read_csv(uploaded_file)

    # Check for specific column titles
    has_bat_speed = "Bat Speed (mph)" in df.columns
    has_exit_velocity = "Velo" in df.columns

    # Get the date range
    min_date, max_date = get_date_range(df)
    date_range = f"{min_date} to {max_date}" if min_date and max_date else "Date range not available"

    # Initialize metrics
    report_body = f"<h2>Baseball Metrics Report</h2>"
    report_body += f"<p><strong>Date Range:</strong> {date_range}</p>"
    report_body += f"<p><strong>File:</strong> {uploaded_file.name}</p>"

    if has_bat_speed:
        # Calculate Bat Speed Metrics
        player_avg_bat_speed = df["Bat Speed (mph)"].mean()
        try:
            top_10_percent_bat_speed = df["Bat Speed (mph)"].quantile(0.90)
            top_10_percent_swings = df[df["Bat Speed (mph)"] >= top_10_percent_bat_speed]

            if not top_10_percent_swings.empty and "Attack Angle" in df.columns:
                avg_attack_angle_top_10 = top_10_percent_swings["Attack Angle"].mean()
            else:
                avg_attack_angle_top_10 = None

            report_body += f"<h3>Bat Speed Metrics</h3>"
            report_body += f"<p>Player Average Bat Speed: {player_avg_bat_speed:.2f} mph</p>"
            report_body += f"<p>Top 10% Bat Speed: {top_10_percent_bat_speed:.2f} mph</p>"
            if avg_attack_angle_top_10 is not None:
                report_body += f"<p>Average Attack Angle (Top 10% Bat Speed Swings): {avg_attack_angle_top_10:.2f}°</p>"
            else:
                report_body += "<p><em>Not enough data to calculate the average attack angle for the top 10% bat speed swings.</em></p>"
        except ValueError:
            report_body += "<p><em>Not enough data in this session to calculate the top 10% bat speed.</em></p>"

        if "Time to Contact" in df.columns:
            avg_time_to_contact = df["Time to Contact"].mean()
            report_body += f"<p>Average Time to Contact: {avg_time_to_contact:.2f} seconds</p>"
        else:
            report_body += "<p><em>Time to Contact data is not available.</em></p>"

    if has_exit_velocity:
        player_avg_exit_velocity = df["Velo"].mean()
        try:
            top_8_percent_exit_velocity = df["Velo"].quantile(0.92)
            top_8_percent_swings = df[df["Velo"] >= top_8_percent_exit_velocity]

            if not top_8_percent_swings.empty:
                avg_launch_angle_top_8 = top_8_percent_swings["Launch Angle"].mean() if "Launch Angle" in df.columns else None
                avg_distance_top_8 = top_8_percent_swings["Distance"].mean() if "Distance" in df.columns else None

                report_body += f"<h3>Exit Velocity Metrics</h3>"
                report_body += f"<p>Player Average Exit Velocity: {player_avg_exit_velocity:.2f} mph</p>"
                report_body += f"<p>Top 8% Exit Velocity: {top_8_percent_exit_velocity:.2f} mph</p>"
                if avg_launch_angle_top_8 is not None:
                    report_body += f"<p>Average Launch Angle (Top 8% Exit Velocity Swings): {avg_launch_angle_top_8:.2f}°</p>"
                else:
                    report_body += "<p><em>Launch Angle data is not available for the top 8% exit velocity swings.</em></p>"

                if avg_distance_top_8 is not None:
                    report_body += f"<p>Average Distance (Top 8% Exit Velocity Swings): {avg_distance_top_8:.2f} ft</p>"
                else:
                    report_body += "<p><em>Distance data is not available for the top 8% exit velocity swings.</em></p>"
            else:
                report_body += "<p><em>Not enough data to calculate the average launch angle and distance for the top 8% exit velocity swings.</em></p>"
        except ValueError:
            report_body += "<p><em>Not enough data in this session to calculate the top 8% exit velocity.</em></p>"

    # Display the DataFrame for reference
    st.write("### Data Overview")
    st.write(f"**Date Range:** {date_range}")
    st.dataframe(df)

    # Option to send the report via email
    st.write("### Email the Report")
    recipient_email = st.text_input("Enter the recipient's email address:")
    if st.button("Send Report"):
        if recipient_email:
            send_email(recipient_email, "Baseball Metrics Report", report_body)
        else:
            st.error("Please enter a valid email address.")
