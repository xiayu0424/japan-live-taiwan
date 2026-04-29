# Crawler Plan — Japan Live Taiwan

本文件規劃 `japan-live-taiwan` 專案的自動爬蟲流程。  
目前專案已完成初步前端，因此下一階段重點是建立一套安全、可維護、可人工審核的 crawler pipeline，用來自動蒐集「日本樂團／日系藝人來台演出」的候選活動資料。

---

## 1. 設計目標

Crawler 的第一版目標不是完全自動上架資料，而是作為「候選活動產生器」。

建議流程如下：

```text
售票平台 / 主辦單位來源
    ↓
Crawler 抓取公開活動資訊
    ↓
Parser 解析成統一格式
    ↓
Artist alias matching
    ↓
Duplicate detection
    ↓
產生 candidates.json / change_requests.json
    ↓
GitHub Actions 自動開 Pull Request
    ↓
人工 review
    ↓
合併到正式 events.json
    ↓
前端網站更新
```

核心原則：

- crawler 不直接修改正式 `events.json`
- crawler 不自動發布到前台
- crawler 只整理公開資訊
- crawler 不登入、不排隊、不購票、不繞過驗證碼
- 所有候選資料必須經過人工 review

---

## 2. Crawler 應該負責的事情

Crawler 應該負責：

- 掃描售票平台或主辦單位活動列表
- 擷取可能的日系演出資訊
- 擷取活動標題、日期、場館、售票連結、票價、主辦單位
- 比對 `artists.json` 中的藝人 aliases
- 產生候選活動 `candidates.json`
- 比對既有 `events.json`
- 偵測可能的加場、延期、取消、售完、票價變更
- 產生 `change_requests.json`
- 產生 `crawler_report.json`

Crawler 不應該負責：

- 自動購票
- 自動登入售票平台
- 自動排隊
- 自動填表
- 驗證碼辨識
- 繞過售票平台限制
- 高頻率刷新售票頁
- 直接更改正式活動資料
- 直接上架新活動

---

## 3. 建議技術棧

### 3.1 Python Crawler Stack

建議使用：

```text
Python + requests + BeautifulSoup + Playwright
```

原因：

- `requests` 適合抓取靜態 HTML
- `BeautifulSoup` 適合解析 HTML
- `Playwright` 適合處理需要 JS render 的頁面
- Python 適合資料清洗、日期解析與 JSON 處理
- 之後可以平滑銜接 PostgreSQL / Supabase / FastAPI

### 3.2 Python 套件

建議 `requirements.txt`：

```txt
requests
beautifulsoup4
lxml
playwright
pydantic
python-dateutil
rapidfuzz
pyyaml
```

安裝方式：

```bash
pip install -r requirements.txt
playwright install chromium
```

套件用途：

| 套件 | 用途 |
|---|---|
| requests | 抓取靜態頁面 |
| beautifulsoup4 | HTML 解析 |
| lxml | HTML parser backend |
| playwright | 動態頁面抓取 |
| pydantic | 資料格式驗證 |
| python-dateutil | 日期解析 |
| rapidfuzz | 藝人名稱 fuzzy matching |
| pyyaml | 讀取 YAML 設定檔 |

---

## 4. 建議專案目錄結構

在現有前端專案中加入以下 crawler 結構：

```text
japan-live-taiwan/
├── public/
│   └── data/
│       ├── events.json
│       ├── artists.json
│       ├── venues.json
│       ├── platforms.json
│       ├── candidates.json
│       ├── change_requests.json
│       └── crawler_report.json
├── scripts/
│   ├── crawlers/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── run_all.py
│   │   ├── kktix.py
│   │   ├── tixcraft.py
│   │   ├── ibon.py
│   │   ├── livenation.py
│   │   └── kklive.py
│   ├── crawler_utils/
│   │   ├── __init__.py
│   │   ├── normalize.py
│   │   ├── match_artist.py
│   │   ├── dedupe.py
│   │   ├── date_parser.py
│   │   ├── price_parser.py
│   │   ├── schemas.py
│   │   └── io.py
│   ├── configs/
│   │   └── crawler_sources.yaml
│   └── review/
│       ├── merge_candidate.py
│       └── reject_candidate.py
├── data_raw/
│   └── .gitkeep
├── requirements.txt
└── .github/
    └── workflows/
        └── crawl-events.yml
```

