# 日系藝人來台演出資訊整理平台 — 實作計畫 README

本專案目標是建立一個整理「日本樂團／日系藝人來台演出資訊」的網站，提供演出日期、場館、票價、售票時間、售票平台、官方購票連結、資料來源與統計分析。

第一版以 **GitHub Pages + 靜態 JSON 資料 + 前端搜尋篩選** 為主，不先導入資料庫與後端服務。等資料結構與功能穩定後，再逐步擴充爬蟲、自動更新、通知系統、後台管理與資料庫。

---

## 1. 專案定位

### 1.1 網站定位

本網站不是售票平台，而是「演出資訊整理與導流平台」。

主要功能：

- 整理日系藝人來台演出資訊
- 顯示官方購票連結
- 統整售票時間、票價、場館、主辦單位
- 提供活動篩選、搜尋、日曆與統計
- 保留每筆資料來源，避免資訊來源不明

### 1.2 目標使用者

- 想追蹤日本樂團／日星／聲優／動漫音樂演出的使用者
- 想快速查詢近期台灣日系演唱會的人
- 想知道售票時間、購票平台、票價區間的人
- 想統計台灣日系演出趨勢的人

### 1.3 第一版收錄範圍

第一版建議先收錄以下類型：

- 日本樂團
- 日本歌手
- 日本偶像團體
- 日本聲優相關演出
- 動漫音樂／Anisong 演出
- 日本音樂祭、拼盤演出中的日系藝人

暫不處理：

- 非音樂性活動
- 非台灣場次
- 沒有官方來源的傳聞資訊
- 需要登入、排隊、驗證碼才能取得的售票狀態
- 自動搶票、自動排隊、自動購票功能

---

## 2. 技術架構

### 2.1 MVP 架構

```text
GitHub Repository
    ↓
Static JSON Data
    ↓
Next.js / React Frontend
    ↓
GitHub Actions Build
    ↓
GitHub Pages Deploy
```

第一版不需要後端，也不需要資料庫。活動資料先以 JSON 檔維護，前端直接讀取 JSON 後進行搜尋、篩選與統計。

### 2.2 推薦技術棧

| 類別 | 技術 | 說明 |
|---|---|---|
| Frontend | Next.js | 建議使用 App Router 或 Pages Router 均可 |
| UI | Tailwind CSS | 快速建立響應式介面 |
| Data | JSON | 第一版用靜態資料檔 |
| Deploy | GitHub Pages | 免費部署靜態網站 |
| CI/CD | GitHub Actions | 自動 build 與 deploy |
| Chart | Recharts / Chart.js | 統計頁面圖表 |
| Calendar | FullCalendar / 自製 Calendar | 顯示演出日與售票日 |
| Search | Fuse.js | 前端模糊搜尋 |
| Crawler | Python / Playwright | 第二階段使用 |
| Validation | Zod / JSON Schema | 驗證資料格式 |

---

## 3. 功能規格

## 3.1 首頁 `/`

首頁顯示近期重點資訊。

### 功能

- 即將開賣活動
- 即將演出活動
- 最新新增活動
- 售完／延期／加場標記
- 快速篩選入口

### 顯示欄位

- 活動名稱
- 藝人名稱
- 演出日期
- 城市
- 場館
- 售票平台
- 售票時間
- 活動狀態
- 購票連結

---

## 3.2 活動列表 `/events`

活動列表是網站的核心頁面。

### 功能

- 顯示所有已收錄活動
- 關鍵字搜尋
- 依日期排序
- 依售票時間排序
- 篩選活動狀態
- 篩選售票平台
- 篩選城市
- 篩選場館
- 篩選藝人類型
- 篩選票價區間

### 篩選條件

| 篩選項目 | 範例 |
|---|---|
| 城市 | 台北、新北、桃園、台中、高雄 |
| 場館 | 台北小巨蛋、Zepp New Taipei、Legacy、北流、高雄巨蛋 |
| 售票平台 | KKTIX、tixCraft、ibon、寬宏、年代、OPENTIX |
| 活動狀態 | 未開賣、已開賣、售完、延期、取消、加場 |
| 藝人類型 | band、idol_group、singer、voice_actor、anisong |
| 票價 | 最低價、最高價 |

