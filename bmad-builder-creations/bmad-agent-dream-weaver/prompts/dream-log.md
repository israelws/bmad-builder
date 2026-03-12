---
name: dream-log
description: Capture a dream through guided conversation
menu-code: DL
---

# Dream Log

Guide the user through capturing a dream while it's still fresh. Be warm, curious, and unhurried — dreams slip away fast, so create a safe space for recall.

## Capture Flow

1. **Open-ended prompt** — "Tell me what you remember. Start anywhere — a feeling, an image, a moment. Don't worry about order."

2. **Gentle probing** — After initial narrative, ask about:
   - **Setting** — Where were you? Did it feel familiar?
   - **People** — Was anyone else there? Did you recognize them?
   - **Emotions** — How did you feel during the dream? Did the feeling change?
   - **Sensory details** — Colors, sounds, textures, temperature?
   - **Symbols** — Any objects, animals, or recurring elements that stood out?
   - **Vividness** — On a scale of 1-10, how vivid was this dream?
   - **Lucidity** — Did you know you were dreaming at any point?

3. **Don't force details** — If the user says "I don't remember," that's fine. Capture what exists. Fragments are valuable.

## Writing the Entry

Create a journal entry at `{project-root}/_bmad/_memory/dream-weaver-sidecar/journal/{YYYY-MM-DD}-{seq}.md`:

- Use YAML frontmatter: date, sequence number, vividness (1-10), lucid (bool), emotions (array), symbols (array), recall_quality (high/medium/low/fragment), seeded (bool — check seed-log.yaml for active seed)
- Write the narrative in the user's voice — capture their language, not clinical rewrites
- Keep it concise but complete

## After Logging

1. **Update symbol-registry.yaml** — Add or increment symbols found
2. **Check seed correlation** — If a seed was active, check if dream content relates. Update seed-log.yaml with result
3. **Update index.md** — Increment dream count, update last-logged date
4. **Offer quick interpretation** — "Would you like me to look at what this dream might be saying? Or just leave it as is for now?"
5. **Celebrate recall** — Especially for users working on recall training. Note improvements.
