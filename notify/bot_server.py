#!/usr/bin/env python3
"""
Serverless Telegram Webhook for GitHub Progress Tracker
Designed to be hosted on Render.com Web Services (Free Tier)
"""
import os
import re
import json
import base64
from datetime import datetime
from flask import Flask, request, jsonify
from github import Github

app = Flask(__name__)

# Load secrets from Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "imranshs08/job"  # Update if repo name changes
FILE_PATH = "03-Progress-Tracker/progress-tracker.md"

def send_telegram(text: str):
    import urllib.request
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"Failed to reply to Telegram: {e}")

def update_tracker_on_github() -> str:
    """Uses PyGithub to fetch, modify, and commit progress-tracker.md."""
    if not GITHUB_TOKEN:
        return "❌ Error: GITHUB_TOKEN not set on server."
    
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        
        # Get the file contents
        file_content = repo.get_contents(FILE_PATH, ref="main")
        content = base64.b64decode(file_content.content).decode("utf-8")
        
        # Identify today's date lines (Aug 21 style)
        today = datetime.today()
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        today_vid_str = f"{months[today.month-1]} {today.day}"
        today_cert_str = f"{months[today.month-1]} {today.day:02d}, {today.year}"
        
        # We need to replace ☐ with ✅ on lines containing today's date
        # It's tricky to do general regex replacement without breaking other lines.
        # Let's split by lines, check if it contains today's date and ☐, and replace.
        lines = content.split('\n')
        modified = False
        new_lines = []
        for line in lines:
            if (today_vid_str in line or today_cert_str in line) and "☐" in line:
                line = line.replace("☐", "✅")
                modified = True
            new_lines.append(line)
            
        if not modified:
            return "⚠️ Everything for today is already marked as ✅! Nothing to commit."
            
        new_content = "\n".join(new_lines)
        
        # Commit back to GitHub
        commit_message = f"progress: mark {today_vid_str} tasks complete via Telegram Bot"
        repo.update_file(
            file_content.path,
            commit_message,
            new_content,
            file_content.sha,
            branch="main"
        )
        
        return f"🎉 Success! Marked today's lessons as ✅ and committed to GitHub."
        
    except Exception as e:
        return f"❌ GitHub API Error: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "DevOps Bot is running!", 200
        
    data = request.json
    if not data or "message" not in data:
        return jsonify({"status": "no message"}), 200
        
    msg = data["message"]
    chat_id = str(msg.get("chat", {}).get("id"))
    text = msg.get("text", "").strip().lower()
    
    # Authorized user check
    if chat_id != str(TELEGRAM_CHAT_ID):
        print(f"Unauthorized access attempt from chat_id {chat_id}")
        return jsonify({"status": "unauthorized"}), 200
        
    if text in ["/done", "done", "mark done"]:
        send_telegram("⏳ Processing... Fetching repository from GitHub...")
        result_msg = update_tracker_on_github()
        send_telegram(result_msg)
    else:
        # Ignore other messages or provide help
        if text.startswith("/"):
            send_telegram("Available commands:\n/done - Mark today's tasks as ✅ on GitHub")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # For Render.com, we configure the port from env
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
