---
title: "Skill Spec: bmad-distillation-generator"
status: "complete"
created: "2026-03-13"
purpose: "Full specification for the skill builder agent to implement"
reference-skill: "bmad-bmm-product-brief-preview (use as architectural pattern)"
---

# bmad-distillation-generator — Skill Specification

## Purpose

A general-purpose utility skill that takes any set of input documents and produces a single hyper-compressed, token-efficient document (a "distillate") that an LLM can consume as sole context input for downstream workflows. The distillate is **lossless compression for an LLM reader** — every fact, decision, constraint, and relationship from the source documents is preserved, but all overhead that humans need and LLMs don't is stripped.

This is a compression task, not a capture task. The skill assumes all relevant information has already been captured in the source documents. Its job is to produce the most token-efficient representation possible without losing signal.

## What a Distillate Is

A distillate is NOT a summary. Summaries are lossy — they capture the gist but drop detail. A distillate preserves all detail through lossless compression optimized for LLM consumption:

- Every fact, decision, and constraint appears exactly once
- No prose transitions, rhetoric, or persuasion
- No repetition — deduplicated across all source documents
- No formatting for human scannability (decorative bold, whitespace for visual breathing room)
- No explaining things an LLM already knows (common terms, well-known companies, standard concepts)
- No hedging language ("we believe", "it's likely that") — state the signal directly
- Relationships between items are explicit, not implied
- Each item carries enough context to be understood without the source documents
- Rejected ideas and open questions are preserved — they prevent downstream re-proposal

