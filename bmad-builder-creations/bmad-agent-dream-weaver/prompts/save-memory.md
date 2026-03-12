---
name: save-memory
description: Explicitly save current session context to memory
menu-code: SM
---

# Save Memory

Immediately persist the current session context to memory.

## Process

1. **Read current index.md** — Load existing context

2. **Update with current session:**
   - Dreams logged this session
   - Coaching progress and technique updates
   - New symbols discovered
   - Recall observations
   - Seeds planted or results noted
   - Next steps to continue

3. **Write updated index.md** — Replace content with condensed, current version

4. **Checkpoint other files if needed:**
   - `patterns.md` — Add new personal symbol meanings or preferences discovered
   - `chronology.md` — Add session summary if significant events occurred
   - `coaching-profile.yaml` — Update if experience level, techniques, or metrics changed
   - `symbol-registry.yaml` — Update if new symbols logged (run `scripts/symbol_stats.py` if multiple dreams were logged)

## Output

Confirm save with brief summary: "Memory saved. {brief-summary-of-what-was-updated}"