### 4.1 `public/data/`

前端可讀取的靜態資料。

| 檔案 | 用途 |
|---|---|
| `events.json` | 正式活動資料 |
| `artists.json` | 藝人資料與 aliases |
| `venues.json` | 場館資料 |
| `platforms.json` | 售票平台資料 |
| `candidates.json` | crawler 產生的候選活動 |
| `change_requests.json` | crawler 偵測到的既有活動變更 |
| `crawler_report.json` | crawler 執行摘要與錯誤報告 |

### 4.2 `scripts/crawlers/`

每個平台一個 crawler：

| 檔案 | 用途 |
|---|---|
| `base.py` | crawler 抽象介面 |
| `run_all.py` | 執行所有 crawler |
| `kktix.py` | KKTIX crawler |
| `tixcraft.py` | tixCraft crawler |
| `ibon.py` | ibon crawler |
| `livenation.py` | Live Nation Taiwan crawler |
| `kklive.py` | KKLIVE crawler |

### 4.3 `scripts/crawler_utils/`

共用工具：

| 檔案 | 用途 |
|---|---|
| `normalize.py` | 文字正規化 |
| `match_artist.py` | 藝人 aliases 比對 |
| `dedupe.py` | 重複活動偵測 |
| `date_parser.py` | 日期解析 |
| `price_parser.py` | 票價解析 |
| `schemas.py` | Pydantic schema |
| `io.py` | JSON 讀寫工具 |

---

## 5. 資料輸出設計

Crawler 不直接輸出正式活動，而是輸出候選活動。

正式活動：

```text
public/data/events.json
```

候選活動：

```text
public/data/candidates.json
```

既有活動變更：

```text
public/data/change_requests.json
```

執行報告：

```text
public/data/crawler_report.json
```

---

## 6. `candidates.json` 規格

### 6.1 欄位說明

| 欄位 | 型別 | 必填 | 說明 |
|---|---|---|---|
| candidate_id | string | yes | 候選活動唯一 ID |
| source_platform | string | yes | 來源平台 |
| source_url | string | yes | 來源 URL |
| title | string | yes | 正規化後活動標題 |
| raw_title | string | yes | 原始標題 |
| matched_artist_ids | string[] | yes | 命中的 artist IDs |
| matched_artist_names | string[] | yes | 命中的藝人名稱 |
| match_confidence | number | yes | 藝人比對信心分數 |
| event_type | string | yes | 活動類型 |
| status | string | yes | candidate 狀態 |
| shows | object[] | yes | 演出場次 |
| ticket_sales | object[] | yes | 售票資訊 |
| prices | object[] | no | 票價資訊 |
| organizers | string[] | no | 主辦單位 |
| sources | object[] | yes | 資料來源 |
| crawler_meta | object | yes | crawler metadata |

### 6.2 範例

