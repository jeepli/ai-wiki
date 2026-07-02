---
name: index-code-repos
description: Use when Codex needs to build, refresh, validate, or repair Serena project indexes, Serena memories, or CodeGraph indexes for local external repository snapshots under external-repos/ declared in code-repos.yml.
---

# Index Code Repos

## Overview

Use this skill after `sync-code-repos` or whenever local code exploration feels stale. It prepares `external-repos/` repositories for fast code Q&A through Serena and CodeGraph without ingesting source code into `wiki/`.

## Workflow

1. Read `code-repos.yml` from the wiki repository root.
2. Confirm each selected repo exists under `external-repos/`. If a repo is missing, run `sync-code-repos` first.
3. Run a dry run:

   ```bash
   python3 .agents/skills/index-code-repos/scripts/index_code_repos.py --dry-run
   ```

4. If the plan is correct, apply it:

   ```bash
   python3 .agents/skills/index-code-repos/scripts/index_code_repos.py --apply
   ```

5. If sandboxing blocks subprocess execution or generated indexes, rerun the same command with approval instead of changing paths.
6. For each successfully indexed repo, update Serena memories through MCP:
   - `mcp__serena.activate_project` with the external repo path.
   - `mcp__serena.write_memory` for `repo-overview`, `index-status`, and `exploration-guide`.
   - Reactivate the wiki project afterward.
7. Report repo name, path, commit, CodeGraph action, Serena action, and failures.

Use `--repo <name>` one or more times for selected repositories.

## Command Reference

```bash
python3 .agents/skills/index-code-repos/scripts/index_code_repos.py --self-test
python3 .agents/skills/index-code-repos/scripts/index_code_repos.py --dry-run
python3 .agents/skills/index-code-repos/scripts/index_code_repos.py --apply --repo <name>
python3 .agents/skills/index-code-repos/scripts/index_code_repos.py --apply --force-codegraph
python3 .agents/skills/index-code-repos/scripts/index_code_repos.py --apply --skip-codegraph --language python --language cpp
python3 .agents/skills/index-code-repos/scripts/index_code_repos.py --memory-template --repo <name>
```

Options:

- `--force-codegraph`: run a full CodeGraph re-index instead of incremental sync when `.codegraph/` already exists.
- `--language <name>`: pass explicit languages to Serena when non-interactive inference would prompt; repeat for multiple languages.
- `--skip-codegraph`: update only Serena.
- `--skip-serena`: update only CodeGraph.
- `--skip-health-check`: skip `serena project health-check`.
- `--memory-template`: print concise memory content candidates; do not write memory automatically.

## Serena Memory Policy

Write memories only in the external repo project, not in the wiki project. Keep them short and operational:

- `repo-overview`: manifest role, upstream, local path, current commit, and scope.
- `index-status`: latest indexing actions, timestamp, CodeGraph status summary when available.
- `exploration-guide`: how to query the repo with Serena and CodeGraph, including `projectPath` for CodeGraph MCP calls.

Do not copy large source snippets into memory. Do not summarize code architecture unless you actually inspected the relevant files or symbols.

## Safety Rules

- Operate only on repositories declared in `code-repos.yml`.
- Refuse absolute paths, `..`, symlink escape, or paths outside `external-repos/`.
- Do not modify `raw/`, `wiki/`, or tracked project source during indexing.
- Do not commit `.codegraph/`, `.serena/`, or `external-repos/` contents.
- Do not use indexing as wiki ingestion. If code-derived knowledge should be written to `wiki/`, switch to the wiki ingest/update workflow and cite repo, file/symbol, and commit.

## Script

Use `scripts/index_code_repos.py` for repeatable command planning and execution. It uses only Python standard library and parses the manifest fields needed for indexing: `name`, `path`, and `upstream`.
