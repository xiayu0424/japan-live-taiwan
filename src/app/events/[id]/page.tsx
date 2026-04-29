import { notFound } from "next/navigation";
import { EventStatusBadge } from "@/components/EventStatusBadge";
import { TicketInfo } from "@/components/TicketInfo";
import { events, getEventById } from "@/lib/data";
import { formatDateTime } from "@/lib/date";
import { getArtistNames, getPriceRange } from "@/lib/event-utils";

export function generateStaticParams() {
  return events.map((event) => ({ id: event.id }));
}

export default function EventDetailPage({ params }: { params: { id: string } }) {
  const event = getEventById(params.id);

  if (!event) {
    notFound();
  }

  return (
    <article className="space-y-8">
      <header className="card p-8">
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <EventStatusBadge status={event.status} />
          <span className="text-sm font-bold uppercase tracking-[0.18em] text-[#c94b2f]">
            {event.event_type}
          </span>
        </div>
        <h1 className="text-4xl font-black leading-tight md:text-5xl">{event.title}</h1>
        <p className="mt-4 text-lg font-semibold text-[#5b4d43]">{getArtistNames(event)}</p>
        {event.tour_name ? <p className="mt-2 text-[#75675c]">{event.tour_name}</p> : null}
      </header>

      <div className="grid gap-6 lg:grid-cols-[1.4fr_0.9fr]">
        <section className="card p-6">
          <h2 className="mb-4 text-2xl font-black">演出資訊</h2>
          <div className="space-y-4">
            {event.shows.map((show) => (
              <div key={show.id} className="rounded-2xl border border-[#e4d6c2] bg-white/60 p-4">
                <p className="font-bold">{formatDateTime(show.start_time)}</p>
                <p className="mt-1 text-[#5b4d43]">
                  {show.city} / {show.venue_name}
                </p>
                {show.address ? (
                  <p className="mt-1 text-sm text-[#75675c]">{show.address}</p>
                ) : null}
              </div>
            ))}
          </div>
        </section>

        <section className="card p-6">
          <h2 className="mb-4 text-2xl font-black">售票資訊</h2>
          <TicketInfo ticketSales={event.ticket_sales} />
        </section>
      </div>

      <section className="card p-6">
        <h2 className="mb-4 text-2xl font-black">票價與來源</h2>
        <p className="mb-4 font-bold">{getPriceRange(event)}</p>
        {event.prices ? (
          <div className="mb-6 grid gap-3 sm:grid-cols-2 md:grid-cols-3">
            {event.prices.map((price) => (
              <div
                key={price.label}
                className="rounded-2xl border border-[#e4d6c2] bg-white/60 p-4"
              >
                <p className="font-bold">{price.label}</p>
                <p className="text-[#5b4d43]">NT${price.price.toLocaleString("zh-TW")}</p>
              </div>
            ))}
          </div>
        ) : null}
        <div className="space-y-2 text-sm text-[#5b4d43]">
          {event.sources.map((source) => (
            <p key={source.url}>
              {source.name}:{" "}
              <a
                href={source.url}
                target="_blank"
                rel="noreferrer"
                className="font-bold text-[#7e251a]"
              >
                {source.url}
              </a>
            </p>
          ))}
          <p>最後更新：{formatDateTime(event.updated_at)}</p>
        </div>
      </section>
    </article>
  );
}
