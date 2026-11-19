# public-apis skill

A small Claude Code personal skill for credential-free discovery of public APIs from a pinned snapshot of the [`public-apis/public-apis`](https://github.com/public-apis/public-apis) catalog.

## Install

Clone or copy this directory to:

```text
~/.claude/skills/public-apis/
```

Claude Code discovers the skill through `SKILL.md`. No Python packages or API keys are required; the search helper uses only the Python 3 standard library.

## Usage

From the skill directory:

```bash
python3 scripts/search_catalog.py --query "exchange rate" --no-auth --https --cors --limit 10
python3 scripts/search_catalog.py --category Geocoding --no-auth --https --cors
python3 scripts/search_catalog.py --help
```

The helper prints candidate APIs plus the catalog path and SHA-256. Catalog values are **upstream claims**, not live endpoint verification. Live HTTPS, CORS, rate limits, pricing, and availability require a separate check.

## Tests

```bash
python3 -m unittest discover -s tests -t . -v
```

## Integrity

```bash
python3 scripts/catalog_integrity.py check
python3 scripts/catalog_integrity.py refresh --dry-run
```

`check` verifies the pinned catalog blob and the sha256 references in `SKILL.md` and `README.md`. `refresh --dry-run` fetches upstream and reports drift without writing. Applying a refresh requires a reviewed `--expected-blob-sha`.

## Provenance

- Catalog source: `public-apis/public-apis`, `master` branch `README.md`
- Local snapshot: `catalog/README.md`
- Snapshot SHA-256: `76386caf705629490bdc4db8ccb2cd246bc16833e5fc7154f5b3745b7976876a`
- Upstream catalog git blob: `cd696bf7f71aa6b5c119e056368d3aff3c264332`
- Upstream license: MIT, Copyright (c) 2022 public-apis (`catalog/LICENSE`)

## Project documents

- [CHANGELOG.md](CHANGELOG.md) — release and hardening history
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution and catalog-update rules
- [PRESSURE-TEST-EVIDENCE.md](PRESSURE-TEST-EVIDENCE.md) — fresh-agent compliance results

## License

MIT. See [LICENSE](LICENSE). The vendored catalog remains under its upstream MIT license.
