# 0034 Entscheiden in Claude Code, die App führt durch die Stufen

- Frage: Wo entscheide ich an den Prüfpunkten, und wie erfahre ich, dass ein Lauf fertig ist?
- Optionen: alles auf der Seite der App (0028); Entscheidungsboxen in Claude Code mit dem Skill redaktion, die App zeigt Stufen und Läufe; für die Nachricht ein Ping in Element, eine Mitteilung von macOS oder keine.
- Wahl: Der Skill redaktion (`/redaktion`, mit oder ohne Ausgabe) liest den Stand und die offenen Punkte über eine JSON Schnittstelle der App, fragt mich in deutschen Boxen mit einer Empfehlung zuerst, schickt mein Urteil an die App und wartet auf den Lauf bis zum nächsten Prüfpunkt. Er entscheidet die Prüfpunkte 4, 5a, 5b, 6, 7, 8 und 11; Freigabe (9) und Buttondown (10) bleiben Knöpfe in der App. Habe ich etwas zu ändern, fragt eine letzte Box "Einarbeiten und weiter" oder "Einarbeiten, dann noch einmal ansehen". Die App zeigt an jedem Prüfpunkt den Befehl zum Kopieren. Der Ping in Element fällt für alle Läufe weg; stattdessen zeigt die App eine Mitteilung von macOS, wenn ein Lauf endet.
- Warum: Meine Worte: "the decision support I get in the terminal is much more natural then what I see in the app." Zum Ping: "the ping in element adds nothing, i won't use it. it can go." Die App bleibt die Karte und das Protokoll der Läufe, damit nichts doppelt gebaut wird.
- Ändert: 0028 (Urteile auch in Claude Code, kein Ping in Element), 0014 (die Prüfpunkte melden sich nicht mehr in Element).
- Datum: 2026-11-03
