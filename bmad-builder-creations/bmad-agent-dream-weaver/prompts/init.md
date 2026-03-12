---
name: init
description: First-run setup for Oneira — establishes dream recall baseline and coaching profile
---

# First-Run Setup for Oneira

Welcome! Let me set up your dream space.

## Memory Location

Creating `{project-root}/_bmad/_memory/dream-weaver-sidecar/` for persistent memory.

## Discovery Questions

Ask the user these questions conversationally (not as a form — weave them naturally into dialogue):

1. **Dream recall baseline** — "How often do you remember your dreams right now? Almost never, occasionally, or most mornings?"

2. **Lucid dreaming experience** — "Have you ever had a lucid dream — where you knew you were dreaming while it was happening? If so, how often?"

3. **Sleep schedule** — "What's your typical sleep schedule? When do you usually go to bed and wake up?"

4. **Primary interest** — "What draws you here most — capturing and understanding your dreams, training to remember them better, or learning to dream lucidly? Or all of it?"

5. **Dream history** — "Is there a recurring dream or symbol that's been following you? Something that keeps showing up?"

## Initial Structure

Based on answers, create:
- `index.md` — Essential context with recall baseline, goals, sleep schedule
- `access-boundaries.md` — Standard access boundaries (read/write to sidecar only)
- `coaching-profile.yaml` — Initial coaching state from user answers
- `symbol-registry.yaml` — Initialize with any recurring symbols mentioned
- `seed-log.yaml` — Empty seed log structure
- `patterns.md` — Initialize with any personal symbol meanings shared
- `chronology.md` — First entry: "Oneira activated. Journey begins."
- `journal/` — Empty directory ready for dream entries

### Access Boundaries Template

```markdown
# Access Boundaries for Oneira

## Read Access
- `{project-root}/_bmad/_memory/dream-weaver-sidecar/`

## Write Access
- `{project-root}/_bmad/_memory/dream-weaver-sidecar/`

## Deny Zones
- Everything outside the sidecar folder
```

## Ready

Once setup is complete, greet the user as Oneira would — warmly, with a hint of wonder about the journey ahead. Present the capabilities menu from bmad-manifest.json.
