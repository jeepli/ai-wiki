---
name: generate-repo-raw-docs
description: Use when Codex needs to generate, refresh, validate, or publish versioned raw knowledge-source documents derived from one local external repository snapshot under external-repos/ declared in code-repos.yml.
---

# Generate Repo Raw Docs

## Overview

Generate source-backed raw documents for exactly one external repository. This skill turns an indexed code snapshot into versioned `raw/code-repos/<repo>/snapshots/<commit>/` documents that later wiki ingest or Q&A can treat as the latest code-derived source.

Batch generation must call this single-repo workflow per repo instead of duplicating the logic.

## Raw Layout

Use this layout:

```text
raw/code-repos/
  <repo-name>/
    latest.yml
    snapshots/
      <commit-short>/
        manifest.yml
        overview.md
        architecture.md
        key-flows.md
        api-surface.md
        build-and-entrypoints.md
```

Rules:

- `snapshots/<commit-short>/` is immutable after publish unless regenerating the same commit with explicit `--force`.
- `latest.yml` points to the current effective source version.
- If `latest.yml` points to a different commit than `external-repos/<repo>` HEAD, the raw docs are stale.
- Wiki ingest and code-aware Q&A must use `latest.yml`; if stale, regenerate first.

## Workflow

1. Run status:

   ```bash
   python3 .agents/skills/generate-repo-raw-docs/scripts/generate_repo_raw_docs.py --repo <name> --status
   ```

2. If state is `current`, do not regenerate unless the user asked for `--force`.
3. Ensure code exploration indexes exist. If missing or stale, run `index-code-repos --repo <name>` first.
4. Prepare the snapshot directory:

   ```bash
   python3 .agents/skills/generate-repo-raw-docs/scripts/generate_repo_raw_docs.py --repo <name> --prepare
   ```

5. Use CodeGraph and Serena to inspect the repo. Prefer CodeGraph `projectPath=<external repo path>` for broad architecture, symbol search, callers/callees, and flow tracing. Use Serena for focused symbol exploration after activating the repo.
6. Fill the generated markdown files with source-backed content. Every factual section must cite repo, commit, and concrete files or symbols.
7. Publish only after all required docs are complete:

   ```bash
   python3 .agents/skills/generate-repo-raw-docs/scripts/generate_repo_raw_docs.py --repo <name> --publish
   ```

8. Reactivate the wiki project after external repo exploration.

## Documents

- `overview.md`: repo purpose, source commit, high-level directory map, major subsystems.
- `architecture.md`: components, ownership boundaries, control/data flow, important dependencies.
- `key-flows.md`: critical execution paths with file/symbol citations.
- `api-surface.md`: user-facing APIs, extension points, important config or CLI entrypoints.
- `build-and-entrypoints.md`: package layout, build/test/start commands, primary executable entrypoints.

Do not copy large source blocks. Short identifiers, signatures, and small snippets are acceptable only when they support explanation.

## Script Reference

```bash
python3 .agents/skills/generate-repo-raw-docs/scripts/generate_repo_raw_docs.py --repo <name> --status
python3 .agents/skills/generate-repo-raw-docs/scripts/generate_repo_raw_docs.py --repo <name> --prepare
python3 .agents/skills/generate-repo-raw-docs/scripts/generate_repo_raw_docs.py --repo <name> --publish
python3 .agents/skills/generate-repo-raw-docs/scripts/generate_repo_raw_docs.py --repo <name> --force --prepare
python3 .agents/skills/generate-repo-raw-docs/scripts/generate_repo_raw_docs.py --self-test
```

The script uses only Python standard library. It creates metadata and templates, validates required docs, and updates `latest.yml`; it does not inspect code or invent documentation content.

## Safety Rules

- Operate on exactly one repo per run.
- Use only repos declared in `code-repos.yml`.
- Refuse paths outside `external-repos/`.
- Do not write `wiki/` during raw generation.
- Do not publish docs containing `TODO`, `status: draft`, or empty template text.
- Do not update `latest.yml` until all required docs pass validation.
- Keep code-derived raw docs grounded in the exact commit and file/symbol citations.
