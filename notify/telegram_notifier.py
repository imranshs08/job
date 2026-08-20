#!/usr/bin/env python3
"""
DevOps Job Tracker — Telegram Progress Notifier
================================================
Usage:
  python telegram_notifier.py --daily   → Full morning summary (run via Task Scheduler)
  python telegram_notifier.py --hook    → Short commit notification (run via git hook)
  python telegram_notifier.py --test    → Test connection only
"""

import re
import sys
import urllib.request
import urllib.parse
import json
from datetime import date, datetime

# ── Load config ──────────────────────────────────────────────────────────────
try:
    from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
except ImportError:
    print("ERROR: notify/config.py not found.")
    print("Copy notify/config.example.py to notify/config.py and fill in your credentials.")
    sys.exit(1)

# ── Constants ─────────────────────────────────────────────────────────────────
TRACKER_PATH = r"c:\Job Tracker\03-Progress-Tracker\progress-tracker.md"
CKA_EXAM_DATE = date(2027, 1, 1)
AZ_EXAM_DATE  = date(2027, 1, 15)
TOTAL_VIDEOS  = 158

# ── Telegram sender ───────────────────────────────────────────────────────────
def send_telegram(message: str) -> bool:
    """Send a message to Telegram. Returns True on success."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False)
    except Exception as e:
        print(f"Telegram send failed: {e}")
        return False

# ── Progress parser ───────────────────────────────────────────────────────────
def parse_tracker() -> dict:
    """Parse progress-tracker.md and return a stats dict."""
    try:
        with open(TRACKER_PATH, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return {}

    # ── Video stats ──
    video_rows = re.findall(
        r"^\|\s*(\d+)\s*\|.*?\|\s*(Aug|Sep|Oct|Nov|Dec|Jan)\s+\d+.*?\|\s*(\u2705|☐)",
        content, re.MULTILINE
    )
    videos_watched = sum(1 for _, _, status in video_rows if status == "✅")

    # ── CKA stats ──
    cka_all    = re.findall(r"\|\s*(✅|☐)\s*\|?\s*\n", content)
    cka_done   = sum(1 for s in cka_all if s == "✅")
    cka_total  = len(cka_all)

    # ── Today's schedule ──
    today = date.today()
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    today_str_vid  = f"{months[today.month-1]} {today.day}"
    today_str_cert = f"{months[today.month-1]} {today.day:02d}, {today.year}"

    # Find today's video
    today_video = None
    today_video_status = "☐"
    vid_match = re.search(
        rf"\|\s*\d+\s*\|\s*\[([^\]]+)\].*?\|\s*{re.escape(today_str_vid)}\s*\|[^|]*?\|\s*(✅|☐)",
        content
    )
    if vid_match:
        today_video = vid_match.group(1)
        today_video_status = vid_match.group(2)

    # Find today's CKA lesson
    today_cka = None
    today_cka_status = "☐"
    cka_match = re.search(
        rf"\|\s*{re.escape(today_str_cert)}\s*\|[^|]+\|\s*([^|]+)\|\s*[^|]+\|\s*(✅|☐)",
        content
    )
    if cka_match:
        raw = cka_match.group(1).strip()
        raw = re.sub(r"<br>", " | ", raw)
        raw = re.sub(r"\*\*(.*?)\*\*", r"\1", raw)
        today_cka = raw[:120]
        today_cka_status = cka_match.group(2)

    # ── Parse data.js for daily routines ──
    daily_quote, daily_prompt, daily_interview = "", "", ""
    try:
        with open(r"c:\Job Tracker\data.js", "r", encoding="utf-8") as f:
            data_content = f.read()
            
        quotes = re.findall(r"^\s*\"([^\"]+)\",*$", data_content, re.MULTILINE)
        prompts = re.findall(r"\{\s*title:\s*\"([^\"]+)\",\s*text:\s*'\"([^\"]+)\"'", data_content)
        iqs = re.findall(r"^\s*\"(Behavioral|Scenario|Technical Explanation):([^\"]+)\",*$", data_content, re.MULTILINE)
        
        day_of_year = today.timetuple().tm_yday
        if quotes: daily_quote = quotes[day_of_year % len(quotes)]
        if prompts:
            p = prompts[day_of_year % len(prompts)]
            daily_prompt = f"<b>{p[0]}</b>\n    <i>{p[1]}</i>"
        if iqs:
            iq = iqs[day_of_year % len(iqs)]
            daily_interview = f"<b>{iq[0]}</b> {iq[1]}"
            
    except Exception as e:
        print(f"Failed to parse data.js: {e}")

    # ── Countdown ──
    days_cka = (CKA_EXAM_DATE - today).days
    days_az  = (AZ_EXAM_DATE  - today).days

    return {
        "videos_watched": videos_watched,
        "videos_total":   TOTAL_VIDEOS,
        "cka_done":       cka_done,
        "cka_total":      cka_total,
        "days_cka":       days_cka,
        "days_az":        days_az,
        "today_video":    today_video,
        "today_video_status": today_video_status,
        "today_cka":      today_cka,
        "today_cka_status": today_cka_status,
        "today_str":      today.strftime("%a %b %d"),
        "cka_date_str":   CKA_EXAM_DATE.strftime("%b %d, %Y"),
        "az_date_str":    AZ_EXAM_DATE.strftime("%b %d, %Y"),
        "daily_quote":    daily_quote,
        "daily_prompt":   daily_prompt,
        "daily_interview": daily_interview
    }

# ── Message builders ──────────────────────────────────────────────────────────
def build_daily_message(s: dict) -> str:
    vid_pct = round(s["videos_watched"] / s["videos_total"] * 100, 1) if s["videos_total"] else 0
    cka_pct = round(s["cka_done"]       / s["cka_total"]   * 100, 1) if s["cka_total"]   else 0

    today_video_line = f"  📺 <b>{s['today_video']}</b>" if s["today_video"] else "  📺 No video scheduled"
    today_cka_line   = f"  ☸️ {s['today_cka']}"         if s["today_cka"]   else "  ☸️ No CKA lesson scheduled"
    
    quote_block = f'<i>"{s["daily_quote"]}"</i>\n' if s.get("daily_quote") else ""

    return f"""☀️ <b>Good Morning! DevOps Daily Brief — {s["today_str"]}</b>
{quote_block}
⏳ <b>Exam Countdowns:</b>
  ☸️  CKA: <b>{s["days_cka"]} days</b> <i>({s["cka_date_str"]})</i>
  ☁️  AZ-104: <b>{s["days_az"]} days</b> <i>({s["az_date_str"]})</i>

