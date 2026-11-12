"""Tests for stand.py. Run with: python3 -m unittest discover skills/runner/tests

The fixtures are small invented edition folders. Real editions live in the
private repository and never come into this public one.
"""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import stand  # noqa: E402

FULL_TEXT = """---
title: "Test"
---

Ein Einstieg mit Text.

## Die Idee

Text.

## Was ihr letztes Mal gesagt habt

## Eine Frage an dich

Text.
"""

EMPTY_TEXT = """---
title: "Test"
---

## Die Idee

## Eine Frage an dich
"""


def make(files, gates=()):
    folder = pathlib.Path(tempfile.mkdtemp())
    for name in files:
        content = "x\n"
        if name == "index.qmd":
            content = FULL_TEXT
        elif name == "index-empty":
            name, content = "index.qmd", EMPTY_TEXT
        (folder / name).write_text(content, encoding="utf-8")
    if gates:
        lines = ["# Prüfpunkte", ""] + [f"- 2026-11-03 10:00 Stufe {g}" for g in gates]
        (folder / "pruefpunkte.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return folder


def nxt(folder):
    return stand.infer(folder)["next"]["id"]


class Order(unittest.TestCase):
    def test_empty_folder_starts_with_recherche(self):
        self.assertEqual(nxt(make([])), "4")

    def test_after_recherche_comes_gliederung_and_gate_4_waits(self):
        state = stand.infer(make(["recherche.md"]))
        self.assertEqual(state["next"]["id"], "5a")
        self.assertEqual(state["gate_waiting"], "4")
        self.assertEqual(state["gate_checkbox"], "4 Recherche")

    def test_gate_closed_by_yes(self):
        state = stand.infer(make(["recherche.md"], ["4 Recherche: ja"]))
        self.assertIsNone(state["gate_waiting"])

    def test_ja_inside_a_change_is_not_a_yes(self):
        gate = '5a Gliederung: geändert: "Punkt 1 (Form): ja, das passt. | Punkt 2: blockiert nichts"'
        state = stand.infer(make(["recherche.md", "gliederung.md", "index-empty"], ["4 Recherche: ja", gate]))
        self.assertEqual(state["gate_waiting"], "5a")

    def test_offen_keeps_gate_waiting(self):
        state = stand.infer(make(["recherche.md"], ["4 Recherche: offen"]))
        self.assertEqual(state["gate_waiting"], "4")

    def test_empty_parts_mean_5b(self):
        state = stand.infer(make(["recherche.md", "gliederung.md", "index-empty"]))
        self.assertEqual(state["next"]["id"], "5b")
        self.assertIn("Die Idee", state["empty_parts"])

    def test_5b_is_an_agent_stage_without_a_gate_before_it_runs(self):
        state = stand.infer(make(["recherche.md", "gliederung.md", "index-empty"], ["5a Gliederung: ja"]))
        self.assertEqual(state["next"]["who"], "agent")
        self.assertIsNone(state["gate_waiting"])

    def test_text_written_means_gate_5b_waits(self):
        state = stand.infer(make(["recherche.md", "gliederung.md", "index.qmd"], ["5a Gliederung: ja"]))
        self.assertEqual(state["next"]["id"], "6")
        self.assertEqual(state["gate_waiting"], "5b")
        state = stand.infer(make(["recherche.md", "gliederung.md", "index.qmd"],
                                 ["5a Gliederung: ja", "5b Text: ja"]))
        self.assertIsNone(state["gate_waiting"])

    def test_optional_part_may_stay_empty(self):
        self.assertEqual(nxt(make(["recherche.md", "gliederung.md", "index.qmd"])), "6")

    def test_blocked_goes_back_to_5b(self):
        files = ["recherche.md", "gliederung.md", "index.qmd", "pruefung-stimme.md", "pruefbericht.md"]
        state = stand.infer(make(files, ["6 Prüfungen: blockiert, zurück zu 5b"]))
        self.assertEqual(state["next"]["id"], "5b")
        self.assertEqual(state["next"]["note"], "nach blockiertem Urteil")
        self.assertIsNone(state["gate_waiting"])

    BASE = ["recherche.md", "gliederung.md", "index.qmd", "pruefung-stimme.md", "pruefbericht.md"]

    def test_grafiken_waits_for_its_output_then_its_gate(self):
        state = stand.infer(make(self.BASE, ["6 Prüfungen: ja"]))
        self.assertEqual(state["next"]["id"], "7")
        self.assertFalse(state["next"]["output_present"])
        state = stand.infer(make(self.BASE + ["grafiken.md"], ["6 Prüfungen: ja"]))
        self.assertEqual(state["gate_waiting"], "7")

    def test_uebersetzung_after_grafiken_yes(self):
        state = stand.infer(make(self.BASE + ["grafiken.md", "index-en.qmd"], ["7 Grafiken: ja"]))
        self.assertEqual(state["next"]["id"], "8")
        self.assertEqual(state["gate_waiting"], "8")

    def test_freigabe_versand_verbreitung_fertig(self):
        files = self.BASE + ["grafiken.md", "index-en.qmd"]
        gates = ["7 Grafiken: ja", "8 Übersetzung: ja"]
        self.assertEqual(nxt(make(files, gates)), "9")
        gates.append("9 Freigabe: ja")
        self.assertEqual(nxt(make(files, gates)), "10")
        gates.append("10 Versand: Entwurf abc123")
        self.assertEqual(nxt(make(files, gates)), "11")
        state = stand.infer(make(files + ["verbreitung.md"], gates))
        self.assertEqual(state["gate_waiting"], "11")
        gates.append("11 Verbreitung: ja")
        self.assertEqual(nxt(make(files + ["verbreitung.md"], gates)), "fertig")

    def test_stage_10_is_not_stage_1(self):
        self.assertFalse(stand.stage_lines(["- x Stufe 1 Intake: ja"], "10"))
        self.assertFalse(stand.has_yes(["- x Stufe 10 Versand: ja"], "1"))


class Labels(unittest.TestCase):
    def test_checkbox_labels_match_issue_template(self):
        labels = [s[5] for s in stand.STAGES]
        self.assertIn("5 Gliederung vom Agenten", labels)
        self.assertIn("9 Freigabe (Merge in main)", labels)


if __name__ == "__main__":
    unittest.main()
