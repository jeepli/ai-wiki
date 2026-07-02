#!/usr/bin/env python3
"""Sync local external-repos snapshots from code-repos.yml."""

from __future__ import annotations

import argparse
import dataclasses
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


@dataclasses.dataclass
class Repo:
    name: str
    path: str
    upstream: str


@dataclasses.dataclass
class Result:
    name: str
    action: str
    branch: str
    old_commit: str
    new_commit: str
    path: str
    ok: bool
    message: str = ""


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_manifest(path: Path) -> list[Repo]:
    repos: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    item_re = re.compile(r"^  -\s+([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*$")
    field_re = re.compile(r"^    ([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*$")

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line:
            continue
        item = item_re.match(line)
        if item:
            if current is not None:
                repos.append(current)
            current = {item.group(1): unquote(item.group(2))}
            continue
        field = field_re.match(line)
        if current is not None and field:
            key, value = field.group(1), unquote(field.group(2))
            if key in {"name", "path", "upstream"}:
                current[key] = value

    if current is not None:
        repos.append(current)

    parsed: list[Repo] = []
    for repo in repos:
        missing = [key for key in ("name", "path", "upstream") if not repo.get(key)]
        if missing:
            raise ValueError(f"repo entry missing fields {missing}: {repo}")
        parsed.append(Repo(name=repo["name"], path=repo["path"], upstream=repo["upstream"]))
    return parsed


def ensure_safe_target(workspace: Path, repo_path: str) -> Path:
    raw = Path(repo_path)
    if raw.is_absolute():
        raise ValueError(f"absolute paths are not allowed: {repo_path}")
    if ".." in raw.parts:
        raise ValueError(f"path traversal is not allowed: {repo_path}")
    if len(raw.parts) < 2 or raw.parts[0] != "external-repos":
        raise ValueError(f"path must be under external-repos/: {repo_path}")

    root = workspace.resolve()
    external_root = (root / "external-repos").resolve(strict=False)
    target = (root / raw).resolve(strict=False)
    if target == external_root or external_root not in target.parents:
        raise ValueError(f"path escapes external-repos/: {repo_path}")
    if target.exists() and target.is_symlink():
        raise ValueError(f"target symlinks are not allowed: {repo_path}")
    return target


