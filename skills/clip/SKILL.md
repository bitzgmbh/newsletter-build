---
name: clip
disable-model-invocation: true
description: >-
  Copy text to the macOS clipboard ready to paste into an email or form.
  Use when the user says "copy to clipboard", "clip it" or invokes /clip
  on a draft from the conversation.
---

# clip

Copy the named text (default: the last draft in the conversation) to the clipboard with `pbcopy`.

- One line per paragraph: no hard wraps inside a paragraph.
- One empty line between paragraphs; keep short lines that belong apart (greeting, sign-off and name) on their own lines.
- Strip markdown: quote markers (`> `), bold, italics, list bullets unless the text is a list, code fences.
- No leading or trailing whitespace.

Write with `printf '%s\n' ... | pbcopy`, then confirm in one line what was copied (first few words). Do not print the text again.
