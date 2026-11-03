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


class OpenPoints(unittest.TestCase):
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
