# grafiken

The skill for stage 7 of the pipeline. It makes the chart of an edition from data I name, twice from one file: a static version from R for the email and an interactive version from Observable Plot for the website.

## Why I use it

Every chart in an edition comes from code that sits next to the edition and runs again (`reproducibility.md`). The email cannot run JavaScript and the website should, so the skill builds both from the same data file and the same numbers. The data comes from me, from a source I name or from my own data in a repository of mine, and it stays out of git: a small script fetches it, and a README next to it records the source, the date and the terms of use. Colours and the font come from the bitz brand (`_brand.yml` in the private repository, read through `R/marke.R`), so both versions look like the rest of bitz and no colour is picked by hand (decision 0039).

## What is in here

- `SKILL.md`: the role, the two renderings, the data rule and the steps.
- `vorlage.md`: the two chunk templates (R for the email, Observable Plot for the website), the source line, an inline number, and the skeleton of the fetch script and its README. No data: the data of a chart always comes from me, never from a source the skill picks. The first render check happens on the first edition with a chart.
