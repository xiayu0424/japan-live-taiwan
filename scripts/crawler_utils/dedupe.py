"""Duplicate detection for crawler candidates."""

from __future__ import annotations

from copy import deepcopy
from difflib import SequenceMatcher

from scripts.crawler_utils.normalize import normalize_text


def mark_duplicates(candidates: list[dict], existing_events: list[dict]) -> list[dict]:
    for candidate in candidates:
        duplicate_id = find_duplicate_event_id(candidate, existing_events)
        candidate.setdefault("crawler_meta", {})
        candidate["crawler_meta"]["is_duplicate"] = duplicate_id is not None
        candidate["crawler_meta"]["duplicate_event_id"] = duplicate_id
    return candidates


def split_candidates_and_change_requests(
    candidates: list[dict],
    existing_events: list[dict],
) -> tuple[list[dict], list[dict]]:
    fresh_candidates: list[dict] = []
    change_requests: list[dict] = []

    for candidate in mark_duplicates(candidates, existing_events):
        existing_event = _find_related_event(candidate, existing_events)
        if existing_event is None:
            fresh_candidates.append(candidate)
            continue

        detected_changes = _build_detected_changes(candidate, existing_event)
        change_requests.append(
            {
                "change_request_id": _build_change_request_id(candidate, existing_event),
                "source_platform": candidate["source_platform"],
                "source_url": candidate["source_url"],
                "existing_event_id": existing_event["id"],
                "detected_changes": detected_changes,
                "review_status": "pending",
            }
        )

    return fresh_candidates, change_requests


def find_duplicate_event_id(candidate: dict, existing_events: list[dict]) -> str | None:
    candidate_artist_ids = set(candidate.get("matched_artist_ids", []))
    candidate_shows = candidate.get("shows", [])

    if not candidate_artist_ids or not candidate_shows:
        return None

    for event in existing_events:
        if not candidate_artist_ids.intersection(event.get("artist_ids", [])):
            continue
        for candidate_show in candidate_shows:
            for event_show in event.get("shows", []):
                if _same_show(candidate_show, event_show):
                    return event.get("id")
    return None


def _same_show(candidate_show: dict, event_show: dict) -> bool:
    return candidate_show.get("date") == event_show.get("date") and normalize_text(
        candidate_show.get("venue_name")
    ) == normalize_text(event_show.get("venue_name"))


def _find_related_event(candidate: dict, existing_events: list[dict]) -> dict | None:
    duplicate_id = candidate.get("crawler_meta", {}).get("duplicate_event_id")
    if duplicate_id:
        for event in existing_events:
            if event.get("id") == duplicate_id:
                return event

    candidate_artist_ids = set(candidate.get("matched_artist_ids", []))
    if not candidate_artist_ids:
        return None

    candidate_title = normalize_text(candidate.get("title"))
    best_match: tuple[float, dict] | None = None

    for event in existing_events:
        if not candidate_artist_ids.intersection(event.get("artist_ids", [])):
            continue

        score = SequenceMatcher(None, candidate_title, normalize_text(event.get("title"))).ratio()
        if score < 0.55:
            continue

        if best_match is None or score > best_match[0]:
            best_match = (score, event)

    return best_match[1] if best_match else None


def _build_detected_changes(candidate: dict, existing_event: dict) -> dict:
    differences = _diff_candidate_against_event(candidate, existing_event)
    if candidate.get("crawler_meta", {}).get("duplicate_event_id"):
        match_type = "possible_update" if differences else "possible_duplicate"
    else:
        match_type = "possible_additional_show"
        if "new_shows" not in differences:
            differences["new_shows"] = deepcopy(candidate.get("shows", []))

    return {
        "match_type": match_type,
        "candidate_snapshot": deepcopy(candidate),
        "differences": differences,
    }


def _diff_candidate_against_event(candidate: dict, existing_event: dict) -> dict[str, object]:
    differences: dict[str, object] = {}
    existing_shows = existing_event.get("shows", [])
    candidate_shows = candidate.get("shows", [])
    new_shows = [
        show for show in candidate_shows if not any(_same_show(show, existing_show) for existing_show in existing_shows)
    ]
    if new_shows:
        differences["new_shows"] = deepcopy(new_shows)

    existing_prices = _normalize_prices(existing_event.get("prices", []))
    candidate_prices = _normalize_prices(candidate.get("prices", []))
    if candidate_prices and candidate_prices != existing_prices:
        differences["prices"] = {"existing": existing_prices, "candidate": candidate_prices}

    existing_sales = _normalize_ticket_sales(existing_event.get("ticket_sales", []))
    candidate_sales = _normalize_ticket_sales(candidate.get("ticket_sales", []))
    if candidate_sales and candidate_sales != existing_sales:
        differences["ticket_sales"] = {"existing": existing_sales, "candidate": candidate_sales}

    existing_status = existing_event.get("status")
    candidate_status = _candidate_status(candidate)
    if candidate_status and candidate_status != existing_status:
        differences["status"] = {"existing": existing_status, "candidate": candidate_status}

    existing_organizers = sorted(existing_event.get("organizers", []))
    candidate_organizers = sorted(candidate.get("organizers", []))
    if candidate_organizers and candidate_organizers != existing_organizers:
        differences["organizers"] = {"existing": existing_organizers, "candidate": candidate_organizers}

    return differences


def _build_change_request_id(candidate: dict, existing_event: dict) -> str:
    raw_hash = candidate.get("crawler_meta", {}).get("raw_hash", "").replace("sha256-", "")
    suffix = raw_hash[:12] if raw_hash else normalize_text(candidate.get("candidate_id"))[:12]
    return f"{candidate['source_platform']}-{existing_event['id']}-{suffix}"


def _normalize_prices(prices: list[dict]) -> list[dict]:
    normalized: list[dict] = []
    for price in prices:
        normalized.append(
            {
                "label": price.get("label"),
                "price": price.get("price"),
                "currency": price.get("currency", "TWD"),
            }
        )
    return normalized


def _normalize_ticket_sales(ticket_sales: list[dict]) -> list[dict]:
    normalized: list[dict] = []
    for sale in ticket_sales:
        normalized.append(
            {
                "type": sale.get("type"),
                "platform": sale.get("platform"),
                "sale_start": sale.get("sale_start"),
                "sale_end": sale.get("sale_end"),
                "ticket_url": sale.get("ticket_url"),
                "status": sale.get("status"),
            }
        )
    return normalized


def _candidate_status(candidate: dict) -> str | None:
    ticket_sales = candidate.get("ticket_sales", [])
    if ticket_sales:
        return ticket_sales[0].get("status")
    return None
