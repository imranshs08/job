# #3 — Making Code Changes
> 🔗 [Watch Video](https://www.youtube.com/watch?v=jrFB_rkf-KU) | **Status:** ☐ Watched

---

## 📝 Summary
This video shows how Gemini CLI actually reads and modifies files in your project. You describe what you want in plain English, and Gemini proposes diffs — you approve or reject each change before it's applied. This makes it safe and transparent: you always see exactly what it wants to change before it touches your code.

## 🔑 Key Concepts
- Gemini CLI operates on **real files** in your working directory — not a sandbox
- Proposed changes are shown as **diffs** (green = added, red = removed)
- You must **approve** each change — nothing is auto-applied without confirmation
- It can create new files, edit existing ones, or delete files
- Works best with clear, specific prompts: "Add a dark mode toggle to index.html"

## 💻 Example Interactions
```
> Add a function to data.js that returns today's motivational quote

> Refactor the renderDashboard() function to extract the video parsing logic into a separate function called parseVideoTasks()

> Create a new file called utils.js and move all date formatting helpers there
```

## 🔄 Approval Flow
```
Gemini proposes change →
  Shows diff →
    [y] Accept / [n] Reject / [e] Edit manually →
      Applied to file
```

## 🔧 Tips for Good Prompts
| ❌ Vague | ✅ Specific |
|----------|------------|
| "Fix my code" | "Fix the date parsing bug in renderDashboard() where Aug vs Aug. doesn't match" |
| "Make it better" | "Add error handling to the fetch() call in init() — show a user-friendly error card if the request fails" |
| "Add a feature" | "Add a copy-to-clipboard button next to the AI prompt block in index.html" |

## ❓ Questions / Unclear Points
- Can it make changes across multiple files in one prompt? (Yes — it handles multi-file edits)
- What if it makes a mistake? (Reject the diff, or use `git checkout` to revert)

## ✅ Action Items
- [ ] Try: "Explain what the renderDashboard() function does in index.html"
- [ ] Try: "Add a comment block to every function in data.js"
