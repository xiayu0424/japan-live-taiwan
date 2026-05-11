"""KKTIX crawler backed by public HTML pages."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from html import unescape
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from scripts.crawler_utils.normalize import normalize_text, slugify
from scripts.crawlers.base import BaseCrawler

DATE_RE = re.compile(
    r"(?P<date>\d{4}[/-]\d{1,2}[/-]\d{1,2})"
    r"(?:\s*[（(]?[一二三四五六日天MonTueWedThuFriSatSun/\s]+[）)]?)?"
    r"(?:\s+(?P<time>\d{1,2}:\d{2}))?"
)
PRICE_RE = re.compile(r"(?:NT\$|TWD\s*|票價[:：]?\s*)(?P<price>\d{3,5})(?!\d)")
ORGANIZER_RE = re.compile(r"(?:主辦單位|主辦|Organizer)[:：]?\s*(?P<name>[^\n|]+)")
ADDRESS_RE = re.compile(r"(?:地址|地點)[:：]?\s*(?P<address>[^\n|]+)")

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
    "keelung": "Keelung",
    "基隆": "Keelung",
    "hsinchu": "Hsinchu",
    "新竹": "Hsinchu",
    "miaoli": "Miaoli",
    "苗栗": "Miaoli",
    "changhua": "Changhua",
    "彰化": "Changhua",
    "nantou": "Nantou",
    "南投": "Nantou",
    "yunlin": "Yunlin",
    "雲林": "Yunlin",
    "chiayi": "Chiayi",
    "嘉義": "Chiayi",
    "yilan": "Yilan",
    "宜蘭": "Yilan",
    "hualien": "Hualien",
    "花蓮": "Hualien",
    "taitung": "Taitung",
    "台東": "Taitung",
    "臺東": "Taitung",
    "penghu": "Penghu",
    "澎湖": "Penghu",
}


class KktixCrawler(BaseCrawler):
    def __init__(self, source: dict[str, Any]) -> None:
        super().__init__(source)
        self.base_url = source.get("base_url", "https://kktix.com")
        self.max_events = int(source.get("max_events", 20))
        self.timeout = int(source.get("request_timeout_seconds", 15))
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
                "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
            }
        )

    def crawl(self) -> list[dict]:
        retrieved_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
        event_links: list[str] = []

        for list_url in self.source.get("list_urls", []):
            html = self._fetch_html(list_url)
            event_links.extend(self.extract_event_links(html, list_url))

        unique_links = list(dict.fromkeys(event_links))[: self.max_events]
        candidates: list[dict] = []

        for event_url in unique_links:
            try:
                html = self._fetch_html(event_url)
                candidate = self.parse_event_detail(html, event_url, retrieved_at)
                if candidate is not None:
                    candidates.append(candidate)
            except Exception:
                continue

        return candidates

    def _fetch_html(self, url: str) -> str:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def extract_event_links(self, html: str, source_url: str) -> list[str]:
        soup = BeautifulSoup(html, "lxml")
        links: list[str] = []

        for anchor in soup.select("a[href]"):
            href = (anchor.get("href") or "").strip()
            if not href or href.startswith(("#", "javascript:", "mailto:")):
                continue
            absolute_url = urljoin(source_url, href)
            if self._is_event_url(absolute_url):
                links.append(absolute_url.split("?")[0])

        return links

    def parse_event_detail(self, html: str, event_url: str, retrieved_at: str) -> dict[str, Any] | None:
        soup = BeautifulSoup(html, "lxml")
        page_text = self._page_text(soup)
        json_ld = self._extract_primary_json_ld(soup)

        if not self._is_offline_taiwan_event(page_text, json_ld):
            return None

        title = self._extract_title(soup, json_ld)
        show = self._extract_show(page_text, json_ld)
        if not title or not show:
            return None

        organizer = self._extract_organizer(page_text, json_ld)
        prices = self._extract_prices(page_text, json_ld)
        status = self._infer_ticket_status(page_text, show["start_time"])
        raw_hash = "sha256-" + hashlib.sha256(html.encode("utf-8")).hexdigest()
        candidate_id = f"kktix-{show['date']}-{slugify(title)}"

        return {
            "candidate_id": candidate_id,
            "source_platform": "kktix",
            "source_url": event_url,
            "title": title,
            "raw_title": title,
            "matched_artist_ids": [],
            "matched_artist_names": [],
            "match_confidence": 0,
            "event_type": self._classify_event_type(title, show["venue_name"], page_text),
            "status": "candidate",
            "shows": [show],
            "ticket_sales": [
                {
                    "type": "general",
                    "platform": "KKTIX",
                    "sale_start": None,
                    "sale_end": None,
                    "ticket_url": event_url,
                    "status": status,
                    "raw_sale_text": self._extract_sale_text(page_text),
                }
            ],
            "prices": prices,
            "organizers": [organizer] if organizer else [],
            "sources": [
                {
                    "type": "official_ticket",
                    "name": "KKTIX",
                    "url": event_url,
                    "retrieved_at": retrieved_at,
                }
            ],
            "crawler_meta": {
                "crawler_name": "kktix",
                "retrieved_at": retrieved_at,
                "raw_hash": raw_hash,
                "is_duplicate": False,
                "duplicate_event_id": None,
                "review_status": "pending",
                "review_note": None,
            },
        }

    def _is_event_url(self, url: str) -> bool:
        return url.startswith(self.base_url) and "/events/" in url and not url.endswith("/registrations/new")

    def _extract_primary_json_ld(self, soup: BeautifulSoup) -> dict[str, Any]:
        for script in soup.select('script[type="application/ld+json"]'):
            raw_json = (script.string or script.get_text() or "").strip()
            if not raw_json:
                continue
            try:
                payload = json.loads(raw_json)
            except json.JSONDecodeError:
                continue

            for item in self._flatten_json_ld(payload):
                item_type = str(item.get("@type", ""))
                if "Event" in item_type:
                    return item

        return {}

    def _flatten_json_ld(self, payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, dict):
            if isinstance(payload.get("@graph"), list):
                return [item for item in payload["@graph"] if isinstance(item, dict)]
            return [payload]
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        return []

    def _extract_title(self, soup: BeautifulSoup, json_ld: dict[str, Any]) -> str:
        candidates = [
            json_ld.get("name"),
            self._meta_content(soup, "meta[property='og:title']"),
            soup.title.string if soup.title and soup.title.string else None,
            self._first_text(soup, ["h1", ".event-title", "[data-testid='event-title']"]),
        ]

        for candidate in candidates:
            cleaned = self._clean_title(candidate)
            if cleaned:
                return cleaned
        return ""

    def _extract_show(self, page_text: str, json_ld: dict[str, Any]) -> dict[str, Any] | None:
        start_time = self._extract_start_time(page_text, json_ld)
        venue_name = self._extract_venue_name(page_text, json_ld)
        city = self._extract_city(page_text, json_ld, venue_name)

        if not start_time or not venue_name or not city:
            return None

        return {
            "raw_date_text": self._extract_raw_date_text(page_text, start_time),
            "date": start_time[:10],
            "start_time": start_time,
            "city": city,
            "venue_name": venue_name,
            "address": self._extract_address(page_text, json_ld),
        }

    def _extract_start_time(self, page_text: str, json_ld: dict[str, Any]) -> str | None:
        for value in [json_ld.get("startDate"), json_ld.get("doorTime")]:
            parsed = self._parse_datetime(value)
            if parsed:
                return parsed

        match = DATE_RE.search(page_text)
        if not match:
            return None

        date_part = match.group("date").replace("/", "-")
        time_part = match.group("time") or "19:00"
        return self._parse_datetime(f"{date_part} {time_part}")

    def _extract_venue_name(self, page_text: str, json_ld: dict[str, Any]) -> str:
        location = json_ld.get("location")
        if isinstance(location, dict):
            venue_name = location.get("name")
            if venue_name:
                return self._clean_whitespace(str(venue_name))

        match = re.search(r"(?:地點|場地|Venue)[:：]?\s*(?P<venue>[^\n|]+)", page_text)
        if match:
            return self._clean_whitespace(match.group("venue"))

        return ""

    def _extract_city(
        self,
        page_text: str,
        json_ld: dict[str, Any],
        venue_name: str,
    ) -> str:
        location = json_ld.get("location")
        address_sources: list[str] = [page_text, venue_name]

        if isinstance(location, dict):
            address = location.get("address")
            if isinstance(address, dict):
                address_sources.extend(
                    [
                        str(address.get("addressLocality", "")),
                        str(address.get("streetAddress", "")),
                        str(address.get("addressRegion", "")),
                    ]
                )
            elif isinstance(address, str):
                address_sources.append(address)

        normalized_sources = " ".join(normalize_text(item) for item in address_sources if item)
        for keyword, city in CITY_KEYWORDS.items():
            if normalize_text(keyword) in normalized_sources:
                return city

        return ""

    def _extract_address(self, page_text: str, json_ld: dict[str, Any]) -> str | None:
        location = json_ld.get("location")
        if isinstance(location, dict):
            address = location.get("address")
            if isinstance(address, dict):
                street = address.get("streetAddress")
                if street:
                    return self._clean_whitespace(str(street))
            if isinstance(address, str):
                return self._clean_whitespace(address)

        match = ADDRESS_RE.search(page_text)
        if match:
            return self._clean_whitespace(match.group("address"))
        return None

    def _extract_organizer(self, page_text: str, json_ld: dict[str, Any]) -> str | None:
        organizer = json_ld.get("organizer")
        if isinstance(organizer, dict) and organizer.get("name"):
            return self._clean_whitespace(str(organizer["name"]))
        if isinstance(organizer, list):
            for item in organizer:
                if isinstance(item, dict) and item.get("name"):
                    return self._clean_whitespace(str(item["name"]))

        match = ORGANIZER_RE.search(page_text)
        if match:
            return self._clean_whitespace(match.group("name"))
        return None

    def _extract_prices(self, page_text: str, json_ld: dict[str, Any]) -> list[dict[str, Any]]:
        prices: list[int] = []
        offers = json_ld.get("offers")
        if isinstance(offers, dict):
            offers = [offers]

        if isinstance(offers, list):
            for offer in offers:
                if isinstance(offer, dict) and offer.get("priceCurrency") == "TWD":
                    try:
                        prices.append(int(float(str(offer.get("price")))))
                    except (TypeError, ValueError):
                        continue

        prices.extend(int(match.group("price")) for match in PRICE_RE.finditer(page_text))
        unique_prices = list(dict.fromkeys(price for price in prices if price > 0))
        return [{"label": "一般票", "price": price, "currency": "TWD"} for price in unique_prices]

    def _infer_ticket_status(self, page_text: str, start_time: str) -> str:
        normalized_text = normalize_text(page_text)
        if "soldout" in normalized_text or "已售完" in page_text or "完售" in page_text:
            return "sold_out"
        if "postponed" in normalized_text or "延期" in page_text:
            return "postponed"
        if "cancelled" in normalized_text or "取消" in page_text:
            return "cancelled"
        if "onsale" in normalized_text or "開賣中" in page_text:
            return "on_sale"
        if "comingsoon" in normalized_text or "即將開賣" in page_text or "尚未開賣" in page_text:
            return "sale_soon"

        event_time = datetime.fromisoformat(start_time)
        if event_time < datetime.now(event_time.tzinfo):
            return "ended"
        return "unknown"

    def _extract_sale_text(self, page_text: str) -> str | None:
        for marker in ["開賣中", "即將開賣", "尚未開賣", "已售完", "完售", "延期", "取消"]:
            if marker in page_text:
                return marker
        return None

    def _classify_event_type(self, title: str, venue_name: str, page_text: str) -> str:
        haystack = " ".join([title, venue_name, page_text]).lower()
        if any(keyword in haystack for keyword in ["fan meeting", "fanmeeting", "見面會"]):
            return "fanmeeting"
        if any(keyword in haystack for keyword in ["legacy", "the wall", "live house", "zepp", "河岸留言"]):
            return "live_house"
        return "concert"

    def _is_offline_taiwan_event(self, page_text: str, json_ld: dict[str, Any]) -> bool:
        attendance_mode = str(json_ld.get("eventAttendanceMode", ""))
        if "OnlineEventAttendanceMode" in attendance_mode:
            return False

        normalized_page = normalize_text(page_text)
        if "線上活動" in page_text or "onlineevent" in normalized_page:
            return False

        location = json_ld.get("location")
        if isinstance(location, dict):
            address = location.get("address")
            if isinstance(address, dict):
                country = str(address.get("addressCountry", ""))
                if country and country not in {"TW", "Taiwan", "台灣", "臺灣"}:
                    return False
            elif isinstance(address, str) and not self._contains_taiwan_text(address):
                return False

        return self._contains_taiwan_text(page_text)

    def _contains_taiwan_text(self, value: str) -> bool:
        normalized_value = normalize_text(value)
        return any(
            token in normalized_value
            for token in [
                "taiwan",
                "taipei",
                "newtaipei",
                "taichung",
                "tainan",
                "kaohsiung",
                "台灣",
                "臺灣",
                "台北",
                "臺北",
                "新北",
                "台中",
                "臺中",
                "台南",
                "臺南",
                "高雄",
            ]
        )

    def _parse_datetime(self, value: Any) -> str | None:
        if not value:
            return None
        try:
            parsed = date_parser.parse(str(value))
        except (TypeError, ValueError, OverflowError):
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc).astimezone().isoformat(timespec="seconds")
        return parsed.isoformat(timespec="seconds")

    def _extract_raw_date_text(self, page_text: str, start_time: str) -> str:
        match = DATE_RE.search(page_text)
        if match:
            return self._clean_whitespace(match.group(0))
        return start_time

    def _page_text(self, soup: BeautifulSoup) -> str:
        return unescape(soup.get_text("\n", strip=True))

    def _meta_content(self, soup: BeautifulSoup, selector: str) -> str | None:
        node = soup.select_one(selector)
        if node:
            return node.get("content")
        return None

    def _first_text(self, soup: BeautifulSoup, selectors: list[str]) -> str | None:
        for selector in selectors:
            node = soup.select_one(selector)
            if node:
                return node.get_text(" ", strip=True)
        return None

    def _clean_title(self, value: Any) -> str:
        if not value:
            return ""
        title = self._clean_whitespace(str(value))
        title = re.sub(r"\s*[-|｜]\s*KKTIX.*$", "", title, flags=re.IGNORECASE)
        return title

    def _clean_whitespace(self, value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
