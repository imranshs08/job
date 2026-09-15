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
* **Vanderbilt University - Prompt Engineering for ChatGPT/Claude**: (Best for core fundamentals of zero-shot, few-shot, and chain of thought).
* **Dave Ebbelaar - AI Agents & LangChain**: (Crucial for understanding how Claude Tool Use actually works in production Python scripts).
* **Anthropic Official Developer Videos**: Deep dives on using the Messages API, Vision API, and JSON scaling.

---

## 🗓️ The 11-Week Weekend Syllabus

### Week 1: Prompt Engineering Fundamentals (Sep 19–20)
* **Saturday (Theory):** 
  * The anatomy of a Claude Prompt. 
  * System Prompts vs User Prompts.
  * The strict requirement of `<XML>` tags for Claude (Claude is heavily trained to parse XML unlike GPT).
* **Sunday (Practice):**
  * Write 5 prompts using `<context>`, `<instructions>`, and `<output_format>` XML brackets.
  * Practice *Few-Shot Prompting* (providing 3 examples to Claude before asking the final question).

### Week 2: Context Windows & Output Parsing (Sep 26–27)
* **Saturday:**
  * Context Window limitations (200k tokens).
  * Prompt chunking strategies.
  * Forcing Claude into `Prefill` responses (e.g., forcing Claude's response to start with `{ "status": `).
* **Sunday:**
  * Build a prompt that forces Claude to ONLY output raw JSON without any markdown formatting using `Prefill`.

### Week 3: Python/JS SDK & Messages API (Oct 3–4)
* **Saturday:**
  * Setup your local Python environment (`pip install anthropic`).
  * Understand the `Messages` API structure (`role: user`, `role: assistant`).
  * Injecting `system` parameters at the API level (it is *not* a message role in Claude 3; it is a top-level parameter).
* **Sunday:**
  * Write a basic Python script that queries the `claude-3-5-sonnet-20240620` model.
  * Handle the API response object natively in Python.

### Week 4: Streaming, Tokens, & Cost (Oct 10–11)
* **Saturday:**
  * Implement `stream=True` in the Python SDK.
  * Tracking `input_tokens` and `output_tokens`.
* **Sunday:**
  * Understand the token costs (Haiku vs Sonnet vs Opus).
  * Build a cost calculator Python script for a 1M token workload.

### Week 5: Tool Use / Function Calling [Part 1] (Oct 17–18)
* **Saturday:**
  * What is Tool Use? (Giving Claude the ability to access external APIs like Weather, Databases, or GitHub).
  * Defining the JSON Schema for a tool definition.
* **Sunday:**
  * Define a `get_stock_price(ticker)` tool in JSON and pass it in the `tools` array to Claude using Python.

### Week 6: Tool Use / Function Calling [Part 2] (Oct 24–25)
* **Saturday:**
  * Handling Claude's `tool_use` Stop Reason.
  * Executing the local Python function and returning the `tool_result` back to Claude.
* **Sunday:**
  * Build a fully functioning local chatbot that can fetch real-time weather data.

### Week 7: Vision API capabilities (Oct 31–Nov 1)
* **Saturday:**
  * Base64 encoding images.
  * Injecting multimodal blocks into the Messages API.
* **Sunday:**
  * Pass a screenshot of a Kubernetes Dashboard to Claude and ask it to diagnose the failing Pod via Python.

### Week 8: Advanced Agentic Workflows (Nov 7–8)
* **Saturday:**
  * Chain-of-Thought (CoT) prompting.
  * RAG (Retrieval-Augmented Generation) fundamentals.
* **Sunday:**
  * Build an orchestration script where Claude-Haiku categorizes an email, and Claude-Sonnet writes the response.

### Week 9: Security, Bias & Prompt Injection (Nov 14–15)
* **Saturday:**
  * Spotting Prompt Injection attacks (Jailbreaks).
  * Using Claude's pre-and-post filtering capabilities.
* **Sunday:**
  * Write a system prompt that explicitly defends against a user trying to make the bot drop a database table.

### Week 10: Optimization & Production Scaling (Nov 21–22)
* **Saturday:**
  * Prompt Caching (A massive Claude 3.5 feature).
  * Error Handling (Rate limits, Overloaded errors - HTTP 429 & 529).
* **Sunday:**
  * Refactor your Week 3 Python script to include Python `try/except` blocks and exponential backoff.

### Week 11: Mock Exams & Drills (Nov 28–29)
* **Saturday:** Review all Cheat Sheets (API structure, SDK commands, XML tags).
* **Sunday:** Build a capstone project using Prompt Caching, Tool Use, and System Prompts in a single 200-line Python script.

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
