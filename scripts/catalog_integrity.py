#!/usr/bin/env python3
"""Verify and refresh the pinned public-apis catalog snapshot."""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import sys
import urllib.request
from collections.abc import Callable

ROOT = pathlib.Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog" / "README.md"
EXPECTED_BLOB_SHA = ROOT / "catalog" / "EXPECTED_BLOB_SHA"
DOCS = (ROOT / "SKILL.md", ROOT / "README.md")
DEFAULT_URL = "https://raw.githubusercontent.com/public-apis/public-apis/master/README.md"


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_sha256_in_docs(root: pathlib.Path, old: str, new: str) -> list[pathlib.Path]:
    changed = []
    if not old or old == new:
        return changed
    for rel in ("SKILL.md", "README.md"):
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if old in text:
            path.write_text(text.replace(old, new), encoding="utf-8")
            changed.append(path)
    return changed


def check(root: pathlib.Path = ROOT) -> list[str]:
    problems: list[str] = []
    catalog = root / "catalog" / "README.md"
    expected_file = root / "catalog" / "EXPECTED_BLOB_SHA"
    if not catalog.is_file():
        return ["catalog snapshot missing"]
    if not expected_file.is_file():
        return ["catalog EXPECTED_BLOB_SHA missing"]
    data = catalog.read_bytes()
    expected = expected_file.read_text(encoding="utf-8").strip()
    actual_blob = git_blob_sha(data)
    if actual_blob != expected:
        problems.append(
            f"catalog git blob mismatch: expected {expected}, got {actual_blob}"
        )
    digest = sha256_hex(data)
    for rel in ("SKILL.md", "README.md"):
        path = root / rel
        if not path.is_file():
            problems.append(f"{rel} missing")
        elif digest not in path.read_text(encoding="utf-8"):
            problems.append(f"{rel} missing current sha256 {digest}")
    return problems


def fetch_url(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()


def refresh(
    root: pathlib.Path = ROOT,
    expected_blob_sha: str = "",
    fetcher: Callable[[str], bytes] = fetch_url,
    url: str = DEFAULT_URL,
    write: bool = True,
) -> dict[str, object]:
    data = fetcher(url)
    blob = git_blob_sha(data)
    digest = sha256_hex(data)
    report: dict[str, object] = {
        "blob_sha": blob,
        "sha256": digest,
        "written": False,
        "status": "verified",
    }
    if expected_blob_sha and blob != expected_blob_sha:
        report["status"] = "drift"
        return report
    if not write:
        return report
    catalog = root / "catalog" / "README.md"
    old_digest = sha256_hex(catalog.read_bytes()) if catalog.is_file() else ""
    catalog.write_bytes(data)
    (root / "catalog" / "EXPECTED_BLOB_SHA").write_text(blob + "\n", encoding="utf-8")
    replace_sha256_in_docs(root, old_digest, digest)
    report["status"] = "updated"
    report["written"] = True
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "refresh"))
    parser.add_argument("--root", type=pathlib.Path, default=ROOT)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument(
        "--expected-blob-sha",
        default="",
        help="required for refresh writes; refuses unexpected upstream bytes",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.expanduser().resolve()
    if args.command == "check":
        problems = check(root)
        if problems:
            for problem in problems:
                print(f"FAIL: {problem}", file=sys.stderr)
            return 1
        print(f"OK: catalog and docs consistent ({sha256_hex((root / 'catalog' / 'README.md').read_bytes())})")
        return 0
    report = refresh(
        root=root,
        expected_blob_sha=args.expected_blob_sha,
        url=args.url,
        write=not args.dry_run,
    )
    print(report)
    return 1 if report["status"] == "drift" else 0


if __name__ == "__main__":
    raise SystemExit(main())
