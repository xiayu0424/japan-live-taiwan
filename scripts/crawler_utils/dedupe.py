"""Duplicate detection for crawler candidates."""

from __future__ import annotations

from scripts.crawler_utils.normalize import normalize_text


def mark_duplicates(candidates: list[dict], existing_events: list[dict]) -> list[dict]:
    for candidate in candidates:
        duplicate_id = find_duplicate_event_id(candidate, existing_events)
        candidate.setdefault("crawler_meta", {})
        candidate["crawler_meta"]["is_duplicate"] = duplicate_id is not None
        candidate["crawler_meta"]["duplicate_event_id"] = duplicate_id
    return candidates


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