---

## 3.3 活動詳細頁 `/events/[id]`

每個活動需要有獨立詳細頁。

### 顯示內容

- 活動名稱
- 藝人名稱
- 巡迴名稱
- 活動狀態
- 演出日期與時間
- 場館名稱
- 城市與地址
- 主辦單位
- 售票平台
- 售票時間
- 票價區間
- 票價表
- 官方購票連結
- 官方公告連結
- 資料來源
- 最後更新時間
- 更新紀錄

### 狀態標籤

```text
announced      已公布
sale_soon      即將開賣
on_sale        已開賣
sold_out       售完
added_show     加場
postponed      延期
cancelled      取消
ended          已結束
unknown        狀態未知
```

---

## 3.4 日曆頁 `/calendar`

日曆頁顯示兩種日期：

1. 演出日期
2. 售票日期

### 功能

- 月曆顯示
- 切換「演出日」與「售票日」
- 點擊活動顯示簡要資訊
- 點擊後進入活動詳細頁

### 日曆標記類型

| 類型 | 說明 |
|---|---|
| performance | 演出日期 |
| general_sale | 一般售票日期 |
| presale | 預售日期 |
| lottery | 抽選日期 |
| added_show_sale | 加場售票日期 |

---

## 3.5 統計頁 `/statistics`

統計頁是網站的差異化功能。

### 統計項目

- 每月日系演出數量
- 每年日系演出數量
- 售票平台分布
- 城市分布
- 場館排名
- 主辦單位排名
- 平均票價
- 最高票價
- 最低票價
- 藝人類型比例
- 開賣日到演出日的平均間隔

### 推薦圖表

| 統計 | 圖表類型 |
|---|---|
| 每月演出數量 | Bar Chart |
| 售票平台分布 | Donut Chart / Bar Chart |
| 城市分布 | Bar Chart |
| 票價區間 | Box Plot / Bar Chart |
| 場館排名 | Horizontal Bar Chart |
| 藝人類型比例 | Donut Chart |

---

## 3.6 藝人頁 `/artists`

列出已收錄的藝人。

### 欄位

- 藝人名稱
- 日文名稱
- 英文名稱
- 中文名稱
- 類型
- 國家
- 官方網站
- 已收錄演出數量

---

## 3.7 藝人詳細頁 `/artists/[id]`

### 顯示內容

- 藝人基本資料
- 別名 aliases
- 官方網站
- 社群連結
- 已收錄來台演出紀錄
- 未來演出
- 過去演出

---

## 3.8 場館頁 `/venues`

### 欄位

- 場館名稱
- 城市
- 地址
- 容量
- 官方網站
- 已舉辦日系演出數量

---

## 4. 資料規格

第一版使用 JSON 作為資料來源。

建議資料放在：

```text
/public/data/events.json
/public/data/artists.json
/public/data/venues.json
/public/data/platforms.json
/public/data/organizers.json
```

---

## 4.1 `events.json`

### 欄位規格

| 欄位 | 型別 | 必填 | 說明 |
|---|---|---|---|
| id | string | yes | 活動唯一 ID |
| title | string | yes | 活動名稱 |
| artist_ids | string[] | yes | 對應 artists.json |
| tour_name | string | no | 巡迴名稱 |
| event_type | string | yes | concert、festival、fanmeeting 等 |
| status | string | yes | 活動狀態 |
| shows | object[] | yes | 演出場次 |
| ticket_sales | object[] | yes | 售票資訊 |
| prices | object[] | no | 票價資訊 |
| organizers | string[] | no | 主辦單位 |
| official_url | string | no | 官方活動頁 |
| notes | string | no | 備註 |
| sources | object[] | yes | 資料來源 |
| created_at | string | yes | 建立時間 ISO 8601 |
| updated_at | string | yes | 更新時間 ISO 8601 |

### 範例

