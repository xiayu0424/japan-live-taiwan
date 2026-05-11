"""Deterministic mock crawler for validating the candidate pipeline."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from scripts.crawler_utils.normalize import slugify
from scripts.crawlers.base import BaseCrawler


class MockCrawler(BaseCrawler):
    def crawl(self) -> list[dict]:
        retrieved_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
        raw_candidates = [
            {
                "title": "LiSA LiVE is Smile Always～15～ in Taipei",
                "date": "2026-06-19",
                "start_time": "2026-06-19T19:00:00+08:00",
                "venue_name": "台北小巨蛋",
                "city": "Taipei",
                "ticket_url": "https://example.org/mock/lisa-2026-taipei",
                "price": 5280,
            },
            {
                "title": "Hikari Loop Summer Signal 2026 in Taipei",
                "date": "2026-11-07",
                "start_time": "2026-11-07T19:00:00+08:00",
                "venue_name": "Legacy Taipei",
                "city": "Taipei",
                "ticket_url": "https://example.org/mock/hikari-loop-2026-summer",
                "price": 2400,
            },
            {
                "title": "折坂悠太 Acoustic Night Taipei",
                "date": "2026-12-12",
                "start_time": "2026-12-12T20:00:00+08:00",
                "venue_name": "The Wall Live House",
                "city": "Taipei",
                "ticket_url": "https://example.org/mock/yuta-orisaka-2026-acoustic",
                "price": 1800,
            },
        ]

        return [self._candidate(item, retrieved_at) for item in raw_candidates]

    def _candidate(self, item: dict, retrieved_at: str) -> dict:
        source_url = item["ticket_url"]
        candidate_id = f"mock-{item['date']}-{slugify(item['title'])}"
        raw_hash = "sha256-" + hashlib.sha256(
            f"{source_url}|{item['title']}|{item['date']}".encode("utf-8")
        ).hexdigest()

        return {
            "candidate_id": candidate_id,
            "source_platform": "mock",
            "source_url": source_url,
            "title": item["title"],
            "raw_title": item["title"],
            "matched_artist_ids": [],
            "matched_artist_names": [],
            "match_confidence": 0,
            "event_type": "concert",
            "status": "candidate",
            "shows": [
                {
                    "raw_date_text": f"{item['date']} {item['start_time'][11:16]}",
                    "date": item["date"],
                    "start_time": item["start_time"],
                    "city": item["city"],
                    "venue_name": item["venue_name"],
                    "address": None,
                }
            ],
            "ticket_sales": [
                {
                    "type": "general",
                    "platform": "Mock",
                    "sale_start": None,
                    "sale_end": None,
                    "ticket_url": source_url,
                    "status": "unknown",
                    "raw_sale_text": None,
                }
            ],
            "prices": [{"label": "一般票", "price": item["price"], "currency": "TWD"}],
            "organizers": ["Mock Source"],
            "sources": [
                {
                    "type": "official_ticket",
                    "name": "Mock crawler",
                    "url": source_url,
                    "retrieved_at": retrieved_at,
                }
            ],
            "crawler_meta": {
                "crawler_name": "mock",
                "retrieved_at": retrieved_at,
                "raw_hash": raw_hash,
                "is_duplicate": False,
                "duplicate_event_id": None,
                "review_status": "pending",
                "review_note": None,
            },
        }
