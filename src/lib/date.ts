import dayjs from "dayjs";

export function formatDate(date: string) {
  return dayjs(date).format("YYYY/MM/DD");
}

export function formatDateTime(date: string) {
  return dayjs(date).format("YYYY/MM/DD HH:mm");
}

export function getFirstShowDate(event: { shows: { date: string }[] }) {
  return [...event.shows].sort((a, b) => a.date.localeCompare(b.date))[0]?.date ?? "";
}

export function getFirstSaleDate(event: { ticket_sales: { sale_start?: string | null }[] }) {
  return (
    event.ticket_sales
      .map((sale) => sale.sale_start)
      .filter((date): date is string => Boolean(date))
      .sort()[0] ?? ""
  );
}