```json
[
  {
    "id": "one-ok-rock-2026-taipei",
    "title": "ONE OK ROCK DETOX Asia Tour 2026 in Taipei",
    "artist_ids": ["one-ok-rock"],
    "tour_name": "DETOX Asia Tour 2026",
    "event_type": "concert",
    "status": "on_sale",
    "shows": [
      {
        "id": "one-ok-rock-2026-taipei-0425",
        "date": "2026-04-25",
        "start_time": "2026-04-25T19:00:00+08:00",
        "doors_open_time": "2026-04-25T17:30:00+08:00",
        "city": "Taipei",
        "venue_id": "taipei-dome",
        "venue_name": "臺北大巨蛋",
        "address": "台北市信義區忠孝東路四段515號"
      }
    ],
    "ticket_sales": [
      {
        "type": "general",
        "platform": "KKTIX",
        "platform_id": "kktix",
        "sale_start": "2026-01-10T12:00:00+08:00",
        "sale_end": null,
        "ticket_url": "https://example.com/ticket",
        "status": "on_sale",
        "notes": "請以官方售票頁資訊為準"
      }
    ],
    "prices": [
      {
        "label": "一般區",
        "price": 2800,
        "currency": "TWD"
      },
      {
        "label": "搖滾區",
        "price": 6800,
        "currency": "TWD"
      }
    ],
    "organizers": ["KKLIVE Taiwan"],
    "official_url": "https://example.com/event",
    "notes": "實際資訊請以主辦單位公告為準。",
    "sources": [
      {
        "type": "official_ticket",
        "name": "KKTIX",
        "url": "https://example.com/ticket",
        "retrieved_at": "2026-04-29T12:00:00+08:00"
      }
    ],
    "created_at": "2026-04-29T12:00:00+08:00",
    "updated_at": "2026-04-29T12:00:00+08:00"
  }
]
```

---

## 4.2 `artists.json`

### 欄位規格

| 欄位 | 型別 | 必填 | 說明 |
|---|---|---|---|
| id | string | yes | 藝人唯一 ID |
| name | string | yes | 主要顯示名稱 |
| name_ja | string | no | 日文名稱 |
| name_en | string | no | 英文名稱 |
| name_zh | string | no | 中文名稱 |
| aliases | string[] | no | 別名，用於搜尋與爬蟲比對 |
| country | string | yes | 國家 |
| artist_type | string | yes | 類型 |
| official_url | string | no | 官方網站 |
| social_links | object | no | 社群連結 |

### 範例

```json
[
  {
    "id": "one-ok-rock",
    "name": "ONE OK ROCK",
    "name_ja": "ONE OK ROCK",
    "name_en": "ONE OK ROCK",
    "name_zh": "ONE OK ROCK",
    "aliases": ["ONE OK ROCK", "OOR", "ワンオクロック"],
    "country": "Japan",
    "artist_type": "band",
    "official_url": "https://www.oneokrock.com/",
    "social_links": {
      "instagram": "",
      "youtube": "",
      "x": ""
    }
  }
]
```

### artist_type 建議值

```text
band
idol_group
singer
voice_actor
anisong
jpop
jrock
vocaloid
other
```

---

## 4.3 `venues.json`

### 欄位規格

| 欄位 | 型別 | 必填 | 說明 |
|---|---|---|---|
| id | string | yes | 場館唯一 ID |
| name | string | yes | 場館名稱 |
| city | string | yes | 城市 |
| district | string | no | 行政區 |
| address | string | no | 地址 |
| capacity | number | no | 容量 |
| official_url | string | no | 官方網站 |
| google_maps_url | string | no | Google Maps 連結 |

### 範例

```json
[
  {
    "id": "zepp-new-taipei",
    "name": "Zepp New Taipei",
    "city": "New Taipei",
    "district": "新莊區",
    "address": "新北市新莊區新北大道四段3號8樓",
    "capacity": 2245,
    "official_url": "https://www.zepp.co.jp/hall/newtaipei/",
    "google_maps_url": ""
  }
]
```

---

## 4.4 `platforms.json`

### 範例

```json
[
  {
    "id": "kktix",
    "name": "KKTIX",
    "url": "https://kktix.com/"
  },
  {
    "id": "tixcraft",
    "name": "tixCraft 拓元售票",
    "url": "https://tixcraft.com/"
  },
  {
    "id": "ibon",
    "name": "ibon 售票系統",
    "url": "https://ticket.ibon.com.tw/"
  }
]
```

---

