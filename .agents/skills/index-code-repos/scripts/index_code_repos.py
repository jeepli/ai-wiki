#!/usr/bin/env python3
"""Build or refresh Serena and CodeGraph indexes for external repositories."""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
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
class Plan:
    repo: Repo
    target: Path
    codegraph_action: str
    serena_action: str
    health_action: str
    commands: list[list[str]]


@dataclasses.dataclass
class Result:
    name: str
    path: str
    commit: str
    codegraph: str
    serena: str
    health: str
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
        parsed.append(Repo(repo["name"], repo["path"], repo["upstream"]))
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


def run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git_commit(target: Path) -> str:
    proc = run(["git", "rev-parse", "--short", "HEAD"], cwd=target)
    if proc.returncode == 0:
        return proc.stdout.strip()
    return "-"


def is_git_repo(target: Path) -> bool:
    proc = run(["git", "rev-parse", "--is-inside-work-tree"], cwd=target)
    return proc.returncode == 0 and proc.stdout.strip() == "true"


def build_plan(
    workspace: Path,
    repo: Repo,
    *,
    force_codegraph: bool,
    languages: list[str],
    include_serena: bool,
    include_codegraph: bool,
    include_health: bool,
) -> Plan:
    target = ensure_safe_target(workspace, repo.path)
    if not target.exists():
        raise FileNotFoundError(f"repo path does not exist; run sync-code-repos first: {repo.path}")
    if not target.is_dir():
        raise ValueError(f"repo path is not a directory: {repo.path}")

    commands: list[list[str]] = []
    codegraph_action = "skip"
    serena_action = "skip"
    health_action = "skip"

    if include_codegraph:
        if not (target / ".codegraph").exists():
            codegraph_action = "init"
            commands.append(["codegraph", "init", "-i", str(target)])
        elif force_codegraph:
            codegraph_action = "index"
            commands.append(["codegraph", "index", "-f", str(target)])
        else:
            codegraph_action = "sync"
            commands.append(["codegraph", "sync", str(target)])

    if include_serena:
        serena_action = "index"
        command = ["serena", "project", "index", "--name", repo.name]
        for language in languages:
            command.extend(["--language", language])
        command.append(str(target))
        commands.append(command)
        if include_health:
            health_action = "health-check"
            commands.append(["serena", "project", "health-check", str(target)])

    return Plan(repo, target, codegraph_action, serena_action, health_action, commands)


def check_cli(plan: Plan) -> None:
    required = {command[0] for command in plan.commands}
    missing = sorted(tool for tool in required if shutil.which(tool) is None)
    if missing:
        raise FileNotFoundError(f"required command not found: {', '.join(missing)}")


def apply_plan(workspace: Path, plan: Plan, dry_run: bool) -> Result:
    commit = git_commit(plan.target) if plan.target.exists() else "-"
    if dry_run:
        return Result(
            plan.repo.name,
            plan.repo.path,
            commit,
            plan.codegraph_action,
            plan.serena_action,
            plan.health_action,
            True,
            "dry-run",
        )

    check_cli(plan)
    if not is_git_repo(plan.target):
        raise ValueError(f"target is not a git repository: {plan.repo.path}")

    for command in plan.commands:
        proc = run(command, cwd=workspace)
        if proc.returncode != 0:
            detail = proc.stderr.strip() or proc.stdout.strip()
            return Result(
                plan.repo.name,
                plan.repo.path,
                commit,
                plan.codegraph_action,
                plan.serena_action,
                plan.health_action,
                False,
                f"{' '.join(command)} failed: {detail}",
            )

    return Result(
        plan.repo.name,
        plan.repo.path,
        commit,
        plan.codegraph_action,
        plan.serena_action,
        plan.health_action,
        True,
        "applied",
    )


def index_one(workspace: Path, repo: Repo, args: argparse.Namespace) -> Result:
    try:
        plan = build_plan(
            workspace,
            repo,
            force_codegraph=args.force_codegraph,
            languages=args.language,
            include_serena=not args.skip_serena,
            include_codegraph=not args.skip_codegraph,
            include_health=not args.skip_serena and not args.skip_health_check,
        )
        return apply_plan(workspace, plan, dry_run=args.dry_run or not args.apply)
    except Exception as exc:  # noqa: BLE001 - command-line tool should summarize per repo
        return Result(repo.name, repo.path, "-", "failed", "failed", "failed", False, str(exc))


def print_results(results: list[Result]) -> None:
    headers = ("repo", "commit", "codegraph", "serena", "health", "ok", "path", "message")
    rows = [
        (
            result.name,
            result.commit,
            result.codegraph,
            result.serena,
            result.health,
            "yes" if result.ok else "no",
            result.path,
            result.message,
        )
        for result in results
    ]
    widths = [len(header) for header in headers]
    for row in rows:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]
    print("  ".join(header.ljust(widths[i]) for i, header in enumerate(headers)))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))