```json
[
  {
    "candidate_id": "kktix-20260712-example-band-live-taipei",
    "source_platform": "kktix",
    "source_url": "https://example.com/events/example-band-live",
    "title": "Example Band Live in Taipei 2026",
    "raw_title": "Example Band Live in Taipei 2026",
    "matched_artist_ids": ["example-band"],
    "matched_artist_names": ["Example Band"],
    "match_confidence": 92,
    "event_type": "concert",
    "status": "candidate",
    "shows": [
      {
        "raw_date_text": "2026/07/12 19:00",
        "date": "2026-07-12",
        "start_time": "2026-07-12T19:00:00+08:00",
        "city": "Taipei",
        "venue_name": "Zepp New Taipei",
        "address": null
      }
    ],
    "ticket_sales": [
      {
        "type": "general",
        "platform": "KKTIX",
        "sale_start": "2026-05-01T12:00:00+08:00",
        "sale_end": null,
        "ticket_url": "https://example.com/events/example-band-live",
        "status": "unknown",
        "raw_sale_text": "2026/05/01 12:00 開賣"
      }
    ],
    "prices": [
      {
        "label": "全區",
        "price": 2800,
        "currency": "TWD"
      }
    ],
    "organizers": ["Example Organizer"],
    "sources": [
      {
        "type": "official_ticket",
        "name": "KKTIX",
        "url": "https://example.com/events/example-band-live",
        "retrieved_at": "2026-04-29T12:00:00+08:00"
      }
    ],
    "crawler_meta": {
      "crawler_name": "kktix",
      "retrieved_at": "2026-04-29T12:00:00+08:00",
      "raw_hash": "sha256-xxxx",
      "is_duplicate": false,
      "duplicate_event_id": null,
      "review_status": "pending",
      "review_note": null
    }
  }
]
```

---

## 7. `change_requests.json` 規格

當 crawler 發現候選資料與既有 `events.json` 的活動高度相似時，不應該新增候選活動，而應產生 change request。

### 7.1 適用情境

- 票價更新
- 售票時間更新
- 活動狀態更新
- 場館異動
- 日期異動
- 加場
- 延期
- 取消
- 售完

### 7.2 範例

```json
[
  {
    "change_id": "change-one-ok-rock-2026-taipei-001",
    "event_id": "one-ok-rock-2026-taipei",
    "source_platform": "kktix",
    "source_url": "https://example.com/ticket",
    "changes": [
      {
        "field": "status",
        "old_value": "sale_soon",
        "new_value": "on_sale"
      },
      {
        "field": "prices",
        "old_value": "2800-6800",
        "new_value": "2800-7200"
      }
    ],
    "retrieved_at": "2026-04-29T12:00:00+08:00",
    "review_status": "pending"
  }
]
```

---

## 8. `crawler_report.json` 規格

Crawler 每次執行都應產生報告，方便在 GitHub Actions 或前端 admin 頁面檢查。

### 8.1 範例

```json
{
  "retrieved_at": "2026-04-29T12:00:00+08:00",
  "summary": {
    "total_sources": 4,
    "success_sources": 3,
    "failed_sources": 1,
    "total_candidates": 12,
    "high_confidence_candidates": 5,
    "medium_confidence_candidates": 4,
    "low_confidence_candidates": 3,
    "change_requests": 2
  },
  "sources": [
    {
      "id": "kktix",
      "status": "success",
      "candidate_count": 6,
      "change_request_count": 1,
      "error": null
    },
    {
      "id": "tixcraft",
      "status": "failed",
      "candidate_count": 0,
      "change_request_count": 0,
      "error": "Timeout while loading activity page"
    }
  ]
}
```

---

## 9. Crawler 設定檔

建議把來源放在 YAML 設定檔，而不是寫死在程式碼中。

### `scripts/configs/crawler_sources.yaml`

```yaml
sources:
  - id: kktix
    name: KKTIX
    enabled: true
    type: ticket_platform
    crawler: kktix
    base_url: "https://kktix.com"
    list_urls:
      - "https://kktix.com/events"
    request_interval_seconds: 3
    use_playwright: false

  - id: tixcraft
    name: tixCraft
    enabled: true
    type: ticket_platform
    crawler: tixcraft
    base_url: "https://tixcraft.com"
    list_urls:
      - "https://tixcraft.com/activity"
    request_interval_seconds: 5
    use_playwright: true

  - id: livenation_tw
    name: Live Nation Taiwan
    enabled: true
    type: organizer
    crawler: livenation
    base_url: "https://www.livenation.com.tw"
    list_urls:
      - "https://www.livenation.com.tw"
    request_interval_seconds: 5
    use_playwright: true
```

---

## 10. Base Crawler Interface

### `scripts/crawlers/base.py`

