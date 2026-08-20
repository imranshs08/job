# #2 — The GEMINI.md File
> 🔗 [Watch Video](https://www.youtube.com/watch?v=Od5SlOSlMQo) | **Status:** ☐ Watched

---

## 📝 Summary
`GEMINI.md` is a special Markdown file you place at the root of your project. It acts as a **persistent system prompt** — every time you start Gemini CLI in that folder, it automatically reads this file. This is how you give Gemini context about your project: tech stack, coding standards, rules, and any special instructions.

## 🔑 Key Concepts
- **`GEMINI.md`** = project-level instruction file read automatically on startup
- Replaces having to re-explain your project every session
- Think of it as a "README for the AI" — the more context, the better the output
- Supports full Markdown: headings, lists, code blocks
- Can include: project description, tech stack, file structure, coding rules, dos & don'ts

## 💻 Example GEMINI.md
```markdown
# Project: Job Tracker DevOps Dashboard

## Tech Stack
- Frontend: HTML, Vanilla CSS, JavaScript
- Data: Markdown files parsed at runtime
- No frameworks — pure vanilla

## Coding Rules
- Use semantic HTML5 elements
- Comment all JavaScript functions
- Keep CSS variables in :root
- Never use inline styles

## Project Structure
- index.html → main dashboard
- data.js → AI prompts & interview questions
- 03-Progress-Tracker/ → progress-tracker.md (source of truth)

## Important Notes
- Do NOT modify progress-tracker.md structure — it is parsed by regex
- All dates in tracker use format: "Aug 21" or "Aug 21, 2026"
```

## 🔧 How to Create It
```bash
# In your project root
touch GEMINI.md
# Then edit it with your project instructions
```

## ❓ Questions / Unclear Points
- Can you have multiple GEMINI.md files in subdirectories? (Yes — Gemini reads both root and subfolder ones)
- Does it count toward token limits per message? (Yes — keep it concise)

## ✅ Action Items
- [ ] Create a `GEMINI.md` in `c:\Job Tracker\` with project context
- [ ] Include: tech stack, file structure, and parsing rules for the tracker
