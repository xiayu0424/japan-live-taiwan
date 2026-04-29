"""Artist alias matching for crawler candidates."""

from __future__ import annotations

from rapidfuzz import fuzz

from scripts.crawler_utils.normalize import normalize_text


def match_artists(candidate: dict, artists: list[dict], threshold: int = 60) -> dict:
    title = candidate.get("title", "")
    normalized_title = normalize_text(title)
    matches: list[dict] = []

    for artist in artists:
        aliases = [artist.get("name", "")]
        aliases.extend(artist.get("aliases", []))
        best_score = 0.0

        for alias in aliases:
            normalized_alias = normalize_text(alias)
            if not normalized_alias:
                continue
            if normalized_alias in normalized_title:
                best_score = max(best_score, 100.0)
            else:
                best_score = max(best_score, float(fuzz.partial_ratio(normalized_alias, normalized_title)))

        if best_score >= threshold:
            matches.append(
                {
                    "artist_id": artist["id"],
                    "artist_name": artist["name"],
                    "score": round(best_score, 2),
                }
            )

    matches.sort(key=lambda item: item["score"], reverse=True)
    candidate["matched_artist_ids"] = [match["artist_id"] for match in matches]
    candidate["matched_artist_names"] = [match["artist_name"] for match in matches]
    candidate["match_confidence"] = matches[0]["score"] if matches else 0
    return candidate
