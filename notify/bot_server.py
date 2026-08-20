#!/usr/bin/env python3
"""
Serverless Telegram Webhook for GitHub Progress Tracker (Render.com)
Added commands: /done, /interview, /prompt, /status, /log
"""
import os
import re
import json
import base64
import random
from datetime import datetime, date
from flask import Flask, request, jsonify
from github import Github
import google.generativeai as genai

app = Flask(__name__)

# Load secrets from Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

REPO_NAME = "imranshs08/job"
TRACKER_PATH = "03-Progress-Tracker/progress-tracker.md"
DATA_PATH = "data.js"
JOURNAL_PATH = "04-Notes/war-journal.md"

CKA_EXAM_DATE = date(2027, 1, 1)
AZ_EXAM_DATE  = date(2027, 1, 15)
TOTAL_VIDEOS  = 158

FOOTER = "\n\n🌐 <a href='https://imranshs08.github.io/job/'>Dashboard</a> • 🐙 <a href='https://github.com/imranshs08/job'>Repository</a>\n👨‍💻 <i>Built by Imran</i>"

def send_telegram(text: str, reply_markup: dict = None, parse_mode: str = "HTML"):
    import urllib.request
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload_dict = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True
    }
    if parse_mode:
        payload_dict["parse_mode"] = parse_mode
    if reply_markup:
        payload_dict["reply_markup"] = reply_markup
        
    payload = json.dumps(payload_dict).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"Failed to reply to Telegram: {e}")

def get_repo():
    if not GITHUB_TOKEN:
        raise Exception("GITHUB_TOKEN not set on server.")
    g = Github(GITHUB_TOKEN)
    return g.get_repo(REPO_NAME)

def get_file_content(repo, path: str) -> str:
    file_content = repo.get_contents(path, ref="main")
    return base64.b64decode(file_content.content).decode("utf-8"), file_content

def command_done() -> str:
    try:
        repo = get_repo()
        content, file_m = get_file_content(repo, TRACKER_PATH)
        
        today = datetime.today()
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        today_vid_str = f"{months[today.month-1]} {today.day}"
        today_cert_str = f"{months[today.month-1]} {today.day:02d}, {today.year}"
        
        lines = content.split('\n')
        modified = False
        new_lines = []
        for line in lines:
            if (today_vid_str in line or today_cert_str in line) and "☐" in line:
                line = line.replace("☐", "✅")
                modified = True
            new_lines.append(line)
            
        if not modified:
            return "⚠️ Everything for today is already marked as ✅! Nothing to commit." + FOOTER
            
        commit_msg = f"progress: mark {today_vid_str} tasks complete via Telegram Bot"
        repo.update_file(
            file_m.path,
            commit_msg,
            "\n".join(new_lines),
            file_m.sha,
            branch="main"
        )
        return f"🎉 Success! Marked today's lessons as ✅ and committed to GitHub.\n\n💬 <b>Commit:</b> <i>{commit_msg}</i>" + FOOTER
    except Exception as e:
        return f"❌ GitHub API Error: {str(e)}" + FOOTER

def command_undo() -> str:
    try:
        repo = get_repo()
        content, file_m = get_file_content(repo, TRACKER_PATH)
        
        today = datetime.today()
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        today_vid_str = f"{months[today.month-1]} {today.day}"
        today_cert_str = f"{months[today.month-1]} {today.day:02d}, {today.year}"
        
        lines = content.split('\n')
        modified = False
        new_lines = []
        for line in lines:
            if (today_vid_str in line or today_cert_str in line) and "✅" in line:
                line = line.replace("✅", "☐")
                modified = True
            new_lines.append(line)
            
        if not modified:
            return "⚠️ Nothing to undo! Today's tasks are already marked as uncompleted (☐)." + FOOTER
            
        commit_msg = f"progress: undo {today_vid_str} tasks via Telegram Bot"
        repo.update_file(
            file_m.path,
            commit_msg,
            "\n".join(new_lines),
            file_m.sha,
            branch="main"
        )
        return f"⏪ Undone! Today's tasks have been reverted back to ☐ on GitHub.\n\n💬 <b>Commit:</b> <i>{commit_msg}</i>" + FOOTER
    except Exception as e:
        return f"❌ GitHub API Error: {str(e)}" + FOOTER

def command_interview() -> str:
    try:
        repo = get_repo()
        content, _ = get_file_content(repo, DATA_PATH)
        iqs = re.findall(r"^\s*\"(Behavioral|Scenario|Technical Explanation):([^\"]+)\",*$", content, re.MULTILINE)
        if not iqs: return "Could not parse interview questions."
        iq = random.choice(iqs)
        return f"🎙️ <b>{iq[0]}</b>\n\n{iq[1].strip()}" + FOOTER
    except Exception as e:
        return f"❌ Error: {str(e)}"

