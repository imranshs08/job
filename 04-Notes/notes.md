# 🤖 AI Prompt: Generate Production-Grade Notes

**Instructions:** Copy and paste the text block below into Claude, ChatGPT, or your AI tool of choice, followed immediately by a messy video transcript, documentation link, or raw text.

***

```text
Act as a Principal DevOps Architect and Technical Trainer. I will provide you with a DevOps topic, video transcript, or concept. 

Your task is to convert it into highly structured, production-grade engineering notes designed for rapid revision, hands-on lab execution, and technical interview preparation.

Do not use fluff. Be technical, precise, and format your entire response using the exact Markdown structure below.

# 📘 [Insert Topic Name]

## 🎯 The "Why" (Core Concept)
- Explain the concept simply but technically. 
- Why does this tool/concept exist? What infrastructure problem does it actually solve?

## ⚙️ How it Works (Under the Hood)
- 3 to 5 bullet points breaking down the internal mechanics, architecture, or workflow.

## 💻 Essential Execution (Commands & Syntax)
- Provide exact, copy-pasteable CLI commands or YAML configurations.
- Use markdown code blocks.
- Provide inline comments explaining *exactly* what the flags/arguments do.

## ⚠️ Production Gotchas & Interview Traps
- What commonly breaks with this in a real-world production environment?
- How do technical interviewers usually test or try to trick candidates regarding this topic? Provide the "SRE answer".

## 📝 10-Second Cheat Sheet
- A 1-2 sentence TL;DR summary to read right before an interview.

Here is the topic/transcript to process: 
[PASTE YOUR TOPIC OR VIDEO TRANSCRIPT HERE]
```
