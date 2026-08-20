# #10 — Using the Nanobanana Extension
> 🔗 [Watch Video](https://www.youtube.com/watch?v=snAzb5bKFww) | **Status:** ☐ Watched

---

## 📝 Summary
Nanobanana is a lightweight MCP extension that gives Gemini CLI the ability to **browse the web** — fetch URLs, read page content, and take screenshots. With it installed, you can ask Gemini to "check the Kubernetes docs for the latest PDB spec" or "find the current AWS EC2 pricing for t3.medium" without leaving your terminal. This video shows how to install it and example use cases.

## 🔑 Key Concepts
- **Nanobanana** = MCP server that adds web browsing to Gemini CLI
- Can fetch any public URL and return its text content to Gemini
- Can take screenshots of web pages (useful for UI debugging)
- Runs as a local Node.js process — no cloud service involved
- Completely free — uses your local browser engine (Playwright/Chromium headless)

## 💻 Installation
```bash
# Install nanobanana MCP server
npm install -g nanobanana

# Verify install
npx nanobanana --version
```

## ⚙️ Add to Gemini CLI Config
```json
// ~/.gemini/settings.json
{
  "mcpServers": {
    "nanobanana": {
      "command": "npx",
      "args": ["nanobanana"]
    }
  }
}
```

## 🔧 Example Use Cases
```
> Fetch the Kubernetes docs page for PodDisruptionBudget and summarise the spec fields

> Go to https://k8s.io/docs/concepts/workloads/pods/ and extract all the key concepts as bullet points

> Check the current GitHub status at https://githubstatus.com and tell me if there are any incidents

> Browse https://aistudio.google.com and tell me the current free rate limits for Gemini models

> Screenshot https://cloud.google.com/kubernetes-engine/pricing and summarise the pricing tiers
```

## 💡 DevOps Use Cases
| Task | Nanobanana Prompt |
|------|--------------------|
| Read K8s docs | "Fetch the kubectl cheat sheet from kubernetes.io" |
| Check Azure pricing | "Go to azure.com/pricing/calculator and get VM pricing for B2s" |
| Read GitHub README | "Fetch the README from github.com/imranshs08/job" |
| Latest CKA curriculum | "Check the CNCF CKA exam curriculum page and list all domains" |
| Terraform doc lookup | "Fetch the Terraform azurerm_kubernetes_cluster resource docs" |

## ⚠️ Limitations
- Can't log into authenticated sites (no cookies/sessions)
- Some sites block headless browsers (returns empty or captcha)
- Screenshots require a display or virtual framebuffer on Linux servers
- Rate-limited by the target website, not by Google

## 🔗 Useful Links
- Nanobanana GitHub: https://github.com/nicholasgasior/nanobanana
- MCP Servers list: https://github.com/modelcontextprotocol/servers
- Playwright (underlying engine): https://playwright.dev

## ❓ Questions / Unclear Points
- Can it fill out forms or click buttons? (Limited — primarily for reading content)
- Does it store browsing history? (No — stateless per request)

## ✅ Action Items
- [ ] Install nanobanana: `npm install -g nanobanana`
- [ ] Add to `~/.gemini/settings.json` under `mcpServers`
- [ ] Test: "Fetch https://kubernetes.io/docs/reference/kubectl/cheatsheet/ and summarise the most useful commands"
- [ ] Try fetching the latest CKA exam curriculum from the CNCF website