## 5. 專案目錄結構

```text
japan-live-taiwan/
├── README.md
├── package.json
├── next.config.js
├── tsconfig.json
├── tailwind.config.ts
├── postcss.config.js
├── public/
│   └── data/
│       ├── events.json
│       ├── artists.json
│       ├── venues.json
│       ├── platforms.json
│       └── organizers.json
├── src/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── events/
│   │   │   ├── page.tsx
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   ├── artists/
│   │   │   ├── page.tsx
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   ├── calendar/
│   │   │   └── page.tsx
│   │   ├── statistics/
│   │   │   └── page.tsx
│   │   └── venues/
│   │       └── page.tsx
│   ├── components/
│   │   ├── EventCard.tsx
│   │   ├── EventFilter.tsx
│   │   ├── EventStatusBadge.tsx
│   │   ├── TicketInfo.tsx
│   │   ├── CalendarView.tsx
│   │   └── ChartBlock.tsx
│   ├── lib/
│   │   ├── data.ts
│   │   ├── filters.ts
│   │   ├── statistics.ts
│   │   ├── date.ts
│   │   └── schema.ts
│   └── types/
│       ├── event.ts
│       ├── artist.ts
│       └── venue.ts
├── scripts/
│   ├── validate-data.ts
│   └── generate-statistics.ts
└── .github/
    └── workflows/
        └── deploy.yml
```

---

## 6. 前端資料型別

建議使用 TypeScript 定義資料型別。

### `src/types/event.ts`

```ts
export type EventStatus =
  | "announced"
  | "sale_soon"
  | "on_sale"
  | "sold_out"
  | "added_show"
  | "postponed"
  | "cancelled"
  | "ended"
  | "unknown";

export type EventType =
  | "concert"
  | "festival"
  | "fanmeeting"
  | "live_house"
  | "anime_music"
  | "other";

export interface Show {
  id: string;
  date: string;
  start_time: string;
  doors_open_time?: string | null;
  city: string;
  venue_id?: string;
  venue_name: string;
  address?: string;
}

export interface TicketSale {
  type: "general" | "presale" | "fanclub" | "credit_card" | "lottery" | "other";
  platform: string;
  platform_id?: string;
  sale_start?: string | null;
  sale_end?: string | null;
  ticket_url: string;
  status: EventStatus;
  notes?: string;
}

export interface Price {
  label: string;
  price: number;
  currency: "TWD" | "JPY" | "USD";
}

export interface Source {
  type: "official_ticket" | "organizer" | "artist_official" | "news" | "social" | "other";
  name: string;
  url: string;
  retrieved_at: string;
}

export interface EventItem {
  id: string;
  title: string;
  artist_ids: string[];
  tour_name?: string;
  event_type: EventType;
  status: EventStatus;
  shows: Show[];
  ticket_sales: TicketSale[];
  prices?: Price[];
  organizers?: string[];
  official_url?: string;
  notes?: string;
  sources: Source[];
  created_at: string;
  updated_at: string;
}
```

---

## 7. 建置流程

## 7.1 建立專案

```bash
npx create-next-app@latest japan-live-taiwan
cd japan-live-taiwan
```

建議選項：

```text
TypeScript: Yes
ESLint: Yes
Tailwind CSS: Yes
src/ directory: Yes
App Router: Yes
Turbopack: optional
Import alias: @/*
```

---

## 7.2 安裝套件

```bash
npm install fuse.js recharts zod dayjs clsx
```

用途：

| 套件 | 用途 |
|---|---|
| fuse.js | 前端模糊搜尋 |
| recharts | 統計圖表 |
| zod | JSON 資料驗證 |
| dayjs | 日期處理 |
| clsx | className 條件組合 |

---

## 7.3 設定 GitHub Pages 靜態輸出

### `next.config.js`

如果部署到：

```text
https://USERNAME.github.io/REPO_NAME/
```

需要設定 `basePath`。

```js
const isProd = process.env.NODE_ENV === "production";

const nextConfig = {
  output: "export",
  images: {
    unoptimized: true,
  },
  basePath: isProd ? "/japan-live-taiwan" : "",
  assetPrefix: isProd ? "/japan-live-taiwan/" : "",
};

module.exports = nextConfig;
```

