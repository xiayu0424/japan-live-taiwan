export type EventStatus =
  | "announced"
  | "sale_soon"
  | "on_sale"
  | "sold_out"
  | "added_show"
  | "postponed"
  | "cancelled"
  | "ended"
  | "unknown";

export type EventType =
  | "concert"
  | "festival"
  | "fanmeeting"
  | "live_house"
  | "anime_music"
  | "other";

export interface Show {
  id: string;
  date: string;
  start_time: string;
  doors_open_time?: string | null;
  city: string;
  venue_id: string;
  venue_name: string;
  address?: string;
}

export interface TicketSale {
  type: "general" | "presale" | "fanclub" | "credit_card" | "lottery" | "other";
  platform: string;
  platform_id: string;
  sale_start?: string | null;
  sale_end?: string | null;
  ticket_url: string;
  status: EventStatus;
  notes?: string;
}

export interface Price {
  label: string;
  price: number;
  currency: "TWD" | "JPY" | "USD";
}

export interface Source {
  type: "official_ticket" | "organizer" | "artist_official" | "news" | "social" | "other";
  name: string;
  url: string;
  retrieved_at: string;
}

export interface EventItem {
  id: string;
  title: string;
  artist_ids: string[];
  tour_name?: string;
  event_type: EventType;
  status: EventStatus;
  shows: Show[];
  ticket_sales: TicketSale[];
  prices?: Price[];
  organizers?: string[];
  official_url?: string;
  notes?: string;
  sources: Source[];
  created_at: string;
  updated_at: string;
}