📊 <b>Overall Progress:</b>
  📺 Videos: {s["videos_watched"]} / {s["videos_total"]}  ({vid_pct}%)
  ☸️  CKA:    {s["cka_done"]} / {s["cka_total"]}  ({cka_pct}%)

📅 <b>Today's Schedule:</b>
{today_video_line}
{today_cka_line}

🤖 <b>AI Prompt of the Day:</b>
  {s['daily_prompt']}

🎙️ <b>Interview Question:</b>
  {s['daily_interview']}

🔥 Every lesson gets you closer. Let's go! 💪"""


def build_hook_message(s: dict) -> str:
    vid_pct = round(s["videos_watched"] / s["videos_total"] * 100, 1) if s["videos_total"] else 0
    cka_pct = round(s["cka_done"]       / s["cka_total"]   * 100, 1) if s["cka_total"]   else 0

    return f"""🔔 <b>Progress Committed — {s["today_str"]}</b>

📊 <b>Current Stats:</b>
  📺 Videos: {s["videos_watched"]} / {s["videos_total"]}  ({vid_pct}%)
  ☸️  CKA:    {s["cka_done"]} / {s["cka_total"]}  ({cka_pct}%)
  ☸️  CKA Exam in <b>{s["days_cka"]} days</b> <i>({s["cka_date_str"]})</i>
  ☁️  AZ-104 Exam in <b>{s["days_az"]} days</b> <i>({s["az_date_str"]})</i>

✅ Keep the momentum going!"""

def build_nightly_message(s: dict) -> str:
    """Nightly status check to see if today's items were completed."""
    status_msg = ""
    all_done = True
    
    if s["today_video"]:
        status_msg += f"{s['today_video_status']} 📺 {s['today_video']}\n"
        if s["today_video_status"] != "✅":
            all_done = False
            
    if s["today_cka"]:
        status_msg += f"{s['today_cka_status']} ☸️ {s['today_cka']}\n"
        if s["today_cka_status"] != "✅":
            all_done = False
            
    if not status_msg:
        return f"🌙 <b>Nightly Check-In</b>\nYou had nothing scheduled for today. Rest up!"
        
    if all_done:
        footer = "🎉 Outstanding! You completed everything today. Great job backing up your goals with action. Rest well!"
    else:
        footer = "⚠️ Looks like some items are still pending.\nIf you're done, don't forget to check them off and Git Commit to update your progress!"

    return f"""🌙 <b>Nightly Progress Check — {s['today_str']}</b>

<b>Today's Checklist:</b>
{status_msg}
{footer}"""

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--daily"

    if mode == "--test":
        ok = send_telegram("✅ <b>Telegram notifier is working!</b>\nYour DevOps progress bot is connected.")
        print("✅ Test message sent!" if ok else "❌ Failed to send. Check token/chat_id in config.py")
        return

    stats = parse_tracker()
    if not stats:
        print(f"ERROR: Could not read tracker at {TRACKER_PATH}")
        sys.exit(1)

    if mode == "--daily":
        msg = build_daily_message(stats)
    elif mode == "--hook":
        msg = build_hook_message(stats)
    elif mode == "--nightly":
        msg = build_nightly_message(stats)
    else:
        print(f"Unknown mode: {mode}. Use --daily, --nightly, --hook, or --test")
        sys.exit(1)

    ok = send_telegram(msg)
    print("✅ Sent!" if ok else "❌ Failed to send.")

if __name__ == "__main__":
    main()
