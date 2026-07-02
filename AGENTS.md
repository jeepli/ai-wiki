# LLM Wiki

An AI learning knowledge base maintained by Codex/Claude.
Based on Andrej Karpathy's LLM Wiki pattern.

## Purpose

This wiki is a structured, interlinked knowledge base for personal AI learning.
The human curates sources, asks questions, and guides interpretation. Agents maintain `wiki/` pages, citations, navigation, and audit reports.

## Folder structure

```
raw/                  -- source documents; treat existing files as immutable during ingest
wiki/                 -- markdown pages maintained by Codex/Claude
wiki/index.md         -- table of contents for the entire wiki
wiki/log.md           -- append-only record of wiki operations
wiki/papers/          -- papers, long-form articles, course notes, and source summaries
wiki/concepts/        -- reusable AI/ML/LLM concepts
wiki/models/          -- model families, architectures, training recipes, and capabilities
wiki/systems/         -- inference, training, data, evaluation, kernel, and infrastructure systems
wiki/math/            -- mathematical foundations and derivations
reports/              -- timestamped wiki lint/audit reports
```

Create another scoped `wiki/` subdirectory only when the content clearly does not fit the default layout.

## Workflows

- Use `ingest-wiki-docs` when ingesting new or updated raw documents into `wiki/`.
- Use `lint-wiki-docs` for wiki lint or audit requests.

### Ingest workflow

- Never modify `raw/` during ingest.
- Before editing `wiki/`, summarize selected sources, learning takeaways, proposed pages, target directories, page granularity, and unresolved source-quality issues; wait for user confirmation.
- Prefer one `wiki/papers/...` summary page for each substantial source or source group.
- Create concept/model/system/math pages only for reusable, central, or recurring ideas.
- Choose directories by page subject: `papers/` for source-bound notes, `concepts/` for reusable definitions or mechanisms, `models/` for model architectures/families/recipes/capabilities, `systems/` for implementation/runtime/training/inference/serving/data/evaluation systems, and `math/` for formulas or derivations.
- Keep paper-specific experiments, author claims, tables, ablations, and limitations in `papers/`; put stable cross-source explanations, common pitfalls, and later-source synthesis in concept/model/system/math pages.
- Cite factual paragraphs, key numbers, paper results, definitions, comparisons, diagrams, and limitations.
- Always update `wiki/index.md` and `wiki/log.md` after wiki page changes.

### Lint workflow

- Lint is report-only by default; do not modify `wiki/`, `raw/`, `wiki/index.md`, or `wiki/log.md` unless the user explicitly asks to fix findings.
- Write audit results to `reports/{{yyyy-mm-dd-hh-mm-ss}}.md`.
- Check root layout, page format, broken links, orphan pages, index/log coverage, citation coverage, source support, raw coverage, concept gaps, contradictions, outdated claims, and prior-report regressions.
- Do not write "No findings" unless all in-scope categories and prior-report regression checks were completed.
- If any category is skipped, call the report a partial audit and list skipped categories in coverage notes.

## Rules

- Do not casually modify `raw/`. Create or update raw files only for explicit source sync or user-requested raw-source tasks; preserve provenance and version/history metadata where applicable.
- Keep root-level `wiki/*.md` limited to `wiki/index.md` and `wiki/log.md`; create content pages under scoped subdirectories.
- Keep directory names and page names lowercase kebab-case, for example `machine-learning.md`.
- Use path-style wiki links, for example `[[papers/flashattention]]` or `[[concepts/attention]]`.
- Prefer updating existing pages over creating duplicates.
- Do not create concept pages for every heading in a paper; avoid page sprawl.
- Write in clear, plain language focused on learning value rather than exhaustive transcription.
- When uncertain about categorization, source reliability, conflicting claims, or target page ownership, ask the user before writing.
