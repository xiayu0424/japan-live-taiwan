"""Pydantic schemas for crawler outputs."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class CandidateShow(BaseModel):
    raw_date_text: str
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    start_time: str
    city: str
    venue_name: str
    address: str | None = None


class CandidateTicketSale(BaseModel):
    type: Literal["general", "presale", "fanclub", "credit_card", "lottery", "other"]
    platform: str
    sale_start: str | None = None
    sale_end: str | None = None
    ticket_url: HttpUrl
    status: Literal[
        "announced",
        "sale_soon",
        "on_sale",
        "sold_out",
        "added_show",
        "postponed",
        "cancelled",
        "ended",
        "unknown",
    ]
    raw_sale_text: str | None = None


class CandidatePrice(BaseModel):
    label: str
    price: int
    currency: Literal["TWD", "JPY", "USD"] = "TWD"


class CandidateSource(BaseModel):
    type: Literal["official_ticket", "organizer", "artist_official", "news", "social", "other"]
    name: str
    url: HttpUrl
    retrieved_at: str


class CrawlerMeta(BaseModel):
    crawler_name: str
    retrieved_at: str
    raw_hash: str
    is_duplicate: bool = False
    duplicate_event_id: str | None = None
    review_status: Literal["pending", "approved", "rejected"] = "pending"
    review_note: str | None = None


class Candidate(BaseModel):
    candidate_id: str
    source_platform: str
    source_url: HttpUrl
    title: str
    raw_title: str
    matched_artist_ids: list[str] = Field(default_factory=list)
    matched_artist_names: list[str] = Field(default_factory=list)
    match_confidence: float = 0
    event_type: Literal["concert", "festival", "fanmeeting", "live_house", "anime_music", "other"]
    status: Literal["candidate"] = "candidate"
    shows: list[CandidateShow]
    ticket_sales: list[CandidateTicketSale]
    prices: list[CandidatePrice] = Field(default_factory=list)
    organizers: list[str] = Field(default_factory=list)
    sources: list[CandidateSource]
    crawler_meta: CrawlerMeta


class ChangeRequest(BaseModel):
    change_request_id: str
    source_platform: str
    source_url: HttpUrl
    existing_event_id: str
    detected_changes: dict[str, object]
    review_status: Literal["pending", "approved", "rejected"] = "pending"


class CrawlerReportSource(BaseModel):
    id: str
    status: Literal["success", "failed"]
    candidate_count: int
    change_request_count: int
    error: str | None = None


class CrawlerReportSummary(BaseModel):
    total_sources: int
    success_sources: int
    failed_sources: int
    total_candidates: int
    high_confidence_candidates: int
    medium_confidence_candidates: int
    low_confidence_candidates: int
    change_requests: int


class CrawlerReport(BaseModel):
    retrieved_at: str
    summary: CrawlerReportSummary
    sources: list[CrawlerReportSource]
