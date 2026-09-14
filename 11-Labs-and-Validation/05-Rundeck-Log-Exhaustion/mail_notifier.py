#!/usr/bin/env python3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import socket
import os

# --- ENTERPRISE SMTP SECRETS ---
SMTP_SERVER = "<YOUR_SMTP_SERVER_URL>"
SMTP_PORT = 587
SENDER = "<YOUR_SENDER_EMAIL@DOMAIN.COM>"
# Pulls standard credential from environments so it's not hardcoded in the script
PASSWORD = os.environ.get("GMAIL_APP_PASSWORD") 
RECIPIENT = "<YOUR_RECIPIENT_EMAIL@DOMAIN.COM>" # Adjust for real alerts

def send_alert(disk_usage):
    if not PASSWORD:
        print("[-] EMAIL FAILED: SMTP password not found in GMAIL_APP_PASSWORD env var.")
        return

    msg = MIMEMultipart("alternative")
    msg['Subject'] = f"🚨 SEV-1: /var Disk Exhaustion Warning ({disk_usage}%)"
    msg['From'] = SENDER
    msg['To'] = RECIPIENT

    html = f"""
    <html>
      <body style="font-family: Arial; padding: 20px; background-color: #f7f7f7;">
        <div style="background-color: white; padding: 30px; border-radius: 10px; border-top: 5px solid #d32f2f;">
            <h2 style="color: #d32f2f; margin-top:0;">🔥 Automated Infrastructure Alert</h2>
            <p>The disk volume on bare-metal server <b>{socket.gethostname()}</b> has critically exceeded the 80% capacity threshold.</p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px; margin-bottom: 20px;">
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 10px; font-weight: bold;">Threshold:</td>
                    <td style="padding: 10px; color: #d32f2f;">> 80%</td>
                </tr>
                <tr>
                    <td style="padding: 10px; font-weight: bold;">Current Usage:</td>
                    <td style="padding: 10px; font-weight: bold; color: orange;">{disk_usage}%</td>
                </tr>
            </table>
            <p style="color: #555;"><i>SRE Script `disk_monitor.sh` is now initiating automated emergency log rotation and compression to restore stability...</i></p>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(html, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER, PASSWORD)
        server.sendmail(SENDER, RECIPIENT, msg.as_string())
        server.quit()
        print("[SMTP] Emergency email successfully dispatched to PagerDuty/SRE team.")
    except Exception as e:
        print(f"[SMTP] EMAIL FAILED: {e}")

if __name__ == "__main__":
    import sys
    usage_val = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    send_alert(usage_val)
