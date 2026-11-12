"""Tests for the email conversion. Run with: uv run python -m unittest discover tests"""
import unittest

from redaktion import buttondown


class Convert(unittest.TestCase):
    META = {"title": "Titel", "date": "2026-11-24", "reihe": ""}

    def test_comments_and_shortcodes(self):
        body = "<!-- weg -->\nText {{< var newsletter.abo_url >}}\n"
        out = buttondown.clean_markdown(body, self.META, {"newsletter": {"abo_url": "https://x"}})
        self.assertEqual(out, "Text https://x\n")

    def test_nur_web_dropped_nur_mail_kept(self):
        body = "::: {.nur-mail}\nMail\n:::\n\n::: {.nur-web}\nWeb\n:::\n"
        out = buttondown.clean_markdown(body, self.META, {})
        self.assertIn("Mail", out)
        self.assertNotIn("Web", out)
        self.assertNotIn(":::", out)

    def test_html_divs_from_gfm(self):
        body = '<div class="nur-web">\nWeb\n</div>\n<div class="nur-mail">\nMail\n</div>\n'
        out = buttondown.clean_markdown(body, self.META, {})
        self.assertEqual(out.strip(), "Mail")

    def test_empty_reihe_line_dropped(self):
        out = buttondown.clean_markdown("*Reihe: {{< meta reihe >}}*\n\nText\n", self.META, {})
        self.assertEqual(out, "Text\n")

    def test_commented_chunk_is_not_code(self):
        self.assertFalse(buttondown.has_code("<!--\n```{r}\nplot(1)\n```\n-->\n"))
        self.assertTrue(buttondown.has_code("```{r}\nplot(1)\n```\n"))

    def test_title_block_dropped(self):
        out = buttondown.drop_title_block("# Titel\n\n2026-11-24\n\nText", self.META)
        self.assertEqual(out, "Text")

    def test_todo_fields_block_versand(self):
        problems = buttondown.check_fields({"title": "T", "subtitle": "TODO: Betreff", "description": ""})
        self.assertEqual(len(problems), 2)

    def test_html_img_from_gfm_becomes_markdown(self):
        body = ('<div class="nur-mail">\n<img src="index_files/figure-commonmark/fig-1.png"\n'
                'data-fig-alt="Zwei\nSäulen" alt="Zwei\nSäulen, &quot;geplant&quot; [hell]" />\n</div>\n')
        out = buttondown.clean_markdown(body, {}, {})
        self.assertEqual(out.strip(), '![Zwei Säulen, "geplant" (hell)](index_files/figure-commonmark/fig-1.png)')
        self.assertEqual(buttondown.local_images(out), ["index_files/figure-commonmark/fig-1.png"])

    def test_local_images(self):
        body = "![a](index_files/x.png) ![b](https://cdn/y.png)"
        self.assertEqual(buttondown.local_images(body), ["index_files/x.png"])



class Entwurf(unittest.TestCase):
    META = {"subtitle": "Titel", "description": "Vorschau"}
    GOOD = {"status": "draft", "subject": "Titel", "description": "Vorschau",
            "filters": {"filters": [{"field": "x", "operator": "equals", "value": "y"}], "groups": [], "predicate": "or"},
            "body": "<!-- buttondown-editor-mode: plaintext -->\nEin Absatz in einer Zeile.\n\n![Alt](https://assets.buttondown.email/images/a.png)\n\n- eins\n- zwei\n"}

    def failed(self, d):
        from redaktion import entwurf
        return [label for ok, label in entwurf.checks(d, self.META) if not ok]

    def test_good_draft_passes(self):
        self.assertEqual(self.failed(self.GOOD), [])

    def test_editor_html_and_wrapped_paragraph_fail(self):
        bad = dict(self.GOOD, body="<p>Ein Absatz<br>mit Umbruch</p>")
        self.assertEqual(len(self.failed(bad)), 2)
        wrapped = dict(self.GOOD, body=self.GOOD["body"].replace("in einer Zeile", "in\nzwei Zeilen"))
        self.assertEqual(len(self.failed(wrapped)), 1)

    def test_local_image_and_missing_filter_fail(self):
        bad = dict(self.GOOD, body=self.GOOD["body"].replace("https://assets.buttondown.email/images/a.png", "index_files/a.png"),
                   filters={"filters": [], "groups": [], "predicate": "and"})
        self.assertEqual(len(self.failed(bad)), 2)

    def test_audience_by_language(self):
        from redaktion import entwurf
        de = [f["value"] for f in entwurf.audience(False)["filters"]]
        en = [f["value"] for f in entwurf.audience(True)["filters"]]
        self.assertEqual(de, ["deutsch", "beide-both", ""])
        self.assertEqual(en, ["english", "beide-both", ""])

if __name__ == "__main__":
    unittest.main()
