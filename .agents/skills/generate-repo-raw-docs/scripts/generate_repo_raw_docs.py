#!/usr/bin/env python3
"""Prepare and publish versioned raw docs for one external repo snapshot."""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import os
import re
import subprocess
import sys
from pathlib import Path


REQUIRED_DOCS = [
    "overview.md",
    "architecture.md",
    "key-flows.md",
    "api-surface.md",
    "build-and-entrypoints.md",
]


@dataclasses.dataclass
class Repo:
    name: str
    path: str
    upstream: str
    domain: str = ""
    role: str = ""


@dataclasses.dataclass
class Context:
    workspace: Path
    repo: Repo
    target: Path
    commit: str
    commit_short: str
    repo_raw_dir: Path
    snapshot_dir: Path
    latest_path: Path


@dataclasses.dataclass
class Status:
    repo: str
    commit: str
    snapshot: str
    state: str
    message: str


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
            if key in {"name", "path", "upstream", "domain", "role"}:
                current[key] = value

    if current is not None:
        repos.append(current)

    parsed: list[Repo] = []
    for repo in repos:
        missing = [key for key in ("name", "path", "upstream") if not repo.get(key)]
        if missing:
            raise ValueError(f"repo entry missing fields {missing}: {repo}")
        parsed.append(
            Repo(
                repo["name"],
                repo["path"],
                repo["upstream"],
                repo.get("domain", ""),
                repo.get("role", ""),
            )
        )
    return parsed


def select_repo(repos: list[Repo], name: str) -> Repo:
    matches = [repo for repo in repos if repo.name == name]
    if not matches:
        known = ", ".join(repo.name for repo in repos)
        raise ValueError(f"unknown repo: {name}; known repos: {known}")
    return matches[0]


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


def run_git(args: list[str], cwd: Path) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return proc.stdout.strip()


def current_commit(target: Path) -> str:
    return run_git(["rev-parse", "HEAD"], cwd=target)


def slug(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9-]+", "-", lowered)
    return lowered.strip("-")


def build_context(workspace: Path, repo: Repo) -> Context:
    target = ensure_safe_target(workspace, repo.path)
    if not target.exists():
        raise FileNotFoundError(f"repo path does not exist: {repo.path}")
    commit = current_commit(target)
    commit_short = commit[:7]
    repo_raw_dir = workspace / "raw" / "code-repos" / slug(repo.name)
    snapshot_dir = repo_raw_dir / "snapshots" / commit_short
    latest_path = repo_raw_dir / "latest.yml"
    return Context(workspace, repo, target, commit, commit_short, repo_raw_dir, snapshot_dir, latest_path)


