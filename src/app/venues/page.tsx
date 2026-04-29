import { events, venues } from "@/lib/data";

export default function VenuesPage() {
  return (
    <div className="space-y-8">
      <header>
        <p className="text-sm font-bold uppercase tracking-[0.2em] text-[#c94b2f]">Venues</p>
        <h1 className="mt-3 text-4xl font-black">場館列表</h1>
        <p className="mt-3 text-[#5b4d43]">整理各城市常見演出場館與已收錄活動數。</p>
      </header>
      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {venues.map((venue) => {
          const eventCount = events.filter((event) =>
            event.shows.some((show) => show.venue_id === venue.id),
          ).length;

          return (
            <article key={venue.id} className="card p-6">
              <p className="mb-2 text-xs font-bold uppercase tracking-[0.18em] text-[#c94b2f]">
                {venue.city}
              </p>
              <h2 className="text-2xl font-black">{venue.name}</h2>
              <p className="mt-2 text-sm text-[#5b4d43]">{venue.address ?? venue.district}</p>
              <dl className="mt-5 grid grid-cols-2 gap-3 text-sm">
                <div>
                  <dt className="font-bold">容量</dt>
                  <dd>{venue.capacity?.toLocaleString("zh-TW") ?? "未提供"}</dd>
                </div>
                <div>
                  <dt className="font-bold">收錄演出</dt>
                  <dd>{eventCount} 場</dd>
                </div>
              </dl>
              {venue.official_url ? (
                <a
                  href={venue.official_url}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-5 inline-flex text-sm font-bold text-[#7e251a]"
                >
                  官方網站
                </a>
              ) : null}
            </article>
          );
        })}
      </div>
    </div>
  );
}
