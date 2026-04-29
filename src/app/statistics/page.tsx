import { BarChartBlock, PieChartBlock } from "@/components/ChartBlock";
import { artists, events } from "@/lib/data";
import {
  getArtistTypeCounts,
  getCityCounts,
  getMonthlyPerformanceCounts,
  getPlatformCounts,
  getVenueCounts,
} from "@/lib/statistics";

export default function StatisticsPage() {
  const prices = events.flatMap((event) => event.prices?.map((price) => price.price) ?? []);
  const averagePrice = Math.round(prices.reduce((sum, price) => sum + price, 0) / prices.length);
  const maxPrice = Math.max(...prices);
  const minPrice = Math.min(...prices);

  return (
    <div className="space-y-8">
      <header>
        <p className="text-sm font-bold uppercase tracking-[0.2em] text-[#c94b2f]">Statistics</p>
        <h1 className="mt-3 text-4xl font-black">統計分析</h1>
        <p className="mt-3 text-[#5b4d43]">所有圖表皆由靜態 JSON sample catalog 自動計算。</p>
      </header>

      <section className="grid gap-4 md:grid-cols-4">
        <Metric label="收錄活動" value={`${events.length}`} />
        <Metric label="平均票價" value={`NT$${averagePrice.toLocaleString("zh-TW")}`} />
        <Metric label="最低票價" value={`NT$${minPrice.toLocaleString("zh-TW")}`} />
        <Metric label="最高票價" value={`NT$${maxPrice.toLocaleString("zh-TW")}`} />
      </section>

      <div className="grid gap-6 xl:grid-cols-2">
        <BarChartBlock title="每月演出數量" data={getMonthlyPerformanceCounts(events)} />
        <PieChartBlock title="售票平台分布" data={getPlatformCounts(events)} />
        <BarChartBlock title="城市分布" data={getCityCounts(events)} />
        <BarChartBlock title="場館排名" data={getVenueCounts(events)} />
        <PieChartBlock title="藝人類型比例" data={getArtistTypeCounts(events, artists)} />
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="card p-5">
      <p className="text-sm font-bold text-[#75675c]">{label}</p>
      <p className="mt-2 text-3xl font-black">{value}</p>
    </div>
  );
}
