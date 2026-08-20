# #1 — Introduction & Setup
> 🔗 [Watch Video](https://www.youtube.com/watch?v=1AF5pFGwRTM) | **Status:** ☐ Watched

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

# First launch: opens browser to authenticate with Google account
# After auth, you're in the interactive REPL
```

## 🔧 First-Run Flow
1. Run `gemini` in terminal
2. Browser opens → Sign in with Google
3. Auth token saved locally
4. REPL starts — type your first prompt

## ❓ Questions / Unclear Points
- Does it work offline? (No — requires internet for API calls)
- Is there a usage limit on the free tier? (Yes — check Google AI Studio for quotas)

## ✅ Action Items
- [ ] Install Gemini CLI: `npm install -g @google/gemini-cli`
- [ ] Authenticate with Google account
- [ ] Run `gemini` in your Job Tracker folder and explore
