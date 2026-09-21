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
| ☐ | 1 | [Kubernetes Gateway API - Is Ingress dead?](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `32m 38s` | |
| ☐ | 2 | [Azure Application Gateway for Containers Setup in AKS](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `37m 57s` | |
| ☐ | 3 | [Host multiple Apps with one AGC on AKS](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `22m 16s` | |

## 🔒 Session 2: Automated TLS, DNS & Certificates (~1h 11m)
*Focus: Wiring up Azure DNS, Cert-Manager, and dynamically securing Gateway API endpoints with Let's Encrypt.*

| Status | # | Video Title | Duration | Notes / Lab |
|:---:|:---:|---|:---:|---|
| ☐ | 4 | [Automate DNS Records for AKS TLS Setup](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `13m 22s` | |
| ☐ | 5 | [Cert-Manager - Automated HTTPS for everyone on AKS](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `25m 44s` | |
| ☐ | 6 | [Cert Manager & Azure DNS for Wildcard Certificates](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `33m 12s` | |

## 🚦 Session 3: Traffic Management, Routing & CI/CD (~1h 24m)
*Focus: HTTPRoutes, header matching, rewrite/redirect rules, and advanced deployments (Canary/A-B).*

| Status | # | Video Title | Duration | Notes / Lab |
|:---:|:---:|---|:---:|---|
| ☐ | 7 | [CI/CD for AKS Dynamic PR Environments with TLS](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `34m 49s` | |
| ☐ | 8 | [AKS Gateway Routing Path, Query, and Headers](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `23m 59s` | |
| ☐ | 9 | [URL Rewrite & URL Redirect with AGC](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `15m 52s` | |
| ☐ | 10 | [AKS Traffic Splitting: Canary and A-B Deployments](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `12m 26s` | |

## 🛡️ Session 4: Security, Monitoring & Alternative Controllers (~1h 26m)
*Focus: Adding WAF policies, integrating Prometheus/Grafana, and exploring non-Azure controllers.*

| Status | # | Video Title | Duration | Notes / Lab |
|:---:|:---:|---|:---:|---|
| ☐ | 11 | [AKS Monitoring with Prometheus and Grafana](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `32m 37s` | |
| ☐ | 12 | [WAF Security for AKS with AGC](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `21m 08s` | |
| ☐ | 13 | [Kubernetes Gateway API with Nginx](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `16m 19s` | |
| ☐ | 14 | [Deploy Traefik Gateway API on AKS in Minutes](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `17m 18s` | |

## 🚀 Session 5: Envoy Gateway & Legacy Migration (~1h 25m)
*Focus: Standing up Envoy Gateway and comparing the new API with traditional NGINX Ingress rules.*

| Status | # | Video Title | Duration | Notes / Lab |
|:---:|:---:|---|:---:|---|
| ☐ | 15 | [Envoy Gateway API Setup and Installation on AKS](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `17m 17s` | |
| ☐ | 16 | [Envoy Gateway + Cert Manager - Zero Touch TLS](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `18m 48s` | |
| ☐ | 17 | [NGINX Ingress & Cert Manager - Legacy Way vs. Gateway API](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `25m 34s` | |
| ☐ | 18 | [AKS Application Gateway for Containers Addon](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `25m 46s` | |

## 🏆 Session 6: Production Readiness & Recap (~1h 44m)
*Focus: End-to-end production pipelines (Terraform/ArgoCD) and Multi-Domain TLS architecture.*

| Status | # | Video Title | Duration | Notes / Lab |
|:---:|:---:|---|:---:|---|
| ☐ | 19 | [Infrastructure to App - Production Ready pipeline](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `50m 47s` | |
| ☐ | 20 | [Gateway API for Kubernetes Series Recap](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `27m 04s` | |
| ☐ | 21 | [Multi Domain TLS in AKS - Cert Manager & DNS Solvers](https://www.youtube.com/watch?list=PLzBajgDniE4k4ye-kqg3oT72rUrrj8lAG) | `27m 35s` | |
