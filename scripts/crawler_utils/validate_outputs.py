"""Validate generated crawler output JSON files."""

from __future__ import annotations

from scripts.crawler_utils.io import DATA_DIR, load_json
from scripts.crawler_utils.schemas import Candidate, ChangeRequest, CrawlerReport


def main() -> None:
    candidates = load_json(DATA_DIR / "candidates.json", [])
    change_requests = load_json(DATA_DIR / "change_requests.json", [])
    crawler_report = load_json(DATA_DIR / "crawler_report.json", {})

    for candidate in candidates:
        Candidate.model_validate(candidate)

    for change_request in change_requests:
        ChangeRequest.model_validate(change_request)

    CrawlerReport.model_validate(crawler_report)

    print(
        f"Validated {len(candidates)} crawler candidates and "
        f"{len(change_requests)} change requests."
    )


if __name__ == "__main__":
    main()
