# Auto-push

Every change in this folder is committed and pushed to
https://github.com/seanmichclarke/apple-ii (private, branch `main`) automatically.

- **How:** `gitwatch` (Homebrew) watches the folder; 30 s after writes settle it runs
  `git add --all`, commits `Auto-commit: <timestamp>`, and pushes to `origin main`.
- **Runs as:** launchd agent `com.seanclarke.apple-ii-autopush`
  (`~/Library/LaunchAgents/com.seanclarke.apple-ii-autopush.plist`), starts at login, restarts if it dies.
- **Ignored:** anything in `.gitignore` (`.venv/`, `.DS_Store`, `__pycache__/`).
- **Log:** `~/Library/Logs/apple-ii-autopush.log`

Pause / resume / remove:

```sh
launchctl bootout   gui/$(id -u)/com.seanclarke.apple-ii-autopush                 # stop
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.seanclarke.apple-ii-autopush.plist  # start
rm ~/Library/LaunchAgents/com.seanclarke.apple-ii-autopush.plist                   # remove (after stop)
```

Caution: deletions are pushed too, and GitHub rejects files over 100 MB.
