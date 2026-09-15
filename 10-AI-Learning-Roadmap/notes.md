# 🤖 Claude Developer – SRE Note Generation Prompts

As you progress through the 11-week Claude Developer syllabus, you should convert the video transcripts or your raw learning into highly structured, enterprise-grade SRE cheat sheets. 

Use the prompts below whenever you want an AI (ChatGPT or Claude) to generate notes for your `04-Notes` directory based on what you just learned. These prompts forcibly constrain the AI to output exactly the format expected in your DevOps 2027 Command Center.

---

## 🛠️ Prompt 1: The Core Architecture Concept (For Theory Videos)
*Use this prompt after watching architecture videos like "SDK vs API vs Managed Agents" or "Understanding MCP".*

> **Copy & Paste this into AI:**
> "I just studied [INSERT TOPIC, e.g., The Claude Messages API vs OpenAI API]. Act as a Senior AI Platform Engineer. Generate a highly structured Markdown cheat sheet for my DevOps notebook. You MUST strictly follow this architecture:
> 
> 1. **The Why (Analogy):** Explain the core concept using a real-world infrastructure analogy (like load balancers or DNS) so it makes intuitive sense to a DevOps engineer.
> 2. **Architecture:** A concise bulleted overview of how the components interact. Use a Mermaid diagram if applicable.
> 3. **Execution Commands:** The exact CLI commands or Python SDK bash snippets required to implement this.
> 4. **Production Gotchas & Interview Traps:** Highlight realistic security risks, token consumption traps, or tricky edge cases that an interviewer would ask about.
> 
> Output ONLY the markdown content, ready to be saved to a `.md` file."

---

## 💻 Prompt 2: The Code Implementation (For Toolkit & SDK Videos)
*Use this prompt after watching "Ep 03: Custom Tools", "Prompt Caching", or "Structured JSON".*

> **Copy & Paste this into AI:**
> "I am studying how to implement [INSERT TOPIC, e.g., Pre-filling Claude's Assistant Role for Structured JSON Output]. Act as a Senior SRE and Python Developer. Generate a technical reference markdown document.
> 
> Please use this exact structure:
> 
> 1. **The Objective:** 2 sentences on what this code achieves.
> 2. **The JSON/Python Payload:** Provide the exact clean, comment-annotated code snippet (Python using `anthropic` SDK).
> 3. **Step-by-Step Breakdown:** Bullet points explaining the key variables (e.g., why we use `stop_reason`).
> 4. **Defensive Coding:** Add a GitHub `> [!WARNING]` alert block detailing what happens if the API fails or how to handle rate limits/timeout exceptions for this specific feature.
> 
> Do not use conversational filler. Give me pure, copy-pasteable Markdown."

---

## 🚨 Prompt 3: Security & Guardrails (For Enterprise Implementation)
*Use this prompt after watching "Ep 04: Hooks, Guardrails & Security".*

> **Copy & Paste this into AI:**
> "I need to document enterprise security guardrails for [INSERT TOPIC, e.g., Preventing Claude Hallucinations during Tool Use]. 
> 
> Generate a security posture playbook using this structure:
> 1. **Threat Vector:** What could maliciously go wrong? (e.g., Prompt Injection).
> 2. **XML Guarding Strategy:** Show exactly how to use Anthropic's `<tags>` logic to sandbox untrusted user input.
> 3. **Validation Layer:** How should a DevOps engineer validate the API output locally before executing it?
> 4. **Incident Response:** What happens when Claude returns a compromised payload, and how do we fail securely?
> 
> Present this clearly using GitHub alert blocks (`> [!CAUTION]`) where appropriate."

---

## 🎯 How to Store These Notes
When the AI generates the Markdown using these prompts, save them directly to:
`C:\Job Tracker\04-Notes\09-AI-Platform-Engineering\` (Create this folder if it doesn't exist). 

Keep the file names lowercase with hyphens (e.g., `claude-tool-use-architecture.md`).
