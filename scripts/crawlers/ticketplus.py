"""Ticket Plus crawler backed by anonymous public JSON endpoints."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime, timedelta, timezone
from html import unescape
from typing import Any

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from scripts.crawler_utils.normalize import normalize_text, slugify
from scripts.crawlers.base import BaseCrawler

SALE_TIME_RE = re.compile(
    r"(?:售票時間|啟售時間|開賣時間)[:：]?\s*"
    r"(?P<value>\d{4}[./-]\d{1,2}[./-]\d{1,2}(?:\s*[（(][^)）]+[）)])?(?:\s*(?:上午|下午))?\s*\d{1,2}:\d{2}(?::\d{2})?)"
)
PRICE_RE = re.compile(r"(?:NT\$\s*|TWD\s*)(?P<price>\d{1,2}(?:,\d{3})+|\d{3,5})(?!\d)")

CITY_KEYWORDS = {
    "taipei": "Taipei",
    "台北": "Taipei",
    "臺北": "Taipei",
    "new taipei": "New Taipei",
    "新北": "New Taipei",
    "taichung": "Taichung",
    "台中": "Taichung",
    "臺中": "Taichung",
    "tainan": "Tainan",
    "台南": "Tainan",
    "臺南": "Tainan",
    "kaohsiung": "Kaohsiung",
    "高雄": "Kaohsiung",
    "taoyuan": "Taoyuan",
    "桃園": "Taoyuan",
}

TAIWAN_TIMEZONE = timezone(timedelta(hours=8))


class TicketplusCrawler(BaseCrawler):
    def __init__(self, source: dict[str, Any]) -> None:
        super().__init__(source)
        self.timeout = int(source.get("request_timeout_seconds", 15))
        self.max_events = int(source.get("max_events", 20))
        self.activity_base_url = source.get("activity_base_url", "https://ticketplus.com.tw/activity")
        self.static_api_base_url = source.get("static_api_base_url", "https://apis.ticketplus.com.tw/config/api/v1")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": source.get(
                    "user_agent",
                    (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/136.0.0.0 Safari/537.36"
                    ),
                ),
                "Accept": "application/json,text/plain,*/*",
                "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
                "Referer": "https://ticketplus.com.tw/",
            }
        )

    def crawl(self) -> list[dict]:
        retrieved_at = datetime.now(UTC).astimezone(TAIWAN_TIMEZONE).isoformat(timespec="seconds")
        main_events = self._get_json("main/mainEvents.json")
        event_ids = self._extract_event_ids(main_events)[: self.max_events]
        candidates: list[dict] = []

        for event_id in event_ids:
            event_summary = self._extract_event_summary(main_events, event_id)
            if bool(event_summary.get("hidden")):
                continue

            event = self._get_json(f"event/{event_id}/event.json")
            sessions_payload = self._get_json(f"event/{event_id}/sessions.json")

            if self._should_skip_event(event_summary, event, sessions_payload):
                continue

            products_payload: dict[str, Any] | None = None
            shows = self._extract_shows(event_id, event, sessions_payload)
            price_rows = self._extract_prices_from_html_sections(event)

            if not price_rows:
                products_payload = self._get_optional_json(f"event/{event_id}/products.json")
                price_rows = self._extract_prices_from_products(products_payload)

            for show in shows:
                candidate = self._build_candidate(
                    event_id=event_id,
                    event=event,
                    show=show,
                    retrieved_at=retrieved_at,
                    prices=price_rows,
                    products_payload=products_payload,
                )
                if candidate is not None:
                    candidates.append(candidate)

        return candidates

    def _get_json(self, path: str) -> dict[str, Any]:
        response = self.session.get(
            f"{self.static_api_base_url}/getS3",
            params={"path": path},
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError(f"Ticket Plus payload for {path} was not a JSON object")
        return payload

    def _get_optional_json(self, path: str) -> dict[str, Any] | None:
        try:
            return self._get_json(path)
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                return None
            raise

    def _extract_event_ids(self, main_events: dict[str, Any]) -> list[str]:
        raw_ids = main_events.get("allEventId")
        if isinstance(raw_ids, list):
            return [str(item) for item in raw_ids if item]

        main_page_info = main_events.get("allEventMainPageInfo", {})
        if isinstance(main_page_info, dict):
            return list(main_page_info.keys())
        return []

    def _extract_event_summary(self, main_events: dict[str, Any], event_id: str) -> dict[str, Any]:
        summary_map = main_events.get("allEventMainPageInfo", {})
        if isinstance(summary_map, dict):
            summary = summary_map.get(event_id)
            if isinstance(summary, dict):
                return summary
        return {}

    def _should_skip_event(
        self,
        event_summary: dict[str, Any],
        event: dict[str, Any],
        sessions_payload: dict[str, Any],
    ) -> bool:
        if bool(event.get("hidden")):
            return True

        status_text = " ".join(
            [
                self._event_text(event),
                self._event_text(event_summary),
                self._event_text(sessions_payload),
            ]
        )
        if "線上" in status_text and "台灣" not in status_text:
            return True

        shows = self._extract_shows(str(event.get("event_id") or ""), event, sessions_payload)
        if not shows:
            return True

        if all(self._is_past_show(show["start_time"]) for show in shows):
            return True

        return False

    def _extract_shows(
        self,
        event_id: str,
        event: dict[str, Any],
        sessions_payload: dict[str, Any],
    ) -> list[dict[str, Any]]:
        sessions = sessions_payload.get("sessions", [])
        shows: list[dict[str, Any]] = []

        if isinstance(sessions, list) and sessions:
            for index, session in enumerate(sessions):
                if not isinstance(session, dict) or bool(session.get("hidden")):
                    continue

                start_time = self._parse_datetime_parts(session.get("date"), session.get("time"))
                if not start_time:
                    continue

                venue_name = self._clean_text(session.get("location")) or self._clean_text(event.get("location"))
                address = self._clean_text(session.get("address")) or self._clean_text(event.get("address"))
                city = self._extract_city(venue_name, address, self._event_text(session))
                if not venue_name or not city:
                    continue

                session_id = str(session.get("sessionId") or f"{event_id}-session-{index + 1}")
                shows.append(
                    {
                        "session_id": session_id,
                        "session_name": self._clean_text(session.get("name")),
                        "raw_date_text": self._build_raw_date_text(session.get("date"), session.get("time")),
                        "date": start_time[:10],
                        "start_time": start_time,
                        "city": city,
                        "venue_name": venue_name,
                        "address": address,
                        "organizers": self._split_organizers(session.get("hosts")),
                    }
                )

        if shows:
            return shows

        start_time = self._extract_event_start_time(event)
        venue_name = self._clean_text(event.get("location"))
        address = self._clean_text(event.get("address"))
        city = self._extract_city(venue_name, address, self._event_text(event))
        if not start_time or not venue_name or not city:
            return []

        return [
            {
                "session_id": "main",
                "session_name": None,
                "raw_date_text": self._build_raw_date_text(event.get("date"), event.get("time")),
                "date": start_time[:10],
                "start_time": start_time,
                "city": city,
                "venue_name": venue_name,
                "address": address,
                "organizers": self._split_organizers(event.get("hosts")),
            }
        ]

    def _build_candidate(
        self,
        event_id: str,
        event: dict[str, Any],
        show: dict[str, Any],
        retrieved_at: str,
        prices: list[dict[str, Any]],
        products_payload: dict[str, Any] | None,
    ) -> dict[str, Any] | None:
        title = self._clean_text(event.get("title"))
        if not title:
            return None

        source_url = f"{self.activity_base_url}/{event_id}"
        section_text = self._combined_section_text(event)
        sale_start = self._extract_sale_start(section_text)
        ticket_status = self._infer_ticket_status(section_text, sale_start)
        organizers = show.get("organizers") or self._split_organizers(event.get("hosts"))
        raw_hash = self._build_raw_hash(event, show, products_payload)
        session_suffix = show.get("session_id") or "main"
        candidate_id = f"ticketplus:{event_id}:{session_suffix}"
        raw_sale_text = self._extract_sale_text(section_text)

        return {
            "candidate_id": candidate_id,
            "source_platform": "ticketplus",
            "source_url": source_url,
            "title": title,
            "raw_title": title,
            "matched_artist_ids": [],
            "matched_artist_names": [],
            "match_confidence": 0,
            "event_type": self._classify_event_type(title, section_text, show.get("venue_name")),
            "status": "candidate",
            "shows": [
                {
                    "raw_date_text": show["raw_date_text"],
                    "date": show["date"],
                    "start_time": show["start_time"],
                    "city": show["city"],
                    "venue_name": show["venue_name"],
                    "address": show["address"],
                }
            ],
            "ticket_sales": [
                {
                    "type": "general",
                    "platform": "ticketplus",
                    "sale_start": sale_start,
                    "sale_end": None,
                    "ticket_url": source_url,
                    "status": ticket_status,
                    "raw_sale_text": raw_sale_text,
                }
            ],
            "prices": prices,
            "organizers": organizers,
            "sources": [
                {
                    "type": "official_ticket",
                    "name": "Ticket Plus",
                    "url": source_url,
                    "retrieved_at": retrieved_at,
                }
            ],
            "crawler_meta": {
                "crawler_name": "ticketplus",
                "retrieved_at": retrieved_at,
                "raw_hash": raw_hash,
                "is_duplicate": False,
                "duplicate_event_id": None,
                "review_status": "pending",
                "review_note": None,
            },
        }

    def _extract_event_start_time(self, event: dict[str, Any]) -> str | None:
        start_time = self._parse_datetime_parts(event.get("date"), event.get("time"))
        if start_time:
            return start_time
        return self._parse_datetime_text(self._clean_text(event.get("time")))

    def _extract_prices_from_products(self, payload: dict[str, Any] | None) -> list[dict[str, Any]]:
        if not payload:
            return []

        price_rows: list[dict[str, Any]] = []
        for price_item in self._walk_price_like_nodes(payload):
            label = self._clean_text(
                price_item.get("productName")
                or price_item.get("name")
                or price_item.get("title")
                or price_item.get("areaName")
                or "票券"
            )
            raw_price = price_item.get("price") or price_item.get("sellPrice") or price_item.get("amount")
            parsed_price = self._coerce_int(raw_price)
            if parsed_price is None or parsed_price <= 0:
                continue
            price_rows.append({"label": label, "price": parsed_price, "currency": "TWD"})

        return self._dedupe_prices(price_rows)

    def _walk_price_like_nodes(self, value: Any) -> list[dict[str, Any]]:
        nodes: list[dict[str, Any]] = []
        if isinstance(value, dict):
            if any(key in value for key in ("price", "sellPrice", "amount")):
                nodes.append(value)
            for child in value.values():
                nodes.extend(self._walk_price_like_nodes(child))
        elif isinstance(value, list):
            for item in value:
                nodes.extend(self._walk_price_like_nodes(item))
        return nodes

    def _extract_prices_from_html_sections(self, event: dict[str, Any]) -> list[dict[str, Any]]:
        text = self._combined_section_text(event)
        prices: list[dict[str, Any]] = []
        seen: set[int] = set()
        for match in PRICE_RE.finditer(text):
            value = int(match.group("price").replace(",", ""))
            if value in seen:
                continue
            seen.add(value)
            prices.append({"label": "一般票", "price": value, "currency": "TWD"})
        return prices

    def _combined_section_text(self, event: dict[str, Any]) -> str:
        sections = [
            event.get("announcement"),
            event.get("info"),
            event.get("notice"),
            event.get("buy_notice"),
            event.get("get_notice"),
            event.get("refund_info"),
        ]
        return "\n".join(self._html_to_text(section) for section in sections if section)

    def _extract_sale_start(self, text: str) -> str | None:
        match = SALE_TIME_RE.search(text)
        if not match:
            return None
        return self._parse_datetime_text(match.group("value"))

    def _infer_ticket_status(self, text: str, sale_start: str | None) -> str:
        normalized = normalize_text(text)
        if re.search(r"(演出|活動|節目|場次).{0,8}(取消|中止)|取消(演出|活動|節目|場次)", text):
            return "cancelled"
        if re.search(r"(演出|活動|節目|場次).{0,8}延期|延期(演出|活動|節目|場次)", text):
            return "postponed"
        if "售完" in text or "完售" in text:
            return "sold_out"
        if any(keyword in text for keyword in ("熱賣中", "開賣中", "販售中")):
            return "on_sale"
        if sale_start:
            sale_start_dt = date_parser.isoparse(sale_start)
            now = datetime.now(UTC).astimezone(TAIWAN_TIMEZONE)
            if sale_start_dt > now:
                return "sale_soon"
            return "on_sale"
        if "開賣" in text or "售票時間" in text or "啟售" in text:
            return "sale_soon"
        if "公布" in text or "敬請期待" in text or "comingsoon" in normalized:
            return "announced"
        return "unknown"

    def _extract_sale_text(self, text: str) -> str | None:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for line in lines:
            if any(keyword in line for keyword in ("售票", "開賣", "啟售", "完售", "取消", "延期")):
                return line[:300]
        return lines[0][:300] if lines else None

    def _classify_event_type(self, title: str, page_text: str, venue_name: str | None) -> str:
        combined = normalize_text(" ".join([title, page_text, venue_name or ""]))
        if "fanmeeting" in combined or "見面會" in combined:
            return "fanmeeting"
        if "livehouse" in combined or "thewall" in combined or "legacy" in combined:
            return "live_house"
        if "anime" in combined or "anisong" in combined or "動漫" in combined:
            return "anime_music"
        if "festival" in combined or "音樂祭" in combined:
            return "festival"
        return "concert"

    def _extract_city(self, venue_name: str | None, address: str | None, extra_text: str | None) -> str:
        haystack = " ".join(item for item in [venue_name, address, extra_text] if item)
        normalized = normalize_text(haystack)
        for keyword, city in CITY_KEYWORDS.items():
            if normalize_text(keyword) in normalized:
                return city
        return ""

    def _build_raw_hash(self, event: dict[str, Any], show: dict[str, Any], products_payload: dict[str, Any] | None) -> str:
        raw_value = json.dumps(
            {"event": event, "show": show, "products": products_payload},
            ensure_ascii=False,
            sort_keys=True,
        )
        return "sha256-" + hashlib.sha256(raw_value.encode("utf-8")).hexdigest()

    def _build_raw_date_text(self, date_value: Any, time_value: Any) -> str:
        parts = [self._clean_text(date_value), self._clean_text(time_value)]
        return " ".join(part for part in parts if part)

    def _is_past_show(self, start_time: str) -> bool:
        try:
            return date_parser.isoparse(start_time) < datetime.now(UTC).astimezone(TAIWAN_TIMEZONE)
        except (TypeError, ValueError):
            return False

    def _parse_datetime_parts(self, date_value: Any, time_value: Any) -> str | None:
        normalized_date = self._normalize_date_token(date_value)
        normalized_time = self._normalize_time_token(time_value)
        if normalized_date and normalized_time:
            return self._parse_datetime_text(f"{normalized_date} {normalized_time}")
        if normalized_date:
            return self._parse_datetime_text(str(normalized_date))
        return None

    def _parse_datetime_text(self, value: str | None) -> str | None:
        if not value:
            return None
        candidate = (
            value.replace("上午", "AM ")
            .replace("下午", "PM ")
            .replace(".", "-")
            .replace("/", "-")
            .strip()
        )
        candidate = re.sub(r"[（(][^)）]+[）)]", " ", candidate)
        candidate = re.sub(r"\s+", " ", candidate).strip()
        try:
            parsed = date_parser.parse(candidate)
        except (TypeError, ValueError, OverflowError):
            return None

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=TAIWAN_TIMEZONE)
        return parsed.isoformat(timespec="seconds")

    def _split_organizers(self, value: Any) -> list[str]:
        if not value:
            return []
        if isinstance(value, list):
            return [self._clean_text(item) for item in value if self._clean_text(item)]

        text = self._clean_text(value)
        if not text:
            return []
        return [
            organizer
            for organizer in [item.strip() for item in re.split(r"[、,/\n]", text)]
            if organizer
        ]

    def _event_text(self, value: Any) -> str:
        if isinstance(value, dict):
            return " ".join(self._event_text(item) for item in value.values())
        if isinstance(value, list):
            return " ".join(self._event_text(item) for item in value)
        return self._clean_text(value)

    def _html_to_text(self, value: Any) -> str:
        if not value:
            return ""
        html = str(value).replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
        text = BeautifulSoup(html, "lxml").get_text("\n")
        lines = [self._clean_text(unescape(line)) for line in text.splitlines()]
        return "\n".join(line for line in lines if line)

    def _clean_text(self, value: Any) -> str:
        if value is None:
            return ""
        return re.sub(r"\s+", " ", str(value)).strip()

    def _coerce_int(self, value: Any) -> int | None:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        digits = re.sub(r"[^\d]", "", str(value))
        if not digits:
            return None
        return int(digits)

    def _normalize_date_token(self, value: Any) -> str:
        text = self._clean_text(value)
        if not text:
            return ""
        text = text.split("~", 1)[0].strip()
        match = re.search(r"\d{4}[./-]\d{1,2}[./-]\d{1,2}", text)
        return match.group(0) if match else text

    def _normalize_time_token(self, value: Any) -> str:
        text = self._clean_text(value)
        if not text:
            return ""
        text = text.split("~", 1)[0].strip()
        match = re.search(r"(?:(?:上午|下午)\s*)?\d{1,2}:\d{2}(?::\d{2})?", text)
        return match.group(0) if match else text

    def _dedupe_prices(self, price_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        deduped: list[dict[str, Any]] = []
        seen: set[tuple[str, int]] = set()
        for price in price_rows:
            key = (slugify(str(price.get("label", ""))) or "price", int(price["price"]))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(price)
        return deduped
