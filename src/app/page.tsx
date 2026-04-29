import Link from "next/link";
import { EventCard } from "@/components/EventCard";
import { events } from "@/lib/data";
import { getFirstSaleDate, getFirstShowDate } from "@/lib/date";
import { sortByShowDate } from "@/lib/event-utils";

export default function HomePage() {
  const sortedEvents = sortByShowDate(events);
  const saleSoonEvents = events
    .filter((event) => event.status === "sale_soon" || event.status === "announced")
    .sort((a, b) => getFirstSaleDate(a).localeCompare(getFirstSaleDate(b)))
    .slice(0, 3);
  const upcomingEvents = sortedEvents.slice(0, 3);
  const latestEvents = [...events]
    .sort(
      (a, b) =>
        b.created_at.localeCompare(a.created_at) ||
        getFirstShowDate(a).localeCompare(getFirstShowDate(b)),
    )
    .slice(0, 3);

  return (
    <div className="space-y-12">
      <section className="card overflow-hidden p-8 md:p-12">
        <p className="mb-4 text-sm font-bold uppercase tracking-[0.25em] text-[#c94b2f]">
          Static MVP
        </p>
        <h1 className="max-w-3xl text-4xl font-black leading-tight md:text-6xl">
          日系藝人來台演出資訊整理平台
        </h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-[#5b4d43]">
          整合演出日期、場館、票價、售票時間、售票平台與官方來源，提供搜尋、篩選、日曆與統計分析。
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link href="/events" className="rounded-full bg-[#201813] px-6 py-3 font-bold text-white">
            瀏覽活動
          </Link>
          <Link
            href="/calendar"
            className="rounded-full border border-[#c94b2f] px-6 py-3 font-bold text-[#7e251a]"
          >
            查看日曆
          </Link>
        </div>
      </section>

      <EventSection title="即將開賣活動" events={saleSoonEvents} />
      <EventSection title="即將演出活動" events={upcomingEvents} />
      <EventSection title="最新新增活動" events={latestEvents} />
    </div>
  );
}

function EventSection({
  title,
  events,
}: {
  title: string;
  events: typeof import("@/lib/data").events;
}) {
  return (
    <section>
      <div className="mb-5 flex items-end justify-between gap-4">
        <h2 className="text-3xl font-black">{title}</h2>
        <Link href="/events" className="text-sm font-bold text-[#7e251a]">
          全部活動
        </Link>
      </div>
      <div className="grid gap-5 md:grid-cols-3">
        {events.map((event) => (
          <EventCard key={event.id} event={event} />
        ))}
      </div>
    </section>
  );
}
