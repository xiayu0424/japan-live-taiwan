import Link from "next/link";
import { formatDate, formatDateTime, getFirstSaleDate, getFirstShowDate } from "@/lib/date";
import { getArtistNames, getPriceRange } from "@/lib/event-utils";
import type { EventItem } from "@/types/event";
import { EventStatusBadge } from "./EventStatusBadge";

export function EventCard({ event }: { event: EventItem }) {
  const firstShow = event.shows[0];
  const firstSale = getFirstSaleDate(event);

  return (
    <article className="card flex h-full flex-col gap-5 p-6 transition hover:-translate-y-1 hover:border-[#c94b2f]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.18em] text-[#c94b2f]">
            {event.event_type}
          </p>
          <h2 className="text-2xl font-black leading-tight">
            <Link href={`/events/${event.id}`}>{event.title}</Link>
          </h2>
          <p className="mt-2 text-sm font-semibold text-[#5b4d43]">{getArtistNames(event)}</p>
        </div>
        <EventStatusBadge status={event.status} />
      </div>

      <dl className="grid gap-3 text-sm text-[#4b3a2d] sm:grid-cols-2">
        <div>
          <dt className="font-bold text-[#201813]">演出日期</dt>
          <dd>{formatDate(getFirstShowDate(event))}</dd>
        </div>
        <div>
          <dt className="font-bold text-[#201813]">城市／場館</dt>
          <dd>
            {firstShow.city} / {firstShow.venue_name}
          </dd>
        </div>
        <div>
          <dt className="font-bold text-[#201813]">票價</dt>
          <dd>{getPriceRange(event)}</dd>
        </div>
        <div>
          <dt className="font-bold text-[#201813]">最近售票</dt>
          <dd>{firstSale ? formatDateTime(firstSale) : "未定"}</dd>
        </div>
      </dl>

      <div className="mt-auto flex flex-wrap gap-3">
        <Link
          href={`/events/${event.id}`}
          className="rounded-full bg-[#201813] px-5 py-2 text-sm font-bold text-white transition hover:bg-[#7e251a]"
        >
          查看詳情
        </Link>
        <a
          href={event.ticket_sales[0]?.ticket_url}
          target="_blank"
          rel="noreferrer"
          className="rounded-full border border-[#c94b2f] px-5 py-2 text-sm font-bold text-[#7e251a] transition hover:bg-[#fff0e8]"
        >
          官方購票
        </a>
      </div>
    </article>
  );
}
