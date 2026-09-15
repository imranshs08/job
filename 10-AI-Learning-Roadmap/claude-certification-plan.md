# 🤖 Claude Certified Developer Foundation — 11-Week Blueprint

> **Exam Target Date:** December 6, 2026
> **Pace:** Weekend Warrior (Saturdays & Sundays ONLY)
> **Preparation Style:** 100% Coverage (Theory, SDK, APIs, Prompt Engineering, Tool Use)

This master syllabus is designed for a DevOps engineer transitioning into AI Platform Engineering. It restricts all learning strictly to the weekends, protecting your weekday cycles for Kubernetes and Azure.

---

## 📚 Curriculum & Ultimate Resources

### 1. Official Documentation (The Source of Truth)
* [Anthropic API Documentation](https://docs.anthropic.com/en/api/getting-started) 
* [Anthropic Prompt Engineering Interactive Tutorial (Google Sheets/Colab)](https://docs.anthropic.com/en/docs/prompt-engineering) *(Mandatory)*
* [Anthropic Cookbook (GitHub)](https://github.com/anthropics/anthropic-cookbook)

### 2. High-Impact YouTube Playlists
* **[The Ultimate Build-Along Course: Claude Certified Developer](https://www.youtube.com/playlist?list=PLYrYhzAmVyKU):** 
  * This is the definitive 15-part video series (featuring a 12-episode core build-along) designed specifically for this exam. 
  * We have mapped these exact episodes directly into your 11-week syllabus below.

---

## 🗓️ The 11-Week Weekend Syllabus (With Playlist Integration)

### Week 1: Foundation & The Raw API (Sep 19–20)
* **Saturday (Theory):** 
  * Watch: **New Claude Certifications Are Coming: Here's What's Actually Confirmed**
  * Watch: **Claude Agent SDK vs API vs Managed Agents: Which Should You Actually Use?**
* **Sunday (Practice):**
  * Watch & Code: **Ep 01 | Your First Agent on the Raw Messages API**

### Week 2: Mastering the Local SDK (Sep 26–27)
* **Saturday:**
  * Watch & Code: **Ep 02 | Claude Agent SDK Explained From Zero**
* **Sunday:**
  * Build a baseline local Python script querying `claude-3-5-sonnet-20240620`. Handle the response payload gracefully.

### Week 3: Tool Use & MCP (Oct 3–4)
* **Saturday:**
  * Watch & Code: **Ep 03 | Custom Tools & MCP**
* **Sunday:**
  * Define a `get_stock_price(ticker)` tool in JSON and pass it in the `tools` array to Claude using Python.

### Week 4: Hooks, Guardrails & Security (Oct 10–11)
* **Saturday:**
  * Watch & Code: **Ep 04 | Hooks, Guardrails & Security**
* **Sunday:**
  * Test input constraints. Write a system prompt that explicitly limits Claude from executing unsafe tool payloads.

### Week 5: Multi-Agent Architectures (Oct 17–18)
* **Saturday:**
  * Watch & Code: **Ep 05 | Subagents & Multi-Agent Orchestration**
* **Sunday:**
  * Implement an orchestration pattern where `Haiku` routes an intent, and `Sonnet` executes the heavy lifting.

### Week 6: State & Memory Management (Oct 24–25)
* **Saturday:**
  * Watch & Code: **Ep 06 | Agent Memory, Sessions, Resume & Forking**
* **Sunday:**
  * Build a chatbot that remembers context from Turn 1 when answering Turn 5.

### Week 7: Structured Output (Oct 31–Nov 1)
* **Saturday:**
  * Watch & Code: **Ep 07 | Structured Output Handling**
* **Sunday:**
  * Pre-fill the `assistant` message with `{` to force Claude to output pure, parseable JSON without conversation filler.

### Week 8: Advanced Skills (Nov 7–8)
* **Saturday:**
  * Watch & Code: **Ep 08 | Claude Agent Skills: Build & Chain Two Real Skills**
* **Sunday:**
  * Chain an API fetch skill directly into a formatting presentation skill.

### Week 9: Model Context Protocol (MCP) Deep Dive (Nov 14–15)
* **Saturday:**
  * Watch & Code: **Ep 09 | How AI Agents Actually Use MCP**
* **Sunday:**
  * Draft a conceptual MCP server wrapper that connects Claude to your local filesystem securely.

### Week 10: Economics & System Profiling (Nov 21–22)
* **Saturday:**
  * Watch: **Claude Certified Architect vs Developer: What Nobody Tells You (2026 Update)**
  * Watch: **Ep 10 | Opus vs Sonnet vs Haiku, Thinking & Effort**
* **Sunday:**
  * Watch & Code: **Ep 11 | Prompt Caching, Token Costs & Error Handling Explained**
  * Calculate token spend profiles between standard calls and Cached calls.

### Week 11: Anthropic Managed Agents & Mock Exams (Nov 28–29)
* **Saturday:** 
  * Watch & Code: **Ep 12 | Claude Managed Agents: Let Anthropic Run It**
* **Sunday:** 
  * Build a final Capstone Project deploying a fully managed agent, linking all 12 modules together!

---

## 🎯 December 6, 2026 — EXAM DAY

*   Review the Security and Prefixing cheat sheets.
*   Log into the certification portal 15 minutes early.

---

## ❓ 5 Sample Benchmark Questions

1. **API Structure:** In the Claude 3 Messages API, how do you provide system instructions, and how is it fundamentally different from OpenAI?
   > *Answer:* You pass it into the top-level `system` property, not as a message in the messages array (like OpenAI's `role: system`).
2. **Formatting:** Why should you always use `<tags>` instead of `[brackets]` or `*markdown*` when defining complex rules for Claude?
   > *Answer:* Anthropic heavily fine-tuned Claude to respect and parse XML tags cleanly, reducing hallucination.
3. **Tool Use:** When Claude decides to use a tool, what `stop_reason` does the API return?
   > *Answer:* `tool_use`.
4. **Prefilling:** How do you guarantee Claude responds in exact JSON format without conversational filler (like "Here is your JSON:")?
   > *Answer:* Pre-fill the assistant's message with `{` in the messages array.
5. **Costing:** Which model is the fastest and cheapest for categorization workloads?
   > *Answer:* Claude 3.5 Haiku.
