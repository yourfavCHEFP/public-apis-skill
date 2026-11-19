---
name: public-apis
description: Use when the user asks for a public or free API, a no-auth HTTPS/CORS endpoint, an API by category such as finance, geocoding, or currency exchange, or help choosing from the public-apis catalog; also when offline, credential-free API discovery is preferred.
---

# Public APIs

Find candidate APIs from a bundled snapshot of the `public-apis/public-apis` catalog. The catalog is a discovery aid, not a live availability guarantee.

## When to use

Use for: “find a free API for X”, “any no-auth geocoding API?”, “APIs with CORS”, or comparison of candidate public APIs.

Do not use for: vendor-specific SDK questions, authenticated enterprise APIs, or a user request to test a live endpoint's current behavior.

## Core rule

Search the bundled catalog first. Report its fields as **catalog claims** with provenance. Live HTTPS, CORS, rate limits, and availability need separate verification and must be labelled as such. Never invent a catalog row, auth value, or capability.

## Quick reference

Run from this skill directory:

```bash
python3 scripts/search_catalog.py --query "exchange rate" --no-auth --https --cors --limit 10
python3 scripts/search_catalog.py --category Geocoding --no-auth --https --cors
python3 scripts/search_catalog.py --help
```

Useful flags: `--query`, `--category`, `--no-auth`, `--https`, `--cors`, `--limit`, `--catalog`.

The helper prints a markdown table plus the catalog path and its sha256. Reuse that digest in the answer when reporting candidates.

## Output contract

Return:

1. A short table in catalog order: API, category, auth, HTTPS, CORS, docs URL.
2. Provenance: `public-apis/public-apis` catalog snapshot, local path, sha256.
3. An evidence sentence: “Catalog claim; live endpoint behavior not re-verified.”

If the user needs a production guarantee, explicitly offer a separate live check with labelled runtime evidence. Do not silently upgrade a catalog `Yes` to verified.

## Credentials and safety

- Never ask for or store an API key to perform catalog lookup.
- Prefer `--no-auth` when the user wants keyless options.
- Do not hit APIs unless the user asks for live verification.
- Do not treat the bundled snapshot as current; mention its provenance.

## Common mistakes

| Mistake | Fix |
|---|---|
| Reporting catalog CORS/HTTPS as live-verified | Label it a catalog claim; offer a separate live check |
| Inventing an API when the catalog has no match | Say no catalog match, then offer a bounded web search |
| Using bare `scripts/search_catalog.py` | Invoke it with `python3` so packaged skills work |
| Omitting provenance | Include the printed sha256 and source path |

## Provenance

Snapshot source: `https://github.com/public-apis/public-apis` (`master`, README catalog). License: MIT, bundled at `catalog/LICENSE`. Expected snapshot sha256: `76386caf705629490bdc4db8ccb2cd246bc16833e5fc7154f5b3745b7976876a`.
