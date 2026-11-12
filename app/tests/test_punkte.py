"""Tests for the open points. Run with: uv run python -m unittest discover tests"""
import unittest

from redaktion import punkte

OUTLINE = """# Gliederung: Test

**Probier es selbst, Form:** ohne Werkzeug. ?

## Einstieg (80 Wörter)

- Die Frage einer Teilnehmerin: "Was mache ich hier?" Weniger als vier Sätze.
- ? Betreff: "A" oder "B".

## Die Idee

- Zahl mit Quelle: acht Durchführungen. ?
"""


QMD = """---
subtitle: "TODO: Betreffzeile der E-Mail"
---

<!-- Vorlage
#| fig-cap: "TODO: eine Aussage pro Grafik"
-->

## Die Idee (TODO: Ist Die Idee der richtige Titel?)

Ein Satz. TODO: das ist veraltet.
"""


class OpenPoints(unittest.TestCase):
    def test_finds_todo_in_text_heading_and_front_matter_not_in_comments(self):
        pts = punkte.open_points(QMD)
        self.assertEqual(len(pts), 3)
        self.assertEqual(pts[0]["text"], "TODO: Betreffzeile der E-Mail (nach: subtitle)")
        self.assertEqual(pts[1]["text"], "TODO: Ist Die Idee der richtige Titel?")
        self.assertEqual(pts[2]["text"], "TODO: das ist veraltet. (nach: Ein Satz)")
        self.assertEqual(pts[1]["section"], "Die Idee")
        self.assertEqual(pts[2]["section"], "Die Idee")

    def test_finds_standalone_question_marks_only(self):
        pts = punkte.open_points(OUTLINE)
        self.assertEqual(len(pts), 3)
        self.assertEqual(pts[0]["section"], "Allgemein, Probier es selbst, Form")
        self.assertEqual(pts[1]["section"], "Einstieg (80 Wörter)")
        self.assertEqual(pts[1]["text"], 'Betreff: "A" oder "B".')
        self.assertEqual(pts[2]["section"], "Die Idee")

    def test_feedback_joins_answers_and_skips_empty(self):
        pts = punkte.open_points(OUTLINE)
        text = punkte.feedback("gliederung.md", pts, {1: "", 2: 'nimm "B"', 3: "ja, so"}, "kürzer")
        self.assertTrue(text.startswith("In gliederung.md einarbeiten."))
        self.assertIn("Punkt 2 (Einstieg (80 Wörter)", text)
        self.assertIn("nimm 'B'", text)
        self.assertNotIn("Punkt 1", text)
        self.assertIn("Allgemein: kürzer", text)
        self.assertNotIn('"', text)
        self.assertNotIn("\n", text)

    def test_no_answers_no_feedback(self):
        self.assertEqual(punkte.feedback("x.md", punkte.open_points(OUTLINE), {}, ""), "")


if __name__ == "__main__":
    unittest.main()


class OffenSection(unittest.TestCase):
    def test_bullets_under_offen_are_points(self):
        text = "# Grafiken\n\n- fig: gut\n\n## Offen\n\n- Erster Punkt.\n- Zweiter Punkt.\n"
        pts = punkte.open_points(text)
        self.assertEqual([p["text"] for p in pts], ["Erster Punkt.", "Zweiter Punkt."])
        self.assertEqual(pts[0]["section"], "Offen")