如果使用自訂網域，例如：

```text
https://jlive.tw
```

可以移除 `basePath` 與 `assetPrefix`。

---

## 7.4 建立資料檔

建立：

```bash
mkdir -p public/data
```

新增：

```text
public/data/events.json
public/data/artists.json
public/data/venues.json
public/data/platforms.json
```

---

## 7.5 讀取資料

### `src/lib/data.ts`

```ts
import type { EventItem } from "@/types/event";

export async function getEvents(): Promise<EventItem[]> {
  const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_PATH || ""}/data/events.json`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to load events data");
  }

  return res.json();
}
```

若資料在 build time 讀取，也可以直接 import JSON：

```ts
import events from "../../public/data/events.json";

export function getStaticEvents() {
  return events;
}
```

---

## 8. GitHub Actions 部署

### `.github/workflows/deploy.yml`

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm

      - name: Install dependencies
        run: npm ci

      - name: Validate data
        run: npm run validate:data

      - name: Build
        run: npm run build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./out

  deploy:
    environment:
      name: github-pages
    runs-on: ubuntu-latest
    needs: build

    steps:
      - name: Deploy to GitHub Pages
        uses: actions/deploy-pages@v4
```

---

## 9. package.json scripts

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "validate:data": "tsx scripts/validate-data.ts",
    "generate:stats": "tsx scripts/generate-statistics.ts"
  }
}
```

需要安裝 `tsx`：

```bash
npm install -D tsx
```

---

## 10. 資料驗證

為避免 JSON 格式錯誤導致網站 deploy 失敗，需要建立資料驗證腳本。

### `src/lib/schema.ts`

```ts
import { z } from "zod";

export const eventStatusSchema = z.enum([
  "announced",
  "sale_soon",
  "on_sale",
  "sold_out",
  "added_show",
  "postponed",
  "cancelled",
  "ended",
  "unknown",
]);

export const eventSchema = z.object({
  id: z.string().min(1),
  title: z.string().min(1),
  artist_ids: z.array(z.string()).min(1),
  tour_name: z.string().optional(),
  event_type: z.string().min(1),
  status: eventStatusSchema,
  shows: z.array(
    z.object({
      id: z.string().min(1),
      date: z.string().min(1),
      start_time: z.string().min(1),
      doors_open_time: z.string().nullable().optional(),
      city: z.string().min(1),
      venue_id: z.string().optional(),
      venue_name: z.string().min(1),
      address: z.string().optional(),
    })
  ),
  ticket_sales: z.array(
    z.object({
      type: z.string().min(1),
      platform: z.string().min(1),
      platform_id: z.string().optional(),
      sale_start: z.string().nullable().optional(),
      sale_end: z.string().nullable().optional(),
      ticket_url: z.string().url(),
      status: eventStatusSchema,
      notes: z.string().optional(),
    })
  ),
  prices: z
    .array(
      z.object({
        label: z.string().min(1),
        price: z.number().nonnegative(),
        currency: z.string().min(1),
      })
    )
    .optional(),
  organizers: z.array(z.string()).optional(),
  official_url: z.string().url().optional(),
  notes: z.string().optional(),
  sources: z.array(
    z.object({
      type: z.string().min(1),
      name: z.string().min(1),
      url: z.string().url(),
      retrieved_at: z.string().min(1),
    })
  ),
  created_at: z.string().min(1),
  updated_at: z.string().min(1),
});

export const eventsSchema = z.array(eventSchema);
```

### `scripts/validate-data.ts`

```ts
import fs from "node:fs";
import path from "node:path";
import { eventsSchema } from "../src/lib/schema";

const eventsPath = path.join(process.cwd(), "public/data/events.json");
const raw = fs.readFileSync(eventsPath, "utf-8");
const json = JSON.parse(raw);

const result = eventsSchema.safeParse(json);

if (!result.success) {
  console.error("Invalid events.json");
  console.error(result.error.format());
  process.exit(1);
}

