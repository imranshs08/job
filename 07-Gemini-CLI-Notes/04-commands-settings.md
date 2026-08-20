# #4 — Commands & Settings
> 🔗 [Watch Video](https://www.youtube.com/watch?v=IUnoewBv2AY) | **Status:** ☐ Watched

---

## 📝 Summary
Gemini CLI has built-in slash commands that control its behaviour from within the REPL. This video covers all the key built-in commands, how to configure settings (like model selection, theme, and safety filters), and where config files are stored on your system.

## 🔑 Key Concepts
- **Slash commands** (`/command`) = control Gemini CLI behaviour mid-session
- **Settings** stored in `~/.gemini/settings.json` (global) or project-level config
- You can switch Gemini models (Flash vs Pro) depending on speed vs quality needs
- Theme, sandbox mode, and telemetry can all be toggled

## 💻 Built-in Slash Commands
```
/help          → List all available commands
/clear         → Clear the conversation context
/quit          → Exit Gemini CLI
/chat          → Switch to pure chat mode (no file access)
/memory        → Show what Gemini knows about your project
/theme         → Change terminal color theme
/stats         → Show token usage for the session
/model         → Switch between Gemini models (Flash / Pro)
```

## ⚙️ Settings File Location
```bash
# Global settings
~/.gemini/settings.json          # Windows: C:\Users\imran\.gemini\settings.json

# View/edit settings
cat ~/.gemini/settings.json
```

## 🔧 Example settings.json
```json
{
  "model": "gemini-2.0-flash",
  "theme": "dark",
  "telemetry": false,
  "sandbox": false
}
```

## 🤖 Model Comparison
| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| `gemini-2.0-flash` | ⚡ Fast | Good | Daily use, quick edits |
| `gemini-2.5-pro` | 🐢 Slower | Excellent | Complex refactors, architecture |

## ❓ Questions / Unclear Points
- Can settings be overridden per-project? (Yes — via project-level config or GEMINI.md)
- Does `/clear` affect the GEMINI.md context? (No — GEMINI.md is always reloaded)

## ✅ Action Items
- [ ] Run `/help` to see all commands available in your version
- [ ] Check `~/.gemini/settings.json` and set `"telemetry": false`
- [ ] Try switching models with `/model` and compare response quality