```python
from abc import ABC, abstractmethod
from typing import Any


class BaseCrawler(ABC):
    def __init__(self, source_config: dict[str, Any]):
        self.source_config = source_config

    @abstractmethod
    def crawl(self) -> list[dict[str, Any]]:
        """
        Return normalized candidate-like dictionaries.
        """
        raise NotImplementedError
```

每個平台 crawler 都應該繼承 `BaseCrawler`，並輸出相同格式的 raw candidate。

---

## 11. Crawler 主流程

### `scripts/crawlers/run_all.py`

建議流程：

```text
讀取 crawler_sources.yaml
    ↓
讀取 artists.json
    ↓
讀取 events.json
    ↓
執行 enabled crawler
    ↓
取得 raw candidates
    ↓
artist alias matching
    ↓
duplicate detection
    ↓
change detection
    ↓
schema validation
    ↓
輸出 candidates.json
    ↓
輸出 change_requests.json
    ↓
輸出 crawler_report.json
```

簡化範例：

```python
import json
from pathlib import Path

from scripts.crawler_utils.match_artist import match_artists
from scripts.crawler_utils.dedupe import mark_duplicates
from scripts.crawlers.kktix import KktixCrawler
from scripts.crawlers.tixcraft import TixcraftCrawler


ROOT = Path(__file__).resolve().parents[2]

EVENTS_PATH = ROOT / "public/data/events.json"
ARTISTS_PATH = ROOT / "public/data/artists.json"
CANDIDATES_PATH = ROOT / "public/data/candidates.json"


def load_json(path: Path):
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main():
    artists = load_json(ARTISTS_PATH)
    existing_events = load_json(EVENTS_PATH)

    crawlers = [
        KktixCrawler({"id": "kktix", "name": "KKTIX"}),
        TixcraftCrawler({"id": "tixcraft", "name": "tixCraft"}),
    ]

    all_candidates = []

    for crawler in crawlers:
        try:
            candidates = crawler.crawl()
            all_candidates.extend(candidates)
        except Exception as exc:
            print(f"[ERROR] crawler failed: {crawler.__class__.__name__}: {exc}")

    matched_candidates = []
    for candidate in all_candidates:
        matched = match_artists(candidate, artists)
        matched_candidates.append(matched)

    deduped_candidates = mark_duplicates(matched_candidates, existing_events)

    save_json(CANDIDATES_PATH, deduped_candidates)

    print(f"Generated {len(deduped_candidates)} candidates")


if __name__ == "__main__":
    main()
```

執行方式：

```bash
python -m scripts.crawlers.run_all
```

---

## 12. Artist Alias Matching

藝人比對是 crawler 品質的核心。

### 12.1 `artists.json` 建議格式

```json
[
  {
    "id": "one-ok-rock",
    "name": "ONE OK ROCK",
    "name_ja": "ONE OK ROCK",
    "name_en": "ONE OK ROCK",
    "name_zh": "ONE OK ROCK",
    "aliases": [
      "ONE OK ROCK",
      "OOR",
      "ワンオクロック"
    ],
    "country": "Japan",
    "artist_type": "band"
  }
]
```

### 12.2 比對規則

優先順序：

```text
1. title 完全包含 alias
2. title 正規化後包含 alias
3. title fuzzy match alias
4. organizer / description 提到 Japan、J-pop、日本、日系
```

### 12.3 信心分數建議

| match_confidence | 處理方式 |
|---:|---|
| 95-100 | 幾乎確定，高優先 review |
| 85-94 | 可能正確，需要人工確認 |
| 60-84 | 低信心候選，可輸出但不自動採用 |
| < 60 | 不輸出，或只記錄在 debug log |

### 12.4 `match_artist.py` 範例