def run_git(args: list[str], cwd: Path, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return proc.stdout.strip()


def is_git_repo(path: Path) -> bool:
    if not path.exists():
        return False
    proc = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=str(path),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return proc.returncode == 0 and proc.stdout.strip() == "true"


def normalize_url(url: str) -> str:
    value = url.strip()
    if value.endswith(".git"):
        value = value[:-4]
    return value.rstrip("/")


def current_origin(path: Path) -> str:
    return run_git(["config", "--get", "remote.origin.url"], cwd=path, check=False)


def current_commit(path: Path) -> str:
    if not is_git_repo(path):
        return "-"
    return run_git(["rev-parse", "--short", "HEAD"], cwd=path, check=False) or "-"


def default_branch(path: Path) -> str:
    run_git(["remote", "set-head", "origin", "-a"], cwd=path, check=False)
    head = run_git(["symbolic-ref", "--short", "refs/remotes/origin/HEAD"], cwd=path, check=False)
    if head.startswith("origin/"):
        return head.split("/", 1)[1]
    for candidate in ("main", "master"):
        if run_git(["rev-parse", "--verify", f"origin/{candidate}"], cwd=path, check=False):
            return candidate
    branch = run_git(["branch", "--show-current"], cwd=path, check=False)
    if branch:
        return branch
    raise RuntimeError("cannot determine remote default branch")


def remove_tree(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def clone_repo(repo: Repo, target: Path, depth: int, dry_run: bool) -> Result:
    if dry_run:
        return Result(repo.name, "clone", "-", "-", "-", repo.path, True, "dry-run")
    target.parent.mkdir(parents=True, exist_ok=True)
    run_git(["clone", "--depth", str(depth), repo.upstream, str(target)], cwd=target.parent)
    branch = run_git(["branch", "--show-current"], cwd=target, check=False) or default_branch(target)
    commit = current_commit(target)
    return Result(repo.name, "cloned", branch, "-", commit, repo.path, True)


def replace_repo(repo: Repo, target: Path, depth: int, dry_run: bool, reason: str) -> Result:
    old = current_commit(target)
    if dry_run:
        return Result(repo.name, "replace", "-", old, "-", repo.path, True, f"dry-run: {reason}")
    remove_tree(target)
    return clone_repo(repo, target, depth, dry_run=False)


def update_repo(repo: Repo, target: Path, depth: int, dry_run: bool) -> Result:
    old = current_commit(target)
    if dry_run:
        return Result(repo.name, "update", "-", old, "-", repo.path, True, "dry-run")

    run_git(["fetch", "--depth", str(depth), "origin"], cwd=target)
    branch = default_branch(target)
    run_git(["checkout", "-B", branch, f"origin/{branch}"], cwd=target)
    run_git(["reset", "--hard", f"origin/{branch}"], cwd=target)
    run_git(["clean", "-fdx"], cwd=target)
    new = current_commit(target)
    return Result(repo.name, "updated", branch, old, new, repo.path, True)


def sync_one(workspace: Path, repo: Repo, depth: int, dry_run: bool) -> Result:
    try:
        target = ensure_safe_target(workspace, repo.path)
        if not target.exists():
            return clone_repo(repo, target, depth, dry_run)
        if not is_git_repo(target):
            return replace_repo(repo, target, depth, dry_run, "target is not a git repo")

        origin = current_origin(target)
        if normalize_url(origin) != normalize_url(repo.upstream):
            return replace_repo(repo, target, depth, dry_run, f"origin mismatch: {origin}")
        return update_repo(repo, target, depth, dry_run)
    except Exception as exc:  # noqa: BLE001 - command-line tool should summarize per repo
        return Result(repo.name, "failed", "-", "-", "-", repo.path, False, str(exc))


def print_results(results: list[Result]) -> None:
    headers = ("repo", "action", "branch", "old", "new", "path", "message")
    rows = [
        (r.name, r.action, r.branch, r.old_commit, r.new_commit, r.path, r.message)
        for r in results
    ]
    widths = [len(h) for h in headers]
    for row in rows:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]
    print("  ".join(h.ljust(widths[i]) for i, h in enumerate(headers)))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        manifest = root / "code-repos.yml"
        manifest.write_text(
            """repos:
  - name: demo
    path: external-repos/demo
    upstream: https://example.com/demo.git
    domain: test
    notes:
      - ignored
""",
            encoding="utf-8",
        )
        repos = parse_manifest(manifest)
        assert repos == [Repo("demo", "external-repos/demo", "https://example.com/demo.git")]
        assert ensure_safe_target(root, "external-repos/demo") == root / "external-repos/demo"
        for unsafe in ("/tmp/demo", "../demo", "raw/demo", "external-repos"):
            try:
                ensure_safe_target(root, unsafe)
            except ValueError:
                pass
            else:
                raise AssertionError(f"unsafe path accepted: {unsafe}")
    print("self-test passed")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Sync external-repos from code-repos.yml")
    parser.add_argument("--manifest", default="code-repos.yml")
    parser.add_argument("--workspace", default=os.getcwd())
    parser.add_argument("--repo", action="append", default=[], help="sync only this repo name")
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--apply", action="store_true", help="perform changes; default is dry-run")
    parser.add_argument("--dry-run", action="store_true", help="show planned actions")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()
    if args.depth < 1:
        print("--depth must be >= 1", file=sys.stderr)
        return 2

    workspace = Path(args.workspace).resolve()
    manifest = (workspace / args.manifest).resolve()
    if not manifest.exists():
        print(f"manifest not found: {manifest}", file=sys.stderr)
        return 2

    try:
        repos = parse_manifest(manifest)
    except Exception as exc:  # noqa: BLE001
        print(f"failed to parse manifest: {exc}", file=sys.stderr)
        return 2

    wanted = set(args.repo)
    if wanted:
        known = {repo.name for repo in repos}
        unknown = sorted(wanted - known)
        if unknown:
            print(f"unknown repo(s): {', '.join(unknown)}", file=sys.stderr)
            return 2
        repos = [repo for repo in repos if repo.name in wanted]

    dry_run = args.dry_run or not args.apply
    results = [sync_one(workspace, repo, args.depth, dry_run) for repo in repos]
    print_results(results)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
