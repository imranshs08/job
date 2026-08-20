# #7 — Custom Commands
> 🔗 [Watch Video](https://www.youtube.com/watch?v=txezKEvSvlU) | **Status:** ☐ Watched

---

## 📝 Summary
Custom commands let you create your own slash commands — reusable, named prompts that you can trigger with a single keyword. Instead of typing a long prompt every time (e.g., "Review this file for security issues and list them as bullet points"), you define it once as `/security-review` and reuse it across sessions. This is a huge productivity boost for repetitive tasks.

## 🔑 Key Concepts
- **Custom commands** = named, reusable prompt templates stored in a config file
- Defined in `.gemini/commands.json` (project-level) or `~/.gemini/commands.json` (global)
- Invoked with `/command-name` in the REPL just like built-in commands
- Can include placeholders for dynamic content
- Great for: code reviews, documentation, testing prompts, standardised analyses

## 💻 Creating Custom Commands
```bash
# Project-level commands (only for this project)
mkdir -p .gemini
# Create/edit .gemini/commands.json

# Global commands (available in all projects)
# Windows: C:\Users\imran\.gemini\commands.json
```

## 📄 commands.json Example
```json
{
  "commands": [
    {
      "name": "review",
      "description": "Review the current file for bugs, code smells, and improvements",
      "prompt": "Please review the file I'm working on. Check for: 1) Bugs or logic errors, 2) Security issues, 3) Performance problems, 4) Code style issues. Present findings as a prioritized bullet list."
    },
    {
      "name": "explain",
      "description": "Explain what the current function/section does in simple terms",
      "prompt": "Explain the selected code in simple terms as if I'm a junior developer. Use analogies where helpful."
    },
    {
      "name": "devops-check",
      "description": "Review for DevOps best practices",
      "prompt": "Review this code/config for DevOps best practices: check for hardcoded secrets, missing error handling, non-idempotent operations, and missing logging. List issues with severity: HIGH / MEDIUM / LOW."
    },
    {
      "name": "commit-msg",
      "description": "Generate a conventional commit message for recent changes",
      "prompt": "Based on the changes we just made, generate a conventional commit message following the format: type(scope): description. Types: feat, fix, docs, refactor, chore. Keep under 72 chars."
    }
  ]
}
```

## 💡 Useful Custom Commands for DevOps Learning
| Command | Purpose |
|---------|---------|
| `/explain` | Explain any K8s YAML or bash script |
| `/devops-check` | Check Terraform/scripts for best practices |
| `/commit-msg` | Auto-generate commit messages |
| `/study-notes` | Summarise current file as study notes |
| `/interview-q` | Generate interview questions about current topic |

## ❓ Questions / Unclear Points
- Can commands call other commands? (Not natively — but you can chain prompts manually)
- Are commands version-controlled? (Yes — commit `.gemini/commands.json` to git)

## ✅ Action Items
- [ ] Create `.gemini/commands.json` in Job Tracker project
- [ ] Add at least 3 custom commands: `/review`, `/commit-msg`, `/explain`
- [ ] Test each with `/command-name` in the REPL