def command_prompt() -> str:
    try:
        repo = get_repo()
        content, _ = get_file_content(repo, DATA_PATH)
        prompts = re.findall(r"\{\s*title:\s*\"([^\"]+)\",\s*text:\s*'\"([^\"]+)\"'", content)
        if not prompts: return "Could not parse prompts."
        p = random.choice(prompts)
        return f"🤖 <b>AI Prompt Sandbox: {p[0]}</b>\n\n<i>{p[1]}</i>" + FOOTER
    except Exception as e:
        return f"❌ Error: {str(e)}"

def command_quote() -> str:
    try:
        repo = get_repo()
        content, _ = get_file_content(repo, DATA_PATH)
        quotes = re.findall(r"\{\s*quote:\s*\"([^\"]+)\",\s*author:\s*\"([^\"]+)\"", content)
        if not quotes: return "Could not parse quotes."
        q = random.choice(quotes)
        return f"💡 <i>\"{q[0]}\"</i>\n— <b>{q[1]}</b>" + FOOTER
    except Exception as e:
        return f"❌ Error: {str(e)}"

def command_ask(query: str) -> None:
    if not GEMINI_API_KEY:
        send_telegram("⚠️ Gemini API Key not configured! Please add `GEMINI_API_KEY` to your Render environment variables.", parse_mode=None)
        return
        
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        sys_prompt = "You are a senior DevOps mentor for someone taking the CKA and AZ-104. Be very concise, helpful, and technically accurate."
        response = model.generate_content(f"{sys_prompt}\n\nUser: {query}")
        
        raw_footer = "\n\n🌐 Dashboard: https://imranshs08.github.io/job/ • 🐙 Repo: https://github.com/imranshs08/job"
        send_telegram(f"✨ AI Insights:\n\n{response.text}{raw_footer}", parse_mode=None)
    except Exception as e:
        send_telegram(f"❌ AI Error: {str(e)}", parse_mode=None)

def command_log(text_to_log: str) -> str:
    try:
        repo = get_repo()
        now = datetime.now().strftime("%b %d, %Y - %H:%M")
        entry = f"\n## 📓 Log: {now}\n{text_to_log}\n"
        
        try:
            content, file_m = get_file_content(repo, JOURNAL_PATH)
            repo.update_file(file_m.path, "docs: telegram daily log appended", content + entry, file_m.sha, branch="main")
        except:
            # File doesn't exist yet
            repo.create_file(JOURNAL_PATH, "docs: init telegram log journal", f"# DevOps Telegram Action Log\n{entry}", branch="main")
            
        return "✅ Logged successfully to `04-Notes/war-journal.md`!" + FOOTER
    except Exception as e:
        return f"❌ Error: {str(e)}"

def command_status() -> str:
    try:
        repo = get_repo()
        content, _ = get_file_content(repo, TRACKER_PATH)
        
        # Parse basics
        video_rows = re.findall(r"^\|\s*(\d+)\s*\|.*?\|\s*(Aug|Sep|Oct|Nov|Dec|Jan)\s+\d+.*?\|\s*(\u2705|☐)", content, re.MULTILINE)
        videos_watched = sum(1 for _, _, status in video_rows if status == "✅")
        cka_all = re.findall(r"\|\s*(✅|☐)\s*\|?\s*\n", content)
        cka_done = sum(1 for s in cka_all if s == "✅")
        cka_total = len(cka_all)
        
        today = date.today()
        days_cka = (CKA_EXAM_DATE - today).days
        days_az = (AZ_EXAM_DATE - today).days
        
        vid_pct = round(videos_watched / TOTAL_VIDEOS * 100, 1)
        cka_pct = round(cka_done / cka_total * 100, 1) if cka_total else 0
        
        cka_date_str = CKA_EXAM_DATE.strftime("%b %d, %Y")
        az_date_str = AZ_EXAM_DATE.strftime("%b %d, %Y")
        
        today_vid_str = f"{months[today.month-1]} {today.day}"
        vid_match = re.search(
            rf"\|\s*\d+\s*\|\s*\[([^\]]+)\]\(([^)]+)\).*?\|\s*{re.escape(today_vid_str)}\s*\|[^|]*?\|\s*(✅|☐)",
            content
        )
        if vid_match:
            today_video_title = vid_match.group(1)
            today_video_url = vid_match.group(2)
            today_video_status = vid_match.group(3)
            today_sched_line = f"\n\n📅 <b>Today's Video:</b>\n  {today_video_status} 📺 <a href='{today_video_url}'>{today_video_title}</a>"
        else:
            # Fallback
            vid_match2 = re.search(
                rf"\|\s*\d+\s*\|\s*\[([^\]]+)\].*?\|\s*{re.escape(today_vid_str)}\s*\|[^|]*?\|\s*(✅|☐)",
                content
            )
            if vid_match2:
                today_video_title = vid_match2.group(1)
                today_video_status = vid_match2.group(2)
                today_sched_line = f"\n\n📅 <b>Today's Video:</b>\n  {today_video_status} 📺 {today_video_title}"
            else:
                today_sched_line = f"\n\n📅 <b>Today:</b>\n  📺 No video scheduled"
        
        return f"""📊 <b>DevOps Command Center Status</b>

⏳ <b>Countdowns:</b>
  ☸️  CKA: {days_cka} days <i>({cka_date_str})</i>
  ☁️  AZ-104: {days_az} days <i>({az_date_str})</i>

✅ <b>Progress:</b>
  📺 Videos: {videos_watched} / {TOTAL_VIDEOS} ({vid_pct}%)
  ☸️  CKA: {cka_done} / {cka_total} ({cka_pct}%){today_sched_line}""" + FOOTER
    except Exception as e:
        return f"❌ Error: {str(e)}"


