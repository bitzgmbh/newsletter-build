# 0029 Buttondown Entwurf über die API

- Frage: Wie kommt eine freigegebene Ausgabe nach Buttondown?
- Optionen: wie in 0023 von Hand übertragen; die App legt einen Entwurf an und ich sende in Buttondown; die App plant den Versand; die App sendet sofort.
- Wahl: Die App legt nach der Freigabe einen Entwurf an (Status draft): Betreff aus `subtitle`, Vorschautext aus `description`, der Text als Markdown aus `index.qmd`, die Grafik als statisches Bild. Ich prüfe die Vorschau in Buttondown und drücke dort auf Senden. Der Schlüssel für die API liegt im Schlüsselbund von macOS (Dienst `bitz-buttondown`), nie in einer Datei.
- Warum: Das Kopieren von Hand kostet Zeit und bringt Fehler bei Bildern und Links. Senden bleibt ein Schritt von mir, in der Oberfläche, in der ich die fertige Mail sehe.
- Ändert: 0023 (die Übertragung von Hand fällt weg; das Archiv von Buttondown bleibt die Webansicht).
- Datum: 2026-11-03
