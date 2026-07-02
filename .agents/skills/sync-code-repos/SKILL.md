---
name: sync-code-repos
description: Use when Codex needs to sync, update, clone, refresh, or overwrite local external repository snapshots under external-repos/ from code-repos.yml.
---

# Sync Code Repos

## Overview

Use this skill to refresh the local code snapshots listed in `code-repos.yml`. Treat `external-repos/` as disposable explorable code cache: update it from upstream, do not version it, and do not ingest source code into `wiki/`.

## Workflow

1. Read `code-repos.yml` from the repository root.
2. Confirm every target `path` is a relative path under `external-repos/`.
3. Run a dry run first:

   ```bash
   python3 .agents/skills/sync-code-repos/scripts/sync_code_repos.py --dry-run
   ```

4. If the requested operation is still intended, run the update:

   ```bash
   python3 .agents/skills/sync-code-repos/scripts/sync_code_repos.py --apply
   ```

5. If network access is blocked by sandboxing, rerun the same command with the required approval rather than changing the workflow.
6. Report a compact table: repo name, action, branch, old commit, new commit, and path.

Use `--repo <name>` one or more times when the user asks to sync only selected repositories.

## Update Semantics

- Missing path: clone `upstream` into `path`.
- Existing path with matching `origin`: fetch upstream, check out the remote default branch, hard-reset to `origin/<default_branch>`, and clean untracked files.
- Existing path with wrong `origin`, broken git metadata, or non-git content: replace it only if the path passes the `external-repos/` safety check.
- Do not preserve local branches, local commits, untracked files, generated build outputs, or local edits inside `external-repos/`.
- Do not create lockfiles, version directories, tags, or history snapshots unless the user explicitly changes the requirement.

## Safety Rules

- Never modify `raw/`, `wiki/`, or tracked project source as part of code snapshot sync.
- Never push to upstream repositories.
- Never operate on a repo that is absent from `code-repos.yml`.
- Refuse absolute paths, `..` path traversal, symlink escape from the workspace, or any path not under `external-repos/`.
- Treat `external-repos/` as ignored cache. Do not commit its contents.
- If the user asks to write code-derived wiki content after exploration, switch to the wiki ingest/update workflow and cite repo, path, symbol or file, and commit.

## Script

Use `scripts/sync_code_repos.py` for the actual sync. It uses only Python standard library and parses the manifest fields needed for repository sync: `name`, `path`, and `upstream`.

Useful commands:

```bash
python3 .agents/skills/sync-code-repos/scripts/sync_code_repos.py --self-test
python3 .agents/skills/sync-code-repos/scripts/sync_code_repos.py --dry-run
python3 .agents/skills/sync-code-repos/scripts/sync_code_repos.py --apply --repo <name>
```
