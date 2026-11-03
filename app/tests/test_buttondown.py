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

    def test_local_images(self):
        body = "![a](index_files/x.png) ![b](https://cdn/y.png)"
        self.assertEqual(buttondown.local_images(body), ["index_files/x.png"])


if __name__ == "__main__":
    unittest.main()
