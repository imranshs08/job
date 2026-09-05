# 🤖 Claude Code for Beginners

## 1. Core Concepts & Definitions

Before jumping into the tool, let's establish what Claude Code actually is and how it differs from traditional AI interfaces.

* **Claude Code:** An official autonomous, terminal-based AI coding assistant created by Anthropic. Instead of chatting in a web browser, it runs directly in your CLI.
* **Agentic Execution:** Unlike ChatGPT where you copy/paste code, Claude Code can *autonomously* read your local files, write files, and even execute terminal commands (like running `git` or `npm test`) on your behalf.
* **Context Awareness:** It automatically understands your entire repository by analyzing the directory structure and file contents without you needing to explicitly upload them.

---

## 2. Architecture Comparison & Visuals

### AI Assistant Tooling Landscape
How does Claude Code fit into the current DevOps and AI ecosystem?

| Feature | Web AI (ChatGPT/Claude.ai) | IDE AI (Copilot/Cursor) | Terminal AI (Claude Code) |
| :--- | :--- | :--- | :--- |
| **Interface** | Web Browser | Inside VS Code / IDE | Terminal (Bash, Zsh, PowerShell) |
| **Command Execution**| ❌ Cannot run commands | ⚠️ Limited terminal integration | ✅ Natively executes bash commands |
| **File Read/Write** | ❌ Manual copy/pasting | ✅ Modifies open files | ✅ Scans and edits entire directories |
| **Best For** | General questions, logic | Autocompleting boilerplate | Infrastructure analysis, running scripts |

---

## 3. CLI Commands & Examples

To use Claude Code, you need Node.js installed on your machine.

### Installation & Authentication
```bash
# 1. Install Claude Code globally via npm
npm install -g @anthropic-ai/claude-code

# 2. Authenticate the CLI with your Anthropic account
claude login
```

### Core Usage Commands
Once installed, starting a session is as simple as typing `claude`.

```bash
# Start an interactive AI session in your current directory
claude

# Have it execute a specific command without entering interactive mode
claude "Review my main.tf file and tell me if the security groups are open to the world"
```

### Slash Commands (Inside the interactive session)
When you are inside the `claude` prompt, you can use slash commands to manage the AI's behavior:
* `/help` - Displays the list of available commands.
* `/clear` - Wipes the current context and conversation history to start fresh (saves tokens).
* `/compact` - Summarizes the conversation to save context space but keeps the AI aware of the goal.
* `/cost` - Displays how much money/API credits your current session has used.

---

## 4. 🧠 The Missing Context: How does it actually work securely?

*If Claude Code can write files and run terminal commands, isn't that incredibly dangerous?*

1. **The Approval Gateway:** By default, Claude Code uses a "Human-in-the-loop" security model. If it decides it needs to run a command that modifies your system (like `rm -rf`, `git push`, or `terraform apply`), **it will pause and ask you for explicit Y/N permission** before execution.
2. **Context Limits & `.claudeignore`:** Just like `.gitignore` prevents files from going to GitHub, you should create a `.claudeignore` file. This tells Claude Code to completely ignore sensitive files (like `.env`, `secrets.yaml`, or massive log files) so they are never read or sent to Anthropic's API.
3. **API Cost Management:** Claude Code uses the Anthropic API (likely Claude 3.7 Sonnet) under the hood. Unlike a $20/month flat subscription, this is billed per token. It is critical to use `/compact` or `/clear` frequently when working in large repos so you don't accidentally burn through API credits parsing the same massive files repeatedly.

---

## 🎤 5. Interview Readiness

**🔥 Common Interview Question:** *"If we integrate local AI CLI agents like Claude Code into our DevOps workflow, how do we prevent them from accidentally leaking our AWS credentials to the AI provider?"*
**Answer:** "We must implement strict boundary controls. Primarily, we ensure `.claudeignore` files are mandated at the root of all repositories, specifically ignoring `.env`, `~/.aws`, and any `*.tfvars` files. Additionally, we enforce minimum-privilege IAM roles on the developer laptops so even if the agent tries to run a destructive AWS command, the local session token will deny it."

**⚠️ The "Gotcha":** *"Does Claude Code run locally on my GPU?"*
**Answer:** No. Claude Code is a CLI *wrapper* that communicates with Anthropic's cloud APIs. Your code and prompts are sent over the internet to Anthropic's servers. For strictly air-gapped or high-compliance environments, you would need a truly local open-source model running via Ollama instead.

---

## 🧪 6. Free Playgrounds & Labs

If you want to practice terminal-based AI tools without risking your own local machine or accidentally executing dangerous commands, try these browser-based sandboxes:

1. **[GitHub Codespaces](https://github.com/features/codespaces)**: Gives you a free Linux container with a terminal in your browser. You can install `npm install -g @anthropic-ai/claude-code` safely here and let it analyze a test repo.
2. **[Killercoda (Ubuntu Playground)](https://killercoda.com/playgrounds)**: A sterile, disposable Ubuntu terminal environment. Perfect for testing how CLI agents interact with the OS.
3. **[Play with Docker](https://labs.play-with-docker.com/)**: Although primarily for Docker, you get root terminal access to test automation scripts safely before running them locally.
