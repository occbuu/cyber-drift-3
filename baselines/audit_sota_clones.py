from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path(__file__).with_name("SOTA_CLONE_MANIFEST.yaml")


def git(path: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), *args],
        text=True,
        stderr=subprocess.STDOUT,
    ).strip()


def verify_clone(name: str, record: dict) -> dict[str, str]:
    path = ROOT / record["path"]
    if not path.is_dir():
        return {"name": name, "status": "missing", "details": str(path)}
    actual_commit = git(path, "rev-parse", "HEAD")
    actual_remote = git(path, "remote", "get-url", "origin")
    expected_commit = record["commit"]
    expected_remote = record["repository"]
    problems: list[str] = []
    if actual_commit != expected_commit:
        problems.append(f"commit={actual_commit}")
    if actual_remote.rstrip("/").removesuffix(".git") != expected_remote.rstrip("/").removesuffix(".git"):
        problems.append(f"remote={actual_remote}")
    return {
        "name": name,
        "status": "ok" if not problems else "mismatch",
        "details": "; ".join(problems) if problems else actual_commit[:12],
    }


def main() -> None:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    for name, record in manifest["verified_clones"].items():
        rows.append(verify_clone(name, record))
        mirror = record.get("author_mirror")
        if mirror:
            rows.append(verify_clone(f"{name}_author_mirror", mirror))
    for name, record in manifest["supporting_artifacts_only"].items():
        for index, artifact in enumerate(record["artifacts"], start=1):
            rows.append(verify_clone(f"{name}_support_{index}", artifact))
    print("clone                         status    details")
    for row in rows:
        print(f"{row['name']:<29} {row['status']:<9} {row['details']}")
    if any(row["status"] != "ok" for row in rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
