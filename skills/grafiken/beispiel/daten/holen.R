# Holt die Daten für die Grafik und schreibt die README daneben.
# Einmal ausführen, aus dem Ordner der Ausgabe: Rscript daten/holen.R
# Die CSV bleibt aus Git (die Organisation ignoriert *.csv). Dieses Skript und
# die README sind der Weg, sie wieder zu holen (reproducibility.md, Punkt 5).

hier <- dirname(normalizePath(sub("--file=", "", grep("--file=", commandArgs(), value = TRUE))))

datensatz <- "Bevölkerung: Durchschnittsalter [Jahre]"
seite <- "https://opendata.swiss/de/dataset/bevolkerung-durchschnittsalter-jahre"
url <- "https://www.web.statistik.zh.ch/ogd/data/KANTON_ZUERICH_809.csv"
herausgeber <- "Amt für Statistik und Daten, Kanton Zürich (Gemeindeporträt, Indikator 809)"
nutzung <- "opendata.swiss, Freie Nutzung, Quellenangabe ist Pflicht (https://opendata.swiss/terms-of-use#terms_by)"
ziel <- file.path(hier, basename(url))

download.file(url, ziel, mode = "wb", quiet = TRUE)
groesse <- file.size(ziel)
pruefsumme <- unname(tools::md5sum(ziel))
heute <- format(Sys.Date(), "%Y-%m-%d")

readme <- c(
  "# Daten",
  "",
  "Geholt mit `holen.R`. Die CSV liegt nicht in Git; das Skript holt sie wieder.",
  "",
  paste0("- Datensatz: ", datensatz),
  paste0("- Seite: ", seite),
  paste0("- Datei: ", url),
  paste0("- Herausgeber: ", herausgeber),
  paste0("- Nutzungsbedingungen: ", nutzung),
  paste0("- Abgerufen am: ", heute),
  paste0("- Grösse: ", format(groesse, big.mark = "'"), " Bytes, MD5 ", pruefsumme),
  "- Felder genutzt: GEBIET_NAME (Filter auf \"Zürich - ganzer Kanton\"), INDIKATOR_JAHR, INDIKATOR_VALUE",
  "- Eine Zeile pro Gemeinde, Bezirk oder Kanton und Jahr; die Grafik nimmt die Zeilen des ganzen Kantons."
)
writeLines(readme, file.path(hier, "README.md"))
cat("geholt:", ziel, "(", groesse, "Bytes )\n")
