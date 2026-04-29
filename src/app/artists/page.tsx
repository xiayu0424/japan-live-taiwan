import Link from "next/link";
import { artists, getEventsForArtist } from "@/lib/data";

export default function ArtistsPage() {
  return (
    <div className="space-y-8">
      <header>
        <p className="text-sm font-bold uppercase tracking-[0.2em] text-[#c94b2f]">Artists</p>
        <h1 className="mt-3 text-4xl font-black">藝人列表</h1>
        <p className="mt-3 text-[#5b4d43]">依 sample catalog 彙整已收錄藝人與演出數量。</p>
      </header>
      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {artists.map((artist) => {
          const relatedEvents = getEventsForArtist(artist.id);

          return (
            <Link
              key={artist.id}
              href={`/artists/${artist.id}`}
              className="card block p-6 transition hover:-translate-y-1"
            >
              <p className="mb-2 text-xs font-bold uppercase tracking-[0.18em] text-[#c94b2f]">
                {artist.artist_type}
              </p>
              <h2 className="text-2xl font-black">{artist.name}</h2>
              <p className="mt-2 text-[#5b4d43]">
                {artist.name_ja ?? artist.name_en ?? artist.country}
              </p>
              <p className="mt-4 text-sm font-bold text-[#7e251a]">
                已收錄 {relatedEvents.length} 場
              </p>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