```python
import re
from rapidfuzz import fuzz


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[｜|:：\-－_～~!！?？【】\[\]（）()]", "", text)
    return text


def match_artists(candidate: dict, artists: list[dict]) -> dict:
    title = candidate.get("title", "")
    normalized_title = normalize_text(title)

    matches = []

    for artist in artists:
        aliases = [artist.get("name", "")]
        aliases += artist.get("aliases", [])

        best_score = 0

        for alias in aliases:
            if not alias:
                continue

            normalized_alias = normalize_text(alias)

            if normalized_alias and normalized_alias in normalized_title:
                best_score = max(best_score, 100)
            else:
                score = fuzz.partial_ratio(normalized_alias, normalized_title)
                best_score = max(best_score, score)

        if best_score >= 85:
            matches.append({
                "artist_id": artist["id"],
                "artist_name": artist["name"],
                "score": best_score,
            })

    candidate["matched_artist_ids"] = [m["artist_id"] for m in matches]
    candidate["matched_artist_names"] = [m["artist_name"] for m in matches]
    candidate["match_confidence"] = max([m["score"] for m in matches], default=0)

    return candidate
```

---

## 13. Duplicate Detection

不同來源可能抓到同一個活動，例如售票平台、主辦單位、藝人官網都公告同一場演出。

### 13.1 判斷依據

建議依照以下特徵做比對：

```text
artist_ids 相同
+ 日期相近
+ 場館相似
+ 標題相似
```

### 13.2 Event Key

可以先使用簡單 key：

```python
event_key = f"{artist_id}-{date}-{venue_name}"
```

### 13.3 Duplicate metadata

如果 candidate 可能已存在正式資料中，標記：

```json
"crawler_meta": {
  "is_duplicate": true,
  "duplicate_event_id": "one-ok-rock-2026-taipei",
  "review_status": "pending"
}
```

不要直接丟掉 duplicate，因為 duplicate 可能代表：

- 多一個官方來源
- 票價更新
- 售票時間更新
- 加場
- 延期
- 售完
- 取消

---

## 14. Change Detection

若 crawler 發現 candidate 與既有 event 高度相似，應該轉為 change request。

### 14.1 建議偵測欄位

| 欄位 | 說明 |
|---|---|
| `status` | 活動狀態 |
| `ticket_sales.sale_start` | 售票開始時間 |
| `ticket_sales.status` | 售票狀態 |
| `prices` | 票價 |
| `shows` | 演出場次 |
| `venue_name` | 場館 |
| `official_url` | 官方連結 |
| `organizers` | 主辦單位 |

### 14.2 輸出策略

- 新活動 → `candidates.json`
- 與既有活動相同但有差異 → `change_requests.json`
- 低信心或資料不足 → `crawler_report.json` debug section

---

## 15. 平台開發順序

不要一開始同時開發所有售票平台。

### 15.1 第一批

建議先做資料較容易取得的來源：

```text
1. KKTIX
2. Live Nation Taiwan
3. KKLIVE / 主辦單位活動頁
```

### 15.2 第二批

再逐步加入：

```text
4. tixCraft
5. ibon
6. 寬宏
7. 年代
8. OPENTIX
```

### 15.3 選擇來源的判斷標準

優先選擇：

- 有公開列表頁
- 不需要登入
- 不需要排隊
- 不需要驗證碼
- HTML 結構穩定
- 能取得活動頁 URL
- 能取得活動日期與場館

---

## 16. GitHub Actions 自動執行

建議 crawler 透過 GitHub Actions 定期執行，並自動開 PR，而不是直接 commit 到 `main`。

### 16.1 建議頻率

| 階段 | 頻率 |
|---|---|
| 開發測試 | 手動執行 |
| MVP 上線後 | 每天 1 次 |
| 活動密集期 | 每天 2 次 |
| 售票日前後 | 不高頻刷新 |
| 搶票時間 | 不執行 crawler |

### 16.2 `.github/workflows/crawl-events.yml`

```yaml
name: Crawl event candidates

on:
  schedule:
    # UTC 00:00 = Taiwan 08:00
    - cron: "0 0 * * *"
  workflow_dispatch:

permissions:
  contents: write
  pull-requests: write

jobs:
  crawl:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium

      - name: Run crawlers
        run: |
          python -m scripts.crawlers.run_all

      - name: Show changed files
        run: |
          git status

      - name: Create pull request for candidates
        uses: peter-evans/create-pull-request@v6
        with:
          commit-message: "Update event candidates"
          title: "Update event candidates"
          body: |
            Auto-generated event candidates from scheduled crawler.

            Please review:
            - public/data/candidates.json
            - public/data/change_requests.json
            - public/data/crawler_report.json
          branch: crawler/update-event-candidates
          delete-branch: true
```

