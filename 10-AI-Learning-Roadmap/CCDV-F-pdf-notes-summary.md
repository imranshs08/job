# 📄 CCDV-F Official Study PDFs — Notes Summary

> **Location:** `C:\Job Tracker\10-AI-Learning-Roadmap\` (local only — not in Git)
> **Source:** Official Udemy Course Companion Materials
> **Last Reviewed:** September 21, 2026

---

## 📦 PDF Inventory

| File | Type | Pages | Status |
|------|------|-------|--------|
| `30-Day+Study+Plan+(Print).pdf` | Study Plan | 2 | ✅ Reviewed |
| `Cram+Sheet+(Print).pdf` | Quick Reference | 6 | ✅ Reviewed |
| `Study+Companion+(Print).pdf` | Textbook | 37 | ✅ Reviewed |
| `CCDV-F+Domain+1+-+Agents+and+Workflows.pdf` | Slide Deck | 182 slides | ✅ Reviewed |
| `CCDV-F+Domain+2+-+Applications+and+Integration.pdf` | Slide Deck | 370 slides | ✅ Reviewed |
| `CCDV-F+Domain+3+-+Claude+Code.pdf` | Slide Deck | ~60 slides | ⬜ To Review |
| `CCDV-F+Domain+4+-+Eval,+Testing,+and+Debugging.pdf` | Slide Deck | ~80 slides | ⬜ To Review |
| `CCDV-F+Domain+5+-+Model+Selection+and+Optimization.pdf` | Slide Deck | ~90 slides | ⬜ To Review |
| `CCDV-F+Domain+6+-+Prompt+and+Context+Engineering.pdf` | Slide Deck | ~100 slides | ⬜ To Review |
| `CCDV-F+Domain+7+-+Security+and+Safety.pdf` | Slide Deck | ~70 slides | ⬜ To Review |
| `CCDV-F+Domain+8+-+Tools+and+MCPs.pdf` | Slide Deck | ~120 slides | ⬜ To Review |

**📖 Open locally:** [pdf-viewer.html](../pdf-viewer.html)

---

## 🔑 Key Extracts — Cram Sheet (6 pages)

### Workflow vs Agent Decision
| | Workflow | Agent |
|--|---------|-------|
| Control flow | Fixed at design time by developer | Model decides at runtime |
| When to use | Known, repeatable sequences | Open-ended, exploratory tasks |
| Risk | Low — deterministic | Higher — requires guardrails |

### Messages API — Critical Fields
```json
{
  "model": "claude-opus-4-5",
  "messages": [{"role": "user", "content": "..."}],
  "tool_choice": "auto|any|tool|none",
  "stop_reason": "tool_use | end_turn | max_tokens"
}
```

### Streaming SSE Event Sequence
```
message_start → content_block_start → input_json_delta → content_block_stop → message_stop
```

### Extended Thinking (Exam Trap!)
| Type | Field | Values |
|------|-------|--------|
| **Adaptive** (new) | `thinking.type: "adaptive"` + `output_config.effort` | `low`, `medium`, `high`, `max` |
| **Legacy** (old) | `thinking.type: "enabled"` + `budget_tokens` | must be < `max_tokens` |

### Prompt Caching — Cost Multipliers
| Operation | Cost |
|-----------|------|
| Cache Read | **0.1x** (90% discount) |
| Cache Write (5-min TTL) | **1.25x** |
| Cache Write (1-hr TTL) | **2.0x** |
| Max breakpoints | **4 per request** |

### Hooks — Lifecycle Events
| Hook | When it fires | Key output field |
|------|--------------|------------------|
| `PreToolUse` | Before tool executes | `permissionDecision`: `allow`/`deny`/`ask` |
| `PostToolUse` | After tool returns | Read-only audit |
| `PreMessage` | Before sending to model | Can modify system prompt |
| `PostMessage` | After model responds | Can intercept/log |

### Cloud Deployment — Exam Traps
| Platform | Key Difference |
|----------|---------------|
| **Amazon Bedrock** | Client: `AnthropicBedrockMantle`, endpoint includes region |
| **Google Vertex AI** | Model ID in URL path; body must include `anthropic_version: "vertex-2023-10-16"` |

### MCP Primitives
| Primitive | Controlled by | Purpose |
|-----------|--------------|---------|
| **Tools** | Model | Functions Claude calls |
| **Resources** | Application | Data exposed to Claude |
| **Prompts** | User | Templates/slash commands |

### MCP Transports
| Transport | Use case |
|-----------|---------|
| `stdio` | Local child process (same machine) |
| `Sockets/HTTP` | Networked/remote service with auth |

---

## 📚 Key Extracts — Study Companion (37 pages)

### Exam Logistics
- **Questions:** 53 scenario-based questions
- **Time:** 120 minutes
- **Pass score:** 720/1000 (~72%)
- **Proctor:** Pearson VUE
- **Format:** All MCQ — no coding required

### Domain Weights (Study Companion version)
| Domain | Topic | Weight |
|--------|-------|--------|
| D1 | Agents and Workflows | 15% |
| D2 | Applications and Integration | **33%** |
| D3 | System Design & Prompting | 22% |
| D4 | Tools & MCP | **30%** |

> ⚠️ **Note:** The Study Companion uses a 4-domain grouping vs. Udemy's 8-domain breakdown. Both cover the same material — Udemy is more granular.

---

## 📅 30-Day Study Plan Summary

| Phase | Days | Activity |
|-------|------|----------|
| **Learn** | Days 1–2 | Domain 1: Agents (Lectures 1–19) |
| **Learn** | Days 3–9 | Domain 2: Applications (Lectures 20–59) |
| **Learn** | Day 10 | Domain 3: Claude Code + **Practice Exam 1** |
| **Learn** | Days 11–13 | Domain 4: Eval & Testing (Lectures 64–75) |
| **Learn** | Days 14–17 | Domain 5: Tools & MCP + **Practice Exam 2** |
| **Learn** | Days 18–21 | Domains 6–8 + **Practice Exam 3** |
| **Review** | Days 22–24 | Re-watch weak areas + memorize Cram Sheet |
| **Practice** | Days 25–27 | Practice Exams 4, 5, 6 — log by domain |
| **Drill** | Days 28–29 | Targeted weakest domain |
| **Final** | Day 30 | Cram Sheet + Study Companion only. Rest. |

---

## 🗂️ Weekend Mapping (Our Adapted Plan)

Since we study weekends only, the 30-day plan maps to our **11-weekend schedule** in `claude-certification-plan.md`. Key adjustment: our plan starts Sep 20, giving us ~10.5 weeks — equivalent to the 30-day program's density.
