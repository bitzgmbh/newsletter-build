# Beispiel für den Skill grafiken

Eine Grafik, zwei Fassungen, aus einer Datei: das Durchschnittsalter der Bevölkerung des Kantons Zürich pro Jahr, aus dem Gemeindeporträt des Amts für Statistik und Daten (opendata.swiss, freie Nutzung mit Quellenangabe).

## Rendern

Aus diesem Ordner:

```
Rscript daten/holen.R
quarto render beispiel.qmd
```

`holen.R` lädt die CSV nach `daten/` und schreibt `daten/README.md` mit Quelle, Datum und Prüfsumme. Die CSV und das gerenderte HTML bleiben aus Git.
