---
name: generate-code-repos-raw-docs
description: Use when Codex needs to batch status-check, prepare, or publish versioned raw code-derived documents for multiple external repositories declared in code-repos.yml by orchestrating the single-repo generate-repo-raw-docs workflow.
---

# Generate Code Repos Raw Docs

## Overview

Batch wrapper for `generate-repo-raw-docs`. Use this skill to run the single-repo raw-doc workflow across many `code-repos.yml` entries without duplicating generation logic.

This skill does not inspect code or write document content by itself. For actual content generation, process each repo through `generate-repo-raw-docs`, using Serena and CodeGraph for source-backed writing.

## Workflow

1. Run batch status first:

   ```bash
   python3 .agents/skills/generate-code-repos-raw-docs/scripts/generate_code_repos_raw_docs.py --status
   ```

2. Prepare missing or stale snapshots:

   ```bash
   python3 .agents/skills/generate-code-repos-raw-docs/scripts/generate_code_repos_raw_docs.py --prepare
   ```

3. For each prepared repo, use `generate-repo-raw-docs` to fill required documents with source-backed content.
4. Publish only after required docs for each selected repo are complete:

   ```bash
   python3 .agents/skills/generate-code-repos-raw-docs/scripts/generate_code_repos_raw_docs.py --publish
   ```

Use `--repo <name>` one or more times to limit the batch.

## Command Reference

```bash
python3 .agents/skills/generate-code-repos-raw-docs/scripts/generate_code_repos_raw_docs.py --self-test
python3 .agents/skills/generate-code-repos-raw-docs/scripts/generate_code_repos_raw_docs.py --status
python3 .agents/skills/generate-code-repos-raw-docs/scripts/generate_code_repos_raw_docs.py --prepare --repo vllm
python3 .agents/skills/generate-code-repos-raw-docs/scripts/generate_code_repos_raw_docs.py --prepare --force
python3 .agents/skills/generate-code-repos-raw-docs/scripts/generate_code_repos_raw_docs.py --publish --repo vllm
python3 .agents/skills/generate-code-repos-raw-docs/scripts/generate_code_repos_raw_docs.py --status --dry-run
```

Options:

- `--status`: run single-repo status for selected repos.
- `--prepare`: prepare draft snapshot directories for selected repos.
- `--publish`: publish selected repos whose required docs are complete.
- `--force`: pass through to single-repo prepare.
- `--dry-run`: print commands without executing them.
- `--fail-fast`: stop at first failed repo.

## Rules

- Keep this skill as a thin wrapper. Do not duplicate raw path, validation, or publishing logic already owned by `generate-repo-raw-docs`.
- Operate only on repos declared in `code-repos.yml`.
- Do not write `wiki/`.
- Do not invent or bulk-copy code documentation content.
- If a repo needs content, switch to `generate-repo-raw-docs` for that repo.
- Treat `raw/code-repos/<repo>/latest.yml` as the current version pointer for ingest and Q&A.

## Script

Use `scripts/generate_code_repos_raw_docs.py` for repeatable batch orchestration. It uses only Python standard library and invokes `generate-repo-raw-docs/scripts/generate_repo_raw_docs.py` as a subprocess.
