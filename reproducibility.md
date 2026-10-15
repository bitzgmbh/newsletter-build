# Reproducibility principles

These principles hold for everything in this repository and for every edition. They answer one test: if the AI were gone tomorrow, could I rebuild the result myself?

1. AI writes the code that makes a figure, never the figure itself. Charts, data plots, tables and diagrams come from code that sits in this repository and runs again.
2. Numbers in the text come from the data through inline code. Nobody types them in, and no model makes them up.
3. The source stays the source. Outputs are rebuilt from it, never edited by hand, and never copied to a second place where they go stale.
4. Citations are keys from my Zotero library, so I can check or swap a reference without the AI.
5. The steps to rebuild an output are written down next to it, with the tool versions.
6. A file with code to render is a Quarto document (`.qmd`). Only plain text stays Markdown (`.md`).

## Where they apply here

- The pipeline map is Mermaid code in [pipeline/map.qmd](pipeline/map.qmd). The command to render it sits under the map.
- Stage 7 (visuals) writes the code for a chart. The chart is rendered from that code.
- Stage 6 (checks) fails a draft when a number has neither inline code nor a cited source behind it.
