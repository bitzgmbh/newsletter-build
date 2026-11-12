# Build the block "Offengelegt" of an edition from its traces: the commits of
# the edition folder, their trailers (Assisted-by, Human-authored), the files
# each stage left behind, and the confirmed sentences in offenlegung.md.
# Decisions 0017 and 0040. The block says in plain words who wrote the text,
# what Claude Code did, who decided, and links to disclosure.md.
#
# Usage: Rscript skills/offenlegung/offenlegung.R <edition folder> [--en] [--schreiben]
# Prints the block. With --schreiben it also writes the block into index.qmd
# (with --en into index-en.qmd) between the markers
# <!-- offenlegung:start --> and <!-- offenlegung:end -->.
#
# offenlegung.md (offenlegung-en.md with --en) holds the sentences no trace
# gives on its own, one per line as "Key: sentence". Claude Code drafts them
# from pruefpunkte.md and the commit messages of the edition, Lars confirms
# them. A sentence replaces the default of its key or adds a line the traces
# do not have. Keys: Text, Recherchiert, Gegliedert, Geprüft, Vorgeschlagen,
# Gebaut, Übersetzt, Verbreitet, Rückmeldung (English: Text, Researched,
# Outlined, Checked, Proposed, Built, Translated, Shared, Feedback).

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) stop("Usage: offenlegung.R <edition folder> [--en] [--schreiben]", call. = FALSE)
folder <- normalizePath(args[1], mustWork = TRUE)
schreiben <- "--schreiben" %in% args
en <- "--en" %in% args
link <- "https://github.com/bitzgmbh/newsletter-build/blob/main/disclosure.md"

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
# A stage file that only says the stage was skipped ("Entfällt ...", written by hand
# so stand.py moves on, decision 0037) is not a trace of a run.
ran <- function(name) {
  if (!has(name)) return(FALSE)
  l <- readLines(file.path(folder, name), warn = FALSE)
  l <- trimws(l[nzchar(trimws(l)) & !grepl("^#", l)])
  !(length(l) > 0 && grepl("^Entfällt", l[1]))
}

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

# "claude-fable-5-2" becomes "Claude Fable 5.2"; several models of one family
# become "Claude Fable 5.1 und 5.2".
pretty_models <- function(ids, und) {
  ids <- sort(ids)
  m <- regmatches(ids, regexec("^claude-([a-z]+)-([0-9]+)-([0-9]+)", ids))
  ok <- vapply(m, length, integer(1)) == 4
  fam <- ifelse(ok, vapply(m, function(x) if (length(x) == 4) paste0("Claude ", toupper(substr(x[2], 1, 1)), substring(x[2], 2)) else "", ""), ids)
  ver <- ifelse(ok, vapply(m, function(x) if (length(x) == 4) paste0(x[3], ".", x[4]) else "", ""), "")
  join <- function(x) if (length(x) < 2) x else paste0(paste(x[-length(x)], collapse = ", "), " ", und, " ", x[length(x)])
  if (all(ok) && length(unique(fam)) == 1) paste(fam[1], join(unique(ver))) else join(unique(trimws(paste(fam, ver))))
}