### 16.3 為什麼用 PR

使用 PR 的優點：

- 可以人工 review
- 可以看資料 diff
- 避免錯誤資料直接上線
- 保留資料變更紀錄
- 可以在 PR 裡討論候選資料是否正確

---

## 17. Review 流程

第一版不建議直接做完整後台，可以先使用 GitHub PR 作為 review 流程。

```text
GitHub Actions 定期執行 crawler
    ↓
產生 candidates.json / change_requests.json
    ↓
自動開 PR
    ↓
人工檢查候選活動
    ↓
手動把正確項目合併到 events.json
    ↓
merge PR
    ↓
GitHub Pages deploy
```

### 17.1 人工檢查項目

每筆 candidate 需要確認：

```text
1. 是否為日本藝人或日系演出？
2. 是否為台灣場？
3. 是否有官方售票頁或主辦公告？
4. 日期是否正確？
5. 場館是否正確？
6. 城市是否正確？
7. 票價是否正確？
8. 售票時間是否正確？
9. 是否已經存在於 events.json？
10. 是否為加場、延期、取消或售完更新？
```

---

## 18. 第一版開發 Milestone

## Milestone 1：建立 crawler 基礎架構

目標：先完成完整 pipeline，不急著接真實網站。

任務：

```text
[ ] 建立 requirements.txt
[ ] 建立 scripts/crawlers/base.py
[ ] 建立 scripts/crawlers/run_all.py
[ ] 建立 scripts/crawler_utils/normalize.py
[ ] 建立 scripts/crawler_utils/match_artist.py
[ ] 建立 scripts/crawler_utils/dedupe.py
[ ] 建立 scripts/crawler_utils/schemas.py
[ ] 建立 candidates.json schema
[ ] 建立 crawler_report.json schema
[ ] 先用 mock crawler 產生 candidates.json
```

完成標準：

```bash
python -m scripts.crawlers.run_all
```

可以產生：

```text
public/data/candidates.json
public/data/crawler_report.json
```

---

## Milestone 2：第一個真實平台 crawler

目標：先完成一個來源，不要同時開太多平台。

任務：

```text
[ ] 選定第一個來源
[ ] 抓活動列表頁
[ ] 抓活動詳細頁
[ ] 解析 title
[ ] 解析 date
[ ] 解析 venue
[ ] 解析 ticket_url
[ ] 解析 organizer
[ ] 解析 price，如果抓不到可先留空
[ ] 輸出 raw candidate
[ ] 跑 artist alias matching
```

完成標準：

```text
可以從一個平台抓出 5 筆以上候選活動
```

---

## Milestone 3：Dedupe 與 Confidence

任務：

```text
[ ] 比對 artists.json aliases
[ ] 計算 match_confidence
[ ] 比對 events.json 既有活動
[ ] 標記 duplicate_event_id
[ ] 標記 high / medium / low confidence
```

完成標準：

```text
candidate 可以被分類為：
- new high confidence
- new medium confidence
- duplicate
- low confidence ignored
```

---

## Milestone 4：GitHub Actions 自動 PR

任務：

```text
[ ] 建立 crawl-events.yml
[ ] 支援 workflow_dispatch 手動執行
[ ] 支援 schedule 每天執行
[ ] 產生 candidates.json
[ ] 產生 crawler_report.json
[ ] 自動開 PR
```

完成標準：

```text
crawler 執行後不直接改 main，而是開 PR 供人工 review
```

---

## Milestone 5：Change Detection

任務：

```text
[ ] 比對既有 events.json
[ ] 偵測票價變更
[ ] 偵測日期變更
[ ] 偵測場館變更
[ ] 偵測售票狀態變更
[ ] 偵測活動狀態變更
[ ] 輸出 change_requests.json
```

