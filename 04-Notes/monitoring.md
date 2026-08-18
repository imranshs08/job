# 📝 Monitoring & Observability — Study Notes

> **Phase:** 4 (November 2026) | **Playlist:** Day 38, 39

---

## Key Concepts

| Concept | Notes |
|---------|-------|
| Three Pillars: Metrics, Logs, Traces | |
| Prometheus Architecture | |
| PromQL (Prometheus Query Language) | |
| Grafana Dashboards | |
| Alert Manager | |
| ELK Stack (Elasticsearch, Logstash, Kibana) | |
| Fluentd / Fluent Bit | |
| Distributed Tracing (Jaeger, Zipkin) | |
| SLI, SLO, SLA | |
| Golden Signals (Latency, Traffic, Errors, Saturation) | |
| AIOps & Predictive Monitoring | |

---

## Commands & Config

```yaml
# Prometheus scrape config
scrape_configs:
  - job_name: 'kubernetes'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

```bash
# PromQL Examples
rate(http_requests_total[5m])
histogram_quantile(0.95, rate(http_duration_seconds_bucket[5m]))
increase(errors_total[1h])
```

---

## Hands-On Lab Notes

### Lab 1: _______________
**Date:** ______ | **Status:** ☐ Complete
```
Notes:


```

---

## Interview Q&A

| # | Question | My Answer |
|---|----------|-----------|
| 1 | What are the three pillars of observability? | |
| 2 | Explain Prometheus architecture | |
| 3 | What is PromQL? Give examples | |
| 4 | How do you set up alerting? | |
| 5 | Compare ELK vs EFK stack | |
| 6 | What are SLIs, SLOs, and SLAs? | |
| 7 | What are the Golden Signals? | |
| 8 | How do you monitor Kubernetes clusters? | |
| 9 | What is distributed tracing? | |
| 10 | How do you handle log aggregation at scale? | |

---

## Resources
- [ ] Playlist: Day 38, 39
- [ ] Prometheus Docs (prometheus.io)
- [ ] Grafana Docs (grafana.com/docs)
