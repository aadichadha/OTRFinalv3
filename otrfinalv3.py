import streamlit as st
import pandas as pd
import numpy as np
import smtplib
import base64
from io import BytesIO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication  # For attaching PDFs
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile

# ---------------------------
# STREAMLIT UI
# ---------------------------
st.title("OTR Baseball Metrics Analyzer (PDF Report)")

bat_speed_file = st.file_uploader("Upload Bat Speed File", type="csv")
exit_velocity_file = st.file_uploader("Upload Exit Velocity File", type="csv")

bat_speed_level = st.selectbox(
    "Select Player Level for Bat Speed",
    ["Youth", "High School", "College", "Indy", "Affiliate"]
)

exit_velocity_level = st.selectbox(
    "Select Player Level for Exit Velocity",
    ["10u", "12u", "14u", "JV/16u", "Var/18u", "College", "Indy", "Affiliate"]
)

# Email config
email_address = "otrdatatrack@gmail.com"
email_password = "YOUR_APP_OR_SMTP_PASSWORD_HERE"
smtp_server = "smtp.gmail.com"
smtp_port = 587

# Player info
player_name = st.text_input("Enter Player Name")
date_range = st.text_input("Enter Date Range")

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
    for "Average" (useful for EV).
    """
    if special_metric:
        # For EV: "Average" if metric in [benchmark-3, benchmark]
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

# Variables to store final metrics
bat_speed_text = None
exit_velocity_text = None
strike_zone_fig = None

# -------------------------
# Process Bat Speed File
# -------------------------
if bat_speed_file:
    df_bat_speed = pd.read_csv(bat_speed_file, skiprows=8)
    bat_speed_data = pd.to_numeric(df_bat_speed.iloc[:, 7], errors='coerce')   # Column H
    attack_angle_data = pd.to_numeric(df_bat_speed.iloc[:, 10], errors='coerce')  # Column K
    time_to_contact_data = pd.to_numeric(df_bat_speed.iloc[:, 15], errors='coerce')  # Column P?

    player_avg_bat_speed = bat_speed_data.mean()
    top_10_percent_bat_speed = bat_speed_data.quantile(0.90)
    avg_attack_angle_top_10 = attack_angle_data[bat_speed_data >= top_10_percent_bat_speed].mean()
    avg_time_to_contact = time_to_contact_data.mean()

    # Benchmarks
    b_bench = benchmarks[bat_speed_level]
    bat_speed_benchmark = b_bench["Avg BatSpeed"]
    top_90_benchmark = b_bench["90th% BatSpeed"]
    time_to_contact_benchmark = b_bench["Avg TimeToContact"]
    attack_angle_benchmark = b_bench["Avg AttackAngle"]

    # Build a text summary
    bat_speed_text = (
        f"### Bat Speed Metrics\n"
        f"Player Avg Bat Speed: {player_avg_bat_speed:.2f} mph (Benchmark: {bat_speed_benchmark})\n"
        f"  - Grade: {evaluate_performance(player_avg_bat_speed, bat_speed_benchmark)}\n\n"
        f"Top 10% Bat Speed: {top_10_percent_bat_speed:.2f} mph (Benchmark: {top_90_benchmark})\n"
        f"  - Grade: {evaluate_performance(top_10_percent_bat_speed, top_90_benchmark)}\n\n"
        f"Avg Attack Angle (Top 10% Swings): {avg_attack_angle_top_10:.2f}° (Benchmark: {attack_angle_benchmark}°)\n"
        f"  - Grade: {evaluate_performance(avg_attack_angle_top_10, attack_angle_benchmark)}\n\n"
        f"Avg Time to Contact: {avg_time_to_contact:.3f} sec (Benchmark: {time_to_contact_benchmark} sec)\n"
        f"  - Grade: {evaluate_performance(avg_time_to_contact, time_to_contact_benchmark, lower_is_better=True)}\n"
    )

# ---------------------------
# Process Exit Velocity File
# ---------------------------
if exit_velocity_file:
    df_exit_velocity = pd.read_csv(exit_velocity_file)
    if len(df_exit_velocity.columns) > 9:
        strike_zone_data = df_exit_velocity.iloc[:, 5]  # F
        exit_velocity_data = pd.to_numeric(df_exit_velocity.iloc[:, 7], errors='coerce')  # H
        launch_angle_data = pd.to_numeric(df_exit_velocity.iloc[:, 8], errors='coerce')   # I
        distance_data = pd.to_numeric(df_exit_velocity.iloc[:, 9], errors='coerce')       # J

        non_zero_ev_rows = exit_velocity_data[exit_velocity_data > 0]
        if not non_zero_ev_rows.empty:
            exit_velocity_avg = non_zero_ev_rows.mean()
            top_8_percent_ev = non_zero_ev_rows.quantile(0.92)

            top_8_mask = exit_velocity_data >= top_8_percent_ev
            avg_launch_angle_top_8 = launch_angle_data[top_8_mask].mean()
            avg_distance_top_8 = distance_data[top_8_mask].mean()
            total_avg_launch_angle = launch_angle_data[launch_angle_data > 0].mean()

            # Benchmarks
            e_bench = benchmarks[exit_velocity_level]
            ev_benchmark = e_bench["Avg EV"]
            top_8_benchmark = e_bench["Top 8th EV"]
            la_benchmark = e_bench["Avg LA"]
            hhb_la_benchmark = e_bench["HHB LA"]

            exit_velocity_text = (
                f"### Exit Velocity Metrics\n"
                f"Average EV (non-zero): {exit_velocity_avg:.2f} mph (Benchmark: {ev_benchmark})\n"
                f"  - Grade: {evaluate_performance(exit_velocity_avg, ev_benchmark, special_metric=True)}\n\n"
                f"Top 8% EV: {top_8_percent_ev:.2f} mph (Benchmark: {top_8_benchmark})\n"
                f"  - Grade: {evaluate_performance(top_8_percent_ev, top_8_benchmark, special_metric=True)}\n\n"
                f"Avg LA (top 8% EV): {avg_launch_angle_top_8:.2f}° (Benchmark: {hhb_la_benchmark}°)\n"
                f"  - Grade: {evaluate_performance(avg_launch_angle_top_8, hhb_la_benchmark)}\n\n"
                f"Total Avg LA: {total_avg_launch_angle:.2f}° (Benchmark: {la_benchmark}°)\n"
                f"  - Grade: {evaluate_performance(total_avg_launch_angle, la_benchmark)}\n\n"
                f"Average Distance (top 8% EV): {avg_distance_top_8:.2f} ft\n"
            )

            # ---- Build Strike-Zone Plot ----
            top_8_df = df_exit_velocity[top_8_mask].copy()
            top_8_df["StrikeZone"] = top_8_df.iloc[:, 5]
            zone_counts = top_8_df["StrikeZone"].value_counts()

            zone_layout = [
                [10, None, 11],
                [1,  2,  3],
                [4,  5,  6],
                [7,  8,  9],
                [12, None, 13]
            ]
            max_count = zone_counts.max() if not zone_counts.empty else 0

            fig, ax = plt.subplots(figsize=(3,5))
            ax.axis('off')
            cmap = plt.get_cmap('Reds')
            cell_w = 1.0
            cell_h = 1.0

            for r, row_zones in enumerate(zone_layout):
                for c, z in enumerate(row_zones):
                    x = c * cell_w
                    y = (len(zone_layout)-1 - r) * cell_h
                    if z is not None:
                        count = zone_counts.get(z, 0)
                        norm_val = (count / max_count) if max_count > 0 else 0
                        color = cmap(norm_val*0.8 + 0.2) if norm_val > 0 else (1,1,1,1)
                        rect = plt.Rectangle((x,y), cell_w, cell_h, facecolor=color, edgecolor='black')
                        ax.add_patch(rect)
                        ax.text(x+0.5*cell_w, y+0.5*cell_h, str(z),
                                ha='center', va='center', fontsize=10)
                    else:
                        rect = plt.Rectangle((x,y), cell_w, cell_h, facecolor='white', edgecolor='black')
                        ax.add_patch(rect)
            ax.set_xlim(0, 3*cell_w)
            ax.set_ylim(0, 5*cell_h)
            strike_zone_fig = fig  # We'll store the figure for the PDF
        else:
            st.error("No valid (non-zero) exit velocity data found.")
    else:
        st.error("The uploaded file does not have the required columns for EV.")

# Display in Streamlit
st.write("## Calculated Metrics")
if bat_speed_text:
    st.markdown(bat_speed_text)
if exit_velocity_text:
    st.markdown(exit_velocity_text)
    if strike_zone_fig:
        buf = BytesIO()
        strike_zone_fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        data_uri = base64.b64encode(buf.read()).decode('utf-8')
        st.markdown(
            f"<h3>Strike Zone Heatmap</h3><img src='data:image/png;base64,{data_uri}'/>",
            unsafe_allow_html=True
        )

# --------------------------
# GENERATE PDF
# --------------------------
def generate_pdf_report(
    player_name,
    date_range,
    bat_speed_level,
    exit_velocity_level,
    bat_speed_text,
    exit_velocity_text,
    strike_zone_fig
) -> bytes:
    """
    Creates a PDF file in memory with:
    1) Title, Player info
    2) Bat Speed & EV metrics text
    3) The strike-zone chart if available
    Returns the PDF bytes.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    # Title
    pdf.cell(0, 10, "OTR Baseball Metrics Report", ln=1, align='C')
    pdf.ln(5)

    # Player info
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 6, f"Player Name: {player_name}", ln=1)
    pdf.cell(0, 6, f"Date Range: {date_range}", ln=1)
    pdf.cell(0, 6, f"Bat Speed Level: {bat_speed_level}", ln=1)
    pdf.cell(0, 6, f"Exit Velocity Level: {exit_velocity_level}", ln=1)
    pdf.ln(5)

    # Bat Speed text
    if bat_speed_text:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, "Bat Speed Metrics", ln=1)
        pdf.set_font("Arial", "", 12)
        for line in bat_speed_text.split('\n'):
            pdf.multi_cell(0, 6, line)
        pdf.ln(3)

    # EV text
    if exit_velocity_text:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, "Exit Velocity Metrics", ln=1)
        pdf.set_font("Arial", "", 12)
        for line in exit_velocity_text.split('\n'):
            pdf.multi_cell(0, 6, line)
        pdf.ln(3)

    # Strike-zone chart
    if strike_zone_fig:
        # Save the figure temporarily
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            strike_zone_fig.savefig(tmp.name, format='png', bbox_inches='tight')
            tmp.flush()
            # Insert the image into PDF
            pdf.add_page()  # new page for the chart
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 8, "Strike Zone Heatmap", ln=1)
            pdf.image(tmp.name, x=10, y=30, w=100)  # adjust as you like

    # Return PDF as bytes
    out_bytes = BytesIO()
    pdf.output(out_bytes, 'F')
    return out_bytes.getvalue()

