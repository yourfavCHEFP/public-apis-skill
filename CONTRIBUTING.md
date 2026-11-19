# Contributing

## Rules

- Add a failing test before changing behavior.
- Keep the helper Python 3 stdlib-only; no runtime dependencies.
- Never commit credentials or live API keys.
- Treat catalog values as upstream claims, not live verification.
- Preserve the vendored catalog byte-for-byte unless a reviewed upstream SHA is pinned.

## Local verification

```bash
python3 -m unittest discover -s tests -t . -v
python3 scripts/catalog_integrity.py check
```

## Updating the catalog

```bash
python3 scripts/catalog_integrity.py refresh --dry-run
```

`refresh --dry-run` reports the upstream git blob SHA and SHA-256 without writing. To apply a reviewed snapshot, rerun with `--expected-blob-sha <reviewed-sha>`. The script refuses unexpected bytes.
