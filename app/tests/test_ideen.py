"""Tests for the Ideen page's reading of _ideen/ (decision 0038)."""
import pathlib
import tempfile
import unittest

from redaktion import editions
from redaktion.config import Config

IDEA = """---
datum: "{datum}"
status: "{status}"
form: "geschrieben"
titel: "{titel}"
quelle: "archive.db:chat_messages/1"
---

{text}

## Verlauf

- 2026-11-08: abgelegt
"""


class IdeenTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        repo = pathlib.Path(self.tmp.name)
        (repo / "_ideen").mkdir()
        (repo / "_ideen" / "README.md").write_text("# Ideen\n", encoding="utf-8")
        for datum, status, titel, text in [
            ("2026-11-06", "neu", "naming things", "When a tool is called X. " * 10),
            ("2026-11-07", "neu", "Effizienzgewinn", "Und was machst du damit?"),
            ("2026-10-18", "verworfen", "Alte Idee", "Passt nicht."),
            ("2026-11-01", "gewählt", "Spiele und Arbeit", "Warum ich Spiele mag."),
        ]:
            (repo / "_ideen" / f"{datum}-{titel.lower().replace(' ', '-')}.md").write_text(
                IDEA.format(datum=datum, status=status, titel=titel, text=text), encoding="utf-8")
        self.cfg = Config(private_repo="x/y", repo_path=repo, element_room="", app_url="", dry_run=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_list_ideas_orders_by_status_then_newest_first(self):
        names = [d["file"] for d in editions.list_ideas(self.cfg)]
        self.assertEqual(names, ["2026-11-07-effizienzgewinn.md", "2026-11-06-naming-things.md",
                                 "2026-11-01-spiele-und-arbeit.md", "2026-10-18-alte-idee.md"])

    def test_start_leaves_out_the_verlauf_and_counts_words(self):
        d = {x["file"]: x for x in editions.list_ideas(self.cfg)}["2026-11-06-naming-things.md"]
        self.assertEqual(d["words"], 60)
        self.assertNotIn("Verlauf", d["start"])
        self.assertTrue(d["start"].startswith("When a tool is called X."))

    def test_board_and_counts(self):
        groups = dict(editions.idea_board(self.cfg))
        self.assertEqual([len(groups[t]) for t in ("Neu", "Besprochen", "Gewählt", "Verworfen")], [2, 0, 1, 1])
        self.assertEqual(editions.idea_counts(self.cfg), {"neu": 2, "besprochen": 0, "gewählt": 1, "verworfen": 1, "total": 4})

    def test_missing_folder_is_empty(self):
        cfg = Config(private_repo="x/y", repo_path=pathlib.Path(self.tmp.name) / "leer", element_room="", app_url="", dry_run=True)
        self.assertEqual(editions.list_ideas(cfg), [])
        self.assertEqual(editions.idea_counts(cfg)["total"], 0)


if __name__ == "__main__":
    unittest.main()
