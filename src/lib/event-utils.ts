import { artistById } from "@/lib/data";
import { getFirstSaleDate, getFirstShowDate } from "@/lib/date";
import type { EventItem, EventStatus } from "@/types/event";

export const statusLabels: Record<EventStatus, string> = {
  announced: "已公布",
  sale_soon: "即將開賣",
  on_sale: "已開賣",
  sold_out: "售完",
  added_show: "加場",
  postponed: "延期",
  cancelled: "取消",
  ended: "已結束",
  unknown: "狀態未知",
};

export function sortByShowDate(events: EventItem[]) {
  return [...events].sort((a, b) => getFirstShowDate(a).localeCompare(getFirstShowDate(b)));
}

export function sortBySaleDate(events: EventItem[]) {
  return [...events].sort((a, b) => getFirstSaleDate(a).localeCompare(getFirstSaleDate(b)));
}

export function getArtistNames(event: EventItem) {
  return event.artist_ids.map((id) => artistById.get(id)?.name ?? id).join(" / ");
}

export function getPriceRange(event: EventItem) {
  if (!event.prices || event.prices.length === 0) {
    return "票價未定";
  }

  const prices = event.prices.map((price) => price.price);
  const min = Math.min(...prices);
  const max = Math.max(...prices);

  if (min === max) {
    return `NT$${min.toLocaleString("zh-TW")}`;
  }

  return `NT$${min.toLocaleString("zh-TW")} - NT$${max.toLocaleString("zh-TW")}`;
}
