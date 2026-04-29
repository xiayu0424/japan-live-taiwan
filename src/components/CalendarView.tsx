"use client";

import Link from "next/link";
import { useState } from "react";
import { getArtistNames } from "@/lib/event-utils";
import type { EventItem } from "@/types/event";

type CalendarMode = "performance" | "ticket";

interface CalendarEntry {
  id: string;
  date: string;
  title: string;
  artistNames: string;
  eventId: string;
  meta: string;
}

export function CalendarView({ events }: { events: EventItem[] }) {
  const [mode, setMode] = useState<CalendarMode>("performance");
  const entries = buildEntries(events, mode);
  const groups = groupByMonth(entries);

  return (
    <div className="space-y-6">
      <div className="card flex flex-wrap gap-3 p-4">
        <button
          type="button"
          onClick={() => setMode("performance")}
          className={buttonClass(mode === "performance")}
        >
          演出日
        </button>
        <button
          type="button"
          onClick={() => setMode("ticket")}
          className={buttonClass(mode === "ticket")}
        >
          售票日
        </button>
      </div>

      <div className="space-y-8">
        {groups.map(([month, monthEntries]) => (
          <section key={month} className="card p-6">
            <h2 className="mb-5 text-2xl font-black">{month}</h2>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {monthEntries.map((entry) => (
                <Link
                  key={entry.id}
                  href={`/events/${entry.eventId}`}
                  className="rounded-2xl border border-[#e4d6c2] bg-white/70 p-4 transition hover:border-[#c94b2f]"
                >
                  <p className="text-sm font-bold text-[#c94b2f]">{entry.date}</p>
                  <h3 className="mt-2 text-lg font-black">{entry.title}</h3>
                  <p className="mt-1 text-sm text-[#5b4d43]">{entry.artistNames}</p>
                  <p className="mt-3 text-xs font-bold uppercase tracking-[0.16em] text-[#75675c]">
                    {entry.meta}
                  </p>
                </Link>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}

function buildEntries(events: EventItem[], mode: CalendarMode): CalendarEntry[] {
  const entries =
    mode === "performance"
      ? events.flatMap((event) =>
          event.shows.map((show) => ({
            id: `${event.id}-${show.id}`,
            date: show.date,
            title: event.title,
            artistNames: getArtistNames(event),
            eventId: event.id,
            meta: `${show.city} / ${show.venue_name}`,
          })),
        )
      : events.flatMap((event) =>
          event.ticket_sales
            .filter((sale) => sale.sale_start)
            .map((sale) => ({
              id: `${event.id}-${sale.platform_id}-${sale.sale_start}`,
              date: sale.sale_start?.slice(0, 10) ?? "",
              title: event.title,
              artistNames: getArtistNames(event),
              eventId: event.id,
              meta: `${sale.platform} / ${sale.type}`,
            })),
        );

  return entries.sort((a, b) => a.date.localeCompare(b.date));
}

function groupByMonth(entries: CalendarEntry[]) {
  const groups = new Map<string, CalendarEntry[]>();

  for (const entry of entries) {
    const month = entry.date.slice(0, 7);
    groups.set(month, [...(groups.get(month) ?? []), entry]);
  }

  return [...groups.entries()];
}

function buttonClass(active: boolean) {
  return active
    ? "rounded-full bg-[#201813] px-5 py-2 text-sm font-bold text-white"
    : "rounded-full border border-[#e4d6c2] bg-white/70 px-5 py-2 text-sm font-bold text-[#4b3a2d]";
}
