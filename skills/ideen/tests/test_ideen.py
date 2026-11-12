"""Tests for ideen.py. Run with: python3 -m unittest discover skills/ideen/tests

The fixtures are an invented archive.db in a temp folder and an empty
repository folder. Real ideas live in the private repository and never
come into this public one.
"""
import pathlib
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import ideen  # noqa: E402

ROOM = "!raum:example.org"
WHEN = "2026-11-08"


def make_db(path):
    con = sqlite3.connect(str(path))
    con.executescript("""
        CREATE TABLE chat_messages (id INTEGER PRIMARY KEY, event_id TEXT UNIQUE NOT NULL,
            room_id TEXT, sent_at TEXT, msgtype TEXT, body TEXT, media_path TEXT,
            replaces TEXT, processed INTEGER DEFAULT 0);
        CREATE TABLE voice_notes (id INTEGER PRIMARY KEY, recorded_at TEXT, duration REAL,
            transcript TEXT, audio_path TEXT, processed INTEGER DEFAULT 0, title TEXT);
    """)
    rows = [
        (1, "$a", ROOM, "2026-11-06T11:57:10+01:00", "m.text", "Newsletter: naming things. When a tool is called X", None, None, 0),
        (2, "$b", ROOM, "2026-11-05T18:20:10+01:00", "m.image", "Newsletter: 100% Schokolade ", "/media/a.jpeg", None, 0),
        (3, "$c", ROOM, "2026-11-07T20:13:59+01:00", "m.audio", "voice-message-recording.ogg", "/media/b.ogg", None, 0),
        (4, "$d", "!anderer:example.org", "2026-11-07T20:17:33+01:00", "m.text", "Newsletter: nicht dieser Raum", None, None, 0),
        (5, "$e", ROOM, "2026-11-01T10:00:00+01:00", "m.text", "schon verarbeitet", None, None, 1),
    ]
    con.executemany("INSERT INTO chat_messages VALUES (?,?,?,?,?,?,?,?,?)", rows)
    con.commit()
    con.close()


def fake_transcriber(con, media_path, sent_at, language):
    con.execute("INSERT INTO voice_notes (recorded_at, duration, transcript, audio_path, processed)"
                " VALUES (?, 3.0, ?, ?, 0)", (sent_at, "Eine gesprochene Idee über Daten.", media_path))
    con.commit()


class IdeenTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self.tmp.name) / "newsletter"
        self.repo.mkdir()
        self.db = pathlib.Path(self.tmp.name) / "archive.db"
        make_db(self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def processed(self, table="chat_messages"):
        con = sqlite3.connect(str(self.db))
        rows = dict(con.execute(f"SELECT id, processed FROM {table}").fetchall())
        con.close()
        return rows

    def test_slug_and_titel(self):
        self.assertEqual(ideen.slug("Und was machst du mit deinem Effizienzgewinn?"), "und-was-machst-du-mit")
        self.assertEqual(ideen.slug("Ärger über Grösse"), "aerger-ueber-groesse")
        self.assertEqual(ideen.slug("!!!"), "idee")
        self.assertEqual(ideen.titel("naming things. When a tool is called X, how"), "naming things. When a tool is")

    def test_eingang_files_text_photo_and_audio_rows(self):
        done = ideen.eingang(self.db, self.repo, ROOM, transcriber=fake_transcriber, when=WHEN)
        self.assertEqual([d["id"] for d in done], [2, 1, 3])  # oldest first
        files = sorted(p.name for p in (self.repo / "_ideen").glob("*.md"))
        self.assertEqual(files, ["2026-11-05-100-schokolade.md", "2026-11-06-naming-things-when-a-tool.md",
                                 "2026-11-07-eine-gesprochene-idee-ueber-daten.md"])
        photo = ideen.read_idea(self.repo / "_ideen" / "2026-11-05-100-schokolade.md")
        self.assertEqual(photo["meta"]["form"], "foto")
        self.assertEqual(photo["meta"]["medien"], "/media/a.jpeg")
        self.assertEqual(photo["meta"]["quelle"], "archive.db:chat_messages/2")
        self.assertEqual(photo["text"], "100% Schokolade")  # prefix gone
        audio = ideen.read_idea(self.repo / "_ideen" / "2026-11-07-eine-gesprochene-idee-ueber-daten.md")
        self.assertEqual(audio["meta"]["form"], "gesprochen")
        self.assertEqual(audio["meta"]["quelle"], "archive.db:chat_messages/3, archive.db:voice_notes/1")
        self.assertEqual(audio["status"], "neu")
        self.assertEqual(audio["verlauf"], [f"- {WHEN}: abgelegt aus dem Raum, archive.db:chat_messages/3, archive.db:voice_notes/1"])
        self.assertEqual(self.processed(), {1: 1, 2: 1, 3: 1, 4: 0, 5: 1})
        self.assertEqual(self.processed("voice_notes"), {1: 1})

    def test_eingang_ids_filter_and_dry_run(self):
        done = ideen.eingang(self.db, self.repo, ROOM, ids=[1], dry_run=True, when=WHEN)
        self.assertEqual(len(done), 1)
        self.assertTrue(done[0]["dry_run"])
        self.assertFalse((self.repo / "_ideen").exists())
        self.assertEqual(self.processed()[1], 0)
        done = ideen.eingang(self.db, self.repo, ROOM, ids=[1], when=WHEN)
        self.assertEqual([d["id"] for d in done], [1])
        self.assertEqual(self.processed(), {1: 1, 2: 0, 3: 0, 4: 0, 5: 1})

    def test_edit_row_replaces_the_text(self):
        ideen.eingang(self.db, self.repo, ROOM, ids=[1], when=WHEN)
        con = sqlite3.connect(str(self.db))
        con.execute("INSERT INTO chat_messages VALUES (6, '$f', ?, '2026-11-06T12:00:00+01:00', 'm.text',"
                    " 'Newsletter: naming things, corrected', NULL, '$a', 0)", (ROOM,))
        con.commit()
        con.close()
        done = ideen.eingang(self.db, self.repo, ROOM, ids=[6], when=WHEN)
        self.assertEqual(done[0]["file"], "2026-11-06-naming-things-when-a-tool.md")
        idea = ideen.read_idea(self.repo / "_ideen" / done[0]["file"])
        self.assertEqual(idea["text"], "naming things, corrected")
        self.assertEqual(len(idea["verlauf"]), 2)
        self.assertEqual(len(list((self.repo / "_ideen").glob("*.md"))), 1)

    def test_liste_orders_by_status_then_date(self):
        ideen.notiz(self.repo, "Alte Idee", "para", "Text", datum="2026-10-18", when=WHEN)
        ideen.notiz(self.repo, "Neue Idee", "para", "Text", datum="2026-11-07", when=WHEN)
        ideen.notiz(self.repo, "Verworfene Idee", "para", "Text", datum="2026-11-08", when=WHEN)
        ideen.set_status(self.repo, "2026-11-08-verworfene-idee.md", "verworfen", text="passt nicht", when=WHEN)
        names = [i["file"] for i in ideen.liste(self.repo)]
        self.assertEqual(names, ["2026-11-07-neue-idee.md", "2026-10-18-alte-idee.md", "2026-11-08-verworfene-idee.md"])

    def test_status_appends_verlauf_and_keeps_the_text(self):
        path = ideen.notiz(self.repo, "Spiele und Arbeit", "archive.db:voice_notes/96", "Warum ich Spiele mag.\n\nZweiter Absatz.",
                           datum="2026-11-01", form="gesprochen", when=WHEN)
        ideen.set_status(self.repo, path.name, "besprochen", text="Behauptung: Arbeit kann sich wie Spiel anfühlen", when="2026-11-09")
        idea = ideen.read_idea(path)
        self.assertEqual(idea["status"], "besprochen")
        self.assertEqual(idea["text"], "Warum ich Spiele mag.\n\nZweiter Absatz.")
        self.assertEqual(idea["verlauf"][-1], "- 2026-11-09: besprochen, Behauptung: Arbeit kann sich wie Spiel anfühlen")
        with self.assertRaises(ValueError):
            ideen.set_status(self.repo, path.name, "fertig")
        with self.assertRaises(FileNotFoundError):
            ideen.set_status(self.repo, "gibt-es-nicht.md", "neu")

    def test_rohentwurf_writes_the_draft_and_marks_the_idea(self):
        path = ideen.notiz(self.repo, "Effizienzgewinn", "archive.db:chat_messages/84", "Und was machst du damit?",
                           datum="2026-11-07", when=WHEN)
        target = ideen.rohentwurf(self.repo, path.name, "effizienzgewinn", "Was machst du mit der gewonnenen Zeit?",
                                  "- Die eine Behauptung\n- Zur Einsicht\n", datum="2026-11-09", when="2026-11-09")
        self.assertEqual(target, self.repo / "_entwuerfe" / "2026-11-09-effizienzgewinn.md")
        meta, body = ideen.split_frontmatter(target.read_text(encoding="utf-8"))
        self.assertEqual(meta, {"datum": "2026-11-09", "form": "besprochen", "ausgabe": "Was machst du mit der gewonnenen Zeit?",
                                "idee": "_ideen/2026-11-07-effizienzgewinn.md"})
        self.assertEqual(body, "- Die eine Behauptung\n- Zur Einsicht\n")
        idea = ideen.read_idea(path)
        self.assertEqual(idea["status"], "gewählt")
        self.assertEqual(idea["meta"]["entwurf"], "_entwuerfe/2026-11-09-effizienzgewinn.md")
        with self.assertRaises(FileExistsError):
            ideen.rohentwurf(self.repo, path.name, "effizienzgewinn", "x", "- a", datum="2026-11-09")
        with self.assertRaises(ValueError):
            ideen.rohentwurf(self.repo, path.name, "Kein Kurzname", "x", "- a")

    def test_unique_path_suffixes_a_second_idea_with_the_same_name(self):
        a = ideen.notiz(self.repo, "Gleicher Titel", "q", "eins", datum="2026-11-08", when=WHEN)
        b = ideen.notiz(self.repo, "Gleicher Titel", "q", "zwei", datum="2026-11-08", when=WHEN)
        self.assertEqual((a.name, b.name), ("2026-11-08-gleicher-titel.md", "2026-11-08-gleicher-titel-2.md"))


if __name__ == "__main__":
    unittest.main()
