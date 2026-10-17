# grafiken

The skill for stage 7 of the pipeline. It makes the chart of an edition from open data, twice from one file: a static version from R for the email and an interactive version from Observable Plot for the website.

## Why I use it

Every chart in an edition comes from code that sits next to the edition and runs again (`reproducibility.md`). The email cannot run JavaScript and the website should, so the skill builds both from the same data file and the same numbers. The data itself stays out of git: a small script fetches it, and a README next to it records the source, the date and the terms of use.

## What is in here

- `SKILL.md`: the role, the two renderings, the data rule and the steps.
- `beispiel/`: a rendered example from open data of the Kanton Zürich. `beispiel.qmd` holds the pattern, `daten/holen.R` fetches the data, `daten/README.md` is what the script writes.

## Try the example

From `beispiel/`: `Rscript daten/holen.R`, then `quarto render beispiel.qmd` and open `beispiel.html`. The csv and the html stay out of git.
