# Changelog

## Unreleased — hardening

- Expanded unit tests to 11 cases covering filters, no-match output, malformed rows, exit codes, and provenance.
- Added `scripts/catalog_integrity.py` with `check` and `refresh` commands.
- Added pinned `catalog/EXPECTED_BLOB_SHA` and CI workflow on push/PR.
- Added pressure-test evidence and contributor documentation.

## Initial release

- `e302cba` — RED catalog filter test.
- `50d9cbb` — Python stdlib catalog search helper.
- `2b5432a` — Pinned MIT-licensed public-apis catalog snapshot.
- `de9721a` — Skill and repository documentation.
