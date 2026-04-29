import unittest

from scripts.crawler_utils.dedupe import mark_duplicates
from scripts.crawler_utils.match_artist import match_artists
from scripts.crawler_utils.normalize import normalize_text, slugify


class CrawlerUtilsTest(unittest.TestCase):
    def test_normalize_text(self):
        self.assertEqual(normalize_text("LiSA： Taipei Live！"), "lisataipeilive")
        self.assertEqual(slugify("LiSA Taipei Live!"), "lisa-taipei-live")

    def test_match_artists_by_alias(self):
        candidate = {"title": "LiSA LiVE is Smile Always in Taipei"}
        artists = [{"id": "lisa", "name": "LiSA", "aliases": ["LiSA"]}]

        result = match_artists(candidate, artists)

        self.assertEqual(result["matched_artist_ids"], ["lisa"])
        self.assertEqual(result["match_confidence"], 100)

    def test_mark_duplicates(self):
        candidates = [
            {
                "matched_artist_ids": ["lisa"],
                "shows": [{"date": "2026-06-19", "venue_name": "台北小巨蛋"}],
                "crawler_meta": {},
            }
        ]
        events = [
            {
                "id": "lisa-live-is-smile-always-15-2026-taipei",
                "artist_ids": ["lisa"],
                "shows": [{"date": "2026-06-19", "venue_name": "台北小巨蛋"}],
            }
        ]

        result = mark_duplicates(candidates, events)

        self.assertTrue(result[0]["crawler_meta"]["is_duplicate"])
        self.assertEqual(
            result[0]["crawler_meta"]["duplicate_event_id"],
            "lisa-live-is-smile-always-15-2026-taipei",
        )


if __name__ == "__main__":
    unittest.main()
