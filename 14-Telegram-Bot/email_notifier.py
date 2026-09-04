#!/usr/bin/env python3
"""
DevOps Job Tracker — Email Progress Notifier
================================================
Usage:
  python email_notifier.py --daily   → Full morning summary
  python email_notifier.py --hook    → Short commit notification
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
GMAIL_ADDRESS      = os.environ.get("GMAIL_ADDRESS")       # sender display address
BREVO_LOGIN        = os.environ.get("BREVO_LOGIN")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")  # Brevo SMTP key

if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
    try:
        from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, BREVO_LOGIN
    except ImportError:
        pass

if not BREVO_LOGIN:
    BREVO_LOGIN = "b7e208001@smtp-brevo.com"

if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
    print("ERROR: GMAIL credentials not found.")
    sys.exit(1)

# ── Beautiful HTML Builder ───────────────────────────────────────────────────
def build_beautiful_html(title, stats, mode="daily", commit_msg=""):
    vid_pct = round(stats.get("videos_watched", 0) / stats.get("videos_total", 1) * 100, 1) if stats.get("videos_total") else 0
    cka_pct = round(stats.get("cka_done", 0) / stats.get("cka_total", 1) * 100, 1) if stats.get("cka_total") else 0

    vid_raw = stats.get("today_video", "No video schedulded")
    if vid_raw is None: vid_raw = "No video scheduled"
    vid_line = f"<a href='{stats.get('today_video_url', '#')}' style='color: #0ea5e9; font-weight: 600; text-decoration: none;'>{vid_raw}</a>" if stats.get("today_video_url") else vid_raw
    
    cka_raw = stats.get("today_cka", "No CKA lesson scheduled")
    if cka_raw is None: cka_raw = "No CKA lesson scheduled"
    cka_line = cka_raw

    html = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; padding: 20px; margin: 0;">
      <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
        
        <!-- Header Gradient -->
        <div style="background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%); padding: 35px 20px; text-align: center; color: white;">
          <h1 style="margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -0.5px;">{title}</h1>
        </div>
        
        <!-- Content Area -->
        <div style="padding: 30px;">
    """
    
    if mode == "test":
        html += f"""
          <div style="text-align: center; padding: 20px; background: #ecfdf5; border: 1px solid #10b981; border-radius: 8px; color: #065f46;">
            <strong>System validation successful!</strong><br>
            The DevOps Command Center securely authenticated with your SMTP relay and fully rendered this beautiful HTML payload.
          </div>
        """
    
    elif mode == "daily" and stats.get("daily_quote"):
        html += f"""
          <div style="font-style: italic; color: #475569; text-align: center; margin-bottom: 25px; padding: 15px; background: #f8fafc; border-left: 4px solid #818cf8; border-radius: 4px;">
            "{stats['daily_quote']}"
          </div>
        """
        
    if mode == "hook" and commit_msg:
        html += f"""
          <div style="margin-bottom: 25px;">
            <h3 style="color: #1e293b; font-size: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 12px;">💬 Commit Message</h3>
            <p style="color: #334155; font-family: 'JetBrains Mono', monospace; background: #f1f5f9; padding: 12px; border-radius: 6px; margin: 0; border: 1px solid #e2e8f0;">{commit_msg}</p>
          </div>
        """

    if mode != "test":
        html += f"""
          <!-- Progress -->
          <div style="margin-bottom: 30px;">
            <h3 style="color: #1e293b; font-size: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 12px;">📊 Active Progress</h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 15px;">
              <tr>
                <td style="padding: 10px 0; color: #475569; border-bottom: 1px solid #f1f5f9;">📺 DevOps Bootcamp</td>
                <td style="text-align: right; font-weight: 700; color: #0f172a; border-bottom: 1px solid #f1f5f9;">{stats.get('videos_watched',0)} / {stats.get('videos_total',0)} <span style="color: #0ea5e9;">({vid_pct}%)</span></td>
              </tr>
              <tr>
                <td style="padding: 10px 0; color: #475569;">☸️ CKA Certification</td>
                <td style="text-align: right; font-weight: 700; color: #0f172a;">{stats.get('cka_done',0)} / {stats.get('cka_total',0)} <span style="color: #0ea5e9;">({cka_pct}%)</span></td>
              </tr>
            </table>
          </div>
        """

    if mode in ["daily", "nightly"]:
        html += f"""
          <!-- Today Schedule -->
          <div style="margin-bottom: 30px;">
            <h3 style="color: #1e293b; font-size: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 12px;">📅 Output Required Today</h3>
            <ul style="list-style: none; padding: 0; margin: 0; font-size: 15px;">
              <li style="padding: 12px 15px; background: #fff; border-radius: 8px; margin-bottom: 10px; border: 1px solid #e2e8f0; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">📺 {vid_line}</li>
              <li style="padding: 12px 15px; background: #fff; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">☸️ {cka_line}</li>
            </ul>
          </div>
        """

    if mode == "daily" and stats.get("daily_prompt"):
        html += f"""
          <!-- AI & Interview -->
          <div style="margin-bottom: 25px;">
            <h3 style="color: #1e293b; font-size: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 12px;">🤖 Prompt Engineering</h3>
            <div style="background: #0f172a; color: #f8fafc; padding: 15px; border-radius: 8px; font-family: 'JetBrains Mono', monospace; font-size: 13px; line-height: 1.5; border-left: 4px solid #38bdf8;">
              {stats['daily_prompt'].replace('<b>', '<strong style="color: #38bdf8;">').replace('</b>', '</strong><br><br>').replace('<i>', '<span style="color: #94a3b8;">').replace('</i>', '</span>')}
            </div>
          </div>
          
          <div style="margin-bottom: 10px;">
            <h3 style="color: #1e293b; font-size: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 12px;">🎙️ Interview Scenario</h3>
            <div style="padding: 15px; background: #ecfdf5; border-left: 4px solid #10b981; border-radius: 8px; color: #064e3b; font-size: 14px; line-height: 1.6;">
              {stats['daily_interview'].replace('<b>', '<strong>').replace('</b>', '</strong><br>')}
            </div>
          </div>
        """

    html += f"""
        </div>
        <!-- Footer -->
        <div style="background: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
          <div style="margin-bottom: 10px;">
            <a href="https://imranshs08.github.io/job/" style="display: inline-block; background: #0ea5e9; color: white; text-decoration: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; font-size: 14px; margin: 0 5px;">View Dashboard</a>
            <a href="https://github.com/imranshs08/job" style="display: inline-block; background: #cbd5e1; color: #334155; text-decoration: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; font-size: 14px; margin: 0 5px;">GitHub Repo</a>
          </div>
          <p style="font-size: 12px; color: #94a3b8; margin: 10px 0 0 0;">Autonomously dispatched by DevOps Command Center</p>
        </div>
      </div>
    </body>
    </html>
    """
    return html

