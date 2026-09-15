# 🤖 Claude Certified Developer – Foundations (CCDV-F) Mock Exam Bank

> **Sprint Dates:** Nov 30, 2026 – Dec 5, 2026
> **Exam Format:** 120 Minutes | 53 Multiple Choice/Response | **72% to Pass**

This document houses the official exam prep strategy and baseline mock questions to drill before your Dec 6 exam. The actual exam is highly technical and implementation-focused—you cannot pass on conceptual knowledge alone.

---

## 🔗 Official Prep Resources & Playlists

If you need more external practice tests to run during the Mock Exam sprint, use these vetted platforms:

1. **Anthropic Official Cookbook** (`github.com/anthropics/anthropic-cookbook`) 
   * *Why:* The exam pulls heavily from their official examples for Prompt Engineering and Tool Use syntax.
2. **FlashGenius** (`flashgenius.net`)
   * *Why:* Offers a free baseline Claude Developer practice test covering all 8 exam domains.
3. **Udemy Practice Exams** 
   * *Why:* Search for "CCDV-F" or "Claude Certified Developer". These are full 53-question timed simulators weighted exactly to the official Anthropic blueprint.
4. **YouTube Technical Walkthroughs**
   * *Why:* Search for *"CCDV-F practice exam walkthrough"*. These videos break down the reasoning behind specific technical questions like tracking Conversation History tokens and building nested agents.

---

## 📝 Practice Questions

Here are 10 highly realistic technical questions based on the official blueprint domains (API, Prompt Engineering, Tool Use, MCP, and Security).

### Domain 1: Messages API & SDK Setup
**Q1. You are initializing the Claude API in Python. You want to pass a global instruction that dictates Claude's persona across the entire conversation. How must this be implemented using the `anthropic` SDK?**
- [ ] A) Append `{"role": "system", "content": "You are a helpful assistant"}` to the messages array.
- [ ] B) In the `client.messages.create()` call, set the top-level property `system="You are a helpful assistant"`.
- [ ] C) Pre-fill the assistant response with the persona definition.
- [ ] D) Pass the persona in the `metadata` JSON object.
> **Answer: B.** Unlike OpenAI, Claude strictly separates the `system` prompt from the `messages` array payload. It must be provided as a top-level string (or array of text blocks).

### Domain 2: Prompt Engineering & Formatting
**Q2. You are asking Claude to extract unstructured text into a specific XML schema. The model keeps failing by prefacing the XML with conversational filler (e.g., "Here is the parsed data:"). What is the Claude-native way to force strict adherence?**
- [ ] A) Set `temperature=0` and `top_p=0.1`.
- [ ] B) Write `"DO NOT INCLUDE CONVERSATIONAL FILLER"` in all caps 5 times.
- [ ] C) Pre-fill the final message in the array as `{"role": "assistant", "content": "<data>"}`.
- [ ] D) Add a `stop_sequence` for the word "Here".
> **Answer: C.** Pre-filling the assistant's message forces Claude to continue generating exactly from that token, bypassing the conversational preamble entirely.

### Domain 3: Tool Use (Function Calling)
**Q3. When defining a tool in the `tools` array for Claude 3.5 Sonnet, what format must the `input_schema` follow?**
- [ ] A) OpenAPI 3.0 specification.
- [ ] B) JSON Schema.
- [ ] C) Anthropic proprietary XML definitions.
- [ ] D) GraphQL schema definitions.
> **Answer: B.** Tool definitions in Claude require a standard JSON Schema object representing the parameters you want Claude to fulfill.

**Q4. You send a request with a tool definition for `get_weather`. Claude decides to call the tool. How will you know to halt your loop and execute the local function?**
- [ ] A) `stop_reason` is `"function_call"`.
- [ ] B) `stop_reason` is `"tool_use"`.
- [ ] C) Claude outputs raw JSON in the `content` block.
- [ ] D) The API throws a `ToolInvocationException`.
> **Answer: B.** The exact string returned by the API when Claude triggers a tool is `"tool_use"`.

### Domain 4: Model Context Protocol (MCP)
**Q5. What is the fundamental purpose of the Model Context Protocol (MCP) in Claude agent architectures?**
- [ ] A) It compresses conversational history to reduce token spend.
- [ ] B) It standardizes how AI agents securely connect to external data sources (like local file systems, Slack, databases).
- [ ] C) It is Anthropic's proprietary caching layer for the `system` prompt.
- [ ] D) It provides a UI layout for Claude Chat.
> **Answer: B.** MCP provides a universal, standardized way for AI models to connect securely to external data sources and tools without writing custom integration code for every API.

### Domain 5: Economics & Optimization
**Q6. You are building an agent that must quickly classify 10,000 short support tickets per day into a static list of 5 categories. Cost and latency are your primary concerns. Which model should you choose?**
- [ ] A) Claude 3 Opus
- [ ] B) Claude 3.5 Sonnet
- [ ] C) Claude 3.5 Haiku
- [ ] D) Claude Instructor
> **Answer: C.** Claude 3.5 Haiku is the fastest and most cost-effective model, designed specifically for rapid categorization, OCR, and high-volume data extraction tasks.

**Q7. You are utilizing Prompt Caching to save costs on a massive 50,000-token system prompt. How long does the cache physically stay alive without any subsequent hits?**
- [ ] A) 5 minutes
- [ ] B) 1 hour
- [ ] C) 24 hours
- [ ] D) 72 hours
> **Answer: A.** Currently, Anthropic's Prompt Caching keeps the cache warm for 5 minutes. If it receives another request hitting the same prefix within 5 minutes, the timer resets.

### Domain 6: Advanced Tool Use Execution
**Q8. After executing a tool locally on your backend, how must the result be appended to the conversation history before sending it back to Claude?**
- [ ] A) As a `system` message.
- [ ] B) As a `user` message containing a `tool_result` content block with the matching `tool_use_id`.
- [ ] C) As an `assistant` message containing the raw JSON.
- [ ] D) It is passed via the `metadata` header.
> **Answer: B.** The result of a tool execution must be sent back as a `user` message with a content block of type `tool_result`, explicitly citing the `tool_use_id` that Claude originally requested.

### Domain 7: Vision & OCR
**Q9. When passing an image to Claude for visual analysis, what image format is explicitly unsupported by the Messages API?**
- [ ] A) JPEG
- [ ] B) PNG
- [ ] C) WebP
- [ ] D) SVG
> **Answer: D.** Vector graphics like SVG are not supported natively by the vision API. Supported formats typically include JPEG, PNG, GIF, and WebP (converted to base64).

### Domain 8: Security & Guardrails
**Q10. You want to ensure Claude does not hallucinate malicious code during a software generation task. What is the most robust Anthropic-recommended security pattern?**
- [ ] A) Append "Do not write bad code" to the user query.
- [ ] B) Use XML tags to separate the secure instructions `<instructions>` from the user-provided untrusted input `<untrusted_input>`.
- [ ] C) Decrease the `max_tokens` limit.
- [ ] D) Use the `security_level=high` parameter in the SDK.
> **Answer: B.** XML tagging is heavily baked into Claude's fine-tuning. By completely wrapping untrusted user input in explicit tags, and telling the system prompt to treat anything in those tags as untrusted data, you severely reduce prompt injection risks.