def print_memory_template(workspace: Path, repos: list[Repo]) -> None:
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    for repo in repos:
        target = ensure_safe_target(workspace, repo.path)
        commit = git_commit(target) if target.exists() else "-"
        print(f"## {repo.name}")
        print()
        print("### repo-overview")
        print(f"- upstream: {repo.upstream}")
        print(f"- local path: {target}")
        print(f"- current commit: {commit}")
        print("- scope: external explorable code snapshot; do not bulk-ingest into wiki")
        print()
        print("### index-status")
        print(f"- updated: {now}")
        print("- codegraph: use projectPath with this local path")
        print("- serena: project indexed with `serena project index` when apply succeeds")
        print()
        print("### exploration-guide")
        print(f"- CodeGraph MCP: pass projectPath={target}")
        print("- Serena MCP: activate this project before symbol exploration, then reactivate ai-wiki afterward")
        print("- Prefer symbol/context/flow tools before raw grep; use rg for literal strings and filenames")
        print()


def select_repos(repos: list[Repo], wanted: list[str]) -> list[Repo]:
    if not wanted:
        return repos
    known = {repo.name for repo in repos}
    unknown = sorted(set(wanted) - known)
    if unknown:
        raise ValueError(f"unknown repo(s): {', '.join(unknown)}")
    wanted_set = set(wanted)
    return [repo for repo in repos if repo.name in wanted_set]


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        manifest = root / "code-repos.yml"
        manifest.write_text(
            """repos:
  - name: demo
    path: external-repos/demo
    upstream: https://example.com/demo.git
    index:
      serena: optional
      codegraph: optional
""",
            encoding="utf-8",
        )
        repos = parse_manifest(manifest)
        assert repos == [Repo("demo", "external-repos/demo", "https://example.com/demo.git")]
        target = root / "external-repos/demo"
        target.mkdir(parents=True)
        assert ensure_safe_target(root, "external-repos/demo") == target
        for unsafe in ("/tmp/demo", "../demo", "wiki/demo", "external-repos"):
            try:
                ensure_safe_target(root, unsafe)
            except ValueError:
                pass
            else:
                raise AssertionError(f"unsafe path accepted: {unsafe}")

        plan = build_plan(
            root,
            repos[0],
            force_codegraph=False,
            languages=["python", "cpp"],
            include_serena=True,
            include_codegraph=True,
            include_health=True,
        )
        assert plan.codegraph_action == "init"
        assert plan.commands[0][:3] == ["codegraph", "init", "-i"]
        assert any(command[:3] == ["serena", "project", "index"] for command in plan.commands)
        assert any("--language" in command for command in plan.commands)
        assert any(command[:3] == ["serena", "project", "health-check"] for command in plan.commands)

        (target / ".codegraph").mkdir()
        plan = build_plan(
            root,
            repos[0],
            force_codegraph=False,
            languages=[],
            include_serena=False,
            include_codegraph=True,
            include_health=False,
        )
        assert plan.codegraph_action == "sync"
        assert plan.commands == [["codegraph", "sync", str(target)]]

        plan = build_plan(
            root,
            repos[0],
            force_codegraph=True,
            languages=[],
            include_serena=False,
            include_codegraph=True,
            include_health=False,
        )
        assert plan.codegraph_action == "index"
        assert plan.commands == [["codegraph", "index", "-f", str(target)]]

    print("self-test passed")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Index external-repos with Serena and CodeGraph")
    parser.add_argument("--manifest", default="code-repos.yml")
    parser.add_argument("--workspace", default=os.getcwd())
    parser.add_argument("--repo", action="append", default=[], help="index only this repo name")
    parser.add_argument("--apply", action="store_true", help="perform indexing; default is dry-run")
    parser.add_argument("--dry-run", action="store_true", help="show planned indexing actions")
    parser.add_argument("--force-codegraph", action="store_true", help="force full CodeGraph re-index")
    parser.add_argument("--language", action="append", default=[], help="language to pass to Serena; repeat for multiple languages")
    parser.add_argument("--skip-codegraph", action="store_true")
    parser.add_argument("--skip-serena", action="store_true")
    parser.add_argument("--skip-health-check", action="store_true")
    parser.add_argument("--memory-template", action="store_true", help="print memory content candidates")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()
    if args.skip_codegraph and args.skip_serena and not args.memory_template:
        print("nothing to do: both CodeGraph and Serena are skipped", file=sys.stderr)
        return 2

    workspace = Path(args.workspace).resolve()
    manifest = (workspace / args.manifest).resolve()
    if not manifest.exists():
        print(f"manifest not found: {manifest}", file=sys.stderr)
        return 2

    try:
        repos = select_repos(parse_manifest(manifest), args.repo)
    except Exception as exc:  # noqa: BLE001
        print(f"failed to load manifest: {exc}", file=sys.stderr)
        return 2

    if args.memory_template:
        print_memory_template(workspace, repos)
        return 0

    results = [index_one(workspace, repo, args) for repo in repos]
    print_results(results)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
