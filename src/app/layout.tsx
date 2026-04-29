import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "Japan Live Taiwan",
  description: "日系藝人來台演出資訊整理平台",
};

const navItems = [
  { href: "/", label: "首頁" },
  { href: "/events", label: "活動" },
  { href: "/calendar", label: "日曆" },
  { href: "/statistics", label: "統計" },
  { href: "/artists", label: "藝人" },
  { href: "/venues", label: "場館" },
];

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="zh-Hant-TW">
      <body>
        <header className="border-b border-[#e4d6c2]/80 bg-[#fffaf2]/80 backdrop-blur">
          <div className="shell flex flex-col gap-4 py-5 md:flex-row md:items-center md:justify-between">
            <Link href="/" className="text-2xl font-black tracking-tight text-[#12100d]">
              Japan Live Taiwan
            </Link>
            <nav className="flex flex-wrap gap-2 text-sm font-semibold text-[#4b3a2d]">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="rounded-full border border-[#e4d6c2] bg-white/60 px-4 py-2 transition hover:border-[#c94b2f] hover:text-[#7e251a]"
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>
        <main className="shell py-10">{children}</main>
      </body>
    </html>
  );
}
