import type { Artist } from "@/types/artist";
import type { EventItem } from "@/types/event";

export function countBy<T>(items: T[], getKey: (item: T) => string) {
  const counts = new Map<string, number>();

  for (const item of items) {
    const key = getKey(item);
    counts.set(key, (counts.get(key) ?? 0) + 1);
  }

  return [...counts.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
}

export function getMonthlyPerformanceCounts(events: EventItem[]) {
  return countBy(
    events.flatMap((event) => event.shows),
    (show) => show.date.slice(0, 7),
  ).sort((a, b) => a.name.localeCompare(b.name));
}

export function getPlatformCounts(events: EventItem[]) {
  return countBy(
    events.flatMap((event) => event.ticket_sales),
    (sale) => sale.platform,
  );
}

export function getCityCounts(events: EventItem[]) {
  return countBy(
    events.flatMap((event) => event.shows),
    (show) => show.city,
  );
}

export function getVenueCounts(events: EventItem[]) {
  return countBy(
    events.flatMap((event) => event.shows),
    (show) => show.venue_name,
  );
}

export function getArtistTypeCounts(events: EventItem[], artists: Artist[]) {
  const artistById = new Map(artists.map((artist) => [artist.id, artist]));

  return countBy(
    events.flatMap((event) => event.artist_ids),
    (artistId) => artistById.get(artistId)?.artist_type ?? "other",
  );
}
