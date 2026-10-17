# Vorlage für eine Grafik

Die Bausteine, die der Skill in `index.qmd` einsetzt, ohne Daten. `<name>` ist der Name der Grafik, `<datei>` die Datei in `daten/`, die `holen.R` geholt hat. Die Daten kommen von Lars (siehe SKILL.md).

## 1. Setup Chunk: Daten lesen, Zahlen rechnen, an OJS übergeben

````markdown
```{r}
#| label: daten-<name>
library(readr)
library(dplyr)
datei <- "daten/<datei>"
d <- read_csv(datei, show_col_types = FALSE) |>
  filter(<nur die Zeilen, die die Grafik braucht>) |>
  transmute(<x> = ..., <y> = ...) |>
  arrange(<x>)
erstes <- d[1, ]
letztes <- d[nrow(d), ]
abgerufen <- format(as.Date(file.info(datei)$mtime), "%d.%m.%Y")
zahl <- function(x) format(x, decimal.mark = ",", nsmall = 1)
quelle <- paste0("Quelle: <Herausgeber>, <Datensatz>, abgerufen am ", abgerufen)
ojs_define(d_<name> = d)
```
````

## 2. Eine Zahl im Text, aus den Daten

````markdown
Im Jahr `r letztes$<x>` lag <die Grösse> bei `r zahl(letztes$<y>)` <Einheit>.
````

## 3. Die statische Grafik für die E-Mail

````markdown
::: {.nur-mail}

```{r}
#| label: fig-<name>
#| fig-cap: !expr sprintf("<Die eine Aussage der Grafik, mit %s für Zahlen aus den Daten.>", zahl(letztes$<y>))
#| fig-alt: !expr sprintf("<Was die Grafik zeigt, für Menschen, die sie nicht sehen: Art, Zeitraum, von %s bis %s.>", zahl(erstes$<y>), zahl(letztes$<y>))
#| fig-width: 7
#| fig-height: 4.2
#| dev: ragg_png
library(ggplot2)
ggplot(d, aes(<x>, <y>)) +
  geom_line(linewidth = 1.2, colour = "#2440a8") +
  geom_point(size = 2.4, colour = "#2440a8") +
  scale_y_continuous(labels = zahl) +
  labs(x = NULL, y = "<Grösse in Einheit>", caption = quelle) +
  theme_minimal(base_size = 16) +
  theme(panel.grid.minor = element_blank(),
        plot.caption = element_text(size = 10, hjust = 0))
```

:::
````

Regeln: `echo: false` gilt für das Dokument, kein Code Folding. Eine Aussage pro Grafik, keine Legende, wenn Farbe nichts bedeutet, Schrift gross genug für das Handy, die Quelle als Caption.

## 4. Die interaktive Grafik für die Website

````markdown
::: {.nur-web}

```{ojs}
//| label: fig-<name>-web
Plot.plot({
  height: 320,
  marginLeft: 50,
  style: {fontSize: "14px"},
  x: {label: null, tickFormat: d => String(d)},
  y: {label: "<Grösse in Einheit>", grid: true, tickFormat: d => d.toLocaleString("de-CH")},
  marks: [
    Plot.line(transpose(d_<name>), {x: "<x>", y: "<y>", stroke: "#2440a8", strokeWidth: 2}),
    Plot.dot(transpose(d_<name>), {x: "<x>", y: "<y>", fill: "#2440a8", r: 4,
      title: d => `${d.<x>}: ${d.<y>.toLocaleString("de-CH")} <Einheit>`, tip: true})
  ]
})
```

`r quelle`.

:::
````

`transpose()` ist die Hilfe von Quarto für Daten aus `ojs_define()`. Die Daten stecken damit im gerenderten Dokument und in `_freeze/`; die Website braucht weder R noch die Datei.

## 5. Skelett von `daten/holen.R`

```r
# Holt die Daten für die Grafik und schreibt die README daneben.
# Einmal ausführen, aus dem Ordner der Ausgabe: Rscript daten/holen.R
# Die Datei bleibt aus Git (die Organisation ignoriert *.csv).

hier <- dirname(normalizePath(sub("--file=", "", grep("--file=", commandArgs(), value = TRUE))))

datensatz <- "<Name des Datensatzes>"
seite <- "<Seite, auf der Lars die Quelle gefunden hat, oder das Repository mit seinen Daten und der Commit>"
url <- "<URL der Datei, oder Pfad im eigenen Repository>"
herausgeber <- "<Herausgeber>"
nutzung <- "<Nutzungsbedingungen oder Lizenz, wörtlich von der Quelle>"
ziel <- file.path(hier, basename(url))

download.file(url, ziel, mode = "wb", quiet = TRUE)   # oder file.copy() aus dem eigenen Repository
groesse <- file.size(ziel)
pruefsumme <- unname(tools::md5sum(ziel))
heute <- format(Sys.Date(), "%Y-%m-%d")

writeLines(c(
  "# Daten",
  "",
  "Geholt mit `holen.R`. Die Datei liegt nicht in Git; das Skript holt sie wieder.",
  "",
  paste0("- Datensatz: ", datensatz),
  paste0("- Seite: ", seite),
  paste0("- Datei: ", url),
  paste0("- Herausgeber: ", herausgeber),
  paste0("- Nutzungsbedingungen: ", nutzung),
  paste0("- Abgerufen am: ", heute),
  paste0("- Grösse: ", format(groesse, big.mark = "'"), " Bytes, MD5 ", pruefsumme),
  "- Felder genutzt: <Felder und Filter>"
), file.path(hier, "README.md"))
cat("geholt:", ziel, "(", groesse, "Bytes )\n")
```

## 6. `grafiken.md` neben der Ausgabe

```markdown
# Grafiken

- fig-<name>: <die Aussage>. Stützt: <der Satz oder die Zahl im Text>. Quelle: <Herausgeber, Datensatz, URL>, abgerufen am <Datum>.
- Versionen: R <x.y.z>, ggplot2 <x.y.z>, readr <x.y.z>, dplyr <x.y.z>, Quarto <x.y.z> (aus sessionInfo() und quarto --version).
```
