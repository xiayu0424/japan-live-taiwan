import { describe, expect, it } from "vitest";
import { artists, events, platforms, venues } from "@/lib/data";
import { artistsSchema, eventsSchema, platformsSchema, venuesSchema } from "@/lib/schema";

describe("static data schemas", () => {
  it("validates the sample event catalog", () => {
    expect(eventsSchema.parse(events)).toHaveLength(20);
    expect(artistsSchema.parse(artists)).toHaveLength(10);
    expect(venuesSchema.parse(venues)).toHaveLength(6);
    expect(platformsSchema.parse(platforms)).toHaveLength(5);
  });

  it("rejects events without sources", () => {
    const invalidEvent = { ...events[0], sources: [] };

    expect(() => eventsSchema.parse([invalidEvent])).toThrow();
  });
});
