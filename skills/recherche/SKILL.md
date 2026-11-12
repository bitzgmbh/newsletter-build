---
name: recherche
disable-model-invocation: true
description: >-
  Research for an edition of bitz (stage 4), in German. Reads Lars's rough
  draft and writes recherche.md with four parts: sources for every claim,
  number and name in the draft; his own material in the arti-vault wiki,
  journals and repositories; outside context from the web; and links to
  earlier bitz editions and reader replies. Every item has a link; unsure
  items carry a "?". Never writes edition text. Use when the runner reaches
  stage 4, or when Lars invokes /recherche on an edition folder.
---

# recherche

The skill works from one role: Fachbibliothekar:in für Datenrecherche (`pipeline/concept.md`, Breite). Primary sources before summaries, and a plain word on how reliable each source is. Stage 4 of the pipeline, after the rough draft and before the outline. What it finds feeds the outline (stimme, mode gliederung) and the checks at stage 6 (pruefung), which require every number in the text to trace back here or to a link in the text.

## Files to read first

- `rohentwurf.md` in the edition folder. If it is missing, the Rohentwurf field of the edition's issue in the private repository.
- `index.qmd` in the edition folder: the front matter names the Hauptleserschaft and the series.
- `pipeline/concept.md`, sections "Für wen" and "Breite", in this repository: who reads, and the role above.
- `skills/stimme/regeln.md`: the German plain rules. They apply to every line of `recherche.md`.

## Input

An edition folder in the private repository `bitzgmbh/newsletter`, `ausgaben/<JJJJ-MM-TT-kurzname>/`. Where to look for Lars's own material:

- The arti-vault graph: `vault_path` in `~/.config/bitz-newsletter.json`, else `~/Documents/gitrepos/cb-laz/arti-vault`. Wiki pages are `pages/wiki___*.md`, project pages `pages/para___*.md`, journals `journals/*.md`.
- His repositories under `~/Documents/gitrepos/`, found by name or with `grep -rl`.
- Earlier editions: the other folders in `ausgaben/` of the private repository, and the Buttondown archive at `https://buttondown.com/bitz/archive` once editions are sent.
- Reader replies: the gate lines and notes in earlier editions' folders, and the part "Was ihr letztes Mal gesagt habt" of the previous edition.

## Steps

1. List what the draft claims. Every fact, number, date, name, quote and named tool or course is one line. Keep the draft's own words in the line.
2. Check each claim against a primary source: the official page, the paper, the data, the course page, the release notes. Fetch the page; quote the sentence that carries the claim and give the date the page shows. A claim found only in a summary or a news piece gets a "?" and the reason. A claim that no source carries gets "? keine Quelle gefunden"; it never gets a guessed source.
3. Look for Lars's own material on the topic of the edition: wiki pages, project pages, journal notes, talks, course material, data packages. One line each, with the path and one sentence on what it adds. Name only pages that exist; read each one before naming it.
4. Look for outside context: two to five recent articles, examples or numbers that fit the one idea of the edition. Prefer sources the main readership trusts (official statistics, public administration, universities). Each with the link, the date, and one sentence on why it fits.
5. Look for earlier bitz editions and reader replies that the edition can point to. One line each with the folder or the archive link.

## Output

Write `recherche.md` into the edition folder, in German:

```
# Recherche: <Titel der Ausgabe>

Stufe 4, am <Datum>, aus <wie vielen> Quellen. Jede Zahl im Text muss hierher oder auf einen Link im Text zurückführen.

## Aussagen aus dem Rohentwurf
- "<Aussage, in Lars's Worten>": <belegt | ? ...>. Quelle: <Link>, Stand <Datum>. "<der Satz aus der Quelle>"

## Eigenes Material
- <Pfad oder Link>: <was es beiträgt>

## Kontext von aussen
- <Link>, <Datum>: <warum es passt>

## Frühere Ausgaben und Antworten
- <Ordner oder Link>: <worauf die Ausgabe verweisen kann>

## Offene Punkte
- <jede Zeile mit "?", gesammelt>
```

Leave a part with "nichts gefunden" rather than padding it. Then stop. Stage 4 has a gate: the runner pings Lars with the counts (belegt, offen, eigenes Material) and the open points.

## What this skill never does

- Write, complete or change the text of an edition, or propose sentences for it.
- Invent a source, a quote, a date or a number. A missing source stays a "?".
- Copy personal details about other people from the journals into `recherche.md`, or cite voice notes, transcripts or recordings. Journals are for finding Lars's own projects and notes; a line from them names the project or the wiki page, not the private note.
- Fetch from sites whose terms forbid automated access (decided case by case; when unsure, name the site and leave it).
