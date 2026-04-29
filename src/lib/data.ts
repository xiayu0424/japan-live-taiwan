import artistsJson from "../../public/data/artists.json";
import eventsJson from "../../public/data/events.json";
import organizersJson from "../../public/data/organizers.json";
import platformsJson from "../../public/data/platforms.json";
import venuesJson from "../../public/data/venues.json";
import type { Artist } from "@/types/artist";
import type { EventItem } from "@/types/event";
import type { Organizer, Platform } from "@/types/platform";
import type { Venue } from "@/types/venue";

export const events = eventsJson as EventItem[];
export const artists = artistsJson as Artist[];
export const venues = venuesJson as Venue[];
export const platforms = platformsJson as Platform[];
export const organizers = organizersJson as Organizer[];

export const artistById = new Map(artists.map((artist) => [artist.id, artist]));
export const venueById = new Map(venues.map((venue) => [venue.id, venue]));
export const platformById = new Map(platforms.map((platform) => [platform.id, platform]));

export function getEventById(id: string) {
  return events.find((event) => event.id === id);
}

export function getArtistById(id: string) {
  return artists.find((artist) => artist.id === id);
}

export function getEventsForArtist(artistId: string) {
  return events.filter((event) => event.artist_ids.includes(artistId));
}

export function getDisplayArtists(event: EventItem) {
  return event.artist_ids.map((id) => artistById.get(id)?.name ?? id);
}
