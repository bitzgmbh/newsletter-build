---
name: grafiken
description: >-
  Makes the chart or charts of an edition of Zur Einsicht from data Lars names: a
  static version for the email and an interactive version for the website,
  both from one data file next to the edition, both from code. Use when Lars
  asks for a Grafik for an edition, or when the runner reaches stage 7. Never
  draws by hand, never embeds an image file, never invents data.
---

# grafiken

The skill works from one role: Datenjournalist:in aus einer Grafikredaktion (`pipeline/concept.md`, Breite). One statement per chart, readable on a phone, the source under the chart. The chart supports one claim of the edition; if no claim needs a chart, the skill says so and stops.

## The data comes from Lars

The data of a chart comes from Lars: either a source he names in `rohentwurf.md` or `recherche.md`, or his own data from a separate repository of his (for example usage data of his course from Posit Cloud, which first has to be extracted into its own repository). Without a named source the skill stops and asks. It never searches for a dataset to fill a chart, and never substitutes a "similar" dataset for the one he meant.

## Files to read first

- `reproducibility.md` in the build repository: code makes the figure, numbers come through inline code, the steps to rebuild sit next to the output.
- `pipeline/concept.md`, section "Für wen": the readers, who mostly know Excel charts.
- The edition's `gliederung.md` and `recherche.md`: which number or claim the chart supports, and whether a data source is already named.
- `vorlage.md` in this folder: the chunk templates and the skeleton of the fetch script.

## Input

An edition folder in `bitzgmbh/zur-einsicht`, `ausgaben/<JJJJ-MM-TT-kurzname>/`, the claim the chart supports, and the data source Lars named. Without one, stop and ask (see above).

## One source, two renderings

The email cannot run JavaScript, so every chart exists twice, from the same data file:

- Static, from an R chunk: ggplot2 through ragg, one statement in the caption, large labels (`theme_minimal(base_size = 16)`), no legend when colour carries no meaning, the source as the plot caption. This is the version the email shows.
- Interactive, from an OJS cell right after it: Observable Plot (D3 based, decision 0008), the same data handed over with `ojs_define()`, so the frozen render carries the data and the website needs neither R nor the file. This is the version the website shows.

The static chart sits in a fenced div `::: {.nur-mail}`, the OJS cell in `::: {.nur-web}`. The website's CSS hides `.nur-mail` (open question 5); the email export at stage 10 takes `.nur-mail` and drops `.nur-web`.

## Data stays out of git

The org `.gitignore` ignores `*.csv`. The skill does not commit data. It writes `daten/holen.R` next to the edition, which downloads the source file into `daten/` and writes `daten/README.md` with the dataset, the URL, the publisher, the terms of use, the date fetched, the size, a checksum and the fields used. The R chunk reads from `daten/`. `_freeze/` is committed, so the publish action renders without R and without the data. The alternative, a negation `!ausgaben/**/daten/*.csv`, is open for Lars and would need the org rule to bend.

## Steps

1. Name the claim and the one statement the chart will make. Check with Lars if the outline does not settle it.
2. Write `daten/holen.R` from the skeleton in `vorlage.md`, run it with `Rscript daten/holen.R` from the edition folder, read `daten/README.md`. For his own data from another repository, the script copies or reads from there and the README names that repository and commit.
3. Insert into `index.qmd`, at the place the outline or Lars names, from the templates in `vorlage.md`:
   - a setup chunk (`label: daten`, no output) that reads the file, keeps the rows and columns needed, computes the numbers the text uses, and calls `ojs_define()`;
   - the figure chunk with `label: fig-<name>`, `fig-cap` and `fig-alt` built with `!expr` from the data, `echo: false`, `dev: ragg_png`, inside `::: {.nur-mail}`;
   - the OJS cell with `Plot.plot()` on `transpose(<name>)`, with tooltips, inside `::: {.nur-web}`, followed by the source line.
   - Numbers from the data in the text as inline R code, never typed.
4. Render the edition with `quarto render` from the repository root and look at the result: both charts present, the caption states one thing, labels legible at phone width.
5. Write `grafiken.md` into the edition folder: the chart's label, the claim, the one statement, the source with URL and date, and the versions from `sessionInfo()` (R, ggplot2, readr, dplyr, Quarto).
6. Stop. The chart is a gate: Lars looks at it and says yes.

## What this skill does not do

- Draw a chart by hand, paste a screenshot, or embed an image file.
- Invent or adjust data, or type a number into the text.
- Commit a data file, or anything outside the edition folder.
- Change the text of an edition beyond inserting the chart block where it was told to.
- Look for a dataset on its own, or take a different one than Lars named.