# ── Email sender ───────────────────────────────────────────────────────────
def send_email(subject: str, html_body: str) -> bool:
    msg = MIMEMultipart()
    msg['From'] = f"DevOps Command Center <{GMAIL_ADDRESS}>"
    msg['To'] = GMAIL_ADDRESS
    msg['Cc'] = "jamiaxpress@gmail.com"
    msg['Subject'] = subject
    msg.attach(MIMEText(html_body, 'html'))
    try:
        server = smtplib.SMTP('smtp-relay.brevo.com', 587)
        server.starttls()
        server.login(BREVO_LOGIN, GMAIL_APP_PASSWORD)
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
        html = build_beautiful_html("🚀 SMTP Handshake Successful", {}, mode="test")
        ok = send_email("✅ DevOps Notifier Working", html)
        print("✅ Test email sent!" if ok else "❌ Failed to send email.")
        return

    stats = telegram_notifier.parse_tracker()
    if not stats:
        print("ERROR: Could not read tracker data.")
        sys.exit(1)

    import subprocess
    commit_msg = "Progress updated"
    if mode == "--hook":
        try:
            raw_out = subprocess.check_output(["git", "log", "-1", "--pretty=%B"], cwd=r"c:\Job Tracker", shell=True)
            commit_msg = raw_out.decode("utf-8").strip()
        except: pass

    subject = "DevOps 2027 Progress"
    title = "DevOps Target"

    if mode == "--daily":
        subject = f"☀️ Daily Brief — {stats.get('today_str', '')}"
        title = f"Morning Strategy<br><span style='font-size: 16px; font-weight: 400;'>{stats.get('today_str', '')}</span>"
    elif mode == "--hook":
        subject = f"🔔 Commit Deployed — {stats.get('today_str', '')}"
        title = f"Codebase Updated"
    elif mode == "--nightly":
        subject = f"🌙 Nightly Status — {stats.get('today_str', '')}"
        title = f"Nightly Review<br><span style='font-size: 16px; font-weight: 400;'>{stats.get('today_str', '')}</span>"

    html = build_beautiful_html(title, stats, mode=mode.replace("--", ""), commit_msg=commit_msg)
    
    ok = send_email(subject, html)
    print("✅ Email Sent!" if ok else "❌ Failed to send Email.")

if __name__ == "__main__":
    main()
