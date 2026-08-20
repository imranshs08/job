# #1 — Introduction & Setup
> 🔗 [Watch Video](https://www.youtube.com/watch?v=1AF5pFGwRTM) | **Status:** ✅ Watched

---

## 📝 Summary
Gemini CLI is Google's free, open-source AI coding assistant that runs directly in your terminal. Unlike browser-based tools, it lives inside your project directory and understands your codebase. This video covers what Gemini CLI is, why it's useful for developers, and how to install and launch it for the first time.

## 🔑 Key Concepts
- **Gemini CLI** = terminal-based AI agent powered by Google's Gemini model
- Runs in the context of your **current project folder** — it can read, write, and edit files
- Uses your **Google account** for free access (generous free tier via Gemini API)
- Interactive REPL mode: you chat with it like a terminal session
- Can handle multi-step tasks: "Create a REST API, add tests, then refactor it"

## 💻 Installation & Setup
```bash
# Install globally via npm
npm install -g @google/gemini-cli

# Launch Gemini CLI in your project folder
cd your-project/
gemini
```

## 🔧 First-Run Flow
1. Run `gemini` in terminal
2. Browser opens → Sign in with Google *(or use API key — see below)*
3. Auth token saved locally
4. REPL starts — type your first prompt

---

## ⚠️ Real-World Gotchas (From My First Session — Aug 21, 2026)

### Gotcha 1: OAuth login is deprecated for individuals
**Error:**
```
Failed to sign in. This client is no longer supported for Gemini Code Assist for individuals.
```
**Fix:** Use an API key instead of Google account OAuth login.
```powershell
# 1. Get free API key from: https://aistudio.google.com/apikey
# 2. Set it in PowerShell (not Git Bash):
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your-key-here", "User")
# 3. Close all terminals, reopen, then run: gemini
```

### Gotcha 2: Run from your PROJECT folder, not system32
```bash
# ❌ Wrong — no project context
C:\WINDOWS\system32> gemini

# ✅ Right — Gemini reads your files
cd "c:\Job Tracker"
gemini
```

### Gotcha 3: Default model (gemini-3-flash-preview) gets 503 errors
**Error:**
```
✕ [API Error: 503 - This model is currently experiencing high demand]
```
**Fix:** Switch to the stable model inside the REPL:
```
/model gemini-2.0-flash
```
Or set permanently in `~/.gemini/settings.json`:
```json
{ "model": "gemini-2.0-flash" }
```

### Gotcha 4: PATH not set after install on Windows
**Error:**
```
claude : The term 'gemini' is not recognized...
```
**Fix:** Add `C:\Users\<you>\.local\bin` to User PATH via System Properties → Environment Variables, then restart terminal.

---

## 🎯 First Session Results
- ✅ Installed via `npm install -g @google/gemini-cli`
- ✅ Authenticated using Gemini API key (AI Studio free key)
- ✅ Ran from `c:\Job Tracker` — Gemini read the project files
- ✅ It correctly identified the repo as "DevOps Job Switch 2027 Command Center"
- ✅ Explained `renderDashboard()` function from `index.html`
- ✅ Switched model to `gemini-2.0-flash` to fix 503 errors

## ✅ Action Items
- [x] Install Gemini CLI: `npm install -g @google/gemini-cli`
- [x] Get API key from https://aistudio.google.com/apikey
- [x] Set `GEMINI_API_KEY` as User environment variable
- [x] Run `gemini` from project folder
- [x] Fix model: `/model gemini-2.0-flash`
- [ ] Create a `GEMINI.md` in the project root for persistent context
