# 0028 Redaktion, eine App vor der Pipeline

- Frage: Wo sehe ich, wo jede Ausgabe steht, und wo gebe ich mein Ja nach einer Stufe?
- Optionen: weiter mit Slash Befehlen und Element; eine kleine eigene App auf meinem Mac; Inkwell aus larnsce/mimeo abspecken; Bram von Jon Udell.
- Wahl: Eine kleine eigene App in `app/`, nur lokal auf meinem Mac und nur für mich, mit deutschen Seiten. Sie zeigt Entwürfe und Ausgaben nach Stufe, ich gebe mein Urteil dort neben der Ausgabe der Stufe, und sie startet den Runner headless mit diesem Urteil. Element bekommt weiter eine kurze Nachricht mit einem Link zur Seite der Ausgabe. Die Freigabe (Stufe 9) ist ein Knopf in der App: Offenlegung schreiben, Prüfpunkt eintragen, `main` auf `dev` vorziehen, beide pushen. Den Text (5b) schreibe ich weiter in meinem Editor.
- Warum: Der Stand einer Ausgabe lag an drei Orten (Dateien, `pruefpunkte.md`, Issue). Von Inkwell übernehme ich nur das Muster: Dateien im Repository sind das Protokoll, Agenten entwerfen, nur ich gebe frei, jede Freigabe steht im Protokoll. Der Versand, die Flows und die Kontakte von Inkwell machen Buttondown schon. Bram deckt die Läufe mit Agenten ab, kennt aber keine Stufen, keine Freigabe und kein Buttondown.
- Ändert: 0014 (das Urteil kommt aus der App, Element bleibt als Hinweis und als Rückweg).
- Datum: 2026-11-03
