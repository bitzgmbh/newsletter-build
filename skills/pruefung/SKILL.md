---
name: pruefung
description: >-
  Checks an edition of Zur Einsicht at stage 6 and never edits it. Hard
  checks: every fact, number, date and link traces to a source or a code
  chunk, and every link resolves; a hard fail blocks the edition. Hints: word
  count per part, AI tells in German, and five reader personas who say where
  they stop reading. Writes pruefbericht.md next to the edition. Use when Lars
  asks for the Prüfung, the checks or the Prüfbericht of an edition, or
  invokes /pruefung on an edition folder or file.
---

# pruefung

The skill works from one role: Schlussredaktion und Faktencheck einer Zeitung (`pipeline/concept.md`, Breite). It checks every number, every link and the length, names the AI tells, and lets the five personas read as the readers. It reports and stops. It never edits the edition and never rewrites a sentence (decision 0016).

## Files to read first

- `pipeline/concept.md`, sections "Für wen" and "Breite": the readers and the five personas.
- `personas.md` in this folder: how each persona reads.
- `blickwinkel.md` in this folder: the three perspectives of the Blickwinkel hint.
- `skills/stimme/regeln.md`: the German plain rules; their patterns are the AI tells.
- `reproducibility.md`: numbers come from code or from a cited source, never typed.
- In the edition folder, when present: `recherche.md` (the sources of stage 4), `rohentwurf.md` (Lars's own words) and `gliederung.md` (the Hauptleserschaft).

## Input

An edition folder in the private repository `bitzgmbh/zur-einsicht`, `ausgaben/<JJJJ-MM-TT-kurzname>/`. By default the skill checks `index.qmd`; a named file in the folder, such as `entwurf-skill.md`, is checked instead when Lars names it. The Hauptleserschaft comes from the front matter or from `gliederung.md`. If neither names it, ask.

## Hard checks

A hard fail blocks the edition until it is fixed. Three checks:

1. **Facts.** Every fact, number, date, name or claim about the world traces to a source: an entry in `recherche.md`, a link in the text, or a code chunk that computes it. Lars's own words quoted from `rohentwurf.md`, and statements of his own experience, judgement or intention, are not facts and are not checked. A claim about the world that no source backs fails, even when it sounds right.
2. **Links.** Run `scripts/links.py <file>`. Every URL must resolve (status 2xx or 3xx). A placeholder where a link belongs, e.g. "[Link]" or a relative `?ref=` without a page, fails, because the edition cannot go out with it.
3. **Numbers.** Every number in the prose comes from a code chunk or from a cited source (`reproducibility.md`). A number typed by hand without a source fails. Dates in the front matter and the word budgets in comments are not prose.

For each item write: Bestanden or Fail, the part and the quoted passage, the reason, and which source would settle it. Name the missing source; do not write the fix.

## Hints

Hints go into the report and Lars decides. They never block.

- **Length.** Run `skills/stimme/scripts/woerter.py <file>`. Report a table with part, count, budget from `pipeline/template.md` and the difference. A total over 1000 is a hint.
- **AI tells.** Read the text against `regeln.md` and the patterns below, adapted from the prose-lint skill for German. Report each finding with the pattern name, the part and the quoted passage. No suggested rewrite.
  - Gegensatz als Figur: "nicht X, sondern Y", "nicht nur X, sondern auch Y", more than once in the text (one is Lars's voice, see `skills/stimme/stimme.md`).
  - Pointe als Fragment: a sentence without a verb as a closer.
  - Dreierreihe aus Rhythmus: three adjectives or clauses where the content did not ask for three.
  - Verstärker ohne Inhalt: "wirklich", "entscheidend", "wichtig", "spannend", "zentral".
  - Doppelpunkt vor einer Pointe, instead of before a list.
  - Rhetorische Frage, above all two in a row.
  - Nachgestellte Deutung: a trailing participle or "was zeigt, dass" that adds interpretation.
  - Vage Quelle: "Studien zeigen", "Expert:innen sagen".
  - Gleicher Satzanfang in consecutive sentences, and synonym cycling for the same thing.
  - Zusammenfassung oder gute Wünsche am Schluss, Ankündigung des nächsten Punkts.
  - Überschrift als "X: Y" repeated across the text.
- **Personas.** Each of the five personas in `personas.md` reads the whole text from her situation and names the first sentence where she stops reading, and why, in one or two sentences in German, in her own words. A persona who reads to the end says so and names what she would do next. The persona of the Hauptleserschaft speaks last, and her entry is marked "(Hauptleserschaft)". Her verdict counts most, as decided in 0016.
- **Blickwinkel.** Read the whole text once from each perspective in `blickwinkel.md` (Psychologie, Didaktik, Philosophie, decision 0018) and report, in one or two German sentences per perspective, what the text misses or what does not hold from that view. No rewrite, no verdict on the idea.

## Output

Write `pruefbericht.md` into the edition folder, in German:

```
# Prüfbericht: <Titel der Ausgabe>

Datum, geprüfte Datei, Hauptleserschaft, Stand von recherche.md (vorhanden oder fehlt).

## Hart
- Fakten: Bestanden oder Fail, je Punkt: Teil, Zitat, Grund, welche Quelle es klären würde.
- Links: Ausgabe von links.py, je URL eine Zeile.
- Zahlen: Bestanden oder Fail, je Zahl.

## Hinweise
### Länge
Tabelle: Teil, Wörter, Budget, Differenz. Total.
### Floskeln und Muster
Je Fund: Muster, Teil, Zitat.
### Personas
Fünf Einträge, die Hauptleserschaft zuletzt und markiert.
### Blickwinkel
Drei Einträge, je ein bis zwei Sätze.

## Urteil
Eine Zeile: "Freigegeben für Stufe 7" oder "Blockiert, bis N harte Punkte behoben sind".
```

Then stop. The report is the gate. Lars decides on every hint and fixes the hard points himself or hands them to the stage that owns them.

## What this skill does not do

- Edit, rewrite or complete the edition. Not a sentence, not a link.
- Invent a source, or count a claim as sourced because it is plausible.
- Judge the voice (that is `stimme`) or the idea (that is Lars).
- Check code for correctness. It checks that numbers come from code, not that the code is right.