完成標準：

```text
既有活動被更新時，不會變成重複 candidate，而是變成待審核 change request
```

---

## 19. 建議的實作順序

目前前端已經完成初步頁面，接下來建議順序：

```text
1. 建立 candidates.json 格式
2. 建立 crawler 資料夾結構
3. 寫 mock crawler
4. 寫 artist alias matching
5. 寫 dedupe
6. 寫 crawler_report.json
7. 接第一個真實網站
8. 加 GitHub Actions 自動 PR
9. 加 change detection
10. 再擴充多平台 crawler
```

不要一開始就做：

- 完整後台
- 資料庫
- 多平台 crawler
- 自動合併正式資料
- 即時售票狀態監控

---

## 20. 安全與合規限制

本專案只做資訊整理，不應涉及售票平台操作。

### 20.1 禁止功能

不得實作：

- 自動購票
- 自動排隊
- 自動登入
- 自動填寫購票表單
- 驗證碼辨識
- 多帳號購票
- 高頻刷新售票頁
- 繞過平台限制
- 票券轉售功能

### 20.2 資料使用原則

建議遵守：

- 只摘要必要資訊
- 保留官方來源 URL
- 不複製完整售票頁內容
- 不儲存使用者個資
- 不儲存售票平台帳密
- 不爬取需要登入或驗證碼的頁面
- 遵守各網站服務條款與 robots.txt

---

## 21. 第一版完成標準

Crawler 第一版完成時，應該能做到：

```text
[ ] 可以手動執行 crawler
[ ] 可以產生 candidates.json
[ ] 可以產生 crawler_report.json
[ ] 可以讀取 artists.json 做 alias matching
[ ] 可以標記 match_confidence
[ ] 可以比對 events.json 標記 duplicate
[ ] 可以透過 GitHub Actions 手動執行
[ ] 可以透過 GitHub Actions 自動開 PR
[ ] 不會直接修改 main branch
[ ] 不會直接發布候選活動到前台正式列表
```

---

## 22. 第二版擴充方向

當第一版穩定後，可以擴充：

- 多平台 crawler
- 自動 change detection
- Admin candidate review page
- Supabase / PostgreSQL
- 後台管理活動
- Telegram / LINE 通知
- 收藏藝人與開賣提醒
- 活動變更紀錄
- 來源可信度評分
- 自動產生統計摘要

---

## 23. 建議先從哪裡開始

下一步最務實的第一個 commit 可以是：

```text
Add crawler planning structure and mock candidate pipeline
```

內容包含：

```text
requirements.txt
scripts/crawlers/base.py
scripts/crawlers/run_all.py
scripts/crawlers/mock.py
scripts/crawler_utils/normalize.py
scripts/crawler_utils/match_artist.py
scripts/crawler_utils/dedupe.py
public/data/candidates.json
public/data/crawler_report.json
```

先讓整條 pipeline 跑起來，再逐步替換 mock crawler 成真實平台 crawler。

---

## 24. Recommended First Command Checklist

```bash
mkdir -p scripts/crawlers
mkdir -p scripts/crawler_utils
mkdir -p scripts/configs
mkdir -p scripts/review
mkdir -p data_raw
touch scripts/crawlers/__init__.py
touch scripts/crawler_utils/__init__.py
touch data_raw/.gitkeep
touch public/data/candidates.json
touch public/data/change_requests.json
touch public/data/crawler_report.json
touch requirements.txt
```

接著新增：

```bash
pip install requests beautifulsoup4 lxml playwright pydantic python-dateutil rapidfuzz pyyaml
pip freeze > requirements.txt
playwright install chromium
```

開發測試：

```bash
python -m scripts.crawlers.run_all
```

---

## 25. Summary

Crawler 系統應該先以「安全、可審核、可追蹤」為主，而不是追求完全自動上架。

第一版最重要的不是抓到最多資料，而是：

- 資料格式穩定
- 來源可追蹤
- 候選資料可 review
- 不污染正式資料
- 不違反售票平台限制
- 後續可以逐步擴充
