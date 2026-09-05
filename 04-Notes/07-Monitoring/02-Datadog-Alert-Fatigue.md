# 🐶 Datadog Alert Fatigue Tuning & Composite Monitors

## 1. Core Concepts & Definitions

Before you can tune alerts, you must understand why on-call engineers suffer from burnout and how modern observability tools solve this.

* **Alert Fatigue:** A state of exhaustion experienced by on-call engineers when they are exposed to a massive number of frequent, un-actionable, or false-positive alarms. The result is ignoring critical alerts (the "boy who cried wolf" effect).
* **Cause-Based Alerting:** Alerting on a system attribute (e.g., "CPU is at 90%"). This is generally a bad practice because high CPU doesn't always negatively impact the user.
* **Symptom-Based Alerting:** Alerting on the *user experience* (e.g., "Checkout page is taking 5 seconds to load"). This is the SRE gold standard.
* **Datadog Composite Monitors:** A feature that combines multiple individual monitors using logic operators (`&&`, `||`) so an alert only triggers if *all* conditions are met.

---

## 2. Structure & Visuals 

### Single Monitors vs. Composite Monitors

| Feature | Single Threshold Monitor (Legacy) | Composite Monitor (Strategic SRE) |
| :--- | :--- | :--- |
| **Logic** | "If CPU > 90%, send a page." | "If [CPU > 90%] AND [Latency > 2s], send a page." |
| **False Positives** | 🔴 Extremely High (e.g., Cron jobs spike CPU safely). | 🟢 Very Low (Only pages if the user is actually suffering). |
| **Actionability** | Often requires no action, just monitoring. | Demands immediate action. |
| **On-Call Health** | Leads to severe Alert Fatigue. | Keeps engineers rested and alert. |

---

## 3. IaC Commands & Examples

In a modern DevOps environment, Datadog monitors should be managed as Code (IaC) using **Terraform**, rather than clicked through the UI.

### Example: Tuning CPU Alerts with Terraform (Composite Monitor)
Here is a real-world example of how to combine a CPU spike with High Latency to prevent useless pages.

```hcl
# 1. Base Monitor A: The Cause (CPU is high)
resource "datadog_monitor" "high_cpu" {
  name  = "High CPU on API Servers"
  type  = "query alert"
  query = "avg(last_5m):avg:system.cpu.system{env:prod} > 90"
  # Note: We do NOT send a notification for this monitor alone!
}

# 2. Base Monitor B: The Symptom (Users are suffering)
resource "datadog_monitor" "high_latency" {
  name  = "High Latency on Checkout API"
  type  = "query alert"
  query = "avg(last_5m):avg:trace.http.request.duration{env:prod} > 2.0"
  # Note: We do NOT send a notification for this monitor alone!
}

# 3. The Composite Monitor: The actual Page
resource "datadog_monitor" "composite_alert" {
  name  = "[CRITICAL] CPU Spike causing High Checkout Latency!"
  type  = "composite"
  query = "${datadog_monitor.high_cpu.id} && ${datadog_monitor.high_latency.id}"
  
  # Only page the on-call team when BOTH are true!
  message = "Users are experiencing latency because the API servers are maxed out. @pagerduty-sre-team"
}
```

---

## 4. 🧠 The Missing Context: Industry Best Practices

*Why was the CPU alerting in the first place?*
The root issue with Alert Fatigue usually comes from ignoring Google SRE's **Four Golden Signals**. 

1. **Latency:** The time it takes to service a request.
2. **Traffic:** A measure of how much demand is being placed on your system.
3. **Errors:** The rate of requests that fail.
4. **Saturation:** How "full" your service is (CPU, Memory).

**The Missing Context:** Saturation (CPU) should almost *never* trigger a PagerDuty call at 3:00 AM on its own! High CPU is expected during traffic spikes. You should only configure paging alerts for **Errors and Latency** (Symptoms). Saturation alerts should just be logged as Jira tickets or Slack messages for the team to investigate during normal business hours.

---

## 🎤 5. Interview Readiness

**🔥 Common Interview Question:** *"Our engineering team is getting paged 20 times a night because pod CPU usage hits 95%. How do you fix this?"*
**Answer:** "CPU hitting 95% is not an incident; it means our autoscaler is being highly efficient! I would demote the CPU alert from 'Page' to a 'Warning' in a Slack channel. I would then create a Datadog Composite Monitor that only pages the team if `CPU > 95%` AND `HTTP 5xx Error Rate > 5%`. We must alert on user-impacting symptoms, not just high resource utilization."

**⚠️ The "Gotcha":** *"Can't we just mute the Datadog alert completely?"*
**Answer:** No. Muting or deleting the alert entirely removes observability. We still need to track if we are under-provisioned. The fix is routing the alert to the right place (a Jira board for capacity planning) instead of PagerDuty.

---

## 🧪 6. Free Playgrounds & Labs

Because Datadog is enterprise software, browser sandboxes don't natively include it, but you can practice the foundational concepts perfectly here:

1. **[Datadog Free 14-Day Trial](https://www.datadoghq.com/)**: Sign up without a credit card. Install the Datadog Agent on an AWS Free Tier EC2 instance or local VM to test writing composite monitors.
2. **[Killercoda Prometheus Playground](https://killercoda.com/playgrounds/scenario/prometheus)**: While it is Prometheus (not Datadog), you can practice the exact same concept using Prometheus Alertmanager to combine metrics securely in a browser.
3. **[PagerDuty Developer Sandbox](https://developer.pagerduty.com/docs/ZG9jOjExMDI5NTUw-developer-sandboxes)**: Practice hooking up a mock alert directly to a PagerDuty API to see how on-call incident routing works.
