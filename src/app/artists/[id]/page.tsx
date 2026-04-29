import Link from "next/link";
import { notFound } from "next/navigation";
import { EventCard } from "@/components/EventCard";
import { artists, getArtistById, getEventsForArtist } from "@/lib/data";
import { sortByShowDate } from "@/lib/event-utils";

export function generateStaticParams() {
  return artists.map((artist) => ({ id: artist.id }));
}

export default function ArtistDetailPage({ params }: { params: { id: string } }) {
  const artist = getArtistById(params.id);

  if (!artist) {
    notFound();
  }

  const relatedEvents = sortByShowDate(getEventsForArtist(artist.id));

  return (
    <div className="space-y-8">
      <header className="card p-8">
        <Link href="/artists" className="text-sm font-bold text-[#7e251a]">
          ← 返回藝人列表
        </Link>
        <p className="mt-5 text-sm font-bold uppercase tracking-[0.2em] text-[#c94b2f]">
          {artist.artist_type}
        </p>
        <h1 className="mt-3 text-4xl font-black md:text-5xl">{artist.name}</h1>
        <dl className="mt-6 grid gap-4 text-sm text-[#5b4d43] md:grid-cols-3">
          <div>
            <dt className="font-bold text-[#201813]">日文名稱</dt>
            <dd>{artist.name_ja ?? "未提供"}</dd>
          </div>
          <div>
            <dt className="font-bold text-[#201813]">國家</dt>
            <dd>{artist.country}</dd>
          </div>
          <div>
            <dt className="font-bold text-[#201813]">別名</dt>
            <dd>{artist.aliases?.join(" / ") ?? "未提供"}</dd>
          </div>
        </dl>
        {artist.official_url ? (
          <a
            href={artist.official_url}
            target="_blank"
            rel="noreferrer"
            className="mt-6 inline-flex rounded-full bg-[#201813] px-5 py-2 text-sm font-bold text-white"
          >
            官方網站
          </a>
        ) : null}
      </header>

      <section>
        <h2 className="mb-5 text-3xl font-black">已收錄演出</h2>
        <div className="grid gap-5 lg:grid-cols-2">
          {relatedEvents.map((event) => (
            <EventCard key={event.id} event={event} />
          ))}
        </div>
      </section>
    </div>
  );
}