def read_scalar_yaml(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    result: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line or raw_line.startswith(" ") or raw_line.startswith("-"):
            continue
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        result[key.strip()] = unquote(value.strip())
    return result


def missing_docs(ctx: Context) -> list[str]:
    return [doc for doc in REQUIRED_DOCS if not (ctx.snapshot_dir / doc).exists()]


def doc_is_complete(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8").strip()
    if len(text) < 80:
        return False
    forbidden = ["TODO", "status: draft", "Replace this template", "Source-backed content goes here"]
    return not any(marker in text for marker in forbidden)


def incomplete_docs(ctx: Context) -> list[str]:
    return [doc for doc in REQUIRED_DOCS if not doc_is_complete(ctx.snapshot_dir / doc)]


def status_for(ctx: Context) -> Status:
    latest = read_scalar_yaml(ctx.latest_path)
    latest_commit = latest.get("commit", "")
    if latest_commit and latest_commit != ctx.commit:
        return Status(ctx.repo.name, ctx.commit, str(ctx.snapshot_dir), "stale", f"latest points to {latest_commit}")
    if not ctx.snapshot_dir.exists():
        return Status(ctx.repo.name, ctx.commit, str(ctx.snapshot_dir), "missing", "snapshot directory missing")
    missing = missing_docs(ctx)
    if missing:
        return Status(ctx.repo.name, ctx.commit, str(ctx.snapshot_dir), "draft", f"missing docs: {', '.join(missing)}")
    incomplete = incomplete_docs(ctx)
    if incomplete:
        return Status(ctx.repo.name, ctx.commit, str(ctx.snapshot_dir), "draft", f"incomplete docs: {', '.join(incomplete)}")
    if latest_commit == ctx.commit:
        return Status(ctx.repo.name, ctx.commit, str(ctx.snapshot_dir), "current", "latest points to current commit")
    return Status(ctx.repo.name, ctx.commit, str(ctx.snapshot_dir), "ready", "snapshot complete but not published")


def write_text_if_allowed(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.write_text(content, encoding="utf-8")


def yaml_list(items: list[str], indent: str = "  ") -> str:
    return "".join(f"{indent}- {item}\n" for item in items)


def manifest_content(ctx: Context) -> str:
    docs = yaml_list(REQUIRED_DOCS)
    generated_at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        f"repo: {ctx.repo.name}\n"
        f"upstream: {ctx.repo.upstream}\n"
        f"domain: {ctx.repo.domain}\n"
        f"role: {ctx.repo.role}\n"
        f"source_path: {ctx.repo.path}\n"
        f"commit: {ctx.commit}\n"
        f"commit_short: {ctx.commit_short}\n"
        f"generated_at: {generated_at}\n"
        "generator: generate-repo-raw-docs\n"
        "status: draft\n"
        "documents:\n"
        f"{docs}"
    )


def doc_template(ctx: Context, doc: str) -> str:
    title = doc.removesuffix(".md").replace("-", " ").title()
    return (
        "---\n"
        f"repo: {ctx.repo.name}\n"
        f"commit: {ctx.commit}\n"
        f"source_version: {ctx.commit_short}\n"
        f"document: {doc}\n"
        "status: draft\n"
        "---\n\n"
        f"# {title}\n\n"
        "Source-backed content goes here. Replace this template with facts cited to repo, commit, files, and symbols.\n"
    )


def prepare_snapshot(ctx: Context, force: bool) -> None:
    ctx.snapshot_dir.mkdir(parents=True, exist_ok=True)
    write_text_if_allowed(ctx.snapshot_dir / "manifest.yml", manifest_content(ctx), force)
    for doc in REQUIRED_DOCS:
        write_text_if_allowed(ctx.snapshot_dir / doc, doc_template(ctx, doc), force)


def update_manifest_published(ctx: Context) -> None:
    manifest = ctx.snapshot_dir / "manifest.yml"
    text = manifest.read_text(encoding="utf-8")
    text = text.replace("status: draft", "status: published")
    manifest.write_text(text, encoding="utf-8")


def latest_content(ctx: Context) -> str:
    docs = yaml_list([f"snapshots/{ctx.commit_short}/{doc}" for doc in REQUIRED_DOCS])
    published_at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        f"repo: {ctx.repo.name}\n"
        f"commit: {ctx.commit}\n"
        f"commit_short: {ctx.commit_short}\n"
        f"snapshot: snapshots/{ctx.commit_short}\n"
        f"published_at: {published_at}\n"
        "documents:\n"
        f"{docs}"
    )


def publish_snapshot(ctx: Context) -> None:
    if not ctx.snapshot_dir.exists():
        raise FileNotFoundError(f"snapshot directory missing: {ctx.snapshot_dir}")
    incomplete = incomplete_docs(ctx)
    if incomplete:
        raise ValueError(f"cannot publish incomplete docs: {', '.join(incomplete)}")
    update_manifest_published(ctx)
    ctx.repo_raw_dir.mkdir(parents=True, exist_ok=True)
    ctx.latest_path.write_text(latest_content(ctx), encoding="utf-8")


def print_status(status: Status) -> None:
    print("repo       state    commit                                    snapshot")
    print("---------  -------  ----------------------------------------  --------")
    print(f"{status.repo:<9}  {status.state:<7}  {status.commit:<40}  {status.snapshot}")
    print(status.message)


def run_self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        repo_dir = root / "external-repos/demo"
        repo_dir.mkdir(parents=True)
        run_git(["init"], cwd=repo_dir)
        run_git(["config", "user.email", "test@example.com"], cwd=repo_dir)
        run_git(["config", "user.name", "Test"], cwd=repo_dir)
        (repo_dir / "demo.py").write_text("def hello():\n    return 'world'\n", encoding="utf-8")
        run_git(["add", "demo.py"], cwd=repo_dir)
        run_git(["commit", "-m", "init"], cwd=repo_dir)
        commit = current_commit(repo_dir)
        manifest = root / "code-repos.yml"
        manifest.write_text(
            """repos:
  - name: demo
    path: external-repos/demo
    upstream: https://example.com/demo.git
    domain: test-domain
    role: Test repository
""",
            encoding="utf-8",
        )
        repo = select_repo(parse_manifest(manifest), "demo")
        ctx = build_context(root, repo)
        assert ctx.commit == commit
        assert status_for(ctx).state == "missing"
        prepare_snapshot(ctx, force=False)
        assert status_for(ctx).state == "draft"
        for doc in REQUIRED_DOCS:
            (ctx.snapshot_dir / doc).write_text(
                f"---\nrepo: demo\ncommit: {commit}\nsource_version: {ctx.commit_short}\n---\n\n# {doc}\n\nSource-backed content.\n",
                encoding="utf-8",
            )
        publish_snapshot(ctx)
        assert status_for(ctx).state == "current"

    print("self-test passed")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Prepare and publish raw docs for one external repo")
    parser.add_argument("--workspace", default=os.getcwd())
    parser.add_argument("--manifest", default="code-repos.yml")
    parser.add_argument("--repo", help="repo name from code-repos.yml")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--force", action="store_true", help="overwrite existing draft/templates for the same commit")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()
    if not args.repo:
        print("--repo is required unless --self-test is used", file=sys.stderr)
        return 2
    if sum(bool(flag) for flag in (args.status, args.prepare, args.publish)) != 1:
        print("choose exactly one of --status, --prepare, or --publish", file=sys.stderr)
        return 2

    workspace = Path(args.workspace).resolve()
    manifest = (workspace / args.manifest).resolve()
    try:
        repo = select_repo(parse_manifest(manifest), args.repo)
        ctx = build_context(workspace, repo)
        if args.prepare:
            prepare_snapshot(ctx, force=args.force)
        elif args.publish:
            publish_snapshot(ctx)
        print_status(status_for(ctx))
    except Exception as exc:  # noqa: BLE001 - CLI should return compact failures
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
