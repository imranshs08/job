# #5 — Managing Context
> 🔗 [Watch Video](https://www.youtube.com/watch?v=KfaOzVY3Luw) | **Status:** ☐ Watched

---

## 📝 Summary
Context is the information Gemini has available in its "working memory" for the current session. This video explains how Gemini CLI loads context (files, conversation history, GEMINI.md), what the token limits are, and how to manage context to avoid hitting limits — including using `/clear`, explicitly referencing files, and being selective about what you include.

## 🔑 Key Concepts
- **Context window** = total amount of text Gemini can "see" at once (input + output)
- Gemini 2.0 Flash has ~1 million token context — very large, but not infinite
- Gemini CLI automatically reads files you reference or it deems relevant
- Long sessions accumulate history → can slow responses or hit limits → use `/clear`
- **Explicit file references** = better accuracy than letting Gemini guess

## 💻 Ways to Add Context
```bash
# Reference a specific file in your prompt
> Look at index.html and explain the renderDashboard function

# Add multiple files
> Compare the structure of data.js and 03-Progress-Tracker/progress-tracker.md

# Tell Gemini to ignore certain files
> Only look at the CSS in index.html, ignore the JavaScript

# Clear context and start fresh (keeps GEMINI.md)
/clear
```

## 📊 Context Management Tips
| Situation | Action |
|-----------|--------|
| Long session, responses getting slow | `/clear` — start fresh |
| Working on one specific file | Mention filename explicitly in every prompt |
| Large codebase | Add key file descriptions in `GEMINI.md` |
| Sensitive files | List them in GEMINI.md under "Do not read" |
| Token limit warning | Clear history, rephrase task more concisely |

## 🔧 What Counts Toward Context
- `GEMINI.md` contents (loaded every session)
- All previous messages in the session
- File contents that were read/shown
- Gemini's own responses

## ❓ Questions / Unclear Points
- Does Gemini read ALL files automatically? (No — it reads what you reference or it decides is relevant)
- Does `/clear` delete GEMINI.md? (No — GEMINI.md persists, only conversation history is cleared)

## ✅ Action Items
- [ ] Run `/stats` mid-session to see token usage
- [ ] Practice using `/clear` between unrelated tasks
- [ ] Add important file descriptions to your `GEMINI.md`
