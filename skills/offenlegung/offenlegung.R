# Build the block "So ist diese Ausgabe entstanden" of an edition from its
# traces: the commits of the edition folder, their trailers (Assisted-by,
# Human-authored, Regent-Session), the Prompts ids in the messages, and the
# files each stage left behind. Decision 0017. Nothing here is typed from
# memory; every line comes from git or from a file next to the edition.
#
# Usage: Rscript skills/offenlegung/offenlegung.R <edition folder> [--schreiben]
# Prints the block. With --schreiben it also writes the block into index.qmd
# between the markers <!-- offenlegung:start --> and <!-- offenlegung:end -->.

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) stop("Usage: offenlegung.R <edition folder> [--schreiben]", call. = FALSE)
folder <- normalizePath(args[1], mustWork = TRUE)
schreiben <- "--schreiben" %in% args

git <- function(...) {
  out <- suppressWarnings(system2("git", c("-C", shQuote(folder), ...), stdout = TRUE, stderr = FALSE))
  status <- attr(out, "status")
  if (!is.null(status) && status != 0) stop("git ", paste(c(...), collapse = " "), " failed", call. = FALSE)
  out
}
# Pathspecs are relative to the folder itself, because git runs with -C <folder>.
trailer <- function(sha, key) {
  v <- git("log", "-1", shQuote(paste0("--format=%(trailers:key=", key, ",valueonly)")), sha)
  trimws(v[nzchar(trimws(v))])
}
has <- function(name) file.exists(file.path(folder, name))

shas <- git("rev-list", "--no-merges", "--reverse", "HEAD", "--", ".")
commits <- lapply(shas, function(sha) list(
  sha = sha,
  files = basename(git("show", "--name-only", "--format=", sha, "--", ".")),
  assisted = trailer(sha, "Assisted-by"),
  human = length(trailer(sha, "Human-authored")) > 0,
  session = trailer(sha, "Regent-Session"),
  prompts = sum(grepl("^- [0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{3}-", git("log", "-1", "--format=%B", sha)))
))
touching <- function(name) Filter(function(c) name %in% c$files, commits)
models <- function(cs) {
  m <- unique(unlist(lapply(cs, function(c) sub("^Claude ", "", c$assisted))))
  m[nzchar(m)]
}
who <- function(cs) {
  a <- length(models(cs)) > 0
  h <- any(vapply(cs, function(c) c$human, logical(1)))
  if (a && h) "beide" else if (a) "agent" else if (h) "mir" else "niemand"
}
with_model <- function(label, cs) {
  m <- models(cs)
  if (length(m)) paste0(label, " (", paste(m, collapse = ", "), ")") else label
}

all_models <- models(commits)
lines <- character(0)
add <- function(x) lines <<- c(lines, x)

if (length(all_models) == 0) {
  add("Diese Ausgabe ist ganz von Hand entstanden, ohne Agent.")
  add(paste0("Spuren: ", length(commits), " Commits von mir."))
} else {
  # Rohentwurf
  if (has("rohentwurf.md")) {
    cs <- touching("rohentwurf.md")
    head_lines <- readLines(file.path(folder, "rohentwurf.md"), n = 5, warn = FALSE)
    spoken <- any(grepl("Sprachnachricht|gesprochen", head_lines, ignore.case = TRUE))
    if (length(cs) == 0) add("Rohentwurf: noch nicht committet")
    else if (who(cs) %in% c("mir", "beide")) add(paste0("Rohentwurf: von mir", if (spoken) ", gesprochen" else ""))
    else add(with_model("Rohentwurf: Agent", cs))
  }
  # Recherche
  if (has("recherche.md")) {
    cs <- touching("recherche.md")
    add(if (who(cs) == "mir") "Recherche: von mir" else with_model("Recherche: Agent", cs))
  }
  # Gliederung
  if (has("gliederung.md")) add(with_model("Gliederung: Skill stimme", touching("gliederung.md")))
  # Text: always named
  text <- readLines(file.path(folder, "index.qmd"), warn = FALSE)
  if (length(text) && text[1] == "---") { end <- which(text == "---")[2]; if (!is.na(end)) text <- text[-seq_len(end)] }
  text <- gsub("<!--.*?-->", "", paste(text, collapse = "\n"))
  text <- gsub("(?m)^\\*Reihe:.*$", "", text, perl = TRUE)
  words <- length(strsplit(trimws(gsub("\\s+", " ", gsub("(?m)^#.*$", "", text, perl = TRUE))), " ")[[1]])
  cs <- touching("index.qmd")
  text_line <- if (words < 50) "Text: noch nicht geschrieben"
    else switch(who(cs), mir = "Text: von mir", beide = "Text: von mir, geprüft vom Skill",
                agent = with_model("Text: Agent", cs), "Text: noch kein Commit")
  if (has("entwurf-skill.md")) text_line <- paste0(text_line, "; ein Testentwurf des Skills liegt daneben")
  add(text_line)
  if (has("pruefung-stimme.md")) add(with_model("Stil: Skill stimme", touching("pruefung-stimme.md")))
  # Prüfung
  if (has("pruefbericht.md")) {
    b <- readLines(file.path(folder, "pruefbericht.md"), warn = FALSE)
    u <- which(grepl("^## Urteil", b))
    urteil <- if (length(u)) { after <- b[(u[1] + 1):length(b)]; trimws(after[nzchar(trimws(after))][1]) } else NA
    # keep the verdict short: the part before the first colon, the details stay in the report
    if (!is.na(urteil) && nchar(urteil) > 60) urteil <- sub(":.*$", "", urteil)
    add(paste0("Prüfung: Skill pruefung, Urteil: ", if (is.na(urteil)) "ohne Urteil" else urteil))
  }
  if (has("grafiken.md")) add("Grafiken: aus Code (Skill grafiken)")
  if (has("verbreitung.md")) add("Posts: Skill verbreitung")
  add(paste0("Modelle: ", paste(all_models, collapse = ", ")))
  n_prompts <- sum(vapply(commits, function(c) c$prompts, numeric(1)))
  if (n_prompts > 0) add(paste0("Prompts: ", n_prompts, " archiviert"))
  n_sessions <- length(unique(unlist(lapply(commits, function(c) c$session))))
  if (n_sessions > 0) add(paste0("Sitzungen: ", n_sessions))
}

block <- paste0("- ", lines)
cat(block, sep = "\n")

if (schreiben) {
  path <- file.path(folder, "index.qmd")
  q <- readLines(path, warn = FALSE)
  s <- which(q == "<!-- offenlegung:start -->"); e <- which(q == "<!-- offenlegung:end -->")
  if (length(s) == 1 && length(e) == 1 && e > s) {
    q <- c(q[1:s], block, q[e:length(q)])
  } else {
    h <- which(grepl("^## So ist diese Ausgabe entstanden", q))
    if (length(h) != 1) stop("Heading 'So ist diese Ausgabe entstanden' not found in index.qmd", call. = FALSE)
    i <- h
    # keep the template comment that follows the heading
    j <- h + 1; while (j <= length(q) && !nzchar(trimws(q[j]))) j <- j + 1
    if (j <= length(q) && startsWith(trimws(q[j]), "<!--")) { while (j <= length(q) && !grepl("-->", q[j])) j <- j + 1; i <- j }
    q <- c(q[1:i], "", "<!-- offenlegung:start -->", block, "<!-- offenlegung:end -->", q[(i + 1):length(q)])
  }
  writeLines(q, path)
  message("Block written into ", path)
}
