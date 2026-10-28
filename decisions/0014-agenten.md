# 0014 Agenten

- Frage: Wie sind die Agenten der Pipeline organisiert?
- Optionen: ein Skill pro Stufe mit einem schlanken Runner; ein Skill pro Stufe, am Anfang von Hand aufgerufen; ein Agent für die ganze Pipeline.
- Wahl: ein Skill pro Stufe, und der Runner kommt gleich mit. Der Runner ruft die Skills nacheinander auf, pingt mich nach jeder Stufe in Element an und wartet auf mein Ja. Jeder Skill arbeitet aus seiner Crew Rolle (concept.md, Breite).
- Warum: Die Prüfpunkte und die Rollen pro Stufe lassen sich mit einem Skill pro Stufe durchsetzen, mit einem grossen Agenten nicht. Der Runner von Anfang an, damit die Prüfpunkte vom ersten Probelauf an so laufen, wie sie später laufen sollen. Wann ein Prüfpunkt ohne mein Ja laufen darf, steht in concept.md.
- Datum: 2026-10-17
