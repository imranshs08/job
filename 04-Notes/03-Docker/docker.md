# 📝 Docker — Study Notes

> **Phase:** 2 (September 2026) | **Playlist:** Day 16, 17, 18, 19, 20

---

## Key Concepts

| Concept | Notes |
|---------|-------|
| Containers vs VMs | |
| Docker Architecture (daemon, client, registry) | |
| Images & Layers | |
| Dockerfile Instructions | |
| Multi-Stage Builds | |
| Docker Compose | |
| Volumes (named, bind, tmpfs) | |
| Networking (bridge, host, overlay) | |
| Docker Hub & Private Registries | |
| Container Security | |
| Resource Limits (CPU, memory) | |
| Docker Logging | |

---

## Commands Cheat Sheet

```bash
# Images
docker build -t name:tag .
docker images
docker pull image:tag
docker push image:tag
docker rmi image

# Containers
docker run -d -p 8080:80 --name myapp image
docker ps / docker ps -a
docker logs -f container
docker exec -it container bash
docker stop/start/restart container
docker rm container

# Compose
docker compose up -d
docker compose down
docker compose logs -f
docker compose ps

# Volumes & Networks
docker volume create mydata
docker network create mynet
docker run -v mydata:/data image
docker run --network mynet image

# Cleanup
docker system prune -a
docker image prune
```

---

## Dockerfile Template

```dockerfile
# Multi-stage build example
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/index.js"]
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
| 1 | What is the difference between CMD and ENTRYPOINT? | |
| 2 | How does multi-stage build optimize image size? | |
| 3 | Explain Docker networking modes | |
| 4 | How do you persist data in Docker? | |
| 5 | What is Docker Compose and when to use it? | |
| 6 | How do you reduce Docker image size? | |
| 7 | What is the difference between COPY and ADD? | |
| 8 | What are Docker security best practices? | |
| 9 | Explain container orchestration | |
| 10 | How do you debug a container that keeps crashing? | |

---

## Resources
- [ ] Playlist: Day 16–20
- [ ] Docker Documentation (docs.docker.com)
- [ ] Docker Best Practices
