import unittest

from scripts.crawler_utils.dedupe import mark_duplicates, split_candidates_and_change_requests
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

    def test_split_candidates_and_change_requests(self):
        candidates = [
            {
                "candidate_id": "ticketplus:e1:s1",
                "source_platform": "ticketplus",
                "source_url": "https://ticketplus.com.tw/activity/e1",
                "title": "LiSA LiVE is Smile Always 2026 in Taipei",
                "matched_artist_ids": ["lisa"],
                "shows": [{"date": "2026-06-19", "venue_name": "台北小巨蛋"}],
                "ticket_sales": [
                    {
                        "type": "general",
                        "platform": "ticketplus",
                        "sale_start": None,
                        "sale_end": None,
                        "ticket_url": "https://ticketplus.com.tw/activity/e1",
                        "status": "on_sale",
                    }
                ],
                "prices": [{"label": "A區", "price": 5280, "currency": "TWD"}],
                "organizers": ["Welcome Music"],
                "crawler_meta": {"raw_hash": "sha256-abcdef123456", "is_duplicate": False, "duplicate_event_id": None},
            },
            {
                "candidate_id": "ticketplus:e2:s2",
                "source_platform": "ticketplus",
                "source_url": "https://ticketplus.com.tw/activity/e2",
                "title": "LiSA LiVE is Smile Always 2026 in Taipei",
                "matched_artist_ids": ["lisa"],
                "shows": [{"date": "2026-06-20", "venue_name": "台北小巨蛋"}],
                "ticket_sales": [
                    {
                        "type": "general",
                        "platform": "ticketplus",
                        "sale_start": None,
                        "sale_end": None,
                        "ticket_url": "https://ticketplus.com.tw/activity/e2",
                        "status": "sale_soon",
                    }
                ],
                "prices": [{"label": "A區", "price": 5280, "currency": "TWD"}],
                "organizers": ["Welcome Music"],
                "crawler_meta": {"raw_hash": "sha256-fedcba654321", "is_duplicate": False, "duplicate_event_id": None},
            },
        ]
        events = [
            {
                "id": "lisa-live-is-smile-always-15-2026-taipei",
                "title": "LiSA LiVE is Smile Always 2026 in Taipei",
                "artist_ids": ["lisa"],
                "status": "sale_soon",
                "shows": [{"date": "2026-06-19", "venue_name": "台北小巨蛋"}],
                "ticket_sales": [],
                "prices": [],
                "organizers": ["Welcome Music"],
            }
        ]

        fresh_candidates, change_requests = split_candidates_and_change_requests(candidates, events)

        self.assertEqual(fresh_candidates, [])
        self.assertEqual(len(change_requests), 2)
        self.assertEqual(change_requests[0]["detected_changes"]["match_type"], "possible_update")
        self.assertEqual(change_requests[1]["detected_changes"]["match_type"], "possible_additional_show")
        self.assertEqual(
            change_requests[1]["detected_changes"]["differences"]["new_shows"][0]["date"],
            "2026-06-20",
        )


if __name__ == "__main__":
    unittest.main()
