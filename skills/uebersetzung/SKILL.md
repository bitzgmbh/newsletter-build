---
name: uebersetzung
disable-model-invocation: true
description: >-
  English version of an edition of bitz (stage 8). Translates the approved
  German index.qmd into index-en.qmd for the second Buttondown email
  (decision 0030): same parts, same chart, same links, in Lars's plain English
  style, nothing added. Use when the runner reaches stage 8, or when Lars
  invokes /uebersetzung on an edition folder.
---

# uebersetzung

The skill works from one role: Fachübersetzer:in Deutsch nach Englisch (`pipeline/concept.md`, Breite). Tone and technical terms, not word for word. Stage 8 of the pipeline, after the checks (6) and the chart (7) have Lars's yes, so the German text is final.

## Files to read first

- `index.qmd` in the edition folder: the approved German text.
- `skills/stimme/stimme.md`: Lars's voice. It carries over to English: short sentences, direct address, his own English terms.
- The plain-writing rules Lars uses for English, in short: simple everyday words, complete sentences, no dashes, no jargon, no analogies, no filler, no emojis, no em dashes. "Due date", never "deadline". No "simply", "simple" or "easy". No "X, not Y" reframes.

## Input

An edition folder in the private repository `bitzgmbh/newsletter`, `ausgaben/<JJJJ-MM-TT-kurzname>/`, whose gate 7 has a yes in `pruefpunkte.md`. If gate 7 has no yes, stop and say so.

## Rules

1. Same parts, same order, same headings translated: Die Idee becomes "The idea", Zur Einsicht stays "Zur Einsicht" (the section name, decision 0020) with "(a look inside)" after it once, Probier es selbst becomes "Try it yourself", Eine Frage an dich becomes "A question for you", Was ihr letztes Mal gesagt habt becomes "What you said last time", Offengelegt stays "Offengelegt" with "(disclosed)" after it once, Weiterlesen becomes "Read more".
2. Nothing added, nothing left out. A sentence that only works for Swiss German readers (a local office, a German term) keeps its meaning with a short explanation in brackets, never a new example.
3. Front matter: translate `title`, `subtitle` (the email subject) and `description` (the preview text). Keep `date`, `reihe` (translated label, same count), `hauptleserschaft`. Add `lang: en`.
4. Code chunks, chart chunks, data paths and the `.nur-mail` and `.nur-web` blocks stay exactly as they are. Translate only `fig-cap` and `fig-alt`, and keep the `!expr` parts unchanged.
5. Links stay the same. Where a link points to a German page and an English version of that page exists, keep the German link and add the English one after it.
6. The block between `<!-- offenlegung:start -->` and `<!-- offenlegung:end -->` is translated line by line, with the same numbers.
7. The question to the reader keeps its form (one click or one reply). Names of courses, tools and people are never translated.
8. Address the reader as "you". Use British or American spelling consistently within one edition; American by default.

## Output

Write `index-en.qmd` into the edition folder. Then add a short list at the end of the run (not in the file): every place where the German needed an explanation in brackets, and every term left in German. Then stop. Stage 8 has a gate: the runner pings Lars with that list.

## What this skill never does

- Change `index.qmd` or any other file than `index-en.qmd`.
- Add a claim, an example or a number that the German text does not have.
- Decide who receives the English email. That is open (decision 0030, open question 2).
