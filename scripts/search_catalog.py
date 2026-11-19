#!/usr/bin/env python3
"""Search the bundled public-apis catalog snapshot without network access."""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import sys
from dataclasses import dataclass

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
DEFAULT_CATALOG = pathlib.Path(__file__).resolve().parents[1] / "catalog" / "README.md"


@dataclass(frozen=True)
class ApiRow:
    name: str
    url: str
    description: str
    auth: str
    https: str
    cors: str
    category: str


def normalize_answer(value: str) -> str:
    return value.strip().strip("`").strip().lower()


def is_yes(value: str) -> bool:
    return normalize_answer(value) == "yes"


def is_no(value: str) -> bool:
    return normalize_answer(value) in {"", "no", "none", "false", "-"}


def parse_catalog(text: str) -> list[ApiRow]:
    rows: list[ApiRow] = []
    category = "Uncategorized"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("### "):
            category = stripped[4:].strip()
            continue
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.split("|")]
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]
        if len(cells) < 5:
            continue
        link = LINK_RE.search(cells[0])
        if not link:
            continue
        rows.append(
            ApiRow(
                name=link.group(1),
                url=link.group(2),
                description=cells[1],
                auth=cells[2].strip("`"),
                https=cells[3],
                cors=cells[4],
                category=category,
            )
        )
    return rows


def matching_rows(
    rows: list[ApiRow],
    query: str,
    category: str,
    no_auth: bool,
    https: bool,
    cors: bool,
) -> list[ApiRow]:
    needle = query.strip().lower()
    wanted_category = category.strip().lower()
    matches = []
    for row in rows:
        if needle and needle not in " ".join(
            (row.name, row.description, row.category)
        ).lower():
            continue
        if wanted_category and wanted_category not in row.category.lower():
            continue
        if no_auth and not is_no(row.auth):
            continue
        if https and not is_yes(row.https):
            continue
        if cors and not is_yes(row.cors):
            continue
        matches.append(row)
    return matches


def render(rows: list[ApiRow], catalog_path: pathlib.Path, digest: str) -> str:
    lines = [
        "| API | Category | Auth | HTTPS | CORS | Docs |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| [{row.name}]({row.url}) | {row.category} | {row.auth} | "
            f"{row.https} | {row.cors} | {row.url} |"
        )
    lines.append("")
    lines.append(f"Source: `{catalog_path}` (sha256 {digest})")
    lines.append("Catalog fields are upstream claims; verify live behavior before relying on an API.")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="", help="case-insensitive text to match")
    parser.add_argument("--category", default="", help="case-insensitive category filter")
    parser.add_argument("--no-auth", action="store_true", help="only rows marked No auth")
    parser.add_argument("--https", action="store_true", help="only rows marked HTTPS Yes")
    parser.add_argument("--cors", action="store_true", help="only rows marked CORS Yes")
    parser.add_argument("--limit", type=int, default=10, help="maximum rows to print")
    parser.add_argument(
        "--catalog",
        type=pathlib.Path,
        default=DEFAULT_CATALOG,
        help="catalog README path (default: bundled snapshot)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    catalog_path = args.catalog.expanduser().resolve()
    if not catalog_path.is_file():
        print(f"catalog not found: {catalog_path}", file=sys.stderr)
        return 2
    raw = catalog_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    rows = parse_catalog(raw.decode("utf-8", errors="replace"))
    matches = matching_rows(
        rows, args.query, args.category, args.no_auth, args.https, args.cors
    )
    print(render(matches[: args.limit], catalog_path, digest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
