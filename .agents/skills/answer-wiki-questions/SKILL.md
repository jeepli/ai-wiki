---
name: answer-wiki-questions
description: Use when Codex needs to answer questions from this AI learning wiki, raw source corpus, raw code-repository snapshots, or local external-repos code, especially when deciding whether wiki evidence is enough or deeper source/code exploration is required.
---

# Answer Wiki Questions

## Overview

Answer questions with the shallowest sufficient source-backed evidence. Search progressively from maintained wiki pages, to immutable raw sources, to code-derived raw docs or local code only when the earlier layer cannot support the answer.

Core rule: after each layer, run the sufficiency gate. If the gate passes, stop exploring and answer.

## Hard Constraints

- Do not edit `wiki/`, `raw/`, `wiki/index.md`, `wiki/log.md`, or `external-repos/` during Q&A unless the user explicitly asks for changes.
- Do not read `raw/` or code when `wiki/` already answers the question with adequate citations.
- Do not inspect local code just to be exhaustive. Enter code only when implementation evidence can change the answer.
- Treat `external-repos/` as explorable code, not wiki content or raw source.
- Prefer CodeGraph and Serena for symbol lookup, callers/callees, flow tracing, and impact analysis. Use `rg` for literal strings, filenames, config keys, logs, comments, and markdown search.
- If CodeGraph is not initialized for a needed code repository, ask before running `codegraph init -i`.

## Search Ladder

Use this ladder in order, stopping at the first sufficient layer:

1. **Wiki layer**: search maintained pages under `wiki/`.
2. **Raw layer**: inspect the cited or relevant source files under `raw/`, including paper PDFs under `raw/paper/`.
3. **Code-derived raw layer**: inspect `raw/code-repos/<repo>/latest.yml` and the referenced snapshot docs.
4. **Local code layer**: inspect `external-repos/<repo>/` with CodeGraph, Serena, and focused reads.

Do not skip straight to raw or code unless the user explicitly asks for original-source or code-level verification.

## Workflow

1. Classify the question:
   - Concept/source synthesis: start in `wiki/`.
   - Paper, post, course note, or source-specific detail: start in `wiki/`, then raw if the wiki citation is absent or too thin.
   - Code implementation, API surface, call flow, config, entrypoint, or behavior: start in `wiki/` and `raw/code-repos/`; enter local code if source docs are missing, stale, or insufficient.
   - Wiki maintenance status, coverage, links, or citations: use wiki and raw metadata; do not answer as a lint audit unless the user asks for an audit.
2. Search `wiki/` first with `rg` or known links from `wiki/index.md`.
3. Read only the relevant pages or sections.
4. Run the sufficiency gate.
5. If insufficient, follow citations or topic matches into `raw/`, then run the gate again.
6. If the answer depends on code, check `code-repos.yml` and `raw/code-repos/<repo>/latest.yml` before exploring `external-repos/`.
7. When using local code, prefer structural tools:
   - "Where is X defined?" -> CodeGraph search/context.
   - "What calls X?" -> CodeGraph callers.
   - "What does X call?" -> CodeGraph callees.
   - "How does X reach Y?" -> CodeGraph trace.
   - Literal strings, filenames, config keys -> `rg`.
8. Answer directly. Include evidence scope, search depth reached, and uncertainty only when it matters.

## Sufficiency Gate

Stop exploring when all are true:

- The core user question can be answered directly.
- Key factual claims have adequate support from a wiki citation, raw source path, code-derived snapshot, or concrete repo path/symbol.
- No unresolved contradiction, stale snapshot, missing citation, or ambiguity would materially change the answer.
- The next layer would add only incidental detail, not change confidence or content.

Continue to the next layer when any are true:

- The wiki page has no citation for the relevant claim.
- The wiki and raw sources conflict, or a newer source may supersede the wiki.
- The user asked for original-source, implementation, or code-level evidence.
- The answer depends on exact symbols, call paths, config keys, entrypoints, generated docs, or runtime behavior.
- A code-derived raw snapshot is missing, stale, or too broad to support the claim.

## Evidence Standards

- Wiki evidence: cite page paths such as `wiki/concepts/attention.md`.
- Raw evidence: cite source paths such as `raw/paper/source.pdf` or `raw/source.md`; include page numbers when already available.
- Code-derived raw evidence: cite repo name, snapshot commit from `latest.yml`, and document path.
- Local code evidence: cite repository name, commit if available, file path, and symbol or function when relevant.
- If support is partial, say what is supported and what remains uncertain.

## Answer Shape

Use a concise answer-first structure:

```markdown
[Direct answer.]

Evidence: `wiki/...`, `raw/...`, or `<repo>:<path>/<symbol>`.
Search depth: wiki | raw | code-derived raw | local code.
Uncertainty: [only if relevant]
```

For simple questions, combine these into prose instead of adding headings.

## Failure Handling

| Condition | Action |
|---|---|
| No wiki coverage | Say so, then search `raw/` if the question is still answerable from sources. |
| Raw source exists but extraction or provenance is weak | Answer only reliable parts and mark uncertain claims. |
| Code docs point to a stale snapshot | Say the snapshot is stale; ask before regenerating docs unless the user requested freshness. |
| Local repo is missing from `external-repos/` | State the missing repo and answer from available wiki/raw evidence if possible. |
| Multiple sources conflict | Present the conflict with source paths instead of choosing silently. |
| User asks to update wiki based on the answer | Switch to `ingest-wiki-docs` before editing. |
| User asks for a full audit | Switch to `lint-wiki-docs`. |

## Do Not Do

- Do not perform a full audit for a normal Q&A request.
- Do not bulk-ingest source code or raw files while answering.
- Do not cite memory or unstated model knowledge as if it came from the wiki.
- Do not keep searching after the sufficiency gate passes.
- Do not hide the fact that the answer stopped at wiki level when deeper evidence was not needed.

## Skill Validation

When creating or revising this skill, read `references/test-scenarios.md` and test both directions:

- wiki evidence is sufficient, so the agent must stop before raw/code;
- wiki evidence is insufficient, so the agent must escalate instead of guessing.
