import clsx from "clsx";
import { statusLabels } from "@/lib/event-utils";
import type { EventStatus } from "@/types/event";

const statusClasses: Record<EventStatus, string> = {
  announced: "border-slate-300 bg-slate-100 text-slate-700",
  sale_soon: "border-amber-300 bg-amber-100 text-amber-800",
  on_sale: "border-emerald-300 bg-emerald-100 text-emerald-800",
  sold_out: "border-zinc-300 bg-zinc-100 text-zinc-700",
  added_show: "border-orange-300 bg-orange-100 text-orange-800",
  postponed: "border-yellow-300 bg-yellow-100 text-yellow-800",
  cancelled: "border-red-300 bg-red-100 text-red-800",
  ended: "border-stone-300 bg-stone-100 text-stone-600",
  unknown: "border-neutral-300 bg-neutral-100 text-neutral-700",
};

export function EventStatusBadge({ status }: { status: EventStatus }) {
  return (
    <span
      className={clsx(
        "inline-flex rounded-full border px-3 py-1 text-xs font-bold",
        statusClasses[status],
      )}
    >
      {statusLabels[status]}
    </span>
  );
}
