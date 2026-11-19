import hashlib
import pathlib
import tempfile
import unittest

from scripts.catalog_integrity import (
    check,
    git_blob_sha,
    replace_sha256_in_docs,
    sha256_hex,
)


def make_fixture(root: pathlib.Path, catalog_text: str = "API | Description\n") -> None:
    (root / "catalog").mkdir()
    (root / "SKILL.md").write_text("snapshot sha256 PLACEHOLDER\n", encoding="utf-8")
    (root / "README.md").write_text("sha256: PLACEHOLDER\n", encoding="utf-8")
    catalog = root / "catalog" / "README.md"
    catalog.write_text(catalog_text, encoding="utf-8")
    (root / "catalog" / "EXPECTED_BLOB_SHA").write_text(
        git_blob_sha(catalog.read_bytes()), encoding="utf-8"
    )
    digest = sha256_hex(catalog.read_bytes())
    replace_sha256_in_docs(root, "PLACEHOLDER", digest)


class CatalogIntegrityTest(unittest.TestCase):
    def test_git_blob_sha_matches_known_hash(self) -> None:
        self.assertEqual(
            git_blob_sha(b"hello\n"),
            "ce013625030ba8dba906f756967f9e9ca394464a",
        )

    def test_sha256_hex_matches_hashlib(self) -> None:
        self.assertEqual(sha256_hex(b"abc"), hashlib.sha256(b"abc").hexdigest())

    def test_consistent_fixture_has_no_problems(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            make_fixture(root)
            self.assertEqual(check(root), [])

    def test_catalog_drift_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            make_fixture(root)
            (root / "catalog" / "README.md").write_text("changed\n", encoding="utf-8")
            problems = check(root)
            self.assertTrue(any("git blob mismatch" in p for p in problems))
            self.assertTrue(any("sha256" in p for p in problems))

    def test_replace_sha256_updates_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            make_fixture(root)
            (root / "SKILL.md").write_text("sha256 PLACEHOLDER\n", encoding="utf-8")
            (root / "README.md").write_text("sha256 PLACEHOLDER\n", encoding="utf-8")
            changed = replace_sha256_in_docs(root, "PLACEHOLDER", "NEWDIGEST")
            self.assertEqual(len(changed), 2)
            for name in ("SKILL.md", "README.md"):
                text = (root / name).read_text(encoding="utf-8")
                self.assertIn("NEWDIGEST", text)
                self.assertNotIn("PLACEHOLDER", text)


if __name__ == "__main__":
    unittest.main()
