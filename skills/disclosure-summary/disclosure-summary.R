# Summarise how AI was used in a range of commits, read from the
# authorship trailers (Assisted-by: and Human-authored:).
#
# Usage, from the repository root:
#   Rscript skills/disclosure-summary/disclosure-summary.R [base] [head]
# Defaults: base = origin/main, head = HEAD. Merge commits are skipped.
# Prints a Markdown section for the body of a pull request.

args <- commandArgs(trailingOnly = TRUE)
base <- if (length(args) >= 1) args[1] else "origin/main"
head <- if (length(args) >= 2) args[2] else "HEAD"

git <- function(...) {
  out <- suppressWarnings(system2("git", c(...), stdout = TRUE))
  status <- attr(out, "status")
  if (!is.null(status) && status != 0) {
    stop("git ", paste(c(...), collapse = " "), " failed with status ", status, call. = FALSE)
  }
  out
}

shas <- git("rev-list", "--no-merges", "--reverse", paste0(base, "..", head))
if (length(shas) == 0) {
  message("No commits between ", base, " and ", head)
  quit(status = 0)
}

# Read the trailers with Git's own parser, so a line in the message body
# that happens to start with "Assisted-by:" does not count.
has_trailer <- function(sha, key) {
  value <- git("log", "-1", shQuote(paste0("--format=%(trailers:key=", key, ",valueonly)")), sha)
  any(nzchar(trimws(value)))
}

category <- function(sha) {
  assisted <- has_trailer(sha, "Assisted-by")
  human <- has_trailer(sha, "Human-authored")
  if (assisted && human) "Mixed"
  else if (assisted) "Claude-assisted"
  else if (human) "Human-authored"
  else "Unmarked"
}

# Lines added and removed; binary files count as zero lines.
line_counts <- function(sha) {
  stat <- git("show", "--numstat", "--format=", sha)
  stat <- stat[nzchar(stat)]
  if (length(stat) == 0) return(c(added = 0, removed = 0))
  parts <- strsplit(stat, "\t")
  to_num <- function(x) suppressWarnings(as.numeric(x))
  added <- sum(vapply(parts, function(p) to_num(p[1]), numeric(1)), na.rm = TRUE)
  removed <- sum(vapply(parts, function(p) to_num(p[2]), numeric(1)), na.rm = TRUE)
  c(added = added, removed = removed)
}

commits <- data.frame(
  sha = shas,
  category = vapply(shas, category, character(1)),
  t(vapply(shas, line_counts, numeric(2))),
  row.names = NULL
)

# Absolute link, because relative links in a pull request body break on
# the Files tab.
remote <- git("remote", "get-url", "origin")
repo_url <- sub("\\.git$", "", sub("^git@github\\.com:", "https://github.com/", remote))

levels <- c("Claude-assisted", "Human-authored", "Mixed", "Unmarked")
rows <- lapply(levels, function(l) {
  sub <- commits[commits$category == l, ]
  c(l, nrow(sub), sum(sub$added), sum(sub$removed))
})
rows <- rows[vapply(rows, function(r) r[2] != "0", logical(1))]
rows[[length(rows) + 1]] <- c("Total", nrow(commits), sum(commits$added), sum(commits$removed))

cat("## How AI was used\n\n")
cat("| | Commits | Lines added | Lines removed |\n")
cat("|---|---:|---:|---:|\n")
for (r in rows) cat("|", paste(r, collapse = " | "), "|\n")
cat("\nCounted from the commit trailers `Assisted-by:` and `Human-authored:`. ")
cat("A commit with both is mixed. Unmarked commits carry neither. ")
cat("See [disclosure.md](", repo_url, "/blob/main/disclosure.md) for how AI use is recorded.\n", sep = "")
