"""Tests for the short view of the check report."""
import unittest

from redaktion import bericht

REPORT = """# Prüfbericht: Test

## Hart

### Fakten

- Bestanden. Einstieg, "A": Quelle.
- Fail. Der Kurs, "B": keine Quelle.
- Bestanden, mit Hinweis. Zur Einsicht, "C": gilt nur oben.

### Zahlen

- Fail: "B", siehe Fakten.

## Hinweise

### Personas

- Behörde: Ich lese bis zum Ende.

## Urteil

Blockiert, bis 1 harter Punkt behoben ist.
"""


class Report(unittest.TestCase):
    def test_counts_and_verdict(self):
        r = bericht.parse(REPORT)
        self.assertTrue(r["blockiert"])
        self.assertEqual(r["hart"][0]["counts"], {"ok": 1, "hinweis": 1, "fail": 1, "info": 0})
        self.assertEqual(r["hinweise"][0]["name"], "Personas")

    def test_points_fail_first_and_no_cross_references(self):
        pts = bericht.open_points(REPORT)
        self.assertEqual([(p["art"], p["text"][:9]) for p in pts], [("muss", "Der Kurs,"), ("kann", "Zur Einsi")])
