# 0003 The map is code

- Question: how is the pipeline map drawn?
- Options: keep the hand-made SVG of draft 1; write the map as Mermaid code in `pipeline/map.qmd`.
- Choice: Mermaid code in `pipeline/map.qmd`. The SVG is removed.
- Why: the map follows the first principle in [reproducibility.md](../reproducibility.md). Code can be changed in one line and rebuilt by anyone, and Quarto draws it in one render. The SVG could only be changed by redrawing it.
- Date: 2026-10-15
