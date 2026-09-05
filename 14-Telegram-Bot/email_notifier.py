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
    labs_pct = round(stats.get("labs_done", 0) / stats.get("labs_total", 1) * 100, 1) if stats.get("labs_total") else 0

    vid_raw = stats.get("today_video", "No video schedulded")
    if vid_raw is None: vid_raw = "No video scheduled"
    vid_line = f"<a href='{stats.get('today_video_url', '#')}' style='color: #0ea5e9; font-weight: 600; text-decoration: none;'>{vid_raw}</a>" if stats.get("today_video_url") else vid_raw
    
    cka_raw = stats.get("today_cka", "No CKA lesson scheduled")
    if cka_raw is None: cka_raw = "No CKA lesson scheduled"
    cka_line = cka_raw

    html = f"""
    <html>
    <head>
      <style>
        .badge {{ display: inline-block; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 700; background: #e0f2fe; color: #0284c7; }}
        .card {{ background: #ffffff; border-radius: 12px; padding: 20px; border: 1px solid #e2e8f0; margin-bottom: 20px; }}
        .card-title {{ font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; margin: 0 0 15px 0; font-weight: 700; }}
      </style>
    </head>
    <body style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8fafc; padding: 20px 10px; margin: 0; line-height: 1.6; color: #334155;">
      <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
        
        <!-- Header -->
        <div style="background: #ffffff; padding: 30px 30px 20px 30px; text-align: left; border-bottom: 1px solid #f1f5f9;">
          <h1 style="margin: 0; font-size: 24px; font-weight: 800; color: #0f172a;">{title}</h1>
          <p style="margin: 5px 0 0 0; font-size: 15px; color: #64748b;">Your specialized daily DevOps update.</p>
        </div>
        
        <!-- Content Area -->
        <div style="padding: 30px; background: #f8fafc;">
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
          <div class="card" style="background-color: #f1f5f9;">
            <h3 class="card-title">💬 Commit Deployed</h3>
            <p style="color: #475569; font-family: 'JetBrains Mono', Courier, monospace; background: #ffffff; padding: 12px; border-radius: 6px; margin: 0; border: 1px solid #e2e8f0; font-size: 13px;">{commit_msg}</p>
          </div>
        """

    if mode != "test":
        html += f"""
          <!-- Progress -->
          <div class="card">
            <h3 class="card-title">📊 Operations Overview</h3>
            <div style="display: flex; flex-direction: column; gap: 12px; font-size: 14px;">
              <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px;">
                <span style="color: #475569; font-weight: 500;">📺 DevOps Bootcamp</span>
                <span style="font-weight: 600; color: #0f172a;">{stats.get('videos_watched',0)} / {stats.get('videos_total',0)} <span class="badge" style="margin-left: 8px;">{vid_pct}%</span></span>
              </div>
              <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px;">
                <span style="color: #475569; font-weight: 500;">☸️ CKA Certification</span>
                <span style="font-weight: 600; color: #0f172a;">{stats.get('cka_done',0)} / {stats.get('cka_total',0)} <span class="badge" style="background:#fce7f3; color:#be185d; margin-left: 8px;">{cka_pct}%</span></span>
              </div>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #475569; font-weight: 500;">🧪 Validation Labs</span>
                <span style="font-weight: 600; color: #0f172a;">{stats.get('labs_done',0)} / {stats.get('labs_total',0)} <span class="badge" style="background:#dcfce7; color:#166534; margin-left: 8px;">{labs_pct}%</span></span>
              </div>
            </div>
          </div>
        """

    if mode in ["daily", "nightly"]:
        html += f"""
          <!-- Today Schedule -->
          <div class="card">
            <h3 class="card-title">📅 Queue for Today</h3>
            <div style="padding: 12px 0; border-bottom: 1px solid #f1f5f9; display: flex; align-items: flex-start;">
              <span style="margin-right: 12px; font-size: 16px;">📺</span>
              <span style="font-size: 15px; color: #334155; line-height: 1.4;">{vid_line}</span>
            </div>
            <div style="padding: 12px 0; border-bottom: 1px solid #f1f5f9; display: flex; align-items: flex-start;">
              <span style="margin-right: 12px; font-size: 16px;">☸️</span>
              <span style="font-size: 15px; color: #334155; line-height: 1.4;">{cka_line}</span>
            </div>
            <div style="padding: 12px 0; display: flex; align-items: flex-start;">
              <span style="margin-right: 12px; font-size: 16px;">🧪</span>
              <span style="font-size: 15px; color: #334155; line-height: 1.4;"><strong>Next Lab:</strong> {stats.get('next_lab', 'All done!')}</span>
            </div>
          </div>
        """

    if mode == "daily" and stats.get("daily_prompt"):
        html += f"""
          <!-- AI & Interview -->
          <div class="card" style="background-color: #f0f9ff; border-color: #bae6fd;">
            <h3 class="card-title" style="color: #0369a1;">🤖 Prompt Engineering</h3>
            <div style="color: #0c4a6e; font-size: 14.5px; line-height: 1.6;">
              {stats['daily_prompt'].replace('<b>', '<strong style="color: #0284c7; display:block; margin-bottom: 8px;">').replace('</b>', '</strong>').replace('<i>', '<span style="color: #0369a1;">').replace('</i>', '</span>')}
            </div>
          </div>
          
          <div class="card" style="background-color: #f0fdf4; border-color: #bbf7d0; margin-bottom: 0;">
            <h3 class="card-title" style="color: #15803d;">🎙️ Interview Scenario</h3>
            <div style="color: #166534; font-size: 14.5px; line-height: 1.6;">
              {stats['daily_interview'].replace('<b>', '<strong style="display:block; margin-bottom: 8px;">').replace('</b>', '</strong>')}
            </div>
          </div>
        """

    html += f"""
          <!-- Signature -->
          <div style="margin-top: 35px; color: #334155; font-size: 15px; line-height: 1.5;">
            Keep pushing forward, <br><br>
            <strong>Imran</strong><br>
            <span style="color: #64748b; font-size: 13px;">Future DevOps & Platform Engineer</span>
          </div>
        </div>
        <!-- Footer -->
        <div style="background: #ffffff; padding: 25px; text-align: center; border-top: 1px solid #f1f5f9;">
          <div style="margin-bottom: 15px;">
            <a href="https://imranshs08.github.io/job/" style="display: inline-block; background: #0f172a; color: white; text-decoration: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; font-size: 13px; margin: 0 6px;">View Dashboard</a>
            <a href="https://github.com/imranshs08/job" style="display: inline-block; background: #f1f5f9; color: #334155; text-decoration: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; font-size: 13px; margin: 0 6px; border: 1px solid #e2e8f0;">GitHub Repo</a>
          </div>
          <p style="font-size: 12px; color: #94a3b8; margin: 0;">Autonomously dispatched by DevOps Command Center</p>
        </div>
      </div>
      <br>
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
