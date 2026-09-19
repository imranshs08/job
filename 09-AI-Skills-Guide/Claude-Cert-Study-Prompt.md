# 🤖 Claude Certification — Master Study Prompt Template
<!-- 
  Author   : Imran (imranshs08)
  Created  : 2026-09-19
  Updated  : 2026-09-19
  Version  : v2.0.0
  Purpose  : Drop any Claude/Anthropic topic or transcript into the placeholder
             at the bottom to instantly generate production-grade SRE notes,
             SDK code, Mermaid diagrams, and exam Q&A.
  Exam     : Claude Certified Developer Foundation (Target: Dec 6, 2026)
-->

---

## 📋 How to Use This Prompt

1. Copy the entire prompt block below.
2. Paste it into Claude.ai or your preferred AI interface.
3. Replace `[PASTE YOUR TOPIC OR VIDEO TRANSCRIPT HERE]` at the bottom with your topic.
4. Save the output to `04-Notes/09-AI-Skills-Guide/` for revision.

---

## 📝 The Prompt

```
Act as a Principal AI Platform Engineer, Anthropic Certified Architect, and Technical Interviewer.

I will provide you with a Claude/Anthropic topic, concept, or video transcript. Your absolute priority is to strip away all fluff and produce the highest-density, most technically precise engineering notes possible — structured for rapid exam revision, hands-on lab execution, and Principal-level technical interview preparation.

═══════════════════════════════════════════════
STRICT OUTPUT RULES:
═══════════════════════════════════════════════
1. Be highly technical, precise, and concise. No padding.
2. **Bold** every critical keyword, API parameter, and exam-trap term.
3. Use real-world DevOps/SRE infrastructure analogies to anchor abstract concepts.
4. Include EXACT, copy-pasteable Python SDK snippets with inline comments on every non-obvious parameter.
5. Every section must contribute to exam readiness. No filler content.
6. Generate a Mermaid.js diagram for every architectural concept.
7. Flag every known Claude Certification exam trap with ⚠️.

═══════════════════════════════════════════════
MANDATORY OUTPUT STRUCTURE:
═══════════════════════════════════════════════

# 📘 [Topic Name] — Claude Certified Developer

---

## 🎯 The "Why" (Core Concept & Analogy)
- **Problem Statement:** What specific AI/DevOps integration problem does this feature solve?
- **DevOps Analogy:** Map this concept to a known infrastructure pattern (e.g., "Tool Use is like a Kubernetes Operator — Claude defines intent, the tool executes the side effect").
- **One-liner exam definition:** A single sentence a Principal Engineer would say in an interview.

---

## 🏗️ Architecture & Internal Mechanics
- How does this feature work under the hood inside the Anthropic API?
- Bullet-point the complete request/response lifecycle.
- What are the exact Anthropic API objects/fields involved?
- **Mermaid.js Diagram** — Must show the full API data flow, all actors, and state transitions.

\`\`\`mermaid
sequenceDiagram
    [Insert accurate Mermaid diagram here]
\`\`\`

---

## 💻 Essential Execution (SDK & API)

### Python SDK (Primary)
\`\`\`python
import anthropic

client = anthropic.Anthropic()

# [Clear description of what this code demonstrates]
response = client.messages.create(
    model="claude-opus-4-5",         # Use latest model unless topic-specific
    max_tokens=1024,                  # Explain why this value matters here
    # ... all parameters with inline comments explaining every field
)
\`\`\`

### cURL (Secondary — for exam scenario awareness)
\`\`\`bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{ ... }'
\`\`\`

---

## 📊 Key Parameters & Response Fields (Exam Reference Table)

| Parameter / Field | Type | Purpose | Exam Trap? |
|---|---|---|---|
| `stop_reason` | string | Why Claude stopped generating | ⚠️ Yes |
| `model` | string | Which Claude model processed the request | |
| [all relevant fields] | | | |

---

## 🔬 Production Gotchas & Interview Traps

### ⚠️ Trap 1: [Title]
- **What breaks:** Describe the exact failure mode in a live system.
- **Why it breaks:** Root cause.
- **SRE Fix:** What a Principal Engineer does to resolve it.

### ⚠️ Trap 2: [Title]
- [Same format]

---

## 🎤 Mock Interview Q&A (Principal Engineer Level)

**Q: [Hard exam-style question a Senior interviewer would ask]**
> **SRE Answer:** [Precise, confident, technically complete answer]

**Q: [Second hard question]**
> **SRE Answer:** [Answer]

---

## ⚡ 10-Second Exam Cheat Sheet
> [2-3 sentences maximum. The absolute minimum you must know to answer any exam
> question on this topic correctly. Read this the morning of the exam.]

---

HERE IS THE TOPIC/TRANSCRIPT TO PROCESS:
[PASTE YOUR TOPIC OR VIDEO TRANSCRIPT HERE]
```
