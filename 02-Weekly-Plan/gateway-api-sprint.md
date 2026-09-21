# 🌐 Kubernetes Gateway API & Azure AGC Sprint Tracker

> **Source:** [Programming with Wolfgang — K8s Gateway API Playlist](https://www.youtube.com/playlist?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG)
> **Goal:** Master the new Kubernetes Gateway API standard and Azure Application Gateway for Containers (AGC)
> **Total Length:** 21 Videos (~8h 52m)
> **Pace:** 6 Sessions (~1.5 hours per session)

---

## 🏃‍♂️ Session 1: Fundamentals & Azure AGC Standup (~1h 31m)
*Focus: Understanding why Ingress is being replaced and how to stand up the new Azure AGC resources on AKS.*

| Status | # | Video Title | Duration | Notes / Lab |
|:---:|:---:|---|:---:|---|
| ☐ | 1 | [Kubernetes Gateway API - Is Ingress dead?](https://youtu.be/dgQQpJq1asc) | `32m 38s` | ☁️ Azure Spot<br>[📝 Notes](../04-Notes/04-Kubernetes/Gateway-API-01-Fundamentals.md) |
| ☐ | 2 | [Azure Application Gateway for Containers Setup in AKS](https://youtu.be/O6k-L6oBCMc) | `37m 57s` | ☁️ Azure Spot |
| ☐ | 3 | [Host multiple Apps with one AGC on AKS](https://youtu.be/JoRQhny4QPM) | `22m 16s` | ☁️ Azure Spot |

## 🔒 Session 2: Automated TLS, DNS & Certificates (~1h 11m)
*Focus: Wiring up Azure DNS, Cert-Manager, and dynamically securing Gateway API endpoints with Let's Encrypt.*

| Status | # | Video Title | Duration | Notes / Lab |
|:---:|:---:|---|:---:|---|
| ☐ | 4 | [Automate DNS Records for AKS TLS Setup](https://youtu.gPvXGWCqkrI) | `13m 22s` | ☁️ Azure Spot |
| ☐ | 5 | [Cert-Manager - Automated HTTPS for everyone on AKS](https://youtu.be/BfynzCAcvTc) | `25m 44s` | ☁️ Azure Spot |
| ☐ | 6 | [Cert Manager & Azure DNS for Wildcard Certificates](https://youtu.be/io9GdZMwAYA) | `33m 12s` | ☁️ Azure Spot |

## 🚦 Session 3: Traffic Management, Routing & CI/CD (~1h 24m)
*Focus: HTTPRoutes, header matching, rewrite/redirect rules, and advanced deployments (Canary/A-B).*

| Status | # | Video Title | Duration | Notes / Lab |
|:---:|:---:|---|:---:|---|
| ☐ | 7 | [CI/CD for AKS Dynamic PR Environments with TLS](https://youtu.be/6p-W7DE7Yd0) | `34m 49s` | ☁️ Azure Spot |
| ☐ | 8 | [AKS Gateway Routing Path, Query, and Headers](https://youtu.be/iT9WhRoukyY) | `23m 59s` | ☁️ Azure Spot |
| ☐ | 9 | [URL Rewrite & URL Redirect with AGC](https://youtu.be/y714oJ2rnwc) | `15m 52s` | ☁️ Azure Spot |
| ☐ | 10 | [AKS Traffic Splitting: Canary and A-B Deployments](https://youtu.be/HG5Qyfu_rSk) | `12m 26s` | ☁️ Azure Spot |

## 🛡️ Session 4: Security, Monitoring & Alternative Controllers (~1h 26m)
*Focus: Adding WAF policies, integrating Prometheus/Grafana, and exploring non-Azure controllers.*

| Status | # | Video Title | Duration | Notes / Lab |
|:---:|:---:|---|:---:|---|
| ☐ | 11 | [AKS Monitoring with Prometheus and Grafana](https://youtu.be/_81ypGr5X9w) | `32m 37s` | 💻 Local/Free |
| ☐ | 12 | [WAF Security for AKS with AGC](https://youtu.be/CW3S2AFe4UE) | `21m 08s` | 💻 Local/Free |
| ☐ | 13 | [Kubernetes Gateway API with Nginx](https://youtu.be/zp-5m88I2wE) | `16m 19s` | 💻 Local/Free |
| ☐ | 14 | [Deploy Traefik Gateway API on AKS in Minutes](https://youtu.be/UkNWjNMhDKE) | `17m 18s` | 💻 Local/Free |

## 🚀 Session 5: Envoy Gateway & Legacy Migration (~1h 25m)
*Focus: Standing up Envoy Gateway and comparing the new API with traditional NGINX Ingress rules.*

| Status | # | Video Title | Duration | Notes / Lab |
|:---:|:---:|---|:---:|---|
| ☐ | 15 | [Envoy Gateway API Setup and Installation on AKS](https://youtu.be/ypl7Bu9zQUM) | `17m 17s` | 💻 Local/Free |
| ☐ | 16 | [Envoy Gateway + Cert Manager - Zero Touch TLS](https://youtu.be/ZLUCt4yhe0Q) | `18m 48s` | 💻 Local/Free |
| ☐ | 17 | [NGINX Ingress & Cert Manager - Legacy Way vs. Gateway API](https://youtu.be/hDjmDKjJ3dQ) | `25m 34s` | 💻 Local/Free |
| ☐ | 18 | [AKS Application Gateway for Containers Addon](https://youtu.be/5arGrivpen8) | `25m 46s` | 💻 Local/Free |

## 🏆 Session 6: Production Readiness & Recap (~1h 44m)
*Focus: End-to-end production pipelines (Terraform/ArgoCD) and Multi-Domain TLS architecture.*

| Status | # | Video Title | Duration | Notes / Lab |
|:---:|:---:|---|:---:|---|
| ☐ | 19 | [Infrastructure to App - Production Ready pipeline](https://youtu.be/8UOj0aJDzXc) | `50m 47s` | 💻 Local/Free |
| ☐ | 20 | [Gateway API for Kubernetes Series Recap](https://youtu.be/Y11sFkvmHnY) | `27m 04s` | 💻 Local/Free |
| ☐ | 21 | [Multi Domain TLS in AKS - Cert Manager & DNS Solvers](https://youtu.be/k28q5bsKfwI) | `27m 35s` | 💻 Local/Free |
