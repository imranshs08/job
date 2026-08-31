# 📝 Linux & Shell Scripting — Study Notes

> **Phase:** 1 (August 2026) | **Playlist:** Day 6, 7, 8

---

## Key Concepts

### Linux Fundamentals
| Concept | Notes |
|---------|-------|
| File System Hierarchy | |
| File Permissions (chmod, chown) | |
| Process Management (ps, top, kill) | |
| Package Management (apt, yum) | |
| User & Group Management | |
| Systemd & Services | |
| Cron Jobs | |
| Networking (netstat, ss, curl) | |

### Shell Scripting
| Concept | Notes |
|---------|-------|
| Variables & Data Types | |
| Conditionals (if/else, case) | |
| Loops (for, while, until) | |
| Functions | |
| Arrays | |
| String Operations | |
| Error Handling (set -e, trap) | |
| Stdin/Stdout/Stderr Redirection | |
| Pipes & Grep/Awk/Sed | |

---

## Commands Cheat Sheet

```bash
# File Operations
ls -la          # List all files with details
cp -r src dst   # Copy recursively
mv old new      # Move/rename
find / -name "*.log" -mtime +7    # Find files

# Process Management
ps aux | grep <process>
kill -9 <PID>
nohup command &  # Run in background

# Disk & Memory
df -h            # Disk usage
du -sh *         # Directory sizes
free -m          # Memory usage

# Networking
curl -v URL      # HTTP request
netstat -tlnp    # Open ports
ss -tlnp         # Socket stats

# Text Processing
grep -rn "pattern" /path
awk '{print $1}' file
sed 's/old/new/g' file
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

### Lab 3: _______________
**Date:** ______ | **Status:** ☐ Complete
```
Notes:


```

---

## Interview Q&A

| # | Question | My Answer |
|---|----------|-----------|
| 1 | What is the difference between soft and hard links? | |
| 2 | Explain file permissions in Linux | |
| 3 | What is inode? | |
| 4 | How do you troubleshoot a process consuming high CPU? | |
| 5 | Explain the boot process of Linux | |
| 6 | What is the difference between bash and sh? | |
| 7 | How do you schedule a cron job? | |
| 8 | What are signals in Linux? | |
| 9 | How do you check open ports? | |
| 10 | Write a script to find files older than 30 days | |

---

## Resources
- [ ] Playlist: Day 6, 7, 8
- [ ] Linux Command Line (tldr.sh)
- [ ] Bash Scripting Guide (tldp.org)
- [ ] Practice: overthewire.org/wargames/bandit