# The words of the block, German and English.
W <- if (en) list(
  und = "and", modell = c("model", "models"),
  hand = "This issue was made entirely by hand, without AI.",
  own = "I wrote the text myself.",
  agent = "Claude Code wrote the text from an outline that I confirmed. I read it through.",
  agent_edit = "Claude Code wrote the text from an outline that I confirmed. I read it through and changed it.",
  agent_only = "Claude Code wrote the text.",
  none = "The text is not written yet.",
  lead_own = "After that I worked on it with Claude Code (%s %s):",
  lead_agent = "What else Claude Code did (%s %s):",
  keys = c(text = "Text", recherche = "Researched", gliederung = "Outlined", pruefung = "Checked",
           vorschlag = "Proposed", grafik = "Built", uebersetzung = "Translated", posts = "Shared",
           rueckmeldung = "Feedback"),
  recherche = "sources and numbers on the topic.",
  gliederung = "the outline of the issue, which I confirmed.",
  pruefung = "style, numbers and links, with a written report.",
  grafik = "the chart, from code.",
  ueb = "this English version, which I read through.",
  ueb_edit = "this English version, which I read through and changed.",
  posts = "drafts of the posts about this issue.",
  schluss = "The ideas, the decisions and the final yes are mine.",
  linktext = "This is how I record the use of AI"
) else list(
  und = "und", modell = c("Modell", "Modelle"),
  hand = "Diese Ausgabe ist ganz von Hand entstanden, ohne KI.",
  own = "Den Text habe ich selbst geschrieben.",
  agent = "Den Text hat Claude Code nach einer Gliederung geschrieben, die ich bestätigt habe. Ich habe ihn durchgesehen.",
  agent_edit = "Den Text hat Claude Code nach einer Gliederung geschrieben, die ich bestätigt habe. Ich habe ihn durchgesehen und geändert.",
  agent_only = "Den Text hat Claude Code geschrieben.",
  none = "Der Text ist noch nicht geschrieben.",
  lead_own = "Danach habe ich mit Claude Code daran gearbeitet (%s %s):",
  lead_agent = "Was Claude Code sonst getan hat (%s %s):",
  keys = c(text = "Text", recherche = "Recherchiert", gliederung = "Gegliedert", pruefung = "Geprüft",
           vorschlag = "Vorgeschlagen", grafik = "Gebaut", uebersetzung = "Übersetzt", posts = "Verbreitet",
           rueckmeldung = "Rückmeldung"),
  recherche = "Quellen und Zahlen zum Thema.",
  gliederung = "den Aufbau der Ausgabe, von mir bestätigt.",
  pruefung = "Stil, Zahlen und Links, mit einem Prüfbericht.",
  grafik = "die Grafik, aus Code.",
  ueb = "die englische Fassung, von mir durchgesehen.",
  ueb_edit = "die englische Fassung, von mir durchgesehen und geändert.",
  posts = "Entwürfe für die Posts zur Ausgabe.",
  schluss = "Die Ideen, die Entscheidungen und das letzte Ja sind von mir.",
  linktext = "So halte ich den Einsatz von KI fest"
)

# Confirmed sentences next to the edition.
notes_file <- if (en) "offenlegung-en.md" else "offenlegung.md"
notes <- character(0)
if (has(notes_file)) {
  nl <- paste(readLines(file.path(folder, notes_file), warn = FALSE), collapse = "\n")
  nl <- strsplit(gsub("<!--.*?-->", "", nl), "\n")[[1]]
  for (l in trimws(nl)) {
    m <- regmatches(l, regexec("^(?:- )?\\*{0,2}([^:*#]+?)\\*{0,2}:\\*{0,2}\\s+(.+)$", l, perl = TRUE))[[1]]
    if (length(m) == 3) {
      k <- names(W$keys)[match(m[2], W$keys)]
      if (is.na(k)) stop("Unknown key in ", notes_file, ": ", m[2], call. = FALSE)
      notes[k] <- m[3]
    }
  }
}
note <- function(k, default = NULL) if (k %in% names(notes)) notes[[k]] else default

all_models <- models(commits)
closing <- paste(c(note("rueckmeldung"), W$schluss, paste0("[", W$linktext, "](", link, ").")), collapse = " ")

