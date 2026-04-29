"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useEffect, useState } from "react";

interface ChartDatum {
  name: string;
  count: number;
}

const colors = ["#c94b2f", "#2f6f73", "#d99b35", "#6c4a2d", "#8f6f4f", "#415a77"];

export function BarChartBlock({ title, data }: { title: string; data: ChartDatum[] }) {
  const mounted = useMounted();

  return (
    <section className="card p-6">
      <h2 className="mb-5 text-2xl font-black">{title}</h2>
      <div className="h-72">
        {mounted ? (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid stroke="#e4d6c2" strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#c94b2f" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <ChartPlaceholder />
        )}
      </div>
    </section>
  );
}

export function PieChartBlock({ title, data }: { title: string; data: ChartDatum[] }) {
  const mounted = useMounted();

  return (
    <section className="card p-6">
      <h2 className="mb-5 text-2xl font-black">{title}</h2>
      <div className="h-72">
        {mounted ? (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                dataKey="count"
                nameKey="name"
                innerRadius={55}
                outerRadius={95}
                label
              >
                {data.map((entry, index) => (
                  <Cell key={entry.name} fill={colors[index % colors.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <ChartPlaceholder />
        )}
      </div>
    </section>
  );
}

function useMounted() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const frame = requestAnimationFrame(() => setMounted(true));
    return () => cancelAnimationFrame(frame);
  }, []);

  return mounted;
}

function ChartPlaceholder() {
  return <div className="h-full rounded-2xl border border-dashed border-[#e4d6c2] bg-white/40" />;
}
