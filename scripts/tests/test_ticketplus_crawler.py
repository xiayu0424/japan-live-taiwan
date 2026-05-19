import json
import unittest
from pathlib import Path

from scripts.crawlers.ticketplus import TicketplusCrawler

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "ticketplus"


class FixtureTicketplusCrawler(TicketplusCrawler):
    def __init__(self, source: dict, payloads: dict[str, dict]) -> None:
        super().__init__(source)
        self.payloads = payloads
        self.requested_paths: list[str] = []

    def _get_json(self, path: str) -> dict:
        self.requested_paths.append(path)
        payload = self.payloads.get(path)
        if payload is None:
            raise AssertionError(f"Missing fixture for {path}")
        return payload


class TicketplusCrawlerTest(unittest.TestCase):
    def setUp(self):
        payloads = {
            "main/mainEvents.json": self._load_fixture("mainEvents.json"),
            "event/eve2026/event.json": self._load_fixture("event_eve2026.json"),
            "event/eve2026/sessions.json": self._load_fixture("sessions_eve2026.json"),
            "event/milet2026/event.json": self._load_fixture("event_milet2026.json"),
            "event/milet2026/sessions.json": self._load_fixture("sessions_milet2026.json"),
            "event/milet2026/products.json": self._load_fixture("products_milet2026.json"),
        }
        self.crawler = FixtureTicketplusCrawler(
            {
                "id": "ticketplus",
                "name": "Ticket Plus",
                "crawler": "ticketplus",
                "max_events": 20,
                "request_timeout_seconds": 15,
            },
            payloads,
        )

    def test_crawl_builds_candidates_from_sessions_and_product_fallback(self):
        candidates = self.crawler.crawl()

        self.assertEqual(len(candidates), 3)
        self.assertEqual(
            [candidate["candidate_id"] for candidate in candidates],
            [
                "ticketplus:eve2026:s01",
                "ticketplus:eve2026:s02",
                "ticketplus:milet2026:main",
            ],
        )
        self.assertEqual(candidates[0]["shows"][0]["city"], "Taipei")
        self.assertEqual(candidates[0]["ticket_sales"][0]["status"], "on_sale")
        self.assertEqual(candidates[0]["prices"][0]["price"], 2800)
        self.assertEqual(candidates[2]["prices"][0]["label"], "全區站席")
        self.assertEqual(candidates[2]["prices"][0]["price"], 2200)
        self.assertEqual(candidates[2]["ticket_sales"][0]["status"], "sale_soon")

    def test_crawl_skips_hidden_events_before_detail_fetch(self):
        self.crawler.crawl()

        self.assertNotIn("event/hidden2026/event.json", self.crawler.requested_paths)
        self.assertNotIn("event/hidden2026/sessions.json", self.crawler.requested_paths)

    def _load_fixture(self, name: str) -> dict:
        return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
