"""Run enabled crawlers and write candidate outputs."""

from __future__ import annotations

from datetime import datetime, timezone

import yaml

from scripts.crawler_utils.dedupe import split_candidates_and_change_requests
from scripts.crawler_utils.io import DATA_DIR, ROOT, load_json, save_json
from scripts.crawler_utils.match_artist import match_artists
from scripts.crawler_utils.schemas import Candidate, ChangeRequest, CrawlerReport
from scripts.crawlers.base import BaseCrawler
from scripts.crawlers.kktix import KktixCrawler
from scripts.crawlers.mock import MockCrawler
from scripts.crawlers.ticketplus import TicketplusCrawler

CONFIG_PATH = ROOT / "scripts" / "configs" / "crawler_sources.yaml"
CHANGE_REQUESTS_PATH = DATA_DIR / "change_requests.json"
CANDIDATES_PATH = DATA_DIR / "candidates.json"
CRAWLER_REPORT_PATH = DATA_DIR / "crawler_report.json"

CRAWLER_REGISTRY: dict[str, type[BaseCrawler]] = {
    "kktix": KktixCrawler,
    "mock": MockCrawler,
    "ticketplus": TicketplusCrawler,
}


def main() -> None:
    retrieved_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    artists = load_json(DATA_DIR / "artists.json", [])
    existing_events = load_json(DATA_DIR / "events.json", [])
    sources = _load_sources()
    all_candidates: list[dict] = []
    report_sources: list[dict] = []

    for source in sources:
        crawler_name = source.get("crawler")
        crawler_cls = CRAWLER_REGISTRY.get(crawler_name)

        if crawler_cls is None:
            report_sources.append(_source_report(source, "failed", 0, f"Unknown crawler: {crawler_name}"))
            continue

        try:
            raw_candidates = crawler_cls(source).crawl()
            matched_candidates = [match_artists(candidate, artists) for candidate in raw_candidates]
            valid_candidates = [Candidate.model_validate(candidate).model_dump(mode="json") for candidate in matched_candidates]
            all_candidates.extend(valid_candidates)
            report_sources.append(_source_report(source, "success", len(valid_candidates), None))
        except Exception as exc:  # pragma: no cover - defensive report path
            report_sources.append(_source_report(source, "failed", 0, str(exc)))

    deduped_candidates, change_requests = split_candidates_and_change_requests(all_candidates, existing_events)
    report_sources = _hydrate_source_counts(report_sources, deduped_candidates, change_requests)
    report = _build_report(retrieved_at, sources, report_sources, deduped_candidates, change_requests)

    CrawlerReport.model_validate(report)
    [ChangeRequest.model_validate(item) for item in change_requests]
    save_json(CANDIDATES_PATH, deduped_candidates)
    save_json(CHANGE_REQUESTS_PATH, change_requests)
    save_json(CRAWLER_REPORT_PATH, report)

    print(f"Generated {len(deduped_candidates)} candidates and {len(change_requests)} change requests")


def _load_sources() -> list[dict]:
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    return [source for source in config.get("sources", []) if source.get("enabled", False)]


def _source_report(source: dict, status: str, candidate_count: int, error: str | None) -> dict:
    return {
        "id": source["id"],
        "status": status,
        "candidate_count": candidate_count,
        "change_request_count": 0,
        "error": error,
    }


def _hydrate_source_counts(report_sources: list[dict], candidates: list[dict], change_requests: list[dict]) -> list[dict]:
    candidate_counts: dict[str, int] = {}
    change_request_counts: dict[str, int] = {}

    for candidate in candidates:
        source_id = candidate.get("source_platform")
        candidate_counts[source_id] = candidate_counts.get(source_id, 0) + 1

    for change_request in change_requests:
        source_id = change_request.get("source_platform")
        change_request_counts[source_id] = change_request_counts.get(source_id, 0) + 1

    hydrated_reports: list[dict] = []
    for report in report_sources:
        source_id = report["id"]
        updated_report = dict(report)
        updated_report["candidate_count"] = candidate_counts.get(source_id, 0)
        updated_report["change_request_count"] = change_request_counts.get(source_id, 0)
        hydrated_reports.append(updated_report)

    return hydrated_reports


def _build_report(
    retrieved_at: str,
    sources: list[dict],
    report_sources: list[dict],
    candidates: list[dict],
    change_requests: list[dict],
) -> dict:
    return {
        "retrieved_at": retrieved_at,
        "summary": {
            "total_sources": len(sources),
            "success_sources": sum(1 for source in report_sources if source["status"] == "success"),
            "failed_sources": sum(1 for source in report_sources if source["status"] == "failed"),
            "total_candidates": len(candidates),
            "high_confidence_candidates": sum(1 for candidate in candidates if candidate["match_confidence"] >= 95),
            "medium_confidence_candidates": sum(1 for candidate in candidates if 85 <= candidate["match_confidence"] < 95),
            "low_confidence_candidates": sum(1 for candidate in candidates if candidate["match_confidence"] < 85),
            "change_requests": len(change_requests),
        },
        "sources": report_sources,
    }


if __name__ == "__main__":
    main()
