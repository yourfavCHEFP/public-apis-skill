import hashlib
import pathlib
import subprocess
import sys
import tempfile
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
SEARCH_SCRIPT = SKILL_DIR / "scripts" / "search_catalog.py"

SAMPLE_CATALOG = """# Public APIs

### Currency Exchange
API | Description | Auth | HTTPS | CORS |
|:---|:---|:---|:---|:---|
| [Free Rates](https://example.test/free) | Free exchange rates | No | Yes | Yes |
| [Key Rates](https://example.test/key) | Exchange rates with key | `apiKey` | Yes | Yes |
| [Insecure Rates](https://example.test/http) | Exchange rates over http | No | No | Yes |
"""


class SearchCatalogTest(unittest.TestCase):
    def test_filters_by_no_auth_https_and_cors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            catalog = pathlib.Path(tmp) / "README.md"
            catalog.write_text(SAMPLE_CATALOG, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SEARCH_SCRIPT),
                    "--catalog",
                    str(catalog),
                    "--query",
                    "exchange",
                    "--no-auth",
                    "--https",
                    "--cors",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Free Rates", result.stdout)
        self.assertNotIn("Key Rates", result.stdout)
        self.assertNotIn("Insecure Rates", result.stdout)

    def run_cli(self, *extra: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            catalog = pathlib.Path(tmp) / "README.md"
            catalog.write_text(SAMPLE_CATALOG, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SEARCH_SCRIPT), "--catalog", str(catalog), *extra],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_category_filter_keeps_only_requested_category(self) -> None:
        result = self.run_cli("--category", "Weather", "--query", "rate")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Free Rates", result.stdout)

    def test_no_match_returns_empty_table_with_provenance(self) -> None:
        result = self.run_cli("--query", "definitely-not-present")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("| API | Category | Auth | HTTPS | CORS | Docs |", result.stdout)
        self.assertIn("Source:", result.stdout)
        self.assertNotIn("Free Rates", result.stdout)

    def test_malformed_rows_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            catalog = pathlib.Path(tmp) / "README.md"
            catalog.write_text(
                SAMPLE_CATALOG + "\n| not a link | short |\n|\n", encoding="utf-8"
            )
            result = subprocess.run(
                [sys.executable, str(SEARCH_SCRIPT), "--catalog", str(catalog)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Free Rates", result.stdout)
        self.assertNotIn("not a link", result.stdout)

    def test_missing_catalog_exits_two(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SEARCH_SCRIPT), "--catalog", "/no/such/catalog.md"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("catalog not found", result.stderr)

    def test_provenance_footer_contains_sha256(self) -> None:
        result = self.run_cli("--query", "exchange")
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = hashlib.sha256(SAMPLE_CATALOG.encode("utf-8")).hexdigest()
        self.assertIn("sha256", result.stdout)
        self.assertIn(expected, result.stdout)


if __name__ == "__main__":
    unittest.main()
