# Day-9: Git and GitHub — Basics and Version Control

## 🧠 What is Version Control?

**Version Control** (also known as source control) is the practice of tracking and managing changes to software code. Version control systems (VCS) act as a "time machine" for developers, allowing them to:
- Compare earlier versions of the code to help fix mistakes.
- Maintain a complete history of every change ever made.
- Work concurrently on the same codebase without overwriting someone else's work (collaboration).

### Types of Version Control:
1. **Centralized Version Control (CVCS):** All file versions are kept on a central server. (e.g., SVN). If the server goes down, nobody can work.
2. **Distributed Version Control (DVCS):** Every user's local machine contains a *full clone* of the repository history. (e.g., Git).


## 🐙 What is Git?

**Git** is a free, open-source **Distributed Version Control System (DVCS)** designed to handle everything from small to massive projects with extreme speed and efficiency. 
*Note: Git is the underlying software running on your computer. **GitHub** is simply a remote hosting service on the internet that stores Git repositories.*

### The 3 Stages of Git:
1. **Working Directory:** The files you are currently modifying (Untracked or Modified).
2. **Staging Area (Index):** A draft space where you prepare the files you want to include in your next commit.
3. **Local Repository:** The `.git` folder where Git officially permanently stores your committed snapshots.

---

## 🛠️ Core Git Commands (The Daily Workflow)

### 1. `git init` (Initialize)
Converts an empty or existing project folder into a Git repository. It creates a hidden `.git` folder that tracks all history.
```bash
# Example
mkdir my-devops-project
cd my-devops-project
git init
# Output: Initialized empty Git repository in /path/to/my-devops-project/.git/
```

### 2. `git add` (Stage files)
Moves changes from the Working Directory into the Staging Area. This tells Git, "I want to include these files in my next save."
```bash
# Example: Adding a specific file
git add index.html

# Example: Adding ALL changed files in the directory
git add .
```

### 3. `git commit` (Save snapshot)
Takes everything in the staging area and permanently saves it to your Local Repository history. Always include a descriptive message.
```bash
# Example
git commit -m "feat: added login page UI components"
# Output: [main (root-commit) 8fa3c2d] feat: added login page UI components
```

### 4. `git push` (Upload to remote)
Transfers your local commits to a remote repository (like GitHub, GitLab, or Bitbucket) so others can see and use your code.
```bash
# Example: Pushing local 'main' branch to remote 'origin'
git push origin main
```

### 5. `git log` (View history)
Shows a list of all past commits, including the author, date, and commit message.
```bash
# Example: Standard log
git log

# Example: Condensed one-line history (Highly Recommended)
git log --oneline
```

---

## 💡 Other Important Git Concepts

### `git status` (The Compass)
Before you run `add` or `commit`, you should always run `git status`. It tells you exactly which files are modified, which are staged, and which branch you are on.
```bash
git status
# Output:
# On branch main
# Changes not staged for commit:
#   modified:   README.md
```

### `git clone` (Download Repo)
Used to download a complete copy of an existing remote repository from GitHub to your local machine.
```bash
git clone https://github.com/imranshs08/job.git
```

### `git pull` (Download Updates)
Fetches the newest changes from the remote repository (GitHub) and immediately merges them into your local branch. This is essential when working in a team.
```bash
git pull origin main
```

### `git branch` & `git checkout` (Branching)
Branching allows you to isolate your work (like a new feature or a bug fix) without affecting the stable `main` codebase.
```bash
# Check existing branches
git branch

# Create and switch to a new branch simultaneously
git checkout -b feature/login-page
```
*(Note: Newer versions of Git use `git switch -c feature/login-page` as a safer alternative to `checkout`)*.

---

## 🚀 DevOps Best Practices for Git
1. **Never commit secrets:** Never commit passwords, API keys, or `.env` files. Use `.gitignore`.
2. **Commit often, but logically:** Don't wait until Friday to make one massive commit. Commit smaller, functional logical units of work.
3. **Use conventional commit messages:** 
   - Good: `fix(auth): resolved null pointer exception in IAM role logic`
   - Bad: `fixed stuff` 
4. **Pull before you Push:** Always run `git pull --rebase` before attempting to push, to safely resolve remote team conflicts.
