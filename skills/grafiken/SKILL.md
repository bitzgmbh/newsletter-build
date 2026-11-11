---
name: grafiken
disable-model-invocation: true
description: >-
  Makes the chart or charts of an edition of bitz from data Lars names: a
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
- `R/marke.R` and `_brand.yml` in the root of `bitzgmbh/newsletter`: the brand helper and the tokens it reads.

## Input

An edition folder in `bitzgmbh/newsletter`, `ausgaben/<JJJJ-MM-TT-kurzname>/`, the claim the chart supports, and the data source Lars named. Without one, stop and ask (see above).

## One source, two renderings

The email cannot run JavaScript, so every chart exists twice, from the same data file:

- Static, from an R chunk: ggplot2 through ragg, one statement in the caption, large labels (`theme_brand(br, base_size = 16)`), no legend when colour carries no meaning, the source as the plot caption. This is the version the email shows.
- Interactive, from an OJS cell right after it: Observable Plot (D3 based, decision 0008), the same data handed over with `ojs_define()`, so the frozen render carries the data and the website needs neither R nor the file. This is the version the website shows.

The static chart sits in a fenced div `::: {.nur-mail}`, the OJS cell in `::: {.nur-web}`. The website hides `.nur-mail` (`styles.css` in `bitzgmbh/newsletter`); the email export at stage 10 takes `.nur-mail` and drops `.nur-web`.

## The brand

Colours and the font of every chart come from the bitz brand, `_brand.yml` in the root of `bitzgmbh/newsletter` (a copy of `bitzgmbh/brand`, decision 0039). The chunks read it through `R/marke.R` in the same repository. No hex value and no font name is written into a chunk, an OJS cell or `grafiken.md`.

- Set-up: `source("../../R/marke.R")` and `br <- load_brand(brand_path())` in the setup chunk.
- Groups without an order: `cat_colours(br, n)`, which gives `chart-1` to `chart-n` in the order of the brand. One series takes `chart-1`. `chart-5` is the lightest colour and is used only for a fifth series. More than five groups means fewer groups or another chart form, never a colour picked by hand. A fixed assignment that Lars asked for (for example openwashdata always violet, `chart-4`) is written as a named vector of token names and noted in `grafiken.md`.
- Ordered levels: `seq_steps(br, n)`, from `seq-low` (little) to `seq-high` (much). The legend follows the order of the levels.
- Text in `foreground`, the source line and annotations in `secondary`, grid lines in `grey-light`. `theme_brand(br)` sets all of this and the font (`typography.base.family`).
- Background: white for the email (`theme_brand()` takes the `white` token by default), no background on the website, where the paper of the page shows through.
- Font: `require_brand_font(br)` comes before the plot. When the font is missing and cannot be fetched from the source the brand names, the render stops with a German message. The skill then reports this and stops; it never switches to another font.
- Web version: the same colour values and the font name go to the OJS cell through `ojs_define()`, next to the data. The page loads the font file.
- The brand files are never edited in the newsletter repository. A newer brand comes in with `bash scripts/marke-holen.sh`, which Lars runs or asks for.

The editions of 12 and 26 November 2026 were built before the shared helper and keep their own `marke.R` next to the edition. Editions that were sent are not rendered again.

## Data stays out of git

The org `.gitignore` ignores `*.csv`. The skill does not commit data. It writes `daten/holen.R` next to the edition, which downloads the source file into `daten/` and writes `daten/README.md` with the dataset, the URL, the publisher, the terms of use, the date fetched, the size, a checksum and the fields used. The R chunk reads from `daten/`. `_freeze/` is committed, so the publish action renders without R and without the data. The alternative, a negation `!ausgaben/**/daten/*.csv`, is open for Lars and would need the org rule to bend.

## Steps

1. Name the claim and the one statement the chart will make. Check with Lars if the outline does not settle it.
2. Write `daten/holen.R` from the skeleton in `vorlage.md`, run it with `Rscript daten/holen.R` from the edition folder, read `daten/README.md`. For his own data from another repository, the script copies or reads from there and the README names that repository and commit.
3. Insert into `index.qmd`, at the place the outline or Lars names, from the templates in `vorlage.md`:
   - a setup chunk (`label: daten`, no output) that reads the file, keeps the rows and columns needed, computes the numbers the text uses, reads the brand, and calls `ojs_define()` with the data and the brand values;
   - the figure chunk with `label: fig-<name>`, `fig-cap` and `fig-alt` built with `!expr` from the data, `echo: false`, `dev: ragg_png`, inside `::: {.nur-mail}`;
   - the OJS cell with `Plot.plot()` on `transpose(<name>)`, with tooltips, inside `::: {.nur-web}`, followed by the source line.
   - Numbers from the data in the text as inline R code, never typed.
4. Render the edition with `quarto render` from the repository root and look at the result: both charts present, the caption states one thing, labels legible at phone width.
5. Write `grafiken.md` into the edition folder: the chart's label, the claim, the one statement, the source with URL and date, the state of the brand from `marke-stand.txt` with the tokens used, and the versions from `sessionInfo()` (R, ggplot2, readr, dplyr, ragg, systemfonts, brand.yml, Quarto).
6. Stop. The chart is a gate: Lars looks at it and says yes.

## What this skill does not do

- Draw a chart by hand, paste a screenshot, or embed an image file.
- Invent or adjust data, or type a number into the text.
- Commit a data file, or anything outside the edition folder.
- Change the text of an edition beyond inserting the chart block where it was told to.
- Look for a dataset on its own, or take a different one than Lars named.
- Write a colour value or a font name into a chunk, or edit `_brand.yml`, `logos/` or `assets/`.
