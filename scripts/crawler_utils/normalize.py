"""Normalization utilities used by matching and dedupe."""

from __future__ import annotations

import re
import unicodedata


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKC", value).lower()
    normalized = re.sub(r"\s+", "", normalized)
    normalized = re.sub(r"[｜|:：\-－_～~!！?？【】\[\]（）()・.,，。/／]", "", normalized)
    return normalized


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).lower()
    normalized = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", normalized)
    return normalized.strip("-")
