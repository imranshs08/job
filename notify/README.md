# 📲 Telegram Progress Notifier — Setup Guide

## Prerequisites
- Python 3.x installed
- A Telegram account

---

## Step 1 — Create Your Telegram Bot

1. Open Telegram → search **@BotFather** → send `/newbot`
2. Follow the prompts → copy your **Bot Token** (e.g. `7123456789:AAFxxx...`)
3. Send any message to your new bot (e.g. "hi")
4. Open this URL: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
5. Find `"id"` inside `"chat"` — that's your **Chat ID**

---

## Step 2 — Add Your Credentials

```bash
# In c:\Job Tracker\notify\
copy config.example.py config.py
# Then edit config.py with your token and chat ID
```

---

## Step 3 — Test the Connection

```bash
cd "c:\Job Tracker"
python notify/telegram_notifier.py --test
```
You should receive a message in Telegram. ✅

---

## Step 4 — Install the Git Hook

The hook is already at `.git/hooks/post-commit`.
Make it executable (run once in Git Bash):

```bash
chmod +x "c:/Job Tracker/.git/hooks/post-commit"
```

Now every `git commit` will automatically send a Telegram update.

---

## Step 5 — Set Up Daily Morning Summary (8 AM)

Run this once in PowerShell (as normal user):

```powershell
schtasks /create /tn "DevOps Morning Brief" `
  /tr "python 'c:\Job Tracker\notify\telegram_notifier.py' --daily" `
  /sc daily /st 08:00 /f
```

To verify it was created:
```powershell
schtasks /query /tn "DevOps Morning Brief"
```

To delete it:
```powershell
schtasks /delete /tn "DevOps Morning Brief" /f
```

---

## Manual Usage

```bash
# Full morning summary (anytime)
python notify/telegram_notifier.py --daily

# Short commit update (anytime)
python notify/telegram_notifier.py --hook

# Test connection
python notify/telegram_notifier.py --test
```

---

## Files

| File | Purpose |
|------|---------|
| `telegram_notifier.py` | Core script (parser + sender) |
| `config.py` | Your bot token + chat ID (**gitignored**) |
| `config.example.py` | Template (safe to commit) |
| `.git/hooks/post-commit` | Auto-trigger on git commit |
