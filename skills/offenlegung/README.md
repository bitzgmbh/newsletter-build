# offenlegung

The disclosure block of an edition, built from the traces (decision 0017).

## Why I use it

Every edition ends with "So ist diese Ausgabe entstanden". I do not want to write that block from memory, because memory flatters. The script reads the commits of the edition folder, their trailers, the prompts archive and the re_gent sessions, and says per stage who did it and with which model. An edition I wrote entirely by hand says exactly that.

## What is in here

- `offenlegung.R`: the script. Prints the block; with `--schreiben` it writes the block into `index.qmd` between two markers.
- `SKILL.md`: when to run it and what it never does.

## Install

Nothing to install beyond R. Run it from the build repository with the path of an edition folder in the private repository.
