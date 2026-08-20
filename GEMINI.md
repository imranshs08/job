# GEMINI.md — Project Context & Instructions

This file provides the foundational context for Gemini CLI interactions within the **DevOps Job Switch 2027 — Command Center** workspace.

---

## 🚀 Project Overview

**DevOps Job Switch 2027** is a high-intensity, structured transition program designed to take a learner from Zero to Hero in DevOps and AI by January 1, 2027. The repository serves as a "Command Center" for tracking study progress, labs, certifications, and career marketing efforts.

### 🎯 Key Goals
- **Certifications:** Secure **CKA** (Target: Jan 1, 2027) and **AZ-104** (Target: Jan 15, 2027).
- **Primary Curriculum:** Abhishek Veeramalla’s "DevOps Engineer in 3 Months" (158 videos).
- **Specialization:** Integration of AI (Claude, ChatGPT, AI Agents) into DevOps workflows.
- **Career:** Transition to a DevOps/SRE role with a focus on AI Platform Engineering.

---

## 📂 Directory Structure & Key Files

| Directory/File | Purpose |
|----------------|---------|
| `01-Roadmap/` | 5-month master plan and milestone breakdown. |
| `02-Weekly-Plan/` | Granular week-by-week study schedule. |
| `03-Progress-Tracker/` | Detailed per-video and per-lab checkbox tracker. |
| `04-Notes/` | Subject-matter notes (K8s, Docker, Terraform, Linux, etc.). |
| `05-Portfolio-Projects/` | Real-world hands-on DevOps projects. |
| `06-Certifications/` | Specialized trackers for CKA (KodeKloud) and AZ-104 exams. |
| `07-Interview-Prep/` | Technical and behavioral question banks (STAR method). |
| `08-Career-Marketing/` | Job hunt checklists, resume templates, and LinkedIn strategies. |
| `09-AI-Skills-Guide/` | Claude, ChatGPT, AI Agents for DevOps. |
| `10-AI-Learning-Roadmap/` | Parallel AI track with Udemy & YouTube courses. |
| `11-Labs-and-Validation/` | Hands-on test labs. |
| `12-Gemini-CLI-Notes/` | Documentation for using Gemini CLI to manage this workspace. |
| `13-Video-Tracker/` | YouTube playlist tracking and future AI Platform Engineering roadmap. |
| `14-Telegram-Bot/` | Render Webhook integration for /done and /ask chat commands. |
| `15-Print-Templates/` | Scripts and templates for generating printable PDF trackers. |
| `16-Automation-Scripts/` | Floating autonomous layout and structure builders. |
| `master-tracker.md` | **The Single Source of Truth** for high-level progress. |
| `data.js` | Data store for AI prompts and interview questions (used by `index.html`). |

---

## 🛠️ Usage & Automation

This project uses Python and Shell scripts to maintain its documentation state:

- **`16-Automation-Scripts/generate_3month_plan.py`**: Regenerates the roadmap, weekly plan.
- **`15-Print-Templates/update_md.py`**: Injects new sections into existing trackers.
- **`16-Automation-Scripts/fix_markdown.py`**: Utility to clean up table formatting and encoding issues across the repo.

### 📝 Tracking Progress
When updating progress, follow this hierarchy:
1.  Check off specific items in `03-Progress-Tracker/progress-tracker.md`.
2.  Update the high-level summary table in `master-tracker.md`.
3.  (Optional) Run `python 15-Print-Templates/update_html.py` to sync the printable tracker.

---

## 🤖 Gemini CLI Conventions

- **Senior Peer Review:** When asked to review notes or labs, act as a Senior DevOps Engineer. Be critical of security, cost-optimization, and high-availability.
- **STAR Method:** For interview prep, always evaluate responses against the Situation, Task, Action, Result framework.
- **Code Generation:** When generating scripts (Bash/Python/Terraform), prioritize "Defensive Scripting" (e.g., `set -euo pipefail` in Bash) and clear commenting.
- **Memory Management:** If I report finishing a module or video, prompt me to update `master-tracker.md` and `progress-tracker.md`.

---

## 📅 Important Dates
- **Project Start:** August 18, 2026
- **CKA Exam Target:** January 1, 2027
- **Job Application Go-Live:** January 1, 2027
- **AZ-104 Exam Target:** January 15, 2027
