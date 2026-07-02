# LLM Wiki

A ai related knowledge base maintained by Codex/Claude.
Based on Andrej Karpathy's LLM Wiki pattern.

## Purpose

This wiki is a structured, interlinked knowledge base for personal ai learning
Codex/Claude maintains the wiki. The human curates sources, asks questions, and guides the analysis.

## Folder structure

```
raw/            -- source documents. Treat existing raw files as immutable during ingest; add/update raw only through explicit source sync
wiki/           -- markdown pages maintained by Codex/Claude
wiki/index.md   -- table of contents for the entire wiki
wiki/log.md     -- append-only record of all operations
```

## Workflows

- Use `ingest-wiki-docs` when ingesting new or updated raw documents into `wiki/`.
- Use `lint-wiki-docs` for wiki lint or audit requests.

## Rules

- Do not casually modify `raw/`. Create or update raw only for explicit source sync, code-derived docs, API-doc sync, ops raw docs, architecture docs, confirmed facts, or user-requested raw-source tasks; preserve provenance and version/history metadata where applicable.
- Always update `wiki/index.md` and `wiki/log.md` after changes
- Keep root-level `wiki/*.md` limited to `wiki/index.md` and `wiki/log.md`; create content pages under scoped/common subdirectories.
- Keep page names lowercase with hyphens (e.g. `machine-learning.md`) and use path-style wiki links.
- Write in clear, plain language
- Keep answers concise unless the task explicitly requires detail.
- When uncertain about how to categorize something, ask the user
