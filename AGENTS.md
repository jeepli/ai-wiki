# LLM Wiki

An AI learning knowledge base maintained by Codex/Claude.
Based on Andrej Karpathy's LLM Wiki pattern.

## Purpose

This wiki is a structured, interlinked knowledge base for personal AI learning.
The human curates sources, asks questions, and guides interpretation. Agents maintain `wiki/` pages, citations, navigation, and audit reports.

## Folder structure

```
raw/                  -- source documents; treat existing files as immutable during ingest
raw/code-repos/       -- generated raw source docs derived from external repo code snapshots, versioned by commit
wiki/                 -- markdown pages maintained by Codex/Claude
wiki/index.md         -- table of contents for the entire wiki
wiki/log.md           -- append-only record of wiki operations
wiki/papers/          -- papers, long-form articles, course notes, and source summaries
wiki/concepts/        -- reusable AI/ML/LLM concepts
wiki/models/          -- model families, architectures, training recipes, and capabilities
wiki/systems/         -- inference, training, data, evaluation, kernel, and infrastructure systems
wiki/math/            -- mathematical foundations and derivations
reports/              -- timestamped wiki lint/audit reports
code-repos.yml        -- tracked manifest for explorable local code repositories
external-repos/       -- local code repository clones; ignored by git and not ingested directly
```

Create another scoped `wiki/` subdirectory only when the content clearly does not fit the default layout.

## Workflows

- Use `ingest-wiki-docs` when ingesting new or updated raw documents into `wiki/`.
- Use `lint-wiki-docs` for wiki lint or audit requests.
- Use `sync-code-repos` when cloning, refreshing, or overwriting local snapshots under `external-repos/` from `code-repos.yml`.
- Use `index-code-repos` when building or refreshing Serena memories and CodeGraph indexes for local snapshots under `external-repos/`.
- Use `generate-repo-raw-docs` when generating or refreshing versioned raw source documents for one `external-repos/` repository.
- Use `generate-code-repos-raw-docs` when batch status-checking, preparing, or publishing code-derived raw documents across `code-repos.yml`.

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

### Code repository sources

- `external-repos/` may contain local clones of inference engines and dependency repositories such as FlashAttention, FlashInfer, vLLM, and SGLang.
- Track allowed explorable repositories in `code-repos.yml`.
- Update local snapshots with `sync-code-repos`; treat the synced checkout as disposable and replaceable.
- Build or refresh code exploration indexes with `index-code-repos` after code snapshots change.
- Treat `external-repos/` as explorable code, not ingestable raw source.
- Do not bulk-ingest source code into `wiki/`.
- Store code-derived raw source documents under `raw/code-repos/<repo>/snapshots/<commit-short>/`; use `raw/code-repos/<repo>/latest.yml` as the current version pointer.
- Batch raw-doc workflows must wrap `generate-repo-raw-docs` per repo rather than duplicating single-repo generation rules.
- Explore code only when implementation evidence is needed for a user question or an explicitly requested code-derived wiki update.
- Prefer Serena and CodeGraph for symbol lookup, focused source reading, callers/callees, flow tracing, and impact analysis.
- Use `rg` for literal strings, filenames, config keys, logs, comments, or when semantic tools are unavailable.
- When writing code-derived facts into `wiki/`, cite repository name, path, symbol or file, and commit/version when available.
- Keep code-derived wiki content focused on stable architecture, APIs, mechanisms, and tradeoffs; do not copy large code blocks.

## Rules

- Do not casually modify `raw/`. Create or update raw files only for explicit source sync or user-requested raw-source tasks; preserve provenance and version/history metadata where applicable.
- Do not commit `external-repos/` contents.
- Keep root-level `wiki/*.md` limited to `wiki/index.md` and `wiki/log.md`; create content pages under scoped subdirectories.
- Keep directory names and page names lowercase kebab-case, for example `machine-learning.md`.
- Use path-style wiki links, for example `[[papers/flashattention]]` or `[[concepts/attention]]`.
- Prefer updating existing pages over creating duplicates.
- Do not create concept pages for every heading in a paper; avoid page sprawl.
- Write in clear, plain language focused on learning value rather than exhaustive transcription.
- When uncertain about categorization, source reliability, conflicting claims, or target page ownership, ask the user before writing.
