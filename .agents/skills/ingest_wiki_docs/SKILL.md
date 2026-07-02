---
name: ingest-wiki-docs
description: Use when ingesting new or updated raw documents into this personal AI learning wiki, including papers, posts, course notes, model/system docs, and PDFs under raw/. Guides source triage, pre-write confirmation, scoped wiki pages, citations, index updates, and log updates.
---

# Ingest Wiki Docs

## Overview

Turn immutable `raw/` sources into maintained `wiki/` pages for a personal AI learning knowledge base inspired by Karpathy's LLM Wiki pattern.

Core rule: read sources, summarize learning value and proposed page changes to the user, wait for confirmation, then write the smallest useful wiki delta with citations, links, `wiki/index.md`, and `wiki/log.md`.

## Hard Constraints

- Never modify `raw/` during ingest.
- Always update `wiki/index.md` and `wiki/log.md` after wiki changes.
- Keep only `wiki/index.md` and `wiki/log.md` directly under `wiki/`.
- Put content pages under scoped subdirectories of `wiki/`.
- Keep directory names and page names lowercase kebab-case.
- Ask before writing when categorization, target ownership, conflicts, or source reliability is unclear.
- Prefer learning clarity over exhaustive transcription.

## Directory Layout

- `wiki/index.md`: table of contents for all wiki pages.
- `wiki/log.md`: append-only ingest and maintenance log.
- `wiki/papers/`: papers, long-form articles, course notes, and source summaries.
- `wiki/concepts/`: reusable AI, ML, LLM, optimization, and systems concepts.
- `wiki/models/`: model families, architectures, training recipes, and capabilities.
- `wiki/systems/`: inference, training, data, evaluation, kernel, and infrastructure systems.
- `wiki/math/`: mathematical foundations and derivations.

Create another scoped directory only when the source set clearly does not fit these categories.

## Source Selection

When the user asks to ingest new files:

1. Inspect repository status and raw inventory.
2. Select new or changed ingestable files under `raw/`.
3. Group sources by topic or learning unit when multiple files cover the same idea.
4. For PDFs, extract enough text to judge structure, citation quality, and OCR/page extraction reliability.

## Required Pre-Write Checkpoint

Before editing `wiki/`, report the learning takeaways and wait for confirmation.

The summary must include:

- selected source files or source groups
- important concepts, claims, methods, results, and limitations
- proposed pages to create or update, including target directories
- proposed granularity: source summary only, concept pages, or both
- unresolved questions, conflicts, or source quality issues

Do not skip this step for "ingest new files" requests.

## Update Workflow

After confirmation:

1. Choose the target directory from the default layout.
2. Create or update one source summary page for each substantial paper, article, or course note.
3. Create or update concept pages only for ideas that are reusable, central to AI learning, or appear across sources.
4. Link related pages with path-style `[[wiki-links]]`, such as `[[papers/flashattention]]` or `[[concepts/attention]]`.
5. Cite factual paragraphs, key numbers, claims, comparisons, diagrams, and limitations.
6. Update `wiki/index.md` with changed pages and one-line descriptions, grouped by directory.
7. Append `wiki/log.md` with date, source name, and changed pages.
8. Verify links, formatting, citations, and root-level file placement before reporting completion.

Prefer updating existing pages over creating duplicates. Do not create a page for one-off details that only matter inside a single source summary.

## Page Granularity

- Use `wiki/papers/...` for substantial source summaries.
- Use `wiki/concepts/...` only for ideas likely to be linked from future notes.
- Use `wiki/systems/...`, `wiki/models/...`, or `wiki/math/...` only for reusable systems, models, architectures, methods, or derivations.
- Keep narrow implementation details inside the source page unless they explain a general pattern.

## Page Format

Every maintained page should include:

```markdown
# Page Title

**Summary**: One to two sentences. (source: raw/source-file.pdf)

**Sources**: `raw/source-a.md`; `raw/path/source-b.md`

**Last updated**: YYYY-MM-DD

---

## Why it matters
## Key ideas
## Method or mechanism
## Results and limitations
## Open questions
## Related pages
```

For concept pages, use concept-oriented headings when useful:

- `## Intuition`
- `## Definition`
- `## Common pitfalls`

## Citation Rules

- Cite every factual paragraph with `(source: ...)`.
- Cite key numbers, paper results, definitions, comparisons, and limitations explicitly.
- Use source paths when basenames would be ambiguous.
- If PDF page numbers are available, include them when useful, such as `(source: raw/paper.pdf, p. 4)`.
- If a claim is useful but not sourced, mark it as needing verification.
- When newer sources supersede older ones, cite the newer source in the updated claim.
- Tables, matrices, and diagrams need explicit block-level source notes; surrounding prose alone is not enough.

## Failure Handling

| Condition | Action |
|---|---|
| PDF extraction is poor or incomplete | Tell the user, summarize only reliable sections, and mark uncertain claims as needing verification. |
| Target directory is unclear | Ask the user before writing. |
| Proposed page overlaps an existing page | Update the existing page unless a new page has a clearer reusable scope. |
| Sources conflict | Report the conflict in the pre-write summary and wait for user direction. |
| Source lacks provenance or date | Record what is known and mark missing metadata explicitly. |

## Do Not Do

- Do not rewrite raw sources or treat `raw/` as scratch space.
- Do not create duplicate pages with slightly different names.
- Do not create concept pages for every heading in a paper.
- Do not copy long passages; summarize and cite.
- Do not leave wiki changes without matching `wiki/index.md` and `wiki/log.md` updates.