@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "DevOps Bot is live!", 200
        
    data = request.json or {}
    
    # Handle Button Clicks (Callback Queries)
    if "callback_query" in data:
        cb = data["callback_query"]
        chat_id = str(cb.get("message", {}).get("chat", {}).get("id"))
        text = cb.get("data", "").strip()
        low_text = text.lower()
        
        # Acknowledge the button press to stop the loading spinner
        import urllib.request
        try:
            cb_id = cb.get("id")
            urllib.request.urlopen(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery?callback_query_id={cb_id}", timeout=5)
        except:
            pass
            
    # Handle Normal Text Messages
    elif "message" in data:
        msg = data["message"]
        chat_id = str(msg.get("chat", {}).get("id"))
        text = msg.get("text", "").strip()
        low_text = text.lower()
    else:
        return jsonify({"status": "ignored"}), 200
        
    # Authorized user check
    if chat_id != str(TELEGRAM_CHAT_ID):
        print(f"Unauthorized chat_id {chat_id}")
        return jsonify({"status": "unauthorized"}), 200

    # Main Command Router
    std_markup = {
        "inline_keyboard": [
            [
                {"text": "📊 Status", "callback_data": "/status"},
                {"text": "✅ Done", "callback_data": "/done"}
            ],
            [
                {"text": "🎙️ Interview", "callback_data": "/interview"},
                {"text": "🤖 Prompt", "callback_data": "/prompt"}
            ],
            [
                {"text": "⏪ Undo", "callback_data": "/undo"},
                {"text": "💡 Quote", "callback_data": "/quote"}
            ]
        ]
    }

    if low_text in ["/done", "done", "✅ done"]:
        send_telegram("⏳ Processing `/done` via GitHub API...")
        send_telegram(command_done())
        
    elif low_text in ["/undo", "undo", "⏪ undo"]:
        send_telegram("⏳ Processing `/undo` via GitHub API...")
        send_telegram(command_undo())
        
    elif low_text in ["/interview", "🎙️ interview"]:
        send_telegram("⏳ Fetching a random interview question...")
        send_telegram(command_interview())
        
    elif low_text in ["/prompt", "🤖 prompt"]:
        send_telegram("⏳ Fetching a random AI prompt...")
        send_telegram(command_prompt())
        
    elif low_text in ["/quote", "💡 quote"]:
        send_telegram("⏳ Fetching a random quote...")
        send_telegram(command_quote())
        
    elif low_text in ["/status", "📊 status"]:
        send_telegram("⏳ Parsing progress-tracker.md...")
        send_telegram(command_status(), reply_markup=std_markup)
        
    elif low_text.startswith("/ask"):
        query = text[4:].strip()
        if not query:
            send_telegram("⚠️ Please provide a prompt! Example: `/ask What is Kubernetes?`", parse_mode="Markdown")
        else:
            send_telegram(f"🧠 Asking Gemini AI: {query}")
            command_ask(query)
        
    elif low_text.startswith("/log "):
        send_telegram("⏳ Writing log entry to GitHub...")
        send_telegram(command_log(text[5:].strip()))
        
    else:
        # Help menu for anything else
        help_menu = """🤖 <b>DevOps Bot Commands:</b>
/done - Check off today's tasks as ✅
/undo - Revert today's tasks back to ☐
/status - Quick progress check
/interview - Practice an interview question
/prompt - Test out an AI scenario
/ask [query] - Chat directly with Gemini AI
/quote - Get a motivational tech quote
/log [text] - Append notes to war-journal.md"""
        send_telegram(help_menu + FOOTER, reply_markup=std_markup)

    return jsonify({"status": "ok"}), 200

@app.route("/cron", methods=["POST"])
def cron_ping():
    data = request.json or {}
    if str(data.get("chat_id")) == str(TELEGRAM_CHAT_ID):
        send_telegram("⏰ <b>6-Hour Scheduled Check-In</b>\n\n" + command_status())
        return jsonify({"status": "pinged"}), 200
    return jsonify({"status": "unauthorized"}), 401

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
