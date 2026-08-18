# 📝 CI/CD (Jenkins & GitHub Actions) — Study Notes

> **Phase:** 3 (October 2026) | **Playlist:** Day 29, 30, 31, 32, 36

---

## Key Concepts

| Concept | Notes |
|---------|-------|
| CI vs CD vs CD (Continuous Delivery vs Deployment) | |
| Jenkins Architecture (master, agents) | |
| Declarative vs Scripted Pipeline | |
| Jenkinsfile Structure | |
| Jenkins Shared Libraries | |
| GitHub Actions Workflows | |
| Actions, Jobs, Steps, Triggers | |
| GitOps Principles | |
| ArgoCD Architecture | |
| Pipeline as Code | |
| Build Agents & Runners | |
| Artifact Management | |

---

## Jenkins Pipeline Template

```groovy
pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'myapp'
    }
    stages {
        stage('Checkout') {
            steps { git 'https://github.com/...' }
        }
        stage('Build') {
            steps { sh 'docker build -t $DOCKER_IMAGE .' }
        }
        stage('Test') {
            steps { sh 'docker run $DOCKER_IMAGE npm test' }
        }
        stage('Deploy') {
            steps { sh 'kubectl apply -f k8s/' }
        }
    }
    post {
        always { cleanWs() }
        failure { echo 'Pipeline failed!' }
    }
}
```

## GitHub Actions Template

```yaml
name: CI/CD Pipeline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker Image
        run: docker build -t myapp .
      - name: Run Tests
        run: docker run myapp npm test
      - name: Deploy
        run: kubectl apply -f k8s/
```

---

## Hands-On Lab Notes

### Lab 1: _______________
**Date:** ______ | **Status:** ☐ Complete
```
Notes:


```

### Lab 2: _______________
**Date:** ______ | **Status:** ☐ Complete
```
Notes:


```

---

## Interview Q&A

| # | Question | My Answer |
|---|----------|-----------|
| 1 | What is the difference between CI and CD? | |
| 2 | Explain Jenkins declarative pipeline | |
| 3 | What are Jenkins shared libraries? | |
| 4 | How do you handle secrets in CI/CD? | |
| 5 | Jenkins vs GitHub Actions — when to use which? | |
| 6 | What is GitOps? How does ArgoCD implement it? | |
| 7 | How do you implement rollback in CI/CD? | |
| 8 | What are pipeline best practices? | |
| 9 | How do you set up multi-branch pipelines? | |
| 10 | Explain blue-green vs canary deployments | |

---

## Resources
- [ ] Playlist: Day 29–32, 36
- [ ] Jenkins Documentation (jenkins.io)
- [ ] GitHub Actions Docs (docs.github.com)
- [ ] ArgoCD Docs (argo-cd.readthedocs.io)
