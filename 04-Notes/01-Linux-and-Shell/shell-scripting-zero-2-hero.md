# 🐚 Shell Scripting for DevOps | Zero 2 Hero (Part 2)

> **Module**: Shell Scripting Interview Q&A & Core Concepts
> **Path**: `01-Linux-and-Shell/`

This document serves as your definitive guide to everyday DevOps shell scripting, focusing on system health, standard text manipulation, network fetching, and defensive scripting practices.

---

## 1. Core System Health Commands

When an alert fires, you usually SSH into a machine and run these four commands first to understand the system's state.

| Command | Purpose | Common DevOps Usage |
| :--- | :--- | :--- |
| `df` | **Disk Free**: Displays available and used disk space on file systems. | `df -h` (Human readable). Used to see if the root `/` or log partitions are 100% full. |
| `free` | **RAM Memory**: Displays total, used, and free memory in the system. | `free -g` (Display in GB) or `free -m` (MB) to check if the machine is swapping due to low RAM. |
| `nproc` | **CPU Cores**: Prints the number of processing units available. | Simply running `nproc` outputs a number (e.g., `4`). Useful in scripts to dynamically set threads during builds (e.g., `make -j $(nproc)`). |
| `top` | **Task Manager**: Provides a dynamic, real-time view of running processes. | Press `shift + m` to sort by memory usage, or `shift + p` for CPU to find rogue processes. |

---

## 2. Defensive Scripting: `nodehealth.sh`

In DevOps, we do not write brittle scripts. We use **Defensive Scripting** to ensure the script fails gracefully instead of destroying the system if something goes wrong.

### The Script (`nodehealth.sh`)
```bash
#!/bin/bash
# Author: Imran
# Purpose: Outputs the system node health metrics (Disk, RAM, CPU)

##############################
# DEBUG & DEFENSIVE SETTINGS #
##############################
set -x # Enable debug mode (prints every command before executing it)
set -e # Exit immediately if a command exits with a non-zero (failed) status
set -o pipefail # If any command in a pipe fails, fail the entire pipe

echo "--- Disk Space ---"
df -h

echo "--- Memory Usage ---"
free -g

echo "--- CPU Cores ---"
nproc
```

### Explanation of `set` Options (Highly asked in Interviews!)
- `set -x`: Very useful for troubleshooting. It acts as an execution trace.
- `set -e`: Prevents disaster. For example: `cd /logs; rm -rf *`. If the `cd` fails (folder doesn't exist), without `set -e`, the script will just run `rm -rf *` in whatever folder it was currently in (which could wipe the OS).
- `set -o pipefail`: Required because `set -e` alone ignores pipe failures. (See next section).

---

## 3. The Pipe Concept (`|`)

The pipe symbol `|` takes the **standard output (stdout)** of the first command and passes it as the **standard input (stdin)** to the second command.

**Example Without Pipe:**
You run `cat /var/log/syslog` and millions of lines flood your terminal.

**Example With Pipe:**
```bash
cat /var/log/syslog | grep "error" | awk '{print $1, $2}'
```
*Flow*: The raw file output -> goes to `grep` (which filters only lines with "error") -> goes to `awk` (which prints only the first two columns).

> **Why `set -o pipefail` is needed:** In bash, a pipeline's exit status is determined by the *last* command in the pipeline. So if `cat nonexistent-file | grep "error"` is run, `cat` fails (causing a cascading empty pipe), but `grep` technically exits successfully with no output! Thus the script ignores the `cat` error. `pipefail` stops this behavior.

---

## 4. Automation via `For` Loops

Loops are essential for iterating over files, numbers, or command outputs.

**Basic Iteration (1 to 100):**
```bash
#!/bin/bash

# This will print the numbers 1 through 100 on new lines.
for i in {1..100}; do
    echo "Currently on number: $i"
done
```

**Real-World DevOps Example (Restarting exactly 3 specific services):**
```bash
for service in nginx mysql redis; do
    echo "Restarting $service..."
    systemctl restart $service
done
```

---

## 5. Network Fetching: `wget` vs `curl`

Both are used to download files or interact with HTTP APIs, but they serve different primary purposes.

| Feature | `curl` (Client URL) | `wget` (Web Get) |
| :--- | :--- | :--- |
| **Primary Use** | Making Web/API requests (REST APIs, testing endpoints). | Downloading large files or mirroring websites. |
| **Output Default** | Prints the downloaded content directly to the terminal stdout. | Automatically saves the downloaded content to a file in the directory. |
| **Recursive Download** | ❌ No native recursive crawling. | ✅ Can download entire websites/folders recursively (`wget -r`). |
| **DevOps Example** | `curl -X POST api.com/status` | `wget https://releases.ubuntu.com/iso/ubuntu.iso` |

---

## 6. Linux Signals & The `trap` Command

### Linux Signals (SIG ETC)
When you tell a Linux process to stop, you are actually sending it a **Signal**.
- **SIGINT (2)**: Interrupt from keyboard (This is what happens when you press `Ctrl+C`). It asks the program to politely stop.
- **SIGTERM (15)**: Termination signal (Default for `kill <PID>`). A polite request to terminate, allowing the script to save state and cleanup.
- **SIGKILL (9)**: Immediate Kill (`kill -9 <PID>`). The kernel immediately forcefully destroys the process. It cannot be caught or ignored.

### The `trap` Command
`trap` is a bash built-in that allows your script to "catch" these signals and execute code before dying. (It cannot catch SIGKILL).

**DevOps Example (Cleaning up temporary files if a user hits Ctrl+C):**
```bash
#!/bin/bash

# 1. Define the cleanup instructions
cleanup() {
    echo "Script interrupted! Deleting temporary scratch files..."
    rm -rf /tmp/my_scratch_dir
    exit 1
}

# 2. Trap the SIGINT (2) and SIGTERM (15) signals
trap cleanup SIGINT SIGTERM

echo "Doing heavy background work... press Ctrl+C to abort."
mkdir -p /tmp/my_scratch_dir
sleep 100 # Simulating work
```

---

## 7. The `grep` Command

`grep` stands for Global Regular Expression Print. It is the core tool used for searching plain-text data sets for lines that match a regular expression.

**DevOps Cheat Sheet for `grep`:**
```bash
# Find a specific keyword in a log file
grep "Exception" /var/log/application.log

# Find a keyword, IGNORE case-sensitivity (-i)
grep -i "error" /var/log/application.log

# Show the lines containing the error, AND the 3 lines PRECEDING it (-B) and FOLLOWING it (-A) for context
grep -B 3 -A 3 "FATAL" /var/log/application.log

# INVERT the search (Show me all lines that DO NOT contain 'INFO') (-v)
grep -v "INFO" /var/log/application.log

# Count the number of times a word appears (-c)
grep -c "Exception" /var/log/application.log
```