**Format:** Dense thematically-grouped bullets. Markdown structure for hierarchy only (## for themes, - for items). No decorative formatting. Every token carries signal.

## Activation & Inputs

### Required Inputs
- **source_documents** — One or more file paths or inline content to distill

### Optional Inputs
- **downstream_consumer** — What workflow or agent will consume this distillate (e.g., "PRD creation", "architecture design", "story implementation"). When provided, the compressor uses this to judge what's signal vs noise. When omitted, preserve everything — no filtering.
- **token_budget** — Approximate target size. When provided and the distillate would exceed it, trigger semantic splitting. When omitted, produce the smallest possible single document.
- **output_path** — Where to save the distillate. When omitted, save adjacent to the primary source document with `-distillate.md` suffix.

### Flags
- **--validate** — After producing the distillate, run a round-trip reconstruction test (see Validation section below)

### Activation Modes
- **Direct invocation:** User calls the skill with inputs
- **Called by another skill:** Other BMAD skills (product brief, PRD, architecture) can invoke this as a final step after producing their primary document + discovery notes

## Skill Architecture

```
bmad-distillation-generator/
  SKILL.md                          # Entry point, input validation, routing
  agents/
    distillate-compressor.md        # Core compression agent
    round-trip-reconstructor.md     # Validation: reconstructs source docs from distillate
  prompts/
    compression-rules.md            # The compression ruleset (shared reference)
    splitting-strategy.md           # Semantic splitting logic for large inputs
  resources/
    distillate-format-reference.md  # Format examples showing before/after
```

## Stages

| # | Stage | Purpose | Location |
|---|-------|---------|----------|
| 1 | Validate & Analyze | Validate inputs, assess total size, detect document types | SKILL.md |
| 2 | Compress | Fan out compressor agent(s), produce distillate | agents/distillate-compressor.md |
| 3 | Verify & Output | Structured completeness check, save output | SKILL.md |
| 4 | Round-Trip Validation | (optional, --validate flag) Reconstruct sources from distillate, diff against originals | agents/round-trip-reconstructor.md |

### Stage 1: Validate & Analyze (SKILL.md)

1. **Validate inputs exist and are readable.** If source documents are paths, read them. If inline content, accept directly.

2. **Assess total input size.** Count approximate tokens across all source documents.

3. **Detect document types.** Understand what each source document is (product brief, discovery notes, research report, architecture doc, PRD, etc.) — this informs how to group themes in the output.

4. **Determine splitting need.** If total input is large (heuristic: source documents collectively exceed ~15,000 tokens of content) AND no token_budget is set, warn the user that the distillate may be large and offer to split semantically. If token_budget is set and would require splitting, proceed automatically.

5. **Route to Stage 2.** Pass all source content, downstream_consumer context, and splitting decision to the compressor.

### Stage 2: Compress (agents/distillate-compressor.md)

The compressor agent is the core of this skill. It receives all source document content and produces the distillate.

**Compression process:**

1. **Extract all discrete facts, decisions, constraints, requirements, relationships, rejected ideas, and open questions** from all source documents. Treat this as entity extraction — pull out every distinct piece of information.

2. **Deduplicate ruthlessly.** If the same fact appears in the brief's executive summary AND the discovery notes' technical context, it appears once in the distillate. Choose the version with the most context.

3. **Apply downstream filtering** (only if downstream_consumer is specified). For each extracted item, ask: "Would the downstream workflow need this?" Drop items that are clearly irrelevant to the stated consumer. When uncertain, keep.

4. **Group thematically.** Organize items into coherent themes derived from the source content — not from a fixed template. The themes should reflect what the documents are actually about. Common groupings: core concept, problem/motivation, solution/approach, users/segments, technical decisions, constraints, scope boundaries, competitive context, rejected alternatives, open questions, risks.

5. **Compress language.** For each item:
   - Strip prose transitions and connective tissue
   - Remove hedging and rhetoric
   - Remove explanations of common knowledge
   - Preserve specific details (numbers, names, versions, dates)
   - Ensure the item is self-contained (understandable without reading the source)
   - Make relationships explicit ("X because Y", "X blocks Y", "X replaces Y")

6. **Apply the compression rules** from `prompts/compression-rules.md` as a final pass.

**If semantic splitting is required:**

7. **Identify natural semantic boundaries** in the source content. These are NOT arbitrary size breaks — they are coherent topic clusters that a downstream workflow might load independently.

8. **Produce a root distillate** that contains: a 3-5 bullet orientation (what was distilled, for whom, how many parts), cross-references to section distillates, and any items that span multiple sections.

9. **Produce section distillates**, each self-sufficient — a reader loading only one section should understand it without the others. Include a 1-line context header: "This section covers [topic]. Part N of M from [source document names]."

### Stage 3: Verify & Output (SKILL.md)

After the compressor returns:

1. **Structured completeness check.** Extract all Level 2+ headings and key named entities (products, people, technologies, decisions) from the source documents. Verify each appears in the distillate. If gaps are found, send them back to the compressor for a targeted fix pass — not a full recompression.

2. **Format check.** Verify the output follows distillate format rules:
   - No prose paragraphs (only bullets)
   - No decorative formatting
   - No repeated information
   - Each bullet is self-contained
   - Themes are clearly delineated

3. **Save output.** Write the distillate to the output path. Use frontmatter:

```yaml
---
type: bmad-distillate
sources:
  - "{source file 1}"
  - "{source file 2}"
downstream_consumer: "{consumer or 'general'}"
created: "{timestamp}"
token_estimate: {approximate token count}
parts: {1 or N if split}
---
```

4. **Report to user or calling skill.** Return the file path(s) and a one-line confirmation. If called by another skill, return structured output:

```json
{
  "status": "complete",
  "distillate": "{path}",
  "section_distillates": ["{path1}", "{path2}"] or null,
  "token_estimate": N,
  "source_documents": ["{path1}", "{path2}"],
  "completeness_check": "pass" or "pass_with_additions"
}
```

## Compression Rules (for prompts/compression-rules.md)

These rules govern how text is compressed. They are the core IP of this skill.

### Strip — Remove entirely
- Prose transitions: "As mentioned earlier", "It's worth noting", "In addition to this"
- Rhetoric and persuasion: "This is a game-changer", "The exciting thing is"
- Hedging: "We believe", "It's likely that", "Perhaps", "It seems"
- Self-reference: "This document describes", "As outlined above"
- Common knowledge explanations: "Vercel is a cloud platform company", "MIT is an open-source license"
- Repeated introductions of the same concept
- Section transition paragraphs
- Formatting-only elements (decorative bold/italic for emphasis, horizontal rules for visual breaks)

### Preserve — Keep always
- Specific numbers, dates, versions, percentages
- Named entities (products, companies, people, technologies)
- Decisions made and their rationale (compressed: "Decision: X. Reason: Y")
- Rejected alternatives and why (compressed: "Rejected: X. Reason: Y")
- Explicit constraints and non-negotiables
- Dependencies and ordering relationships
- Open questions and unresolved items
- Scope boundaries (in/out/deferred)
- Success criteria and how they're validated
- User segments and what success means for each

### Transform — Change form for efficiency
- Long prose paragraphs → single dense bullet capturing the same information
- "We decided to use X because Y and Z" → "X (rationale: Y, Z)"
- Repeated category labels → group under a single heading, no per-item labels
- "Risk: ... Severity: high" → "HIGH RISK: ..."
- Conditional statements → "If X → Y" form
- Multi-sentence explanations → semicolon-separated compressed form

### Deduplication Rules
- Same fact in multiple documents → keep the version with most context
- Same concept at different detail levels → keep the detailed version
- Overlapping lists → merge into single list, no duplicates
- When source documents disagree → note the conflict explicitly: "Brief says X; discovery notes say Y — unresolved"

## Format Reference (for resources/distillate-format-reference.md)

### Before (human-readable brief excerpt)
```
## What Makes This Different

**The anti-fragmentation layer.** The AI tooling space is fracturing across 40+
platforms with no shared methodology layer. BMAD is uniquely positioned to be the
cross-platform constant — the structured approach that works the same in Cursor,
Claude Code, Windsurf, Copilot, and whatever launches next month. Every other
methodology or skill framework maintains its own platform support matrix. By
building on the open-source skills CLI ecosystem, BMAD offloads the highest-churn
maintenance burden and focuses on what actually differentiates it: the methodology
itself.
```

### After (distillate)
```
## Differentiation
- Anti-fragmentation positioning: BMAD = cross-platform constant across 40+ fragmenting AI tools; no competitor provides shared methodology layer
- Platform complexity delegated to Vercel skills CLI ecosystem (MIT); BMAD maintains methodology, not platform configs
```

### Before (discovery notes excerpt)
```
## Competitive Landscape

- **Vercel Skills.sh**: 83K+ skills, 18 agents, largest curated leaderboard —
  but dev-only, skills trigger unreliably (20% without explicit prompting)
- **SkillsMP**: 400K+ skills directory, pure aggregator with no curation or CLI
- **ClawHub/OpenClaw**: ~3.2K curated skills with versioning/rollback, small ecosystem
- **Lindy**: No-code AI agent builder for business automation — closed platform,
  no skill sharing
- **Microsoft Copilot Studio**: Enterprise no-code agent builder — vendor-locked
  to Microsoft
- **MindStudio**: No-code AI agent platform — siloed, no interoperability
- **Make/Zapier AI**: Workflow automation adding AI agents — workflow-centric,
  not methodology-centric
- **Key gap**: NO competitor combines structured methodology with plugin
  marketplace — this is BMAD's whitespace
```

### After (distillate)
```
## Competitive Landscape
- No competitor combines structured methodology + plugin marketplace (whitespace)
- Skills.sh (Vercel): 83K skills, 18 agents, dev-only, 20% trigger reliability
- SkillsMP: 400K skills, aggregator only, no curation/CLI
- ClawHub: 3.2K curated, versioning, small ecosystem
- No-code platforms (Lindy, Copilot Studio, MindStudio, Make/Zapier): closed/siloed, no skill portability, business-only
```

## Stage 4: Round-Trip Validation (agents/round-trip-reconstructor.md)

**Triggered by:** `--validate` flag. Optional. Not run by default.

**Purpose:** Prove the distillate is lossless by reconstructing the original source documents from the distillate alone, then diffing against the originals to surface any information loss.

### Process

1. **The reconstructor agent receives ONLY the distillate.** It has no access to the original source documents. This is critical — if it could see the originals, the test is meaningless.

2. **Detect source document types from the distillate's frontmatter.** The `sources` field lists what was distilled. The reconstructor uses the document type (product brief, discovery notes, architecture doc, etc.) to understand what kind of document to reconstruct.

3. **Reconstruct each source document.** For each source listed in frontmatter, produce a full human-readable document from the distillate's content alone. The reconstruction should:
   - Use appropriate prose, structure, and formatting for the document type
   - Include all sections the original would have had
   - Not invent information — only use what's in the distillate
   - Flag any places where the distillate felt insufficient with `[POSSIBLE GAP]` markers

4. **Save reconstructions** as temporary files adjacent to the distillate with `-reconstruction-{N}.md` suffixes.

### Diff Analysis (back in SKILL.md)

After the reconstructor returns, the main skill performs the diff:

1. **Read both the original source documents and the reconstructions.**

2. **Semantic diff, not text diff.** Don't compare prose word-for-word — compare information content. For each section of the original, ask:
   - Is the core information present in the reconstruction?
   - Are specific details preserved (numbers, names, decisions)?
   - Are relationships and rationale intact?
   - Did the reconstruction add anything not in the original? (indicates hallucination to fill gaps)

3. **Produce a validation report** saved adjacent to the distillate as `-validation-report.md`:

```markdown
---
type: distillate-validation
distillate: "{distillate path}"
sources: ["{source paths}"]
created: "{timestamp}"
---

## Validation Summary
- Status: PASS | PASS_WITH_WARNINGS | FAIL
- Information preserved: {percentage estimate}
- Gaps found: {count}
- Hallucinations detected: {count}

## Gaps (information in originals but missing from reconstruction)
- {gap description} — Source: {which original}, Section: {where}

## Hallucinations (information in reconstruction not traceable to originals)
- {hallucination description} — appears to fill gap in: {section}

## Possible Gap Markers (flagged by reconstructor)
- {marker description}
```

4. **If gaps are found**, offer to run a targeted fix pass on the distillate — adding the missing information without full recompression.

5. **Clean up** — delete the temporary reconstruction files after the report is generated (the report preserves the findings).

### When to use --validate

- During development/testing of the distillation generator itself
- When distilling critical documents where information loss is unacceptable (architecture decisions, compliance-relevant specs)
- As a quality gate before handing off a distillate to a high-stakes downstream workflow
- NOT for routine use — it adds significant token cost (full reconstruction + diff analysis)

## Design Rationale

### Why a separate skill, not inline in each workflow?
Compression is a distinct competency. The agent producing a brief is optimized for collaborative discovery and persuasive writing. The agent producing a distillate is optimized for ruthless information extraction and deduplication. Separating them means each can be excellent at its job. It also means any BMAD workflow can call the same distillation skill — briefs, PRDs, architecture docs, research reports — without each reimplementing compression logic.

### Why self-check instead of a separate validator?
The completeness check is mechanical (does each heading/entity from source appear in output?) not judgmental. A checklist-based self-audit is reliable for this task. A separate validator agent adds a round-trip and token cost for marginal benefit. If the downstream workflow finds gaps, it can always read the source documents directly — the distillate is an optimization, not a single point of failure. A validator can be added later if needed.

### Why round-trip reconstruction for validation?
The strongest proof of lossless compression is reconstruction. If an LLM reading only the distillate can reproduce both source documents with no meaningful information loss, the distillate is complete. The delta between originals and reconstructions is a precise quality metric: missing information = compression loss, added information = hallucination filling gaps (which also flags where the distillate was too terse). This is more rigorous than any checklist-based approach because it tests actual recoverability, not just presence of keywords.

### Why semantic splitting instead of size-based?
Arbitrary splits (every N tokens) break coherence. A downstream workflow loading "part 2 of 4" of a size-split distillate gets context fragments. Semantic splits produce self-contained topic clusters that a workflow can load selectively — "give me just the technical decisions section" — which is more useful and more token-efficient for the consumer.

## Integration Points

### As a standalone skill
User invokes directly: "distill these documents for PRD creation" or "create a distillate of the architecture doc"

### Called by other BMAD skills
Any skill that produces a primary document + discovery notes can call this as a final optional step:
- Product Brief → offers distillate for PRD creation
- PRD → offers distillate for architecture/story creation
- Architecture → offers distillate for implementation stories
- Research Reports → offers distillate for brief/PRD input

### Calling convention for other skills
Other skills invoke this by telling the LLM to run the `bmad-distillation-generator` skill with the source documents and downstream consumer specified. The distillation skill handles everything else and returns the output path.
