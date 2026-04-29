import { formatDateTime } from "@/lib/date";
import type { TicketSale } from "@/types/event";

export function TicketInfo({ ticketSales }: { ticketSales: TicketSale[] }) {
  return (
    <div className="space-y-3">
      {ticketSales.map((sale) => (
        <a
          key={`${sale.platform_id}-${sale.type}-${sale.sale_start ?? "na"}`}
          href={sale.ticket_url}
          target="_blank"
          rel="noreferrer"
          className="block rounded-2xl border border-[#e4d6c2] bg-white/70 p-4 transition hover:border-[#c94b2f]"
        >
          <div className="flex items-center justify-between gap-4">
            <strong>{sale.platform}</strong>
            <span className="text-sm text-[#75675c]">{sale.type}</span>
          </div>
          <p className="mt-2 text-sm text-[#5b4d43]">
            {sale.sale_start ? formatDateTime(sale.sale_start) : "售票時間未定"}
          </p>
          {sale.notes ? <p className="mt-2 text-xs text-[#75675c]">{sale.notes}</p> : null}
        </a>
      ))}
    </div>
  );
}
