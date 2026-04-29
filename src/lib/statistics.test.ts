import { describe, expect, it } from "vitest";
import { artists, events } from "@/lib/data";
import {
  getArtistTypeCounts,
  getCityCounts,
  getMonthlyPerformanceCounts,
  getPlatformCounts,
} from "@/lib/statistics";

describe("statistics helpers", () => {
  it("counts monthly performances from event shows", () => {
    expect(getMonthlyPerformanceCounts(events)).toEqual(
      expect.arrayContaining([
        { name: "2026-05", count: 1 },
        { name: "2026-06", count: 6 },
        { name: "2025-06", count: 1 },
      ]),
    );
  });

  it("counts ticket platforms and cities", () => {
    expect(getPlatformCounts(events)[0]).toEqual({ name: "KKTIX", count: 9 });
    expect(getCityCounts(events)).toEqual(
      expect.arrayContaining([
        { name: "Taipei", count: 15 },
        { name: "New Taipei", count: 4 },
      ]),
    );
  });

  it("counts artist types through event artist references", () => {
    expect(getArtistTypeCounts(events, artists)).toEqual(
      expect.arrayContaining([
        { name: "band", count: 5 },
        { name: "anisong", count: 4 },
        { name: "singer", count: 7 },
      ]),
    );
  });
});
