import { EventCard } from "@/components/EventCard";
import { events } from "@/lib/data";
import { sortByShowDate } from "@/lib/event-utils";

export default function EventsPage() {
  const sortedEvents = sortByShowDate(events);

  return (
    <div className="space-y-8">
      <header>
        <p className="text-sm font-bold uppercase tracking-[0.2em] text-[#c94b2f]">Events</p>
        <h1 className="mt-3 text-4xl font-black">活動列表</h1>
        <p className="mt-3 text-[#5b4d43]">目前收錄 {sortedEvents.length} 筆 sample 活動資料。</p>
      </header>
      <div className="grid gap-5 lg:grid-cols-2">
        {sortedEvents.map((event) => (
          <EventCard key={event.id} event={event} />
        ))}
      </div>
    </div>
  );
}
