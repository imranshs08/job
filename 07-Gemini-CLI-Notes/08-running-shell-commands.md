# #8 — Running Shell Commands
> 🔗 [Watch Video](https://www.youtube.com/watch?v=z7xEiXI1v24) | **Status:** ☐ Watched

---

## 📝 Summary
Gemini CLI can run shell commands directly on your system — not just read/write files. You can ask it to run tests, install packages, execute scripts, or perform any terminal operation. Gemini proposes the command first, you confirm, then it runs it and reads the output to continue the task. This makes it a true AI agent, not just a code editor.

## 🔑 Key Concepts
- Gemini CLI can **execute shell commands** on your behalf (with your approval)
- It reads the **command output** and reasons about it — e.g., it sees test failures and auto-fixes
- Works on: bash, PowerShell, cmd — whatever your system shell is
- You always see and approve the command before it runs
- Enables **agentic loops**: write code → run tests → see failure → fix → re-run

## 💻 Example Interactions
```
> Run the tests and fix any that fail

> Install the missing npm dependencies and then try running the app again

> List all files modified in the last git commit

> Check if port 8080 is in use and kill the process if it is

> Run git status and create a commit message based on the changes shown
```

## 🔄 Agentic Loop Example
```
You: "Run the tests and fix failures automatically"

Gemini: Proposes → git test
        [You approve]
        Sees: 2 tests FAIL (null reference in utils.js)
        Proposes → edit utils.js (shows diff)
        [You approve]
        Proposes → run tests again
        [You approve]
        Sees: All tests pass ✅
        Reports: "Fixed null reference by adding guard clause"
```

## ⚡ Useful Shell Command Prompts for DevOps
```
> Check kubectl cluster status and tell me if anything looks unhealthy

> Run terraform plan and explain the proposed changes in plain English

> Show me the last 20 git commits and summarise what was worked on

> Check if docker is running and list all active containers

> Show disk usage and warn me if any mount is above 80%
```

## ⚠️ Safety Notes
- Always **read the proposed command** before approving  
- Be careful with destructive commands (`rm`, `kubectl delete`, `terraform destroy`)
- Gemini will warn you about risky operations — read those warnings
- In sensitive environments, use `--sandbox` flag to restrict shell access

## ❓ Questions / Unclear Points
- Can it run commands in the background? (No — it runs synchronously and waits for output)
- What if the command hangs? (Ctrl+C to interrupt, then Gemini will handle it)

## ✅ Action Items
- [ ] Try: "Run `git log --oneline -10` and summarise what was worked on recently"
- [ ] Try: "Check if Node.js is installed and what version"
- [ ] Experiment with an agentic loop on a small task
