import { z } from "zod";

export const eventStatusSchema = z.enum([
  "announced",
  "sale_soon",
  "on_sale",
  "sold_out",
  "added_show",
  "postponed",
  "cancelled",
  "ended",
  "unknown",
]);

export const eventTypeSchema = z.enum([
  "concert",
  "festival",
  "fanmeeting",
  "live_house",
  "anime_music",
  "other",
]);

export const artistTypeSchema = z.enum([
  "band",
  "idol_group",
  "singer",
  "voice_actor",
  "anisong",
  "jpop",
  "jrock",
  "vocaloid",
  "other",
]);

const optionalUrl = z.string().url().optional();

export const artistSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  name_ja: z.string().optional(),
  name_en: z.string().optional(),
  name_zh: z.string().optional(),
  aliases: z.array(z.string()).optional(),
  country: z.string().min(1),
  artist_type: artistTypeSchema,
  official_url: optionalUrl,
  social_links: z.record(z.string(), z.string()).optional(),
});

export const venueSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  city: z.string().min(1),
  district: z.string().optional(),
  address: z.string().optional(),
  capacity: z.number().nonnegative().optional(),
  official_url: optionalUrl,
  google_maps_url: optionalUrl,
});

export const platformSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  official_url: z.string().url(),
});

export const organizerSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  official_url: optionalUrl,
});

export const eventSchema = z.object({
  id: z.string().min(1),
  title: z.string().min(1),
  artist_ids: z.array(z.string()).min(1),
  tour_name: z.string().optional(),
  event_type: eventTypeSchema,
  status: eventStatusSchema,
  shows: z
    .array(
      z.object({
        id: z.string().min(1),
        date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
        start_time: z.string().datetime({ offset: true }),
        doors_open_time: z.string().datetime({ offset: true }).nullable().optional(),
        city: z.string().min(1),
        venue_id: z.string().min(1),
        venue_name: z.string().min(1),
        address: z.string().optional(),
      }),
    )
    .min(1),
  ticket_sales: z
    .array(
      z.object({
        type: z.enum(["general", "presale", "fanclub", "credit_card", "lottery", "other"]),
        platform: z.string().min(1),
        platform_id: z.string().min(1),
        sale_start: z.string().datetime({ offset: true }).nullable().optional(),
        sale_end: z.string().datetime({ offset: true }).nullable().optional(),
        ticket_url: z.string().url(),
        status: eventStatusSchema,
        notes: z.string().optional(),
      }),
    )
    .min(1),
  prices: z
    .array(
      z.object({
        label: z.string().min(1),
        price: z.number().nonnegative(),
        currency: z.enum(["TWD", "JPY", "USD"]),
      }),
    )
    .optional(),
  organizers: z.array(z.string()).optional(),
  official_url: optionalUrl,
  notes: z.string().optional(),
  sources: z
    .array(
      z.object({
        type: z.enum([
          "official_ticket",
          "organizer",
          "artist_official",
          "news",
          "social",
          "other",
        ]),
        name: z.string().min(1),
        url: z.string().url(),
        retrieved_at: z.string().datetime({ offset: true }),
      }),
    )
    .min(1),
  created_at: z.string().datetime({ offset: true }),
  updated_at: z.string().datetime({ offset: true }),
});

export const artistsSchema = z.array(artistSchema);
export const venuesSchema = z.array(venueSchema);
export const platformsSchema = z.array(platformSchema);
export const organizersSchema = z.array(organizerSchema);
export const eventsSchema = z.array(eventSchema);
