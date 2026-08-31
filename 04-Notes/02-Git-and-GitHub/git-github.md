# 📝 Git & GitHub — Study Notes

> **Phase:** 1 (August 2026) | **Playlist:** Day 9, 10, 11

---

## Key Concepts

| Concept | Notes |
|---------|-------|
| Repository (local vs remote) | |
| Staging Area vs Working Directory | |
| Commits (SHA, messages, amend) | |
| Branching (create, switch, delete) | |
| Merging (fast-forward, 3-way) | |
| Rebasing vs Merging | |
| Cherry-Pick | |
| Stashing | |
| Tags (lightweight, annotated) | |
| Pull Requests / Code Reviews | |
| Merge Conflicts Resolution | |
| Git Hooks | |
| Git Flow vs Trunk-Based Development | |
| Submodules & Subtrees | |

---

## Commands Cheat Sheet

```bash
# Setup
git init
git clone <url>
git config --global user.name "Name"

# Daily Workflow
git status
git add . / git add <file>
git commit -m "message"
git push origin <branch>
git pull origin <branch>

# Branching
git branch <name>
git checkout -b <name>
git merge <branch>
git branch -d <branch>

# Advanced
git rebase <branch>
git cherry-pick <sha>
git stash / git stash pop
git log --oneline --graph --all
git reset --hard HEAD~1
git revert <sha>
git reflog
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
| 1 | What is the difference between git merge and git rebase? | |
| 2 | How do you resolve a merge conflict? | |
| 3 | What is cherry-pick and when to use it? | |
| 4 | Explain Git Flow branching strategy | |
| 5 | What is git stash? | |
| 6 | How do you revert a commit that's already pushed? | |
| 7 | What is the difference between git reset and git revert? | |
| 8 | Explain .gitignore | |
| 9 | What are Git hooks? Give examples | |
| 10 | How do you squash commits? | |

---

## Resources
- [ ] Playlist: Day 9, 10, 11
- [ ] Git documentation (git-scm.com)
- [ ] Learn Git Branching (learngitbranching.js.org)
