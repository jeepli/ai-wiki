#!/usr/bin/env python3
"""Batch wrapper around generate-repo-raw-docs."""

from __future__ import annotations

import argparse
import dataclasses
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


@dataclasses.dataclass
class Result:
    repo: str
    action: str
    ok: bool
    message: str


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_repo_names(manifest: Path) -> list[str]:
    names: list[str] = []
    current_name = ""
    item_re = re.compile(r"^  -\s+([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*$")
    field_re = re.compile(r"^    ([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*$")

    for raw_line in manifest.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line:
            continue
        item = item_re.match(line)
        if item:
            if current_name:
                names.append(current_name)
            current_name = unquote(item.group(2)) if item.group(1) == "name" else ""
            continue
        field = field_re.match(line)
        if field and field.group(1) == "name":
            current_name = unquote(field.group(2))

    if current_name:
        names.append(current_name)
    return names


def select_repos(repos: list[str], wanted: list[str]) -> list[str]:
    if not wanted:
        return repos
    known = set(repos)
    unknown = sorted(set(wanted) - known)
    if unknown:
        raise ValueError(f"unknown repo(s): {', '.join(unknown)}")
    wanted_set = set(wanted)
    return [repo for repo in repos if repo in wanted_set]


def single_repo_script(workspace: Path) -> Path:
    return workspace / ".agents/skills/generate-repo-raw-docs/scripts/generate_repo_raw_docs.py"


def build_commands(single_script: Path, repos: list[str], action: str, force: bool) -> list[list[str]]:
    action_flag = f"--{action}"
    commands: list[list[str]] = []
    for repo in repos:
        command = [sys.executable, str(single_script), "--repo", repo, action_flag]
        if action == "prepare" and force:
            command.append("--force")
        commands.append(command)
    return commands


def run_command(command: list[str], cwd: Path) -> Result:
    repo = command[command.index("--repo") + 1] if "--repo" in command else "unknown"
    action = next((arg[2:] for arg in command if arg in {"--status", "--prepare", "--publish"}), "unknown")
    proc = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    output = (proc.stdout.strip() or proc.stderr.strip()).replace("\n", " | ")
    if len(output) > 240:
        output = output[:237] + "..."
    return Result(repo, action, proc.returncode == 0, output)


def print_results(results: list[Result]) -> None:
    headers = ("repo", "action", "ok", "message")
    rows = [(r.repo, r.action, "yes" if r.ok else "no", r.message) for r in results]
    widths = [len(header) for header in headers]
    for row in rows:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]
    print("  ".join(header.ljust(widths[i]) for i, header in enumerate(headers)))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        manifest = root / "code-repos.yml"
        manifest.write_text(
            """repos:
  - name: alpha
    path: external-repos/alpha
    upstream: https://example.com/alpha.git
  - name: beta
    path: external-repos/beta
    upstream: https://example.com/beta.git
""",
            encoding="utf-8",
        )
        repos = parse_repo_names(manifest)
        assert repos == ["alpha", "beta"]
        assert select_repos(repos, ["beta"]) == ["beta"]
        single = root / ".agents/skills/generate-repo-raw-docs/scripts/generate_repo_raw_docs.py"
        assert build_commands(single, repos, "status", force=False) == [
            [sys.executable, str(single), "--repo", "alpha", "--status"],
            [sys.executable, str(single), "--repo", "beta", "--status"],
        ]
        assert build_commands(single, ["alpha"], "prepare", force=True) == [
            [sys.executable, str(single), "--repo", "alpha", "--prepare", "--force"]
        ]
    print("self-test passed")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Batch raw-doc workflow across code-repos.yml")
    parser.add_argument("--workspace", default=os.getcwd())
    parser.add_argument("--manifest", default="code-repos.yml")
    parser.add_argument("--repo", action="append", default=[], help="repo name to include; repeat for multiple")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--force", action="store_true", help="pass through to prepare")
    parser.add_argument("--dry-run", action="store_true", help="print commands without executing")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()
    actions = [name for name in ("status", "prepare", "publish") if getattr(args, name)]
    if len(actions) != 1:
        print("choose exactly one of --status, --prepare, or --publish", file=sys.stderr)
        return 2
    action = actions[0]
    if args.force and action != "prepare":
        print("--force is only valid with --prepare", file=sys.stderr)
        return 2

    workspace = Path(args.workspace).resolve()
    manifest = (workspace / args.manifest).resolve()
    script = single_repo_script(workspace)
    if not manifest.exists():
        print(f"manifest not found: {manifest}", file=sys.stderr)
        return 2
    if not script.exists():
        print(f"single-repo script not found: {script}", file=sys.stderr)
        return 2

    try:
        repos = select_repos(parse_repo_names(manifest), args.repo)
    except Exception as exc:  # noqa: BLE001
        print(f"failed to select repos: {exc}", file=sys.stderr)
        return 2

    commands = build_commands(script, repos, action, args.force)
    if args.dry_run:
        for command in commands:
            print(" ".join(command))
        return 0

    results: list[Result] = []
    for command in commands:
        result = run_command(command, workspace)
        results.append(result)
        if args.fail_fast and not result.ok:
            break
    print_results(results)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
