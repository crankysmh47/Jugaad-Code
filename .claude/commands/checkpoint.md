---
description: Emergency manual checkpoint — commit all dirty changes immediately
model: claude-sonnet-4-6
allowed-tools: Bash
---

Immediately checkpoint all uncommitted work.

1. Run `git status --porcelain` to check if repo is dirty.
2. If dirty:
   - `git add -A`
   - `git commit -m "chore: [PK-checkpoint] manual @ $(date '+%Y-%m-%d %H:%M')"`
   - Report what was committed
3. If clean: report "Sab theek hai — kuch commit karne ki zaroorat nahi."
4. Optionally run `git push` if remote is configured and internet is healthy.
