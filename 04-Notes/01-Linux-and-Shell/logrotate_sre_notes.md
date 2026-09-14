# 📘 Linux Logrotate (SRE Guide)

## 🎯 The "Why" (Core Concept)
**Logrotate** is the native Linux system utility responsible for aging, compressing, and permanently deleting log files before they fill up the disk storage and crash applications.

*Analogy:* Imagine a highly secure corporate vault (the server disk). Every day, guards stack new paperwork (logs) into the vault. Erasing files indiscriminately will result in lawsuits (data loss/compliance failure). `logrotate` is the head archivist who comes in at 2 AM every night, neatly binds yesterday's loose papers together, shrinks them with a hydraulic press (Compression), and permanently burns papers older than 7 days (Deletion) to ensure you never run out of room.

**What catastrophic problem does this solve?**
Without `logrotate`, services like Docker, NGINX, or custom Java Apps write indefinitely to files like `/var/log/app.log`. When the storage disk reaches 100% capacity/inodes (File Exhaustion), the file-system locks. Databases will halt, web servers will return 500s, and standard users will be unable to login. `logrotate` provides deterministic storage cap guarantees.

## ⚙️ Architecture & Under the Hood
*   **The Split Architecture:**
    1.  **Global Config (`/etc/logrotate.conf`):** The baseline rules for the entire server (e.g., rotate weekly, keep 4 archives).
    2.  **App Drop-ins (`/etc/logrotate.d/`):** Dedicated configuration files for specific apps (e.g., `/etc/logrotate.d/nginx`) that strictly override the global baseline.
*   **Cron Triggered:** Logrotate does *not* run continuously. It is natively executed once per day via the Linux Cron scheduler (`/etc/cron.daily/logrotate`). 
*   **State Tracking (`/var/lib/logrotate/status`):** Logrotate is stateless by default. It utilizes this exact file to memorize the timestamp of when it last rotated a file, preventing it from rotating the same file twice in one 24-hour period.
*   **The Handle Problem (copytruncate vs native):**
    *   Normally, `logrotate` renames a file (e.g., `app.log` -> `app.log.1`) and tells the application to reload its file pointers natively via a `postrotate` script.
    *   If the app *doesn't* support reloading gracefully (unable to let go of the file handle), logrotate utilizes `copytruncate`, which duplicates the file contents into an archive and clears the live file back to `0 bytes` instantaneously without moving it.
*   **Delay Compress Strategy:** Using `delaycompress` tells the engine to rotate the file today, but hold off on actually `.gz` compressing it until *tomorrow's* rotation. This ensures the most recent 24-48 hours of historical logs remain purely uncompressed for instant `tail -f` and `grep` SRE troubleshooting.

## 💻 Essential Execution (Commands & YAML)

### 1. The Core SRE Configuration (`/etc/logrotate.d/my_app`)
```text
/var/log/my_app/*.log {
    daily               # Execute rotation every single day
    size 10M            # Alternate trigger: Force rotation if file breaches 10MB
    rotate 7            # Retain exactly 7 archived files. The 8th is hard-deleted.
    compress            # Auto-gzip the older logs 
    delaycompress       # Skip compression on 'file.log.1' for rapid SRE querying
    missingok           # Suppress error codes if the log file hasn't been generated yet
    notifempty          # Do not process anything if the file is 0 bytes
    copytruncate        # Extremely aggressive in-place clear without breaking file handles!
}
```

### 2. Manual Diagnostics & Executions
```bash
# Verify the installed binary version and capabilities
logrotate --version

# The 'Dry-Run': Process the config and output what *would* happen to terminal safely
logrotate -d /etc/logrotate.d/my_app

# The 'Force Execute': Bypass the 24-hour wait limit in the status file and trigger NOW
logrotate -vf /etc/logrotate.d/my_app

# View the logrotate brain (shows exactly when files were last shifted)
cat /var/lib/logrotate/status
```

## ⚠️ Production Gotchas & Interview Traps
*   **The Gotcha (Log Bloat between Crons):** The `size 100M` parameter does *not* mean the file is instantly cut the second it hits 100MB! Because `logrotate` only wakes up once per day (usually 2:00 AM), if a runaway application writes 50 Gigabytes of data in 4 hours, it will still crash the server before `logrotate` ever gets a chance to awake and check the `size` rule! For hyper-active logs, you must manually run logrotate via a custom 5-minute cronjob.
*   **The Interview Trap:** "An engineer deleted a 50GB log file via `rm -rf`, but the disk is still 100% full. Why?"
    *   *The SRE Answer:* The application (like Docker or Tomcat) still holds an active file handle to the inode. The name pointer is gone, creating a "Ghost File". You must restart the application to free the inode, or use `> file.log` / `copytruncate` to properly empty it in-place.
*   **Copytruncate CPU Overhead:** `copytruncate` involves reading the entire file and writing a raw copy to disk before truncating. On an extremely hot 500GB log file, this can cause massive I/O spikes and bring down an undersized Virtual Machine. 

## 🔍 Debugging (Where to look when it fails)
If your Linux disk is exhausted and you suspect logrotate failure:

1.  **Read the daily cron execution logs:**
    ```bash
    cat /var/log/cron | grep logrotate
    ```
2.  **Ensure you didn't create a syntax error in your config:**
    ```bash
    # SREs ALWAYS run this after modifying drop-in configs
    logrotate -d /etc/logrotate.conf
    ```
3.  **Check for "Ghost Files" taking up unseen space:**
    ```bash
    sudo lsof | grep deleted
    ```

## 📝 10-Second Cheat Sheet
`logrotate` is the automated Linux garbage collector for log files. It lives in `/etc/logrotate.d/` and utilizes `cron` to run nightly. SREs configure arguments like `rotate 7` (retention quantity) and `compress` (gzip storage tiering) to deterministically ensure applications never encounter a `No space left on device` severity-1 outage. When modifying configurations, always use `logrotate -d` to dry-run test, and `logrotate -f` to force execution.
