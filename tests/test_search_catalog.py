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


if __name__ == "__main__":
    unittest.main()
