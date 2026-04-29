import { CalendarView } from "@/components/CalendarView";
import { events } from "@/lib/data";
import { sortByShowDate } from "@/lib/event-utils";

export default function CalendarPage() {
  return (
    <div className="space-y-8">
      <header>
        <p className="text-sm font-bold uppercase tracking-[0.2em] text-[#c94b2f]">Calendar</p>
        <h1 className="mt-3 text-4xl font-black">活動日曆</h1>
        <p className="mt-3 text-[#5b4d43]">切換演出日與售票日，快速查看即將到來的重點日期。</p>
      </header>
      <CalendarView events={sortByShowDate(events)} />
    </div>
  );
}