console.log("events.json is valid");
```

---

## 11. UI 規格

## 11.1 Event Card

活動卡片應顯示：

- 活動名稱
- 藝人名稱
- 演出日期
- 城市／場館
- 票價區間
- 售票平台
- 售票狀態
- 最近售票時間
- 官方購票按鈕

### 狀態顏色建議

| 狀態 | 顯示文字 | UI 意義 |
|---|---|---|
| announced | 已公布 | 一般資訊 |
| sale_soon | 即將開賣 | 強調 |
| on_sale | 已開賣 | 可購票 |
| sold_out | 售完 | 不可購票 |
| added_show | 加場 | 強調 |
| postponed | 延期 | 警示 |
| cancelled | 取消 | 危險 |
| ended | 已結束 | 弱化 |
| unknown | 狀態未知 | 中性 |

---

## 11.2 Search / Filter

搜尋支援：

- 活動名稱
- 藝人名稱
- 場館名稱
- 城市
- 售票平台
- 主辦單位

推薦使用 Fuse.js：

```ts
import Fuse from "fuse.js";
import type { EventItem } from "@/types/event";

export function searchEvents(events: EventItem[], keyword: string) {
  const fuse = new Fuse(events, {
    keys: ["title", "tour_name", "organizers", "shows.venue_name", "shows.city"],
    threshold: 0.35,
  });

  if (!keyword.trim()) return events;

  return fuse.search(keyword).map((result) => result.item);
}
```

---

## 12. 資料維護流程

## 12.1 第一版：人工維護

第一版先以人工新增資料為主。

流程：

```text
發現新活動
    ↓
確認官方售票頁或主辦公告
    ↓
新增 / 修改 public/data/events.json
    ↓
執行 npm run validate:data
    ↓
Commit & Push
    ↓
GitHub Actions 自動部署
```

### Commit 範例

```bash
git add public/data/events.json
git commit -m "Add ONE OK ROCK Taipei 2026 event"
git push origin main
```

---

## 12.2 第二版：半自動更新

第二版加入 crawler，但不直接自動發布到前台。

建議流程：

```text
Crawler 抓取售票網站
    ↓
產生 candidates.json
    ↓
人工檢查候選資料
    ↓
確認後合併到 events.json
    ↓
Deploy
```

建議新增：

```text
public/data/candidates.json
scripts/crawlers/kktix.py
scripts/crawlers/tixcraft.py
scripts/crawlers/ibon.py
scripts/merge-candidates.ts
```

---

## 12.3 第三版：資料庫與後台

當資料量變大後，改成：

```text
Crawler
    ↓
PostgreSQL
    ↓
Admin Dashboard
    ↓
API
    ↓
Frontend
```

第三版可使用：

- Supabase / Neon PostgreSQL
- FastAPI / Next.js API routes
- Prisma ORM
- Admin Dashboard
- 使用者收藏與通知

---

## 13. GitHub Actions 定期更新資料

若第二版要讓 GitHub Actions 定期跑 crawler，可以新增 schedule。

```yaml
name: Update event data

on:
  schedule:
    - cron: "0 0 * * *"
  workflow_dispatch:

jobs:
  update-data:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Python dependencies
        run: pip install -r requirements.txt

      - name: Run crawlers
        run: python scripts/crawlers/run_all.py

      - name: Commit updated data
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "Update event data"
          file_pattern: public/data/*.json
```

注意：

- cron 使用 UTC，不是台灣時間
- 不建議高頻率爬取售票網站
- 不要爬需要驗證碼、登入或排隊的頁面
- 不要模擬搶票行為
- 應遵守網站 robots.txt 與服務條款

---

## 14. Crawler 規格

第二階段才需要實作 crawler。

## 14.1 Crawler 目標

Crawler 只負責「發現與更新演出資訊」，不處理購票。

可抓取欄位：

- 活動名稱
- 活動 URL
- 演出時間
- 場館
- 主辦單位
- 售票時間
- 票價
- 售票平台
- 活動狀態

不可做：

- 自動登入
- 自動排隊
- 自動購票
- 繞過驗證碼
- 高頻率請求
- 儲存個人帳號資訊

## 14.2 Crawler 輸出格式

```json
[
  {
    "source": "kktix",
    "source_url": "https://example.com/event",
    "title": "Example Live in Taipei",
    "raw_date_text": "2026/05/01",
    "raw_venue_text": "Zepp New Taipei",
    "raw_price_text": "NT$2,800 / NT$3,800",
    "matched_artist_ids": ["example-artist"],
    "confidence": 85,
    "retrieved_at": "2026-04-29T12:00:00+08:00"
  }
]
```

## 14.3 藝人比對規則

使用 `artists.json` 的 aliases 做比對。

比對邏輯：

```text
活動標題
    ↓
正規化文字
    ↓
比對 artist aliases
    ↓
命中則產生 candidate
    ↓
人工確認
```

文字正規化：

- 大小寫統一
- 全形半形轉換
- 移除多餘空白
- 移除標點符號
- 日文假名、英文名與中文名 aliases 都要保留

---

## 15. SEO 規格

每個活動詳細頁需要基本 SEO。

### Metadata

```text
Title: 活動名稱｜日系藝人來台演出資訊
Description: 整理活動日期、場館、售票時間、票價與官方購票連結。
```

### 結構化資料

可考慮加入 Event structured data：

- name
- startDate
- location
- performer
- offers
- eventStatus

---

## 16. 資訊可信度規則

每筆活動必須至少有一個 source。

### source_type 優先順序

| 優先級 | 類型 | 說明 |
|---|---|---|
| 1 | official_ticket | 官方售票頁 |
| 2 | organizer | 主辦單位公告 |
| 3 | artist_official | 藝人官方網站／社群 |
| 4 | news | 新聞整理 |
| 5 | social | 非官方社群資訊 |

### 發布規則

建議只有符合以下條件之一才發布：

- 有官方售票頁
- 有主辦單位公告
- 有藝人官方公告
- 至少兩個可信來源互相佐證

不建議只根據粉專留言、論壇、未附來源的整理文發布。

---

## 17. 安全與合規

本專案只提供資訊整理，不提供自動購票或繞過售票限制的功能。

### 不實作功能

- 自動購票
- 自動排隊
- 自動填表
- 驗證碼辨識
- 多帳號搶票
- 票券轉售
- 黃牛資訊整理

### 資料使用原則

- 只摘要必要資訊
- 附上官方來源
- 不複製完整售票頁內容
- 不儲存使用者個資
- 不儲存售票平台帳號密碼
- 遵守各網站服務條款

---

## 18. 開發 Milestone

## Milestone 1：靜態資料版

目標：完成可上線的第一版。

### 任務

- [ ] 建立 Next.js 專案
- [ ] 設定 Tailwind CSS
- [ ] 設定 GitHub Pages static export
- [ ] 建立 `events.json`
- [ ] 建立 `artists.json`
- [ ] 建立 `venues.json`
- [ ] 建立活動列表頁
- [ ] 建立活動卡片元件
- [ ] 建立活動詳細頁
- [ ] 建立基本搜尋與篩選
- [ ] 建立資料驗證腳本
- [ ] 建立 GitHub Actions deploy

### 完成標準

- 可以從 GitHub Pages 開啟網站
- 至少顯示 20 筆活動資料
- 可以依城市、平台、狀態篩選
- 每筆活動都有來源連結
- JSON 格式錯誤時 deploy 會失敗

---

## Milestone 2：日曆與統計

### 任務

- [ ] 建立日曆頁
- [ ] 支援演出日顯示
- [ ] 支援售票日顯示
- [ ] 建立統計頁
- [ ] 每月演出數量圖表
- [ ] 售票平台分布圖表
- [ ] 場館排名圖表
- [ ] 城市分布圖表

### 完成標準

- 可以從日曆查看演出與售票時間
- 可以看到基本趨勢統計
- 圖表資料從 `events.json` 自動計算

---

## Milestone 3：候選資料與半自動爬蟲

### 任務

- [ ] 建立 crawler scripts
- [ ] 建立 `candidates.json`
- [ ] 建立候選活動格式
- [ ] 建立藝人 aliases 比對
- [ ] 建立人工 review 流程
- [ ] GitHub Actions 定期執行 crawler

### 完成標準

- crawler 可以產生候選資料
- 不會直接覆蓋正式 `events.json`
- 人工確認後才能發布到前台

---

## Milestone 4：後台與資料庫

### 任務

- [ ] 導入 PostgreSQL
- [ ] 建立 events 資料表
- [ ] 建立 artists 資料表
- [ ] 建立 venues 資料表
- [ ] 建立 sources 資料表
- [ ] 建立 admin dashboard
- [ ] 支援新增／編輯活動
- [ ] 支援合併重複活動
- [ ] 支援更新紀錄

### 完成標準

- 不需要手動編輯 JSON
- 可以透過後台管理活動
- 可以保留資料變更紀錄

---

## Milestone 5：通知與個人化

### 任務

- [ ] LINE / Telegram 通知
- [ ] Email 通知
- [ ] 收藏藝人
- [ ] 收藏活動
- [ ] 即將開賣提醒
- [ ] 新增活動提醒

### 完成標準

- 使用者可以追蹤特定藝人
- 售票日前可收到提醒
- 新增活動時可通知使用者

---

## 19. 本機開發

### 安裝依賴

```bash
npm install
```

### 啟動開發伺服器

```bash
npm run dev
```

### 驗證資料

```bash
npm run validate:data
```

### 建置靜態網站

```bash
npm run build
```

Next.js static export 會輸出到：

```text
out/
```

---

## 20. 部署流程

### GitHub Pages 設定

1. 到 GitHub repository
2. 進入 Settings
3. 進入 Pages
4. Source 選擇 GitHub Actions
5. Push 到 main branch
6. 等待 Actions 完成部署

### 部署指令

```bash
git add .
git commit -m "Initial MVP website"
git push origin main
```

---

## 21. 未來可擴充方向

### 21.1 資料層

- PostgreSQL
- Supabase
- Neon
- Prisma ORM
- 自動資料差異比對
- 活動變更紀錄

### 21.2 後端 API

- FastAPI
- Next.js API routes
- NestJS
- REST API
- GraphQL

### 21.3 搜尋

- Meilisearch
- Typesense
- Elasticsearch

### 21.4 通知

- Telegram Bot
- LINE Messaging API
- Email
- Web Push Notification

### 21.5 使用者功能

- 收藏藝人
- 收藏活動
- 自訂提醒時間
- 個人日曆匯出
- Google Calendar 匯入

### 21.6 資料品質

- duplicate detection
- source confidence score
- 自動偵測延期與取消
- 自動偵測加場
- 自動偵測票價變更

---

## 22. 開發優先順序建議

建議不要一開始就做完整後台與 crawler。

最推薦順序：

```text
1. 先做靜態網站
2. 手動整理 20-50 筆活動資料
3. 確認資料欄位是否足夠
4. 加入搜尋與篩選
5. 加入日曆
6. 加入統計頁
7. 再做 crawler candidate
8. 最後才導入資料庫與後台
```

原因：

- 活動資料欄位一開始很容易改
- 直接做資料庫會增加維護成本
- 售票網站格式不同，crawler 很容易花太多時間
- 先有前台才能確認使用者真正需要哪些資訊

---

## 23. 第一版最低可行產品 MVP

MVP 只需要做到：

- 首頁
- 活動列表
- 活動詳細頁
- JSON 資料
- 搜尋
- 基本篩選
- GitHub Pages 部署
- 官方來源連結

MVP 不需要：

- 登入
- 資料庫
- 後台
- 自動爬蟲
- 即時通知
- 使用者收藏

---

## 24. 專案命名建議

可考慮：

- `japan-live-taiwan`
- `jlive-tw`
- `jp-live-calendar-tw`
- `taiwan-jmusic-live`
- `jpop-live-tw`

建議 repo 名稱：

```text
japan-live-taiwan
```

網站標題：

```text
日系藝人來台演出資訊整理
```

英文副標：

```text
Japan Live Calendar Taiwan
```

---

## 25. License

建議程式碼使用 MIT License。

資料部分建議另行標示：

```text
本網站整理之活動資訊僅供參考，實際演出、票價、售票時間與購票規則請以官方售票平台與主辦單位公告為準。
```

---

## 26. Disclaimer

本網站不是售票平台，亦不提供購票、代購、轉售、自動搶票或繞過售票系統限制的功能。所有票務資訊、演出資訊與票價內容，請以官方售票平台與主辦單位公告為準。