# --------------------------
# SEND EMAIL WITH PDF
# --------------------------
def send_email_with_pdf(recipient_email, pdf_bytes):
    """
    Sends an email with the PDF (in pdf_bytes) attached.
    """
    msg = MIMEMultipart()
    msg["From"] = email_address
    msg["To"] = recipient_email
    msg["Subject"] = "OTR Baseball Metrics PDF Report"

    # Body text
    body = """Hello,

Please find attached your OTR Baseball metrics report in PDF format.

Best,
OTR Baseball
"""
    msg.attach(MIMEText(body, "plain"))

    # Attach PDF
    attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
    attachment.add_header('Content-Disposition', 'attachment', filename="OTR_Report.pdf")
    msg.attach(attachment)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg)
        st.success("Report (PDF) sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# --------------------------
# Streamlit: Button to Send
# --------------------------
recipient_email = st.text_input("Enter Recipient Email")

if st.button("Generate & Send PDF"):
    if not recipient_email:
        st.error("Please enter a valid email address.")
    else:
        # Build the PDF
        pdf_data = generate_pdf_report(
            player_name,
            date_range,
            bat_speed_level,
            exit_velocity_level,
            bat_speed_text,
            exit_velocity_text,
            strike_zone_fig
        )
        # Send it
        send_email_with_pdf(recipient_email, pdf_data)