if (length(all_models) == 0) {
  block <- c(paste(c(note("text"), W$hand), collapse = " "), "", closing)
} else {
  # Who wrote the text. Since decision 0032 the skill stimme writes it at 5b
  # and I review it; since 0037 an edition can also be my own text, reviewed
  # in the chat, and its 5b gate line then says "Text von Lars" or "Text von mir".
  text <- readLines(file.path(folder, "index.qmd"), warn = FALSE)
  if (length(text) && text[1] == "---") { end <- which(text == "---")[2]; if (!is.na(end)) text <- text[-seq_len(end)] }
  text <- gsub("<!--.*?-->", "", paste(text, collapse = "\n"))
  text <- gsub("(?m)^\\*Reihe:.*$", "", text, perl = TRUE)
  words <- length(strsplit(trimws(gsub("\\s+", " ", gsub("(?m)^#.*$", "", text, perl = TRUE))), " ")[[1]])
  cs <- touching("index.qmd")
  pp <- file.path(folder, "pruefpunkte.md")
  gates <- if (file.exists(pp)) readLines(pp, warn = FALSE) else character(0)
  lines_5b <- gates[grepl("Stufe 5b", gates)]
  own_text <- any(grepl("Text von (Lars|mir)", lines_5b))
  agent_text <- length(lines_5b) > 0 && !own_text
  opening <- if (words < 50) W$none
    else if (own_text) W$own
    else if (agent_text) switch(who(cs), beide = W$agent_edit, agent = W$agent, W$own)
    else switch(who(cs), agent = W$agent_only, W$own)
  mine <- identical(opening, W$own)
  opening <- note("text", opening)

  # What Claude Code did, one line per verb, from the files of the stages.
  did <- list()
  if (ran("recherche.md") && who(touching("recherche.md")) != "mir") did$recherche <- W$recherche
  if (ran("gliederung.md")) did$gliederung <- W$gliederung
  if (ran("pruefbericht.md") || has("pruefung-stimme.md")) did$pruefung <- W$pruefung
  if (has("grafiken.md")) did$grafik <- W$grafik
  if (has("index-en.qmd")) {
    w <- who(touching("index-en.qmd"))
    if (w == "beide") did$uebersetzung <- W$ueb_edit else if (w == "agent") did$uebersetzung <- W$ueb
  }
  if (has("verbreitung.md")) did$posts <- W$posts
  order <- c("recherche", "gliederung", "pruefung", "vorschlag", "grafik", "uebersetzung", "posts")
  bullets <- character(0)
  for (k in order) {
    s <- note(k, did[[k]])
    if (!is.null(s)) bullets <- c(bullets, paste0("- **", W$keys[[k]], ":** ", s))
  }
  mod <- sprintf(if (mine) W$lead_own else W$lead_agent,
                 W$modell[if (length(all_models) > 1) 2 else 1], pretty_models(all_models, W$und))
  block <- if (length(bullets)) c(paste(opening, mod), "", bullets, "", closing)
           else c(opening, "", closing)
}

cat(block, sep = "\n")
# For me, not for the block: what the traces hold.
n_assisted <- sum(vapply(commits, function(c) length(c$assisted) > 0, logical(1)))
n_prompts <- sum(vapply(commits, function(c) c$prompts, numeric(1)))
n_sessions <- length(unique(unlist(lapply(commits, function(c) c$session))))
message("Spuren: ", length(commits), " Commits, ", n_assisted, " mit Claude, ", n_prompts,
        " Prompts archiviert, ", n_sessions, " re_gent Sitzungen. Sätze aus ", notes_file, ": ",
        if (length(notes)) paste(W$keys[names(notes)], collapse = ", ") else "keine")

if (schreiben) {
  path <- file.path(folder, if (en) "index-en.qmd" else "index.qmd")
  q <- readLines(path, warn = FALSE)
  s <- which(q == "<!-- offenlegung:start -->"); e <- which(q == "<!-- offenlegung:end -->")
  if (length(s) == 1 && length(e) == 1 && e > s) {
    q <- c(q[1:s], block, q[e:length(q)])
  } else {
    h <- which(grepl("^## Offengelegt", q))
    if (length(h) != 1) stop("Heading 'Offengelegt' not found in ", basename(path), call. = FALSE)
    i <- h
    # keep the template comment that follows the heading
    j <- h + 1; while (j <= length(q) && !nzchar(trimws(q[j]))) j <- j + 1
    if (j <= length(q) && startsWith(trimws(q[j]), "<!--")) { while (j <= length(q) && !grepl("-->", q[j])) j <- j + 1; i <- j }
    rest <- if (i < length(q)) q[(i + 1):length(q)] else character(0)
    q <- c(q[1:i], "", "<!-- offenlegung:start -->", block, "<!-- offenlegung:end -->", rest)
  }
  writeLines(q, path)
  message("Block written into ", path)
}
