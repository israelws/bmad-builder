---
name: dream-query
description: Search dream history by symbol, emotion, date, or keyword
menu-code: DQ
---

# Dream Query

Search the dream journal for specific dreams, symbols, or patterns. This is the user's way to ask "When did I last dream about X?"

## Query Types

**By symbol** — "When did I dream about water?"
- Search `symbol-registry.yaml` for the symbol
- Find all journal entries containing that symbol in frontmatter
- Present chronologically with brief excerpts

**By emotion** — "Show me my anxious dreams"
- Search journal entries with matching emotion in frontmatter
- Present with dates, vividness, and key symbols

**By date/range** — "What did I dream last week?"
- List journal entries within the date range
- Show date, title, key symbols, vividness

**By keyword** — "Did I ever dream about my grandmother?"
- Full-text search across journal narrative content
- Present matching entries with relevant excerpts

**By attribute** — "Show me my most vivid dreams" / "Which dreams were lucid?"
- Filter by vividness score, lucid flag, recall quality
- Present sorted by the relevant attribute

## Presentation

- Show results as a brief list first (date, title, key symbols)
- Offer to dive deeper into any specific entry
- If patterns emerge across results, mention them: "Interesting — your grandmother appears in three dreams, always near water."

## No Results

If nothing matches: "I don't see that in your journal yet. But now that you're looking for it, you might start noticing it. Dreams are funny that way."
