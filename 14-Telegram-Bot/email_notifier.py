#!/usr/bin/env python3
"""
DevOps Job Tracker — Email Progress Notifier
================================================
Usage:
  python email_notifier.py --daily   → Full morning summary (run via Task Scheduler / GitHub Actions)
  python email_notifier.py --hook    → Short commit notification (run via git hook)
  python email_notifier.py --nightly → Nightly status check
  python email_notifier.py --test    → Test SMTP connection
"""

import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import telegram_notifier

# ── Load config ──────────────────────────────────────────────────────────────
GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
    try:
        from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD
    except ImportError:
        pass

if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
    print("ERROR: GMAIL credentials not found in env vars or config.py.")
    print("Add GMAIL_ADDRESS and GMAIL_APP_PASSWORD to 14-Telegram-Bot/config.py")
    sys.exit(1)

# ── Email sender ───────────────────────────────────────────────────────────
def send_email(subject: str, html_body: str) -> bool:
    """Send an HTML email via Gmail SMTP. Returns True on success."""
    msg = MIMEMultipart()
    msg['From'] = GMAIL_ADDRESS
    msg['To'] = GMAIL_ADDRESS
    msg['Subject'] = subject

    # Wrap the Telegram HTML snippet in a proper email layout
    html_body_br = html_body.replace('\n', '<br>')
    full_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; background-color: #fafafa;">
          {html_body_br}
        </div>
      </body>
    </html>
    """
    
    msg.attach(MIMEText(full_html, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Email send failed: {e}")
        return False

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--daily"

    if mode == "--test":
        ok = send_email("✅ Email Notifier Working", "<b>System validation successful!</b><br>The DevOps Command Center successfully authenticated to your SMTP relay.")
        print("✅ Test email sent!" if ok else "❌ Failed to send email. Check credentials.")
        return

    stats = telegram_notifier.parse_tracker()
    if not stats:
        print("ERROR: Could not read tracker data.")
        sys.exit(1)

    subject = "DevOps 2027 Progress Update"
    msg_html = ""

    if mode == "--daily":
        msg_html = telegram_notifier.build_daily_message(stats)
        subject = f"☀️ DevOps Daily Brief — {stats['today_str']}"
    elif mode == "--hook":
        msg_html = telegram_notifier.build_hook_message(stats)
        subject = f"🔔 Progress Committed — {stats['today_str']}"
    elif mode == "--nightly":
        msg_html = telegram_notifier.build_nightly_message(stats)
        subject = f"🌙 Nightly Progress Check — {stats['today_str']}"
    else:
        print(f"Unknown mode: {mode}. Use --daily, --nightly, --hook, or --test")
        sys.exit(1)

    ok = send_email(subject, msg_html)
    print("✅ Email Sent!" if ok else "❌ Failed to send Email.")

if __name__ == "__main__":
    main()
