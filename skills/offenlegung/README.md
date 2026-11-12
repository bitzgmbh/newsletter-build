# offenlegung

The disclosure block of an edition, built from the traces (decisions 0017 and 0040).

## Why I use it

Every edition ends with "Offengelegt", the block that shows how it was made (0020). I do not want to write that block from memory, because memory flatters. The script reads the commits of the edition folder, their trailers and the files of the stages, and says in sentences who wrote the text, what Claude Code did, with which model, and who decided. It ends with a link to [disclosure.md](../../disclosure.md). What no trace gives on its own (a proposal made in the chat, people who read the draft) I confirm as a sentence in `offenlegung.md` next to the edition, and the script puts it in. An edition I wrote entirely by hand says exactly that.

## What is in here

- `offenlegung.R`: the script. Prints the block; with `--schreiben` it writes the block into `index.qmd` between two markers, with `--en` the English block into `index-en.qmd`.
- `SKILL.md`: when to run it and what it never does.

## Install

Nothing to install beyond R. Run it from the build repository with the path of an edition folder in the private repository.
