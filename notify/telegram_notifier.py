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
    cka_rows = re.findall(r"\|\s*(✅|☐)\s*\|?\s*$", content, re.MULTILINE)
    # More robust: count status column in CKA table
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
    vid_match = re.search(
        rf"\|\s*\d+\s*\|\s*\[([^\]]+)\].*?\|\s*{re.escape(today_str_vid)}\s*\|",
        content
    )
    if vid_match:
        today_video = vid_match.group(1)

    # Find today's CKA lesson
    today_cka = None
    cka_match = re.search(
        rf"\|\s*{re.escape(today_str_cert)}\s*\|[^|]+\|\s*([^|]+)\|",
        content
    )
    if cka_match:
        raw = cka_match.group(1).strip()
        # Strip HTML <br> tags and bold markers
        raw = re.sub(r"<br>", " | ", raw)
        raw = re.sub(r"\*\*(.*?)\*\*", r"\1", raw)
        today_cka = raw[:120]

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
        "today_cka":      today_cka,
        "today_str":      today.strftime("%a %b %d"),
    }

# ── Message builders ──────────────────────────────────────────────────────────
def build_daily_message(s: dict) -> str:
    vid_pct = round(s["videos_watched"] / s["videos_total"] * 100, 1) if s["videos_total"] else 0
    cka_pct = round(s["cka_done"]       / s["cka_total"]   * 100, 1) if s["cka_total"]   else 0

    today_video_line = f"  📺 <b>{s['today_video']}</b>" if s["today_video"] else "  📺 No video scheduled"
    today_cka_line   = f"  ☸️ {s['today_cka']}"         if s["today_cka"]   else "  ☸️ No CKA lesson scheduled"

    return f"""☀️ <b>Good Morning! DevOps Daily Brief — {s["today_str"]}</b>

⏳ <b>Exam Countdowns:</b>
  ☸️  CKA  (Jan 01):  <b>{s["days_cka"]} days</b>
  ☁️  AZ-104 (Jan 15): <b>{s["days_az"]} days</b>

📊 <b>Overall Progress:</b>
  📺 Videos: {s["videos_watched"]} / {s["videos_total"]}  ({vid_pct}%)
  ☸️  CKA:    {s["cka_done"]} / {s["cka_total"]}  ({cka_pct}%)

📅 <b>Today's Schedule:</b>
{today_video_line}
{today_cka_line}

🔥 Every lesson gets you closer. Let's go! 💪"""


def build_hook_message(s: dict) -> str:
    vid_pct = round(s["videos_watched"] / s["videos_total"] * 100, 1) if s["videos_total"] else 0
    cka_pct = round(s["cka_done"]       / s["cka_total"]   * 100, 1) if s["cka_total"]   else 0

    return f"""🔔 <b>Progress Committed — {s["today_str"]}</b>

📊 <b>Current Stats:</b>
  📺 Videos: {s["videos_watched"]} / {s["videos_total"]}  ({vid_pct}%)
  ☸️  CKA:    {s["cka_done"]} / {s["cka_total"]}  ({cka_pct}%)
  ☸️  CKA Exam in <b>{s["days_cka"]} days</b>
  ☁️  AZ-104 Exam in <b>{s["days_az"]} days</b>

✅ Keep the momentum going!"""

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
    else:
        print(f"Unknown mode: {mode}. Use --daily, --hook, or --test")
        sys.exit(1)

    ok = send_telegram(msg)
    print("✅ Sent!" if ok else "❌ Failed to send.")

if __name__ == "__main__":
    main()
