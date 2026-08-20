# #9 — MCP Servers & Extensions
> 🔗 [Watch Video](https://www.youtube.com/watch?v=SwDofnGOwsU) | **Status:** ☐ Watched

---

## 📝 Summary
MCP (Model Context Protocol) is an open standard that lets AI models connect to external tools and data sources. Gemini CLI supports MCP servers as **extensions** — they give Gemini new capabilities beyond files and shell commands: web browsing, database access, GitHub integration, and more. This video covers what MCP is, how to find extensions, and how to add them to your Gemini CLI config.

## 🔑 Key Concepts
- **MCP** = Model Context Protocol — open standard by Anthropic, adopted broadly
- **MCP Server** = a local or remote process that exposes tools to the AI
- Gemini CLI reads MCP config from `.gemini/settings.json` or `~/.gemini/settings.json`
- Each MCP server exposes "tools" that Gemini can call (e.g., `search_web`, `query_db`)
- Extensions dramatically expand what Gemini CLI can do autonomously

## 🏗️ How MCP Works
```
Your Prompt → Gemini CLI
                  ↓
          Selects relevant MCP tool
                  ↓
          Calls MCP Server (local process)
                  ↓
          Gets result back
                  ↓
          Uses result to answer / continue task
```

## 💻 Adding MCP Servers to Config
```json
// .gemini/settings.json or ~/.gemini/settings.json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allow"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token-here"
      }
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your-key-here"
      }
    }
  }
}
```

## 🔌 Popular MCP Servers
| Server | What It Does | Install |
|--------|-------------|---------|
| `@mcp/server-filesystem` | Read/write files with directory restrictions | npm |
| `@mcp/server-github` | Read repos, PRs, issues | npm |
| `@mcp/server-brave-search` | Search the web | npm |
| `@mcp/server-postgres` | Query PostgreSQL databases | npm |
| `@mcp/server-kubernetes` | Interact with K8s clusters | npm |
| `nanobanana` | Web browsing + screenshots | npm |

## 🌐 Where to Find MCP Servers
- Official list: https://github.com/modelcontextprotocol/servers
- Community: https://mcp.so
- npm search: `npm search modelcontextprotocol`

## ❓ Questions / Unclear Points
- Are MCP servers safe? (Only install from trusted sources — they run locally with your system access)
- Do they work offline? (No — most need internet to function)

## ✅ Action Items
- [ ] Read the MCP specification: https://modelcontextprotocol.io
- [ ] Try the GitHub MCP server: connect Gemini to your `imranshs08/job` repo
- [ ] Browse https://mcp.so for DevOps-relevant extensions (K8s, Terraform, GitHub)
