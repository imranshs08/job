# 🎯 DevOps & SRE Interview Preparation

Welcome to the Interview Preparation directory. This folder tracks high-level technical deep dives, architectural breakdowns, and debugging scenarios structured specifically to help pass Senior-level DevOps and SRE interviews.

## 🤖 AI Prompt Generators

If you want to generate more standard template guides for this directory, or if you want to practice live with an AI, use the following tested and highly optimized prompt templates.

---

### 1. The "Ultimate Debug Guide" Generator
*Use this prompt to generate highly structured `[Topic]-Debug-Guide.md` files (like the K8s CrashLoopBackOff or Systemd guides).*

```text
[Paste your Scenario, Issue, or Error Log here]

=================

Act as a Principal Site Reliability Engineer (SRE). I need you to generate a "Production-Grade Debugging Guide" based on the disaster scenario provided above.

Please structure your entire response using the exact format below. Do not deviate from these phases:

# 🔥 Production-Grade Debugging Guide

## 🎯 Scenario
- Briefly describe the cluster, version, namespace, and symptom based on my input.

## 🧠 Core Concepts
- Provide 3-4 bullet points defining the foundational technologies involved.

## 📋 Phase 1: Triage — Confirm the Problem
- Provide the immediate CLI commands used to get the big picture (e.g., `kubectl get pods`, `systemctl`, etc.).
- Provide mock/simulated "Actual Output" showing the exact error or red flag. Highlight the red flag.

## 📋 Phase 2: Deep Dive — Logs & Resource Analysis
- Provide the CLI commands to dig into the container logs, pod metrics, or system logs.
- Provide mock "Actual Output" pinpointing the exact line where the failure occurs.

## 📋 Phase 3: The Fix
- Provide Option A (The Fastest/Inline Fix). Include the exact command.
- Provide Option B (The Proper/Manifest Edit).
- Provide Option C (The Emergency Rollback/Mitigation).

## 📋 Phase 5: Verify the Fix
- Provide the commands to verify the system is stable and the error has stopped. Include mock output proving the fix worked.

## 📋 Phase 6: Root Cause Summary & Prevention
- Add a table summarizing What broke, Why it broke, and the Exit Code.
- Provide a "Prevention Checklist" (e.g., configuring alerts, setting resource limits) with exact commands.

## 🧠 Debug Decision Tree
- Create an ASCII text decision tree showing how to visually run through this type of error logically. (e.g., Pod not Ready? -> Check Status -> If CrashLoop: Check Logs).

## ⚡ Quick Reference Commands
- A block of 5-8 continuous commands I can copy/paste in an emergency related to this issue.
```

---

### 2. The "Active Mock Interviewer" Prompt
*Use this prompt in ChatGPT or Claude for an interactive chat session to practice thinking on your feet and answering out loud.*

```text
Act as a Lead Cloud Architect / SRE Manager at a top-tier tech company. I am preparing for a Senior DevOps Engineer interview.

The topic I want to be interviewed on today is: [INSERT TOPIC HERE - e.g., "Kubernetes Pod CrashLoopBackOff", "Terraform State Management"]

Please conduct a rigorous mock interview by strictly following these rules:
1. Ask me 3 challenging questions based on the topic. The questions should be formatted as follows:
   - Question 1 (Technical Deep Dive): Ask me to explain how a specific mechanism works under the hood.
   - Question 2 (Scenario / Troubleshooting): Give me a high-pressure production outage scenario and ask exactly how I would debug and mitigate it.
   - Question 3 (Behavioral / STAR): Ask me a behavioral question about a time I successfully implemented this or failed while using it.
2. Ask me ONLY ONE question at a time. Do NOT provide the answers. Wait for my response.
3. Once I reply, critique my answer strictly. Tell me exactly what I missed, how I could have sounded more senior, and if I forgot to mention business impact.
4. Finally, provide me with the "Perfect 10/10 Senior Answer" framework for that specific question so I can study it.

Are you ready? Please ask me the first question.
```
