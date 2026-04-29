import fs from "node:fs";
import path from "node:path";
import {
  artistsSchema,
  eventsSchema,
  organizersSchema,
  platformsSchema,
  venuesSchema,
} from "../src/lib/schema";

const dataDir = path.join(process.cwd(), "public", "data");

function readJson(fileName: string) {
  return JSON.parse(fs.readFileSync(path.join(dataDir, fileName), "utf-8"));
}

function assertUnique(ids: string[], label: string) {
  const duplicates = ids.filter((id, index) => ids.indexOf(id) !== index);
  if (duplicates.length > 0) {
    throw new Error(`${label} contains duplicate IDs: ${[...new Set(duplicates)].join(", ")}`);
  }
}

const artists = artistsSchema.parse(readJson("artists.json"));
const venues = venuesSchema.parse(readJson("venues.json"));
const platforms = platformsSchema.parse(readJson("platforms.json"));
const organizers = organizersSchema.parse(readJson("organizers.json"));
const events = eventsSchema.parse(readJson("events.json"));

assertUnique(
  artists.map((artist) => artist.id),
  "artists.json",
);
assertUnique(
  venues.map((venue) => venue.id),
  "venues.json",
);
assertUnique(
  platforms.map((platform) => platform.id),
  "platforms.json",
);
assertUnique(
  organizers.map((organizer) => organizer.id),
  "organizers.json",
);
assertUnique(
  events.map((event) => event.id),
  "events.json",
);

const artistIds = new Set(artists.map((artist) => artist.id));
const venueIds = new Set(venues.map((venue) => venue.id));
const platformIds = new Set(platforms.map((platform) => platform.id));

for (const event of events) {
  for (const artistId of event.artist_ids) {
    if (!artistIds.has(artistId)) {
      throw new Error(`${event.id} references missing artist ${artistId}`);
    }
  }

  for (const show of event.shows) {
    if (!venueIds.has(show.venue_id)) {
      throw new Error(`${event.id} references missing venue ${show.venue_id}`);
    }
  }

  for (const sale of event.ticket_sales) {
    if (!platformIds.has(sale.platform_id)) {
      throw new Error(`${event.id} references missing platform ${sale.platform_id}`);
    }
  }
}

console.log(
  `Validated ${events.length} events, ${artists.length} artists, and ${venues.length} venues.`,
);
