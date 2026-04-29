"use client";

import Fuse from "fuse.js";
import { useDeferredValue, useState } from "react";
import { EventCard } from "@/components/EventCard";
import { artists } from "@/lib/data";
import { getFirstSaleDate, getFirstShowDate } from "@/lib/date";
import { getArtistNames, getPriceRange, statusLabels } from "@/lib/event-utils";
import type { EventItem, EventStatus } from "@/types/event";

type SortMode = "showDate" | "saleDate";

const artistTypeLabels: Record<string, string> = {
  band: "Band",
  idol_group: "Idol group",
  singer: "Singer",
  voice_actor: "Voice actor",
  anisong: "Anisong",
  jpop: "J-pop",
  jrock: "J-rock",
  vocaloid: "Vocaloid",
  other: "Other",
};

export function EventExplorer({ events }: { events: EventItem[] }) {
  const [keyword, setKeyword] = useState("");
  const [city, setCity] = useState("all");
  const [platform, setPlatform] = useState("all");
  const [status, setStatus] = useState<EventStatus | "all">("all");
  const [venue, setVenue] = useState("all");
  const [artistType, setArtistType] = useState("all");
  const [priceBand, setPriceBand] = useState("all");
  const [sortMode, setSortMode] = useState<SortMode>("showDate");
  const deferredKeyword = useDeferredValue(keyword);

  const artistById = new Map(artists.map((artist) => [artist.id, artist]));
  const searchableEvents = events.map((event) => ({
    ...event,
    artist_names: getArtistNames(event),
    venue_names: event.shows.map((show) => show.venue_name).join(" "),
    cities: event.shows.map((show) => show.city).join(" "),
    platforms: event.ticket_sales.map((sale) => sale.platform).join(" "),
    price_range: getPriceRange(event),
  }));

  const fuse = new Fuse(searchableEvents, {
    keys: [
      "title",
      "tour_name",
      "artist_names",
      "venue_names",
      "cities",
      "platforms",
      "organizers",
    ],
    threshold: 0.35,
  });

  const cities = unique(events.flatMap((event) => event.shows.map((show) => show.city)));
  const platforms = unique(
    events.flatMap((event) => event.ticket_sales.map((sale) => sale.platform)),
  );
  const venues = unique(events.flatMap((event) => event.shows.map((show) => show.venue_name)));
  const artistTypes = unique(
    events.flatMap((event) =>
      event.artist_ids.map((artistId) => artistById.get(artistId)?.artist_type ?? "other"),
    ),
  );

  const baseResults = deferredKeyword.trim()
    ? fuse.search(deferredKeyword).map((result) => result.item)
    : searchableEvents;

  const filteredEvents = baseResults
    .filter((event) => city === "all" || event.shows.some((show) => show.city === city))
    .filter(
      (event) =>
        platform === "all" || event.ticket_sales.some((sale) => sale.platform === platform),
    )
    .filter((event) => status === "all" || event.status === status)
    .filter((event) => venue === "all" || event.shows.some((show) => show.venue_name === venue))
    .filter(
      (event) =>
        artistType === "all" ||
        event.artist_ids.some((artistId) => artistById.get(artistId)?.artist_type === artistType),
    )
    .filter((event) => matchesPriceBand(event, priceBand))
    .sort((a, b) => {
      if (sortMode === "saleDate") {
        return getFirstSaleDate(a).localeCompare(getFirstSaleDate(b));
      }

      return getFirstShowDate(a).localeCompare(getFirstShowDate(b));
    });

  return (
    <div className="space-y-6">
      <section className="card grid gap-4 p-5 md:grid-cols-2 xl:grid-cols-4">
        <label className="space-y-2 md:col-span-2">
          <span className="text-sm font-bold">關鍵字</span>
          <input
            value={keyword}
            onChange={(event) => setKeyword(event.target.value)}
            placeholder="搜尋活動、藝人、場館、城市、平台"
            className="w-full rounded-2xl border border-[#e4d6c2] bg-white px-4 py-3 outline-none focus:border-[#c94b2f]"
          />
        </label>
        <Select label="排序" value={sortMode} onChange={(value) => setSortMode(value as SortMode)}>
          <option value="showDate">依演出日期</option>
          <option value="saleDate">依售票時間</option>
        </Select>
        <Select label="城市" value={city} onChange={setCity}>
          <option value="all">全部城市</option>
          {cities.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </Select>
        <Select label="售票平台" value={platform} onChange={setPlatform}>
          <option value="all">全部平台</option>
          {platforms.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </Select>
        <Select
          label="活動狀態"
          value={status}
          onChange={(value) => setStatus(value as EventStatus | "all")}
        >
          <option value="all">全部狀態</option>
          {Object.entries(statusLabels).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </Select>
        <Select label="場館" value={venue} onChange={setVenue}>
          <option value="all">全部場館</option>
          {venues.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </Select>
        <Select label="藝人類型" value={artistType} onChange={setArtistType}>
          <option value="all">全部類型</option>
          {artistTypes.map((item) => (
            <option key={item} value={item}>
              {artistTypeLabels[item] ?? item}
            </option>
          ))}
        </Select>
        <Select label="票價" value={priceBand} onChange={setPriceBand}>
          <option value="all">全部票價</option>
          <option value="under2000">NT$2,000 以下</option>
          <option value="2000to4000">NT$2,000 - NT$4,000</option>
          <option value="over4000">NT$4,000 以上</option>
        </Select>
      </section>

      <p className="text-sm font-bold text-[#5b4d43]">符合條件：{filteredEvents.length} 筆</p>

      <div className="grid gap-5 lg:grid-cols-2">
        {filteredEvents.map((event) => (
          <EventCard key={event.id} event={event} />
        ))}
      </div>
    </div>
  );
}

function Select({
  label,
  value,
  onChange,
  children,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  children: React.ReactNode;
}) {
  return (
    <label className="space-y-2">
      <span className="text-sm font-bold">{label}</span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-2xl border border-[#e4d6c2] bg-white px-4 py-3 outline-none focus:border-[#c94b2f]"
      >
        {children}
      </select>
    </label>
  );
}

function unique(values: string[]) {
  return [...new Set(values)].sort((a, b) => a.localeCompare(b));
}

function matchesPriceBand(event: EventItem, priceBand: string) {
  if (priceBand === "all") {
    return true;
  }

  const prices = event.prices?.map((price) => price.price) ?? [];
  if (prices.length === 0) {
    return false;
  }

  const min = Math.min(...prices);
  const max = Math.max(...prices);

  if (priceBand === "under2000") {
    return min < 2000;
  }

  if (priceBand === "2000to4000") {
    return min <= 4000 && max >= 2000;
  }

  return max > 4000;
}
