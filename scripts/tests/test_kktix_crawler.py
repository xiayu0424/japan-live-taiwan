import unittest
from pathlib import Path

from scripts.crawlers.kktix import KktixCrawler

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "kktix"


class KktixCrawlerTest(unittest.TestCase):
    def setUp(self):
        self.crawler = KktixCrawler(
            {
                "id": "kktix",
                "name": "KKTIX",
                "crawler": "kktix",
                "base_url": "https://kktix.com",
                "list_urls": ["https://kktix.com/events"],
                "max_events": 20,
                "request_timeout_seconds": 15,
            }
        )

    def test_extract_event_links(self):
        html = (FIXTURE_DIR / "list.html").read_text(encoding="utf-8")

        links = self.crawler.extract_event_links(html, "https://kktix.com/events")

        self.assertEqual(
            links,
            [
                "https://kktix.com/events/lisa-2026",
                "https://kktix.com/events/hikari-loop-2026",
                "https://kktix.com/events/lisa-2026",
                "https://kktix.com/events/online-show-2026",
            ],
        )

    def test_parse_event_detail_builds_valid_candidate(self):
        html = (FIXTURE_DIR / "detail_complete.html").read_text(encoding="utf-8")

        candidate = self.crawler.parse_event_detail(
            html,
            "https://kktix.com/events/lisa-2026",
            "2026-05-11T12:00:00+08:00",
        )

        self.assertIsNotNone(candidate)
        self.assertEqual(candidate["candidate_id"], "kktix-2026-06-19-lisa-live-is-smile-always-2026-in-taipei")
        self.assertEqual(candidate["shows"][0]["city"], "Taipei")
        self.assertEqual(candidate["shows"][0]["venue_name"], "台北小巨蛋")
        self.assertEqual(candidate["ticket_sales"][0]["status"], "on_sale")
        self.assertEqual(candidate["event_type"], "concert")
        self.assertEqual(candidate["organizers"], ["Welcome Music"])
        self.assertEqual(candidate["prices"][0]["price"], 5280)

    def test_parse_event_detail_keeps_empty_prices_and_live_house_type(self):
        html = (FIXTURE_DIR / "detail_no_price_live_house.html").read_text(encoding="utf-8")

        candidate = self.crawler.parse_event_detail(
            html,
            "https://kktix.com/events/hikari-loop-2026",
            "2026-05-11T12:00:00+08:00",
        )

        self.assertIsNotNone(candidate)
        self.assertEqual(candidate["prices"], [])
        self.assertEqual(candidate["ticket_sales"][0]["status"], "sale_soon")
        self.assertEqual(candidate["event_type"], "live_house")

    def test_parse_event_detail_skips_online_event(self):
        html = (FIXTURE_DIR / "detail_online.html").read_text(encoding="utf-8")

        candidate = self.crawler.parse_event_detail(
            html,
            "https://kktix.com/events/online-show-2026",
            "2026-05-11T12:00:00+08:00",
        )

        self.assertIsNone(candidate)


if __name__ == "__main__":
    unittest.main()
