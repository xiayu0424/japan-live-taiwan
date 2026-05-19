# 台灣常見購票網站爬蟲方式與演出資訊 API 取得規劃

本文件整理 `japan-live-taiwan` 專案可採用的台灣常見售票網站爬蟲策略，以及如何取得演出資訊對應的 API / HTML 資料來源。

設計目標是建立「演出資訊候選資料產生器」，而不是購票工具。Crawler 只應抓取公開演出資訊，例如活動名稱、演出日期、場館、票價、售票時間、主辦單位與官方連結。

> 注意：多數台灣售票平台沒有穩定公開 API。以下「API 取得方式」主要指透過瀏覽器 DevTools 檢查公開頁面載入時使用的 XHR / Fetch endpoint。這些 endpoint 可能不是官方文件化 API，可能改版失效，因此應搭配 HTML parser / JSON-LD parser fallback。

---

## 1. 基本原則

### 1.1 Crawler 只做資訊整理

允許抓取：

- 活動名稱
- 藝人名稱
- 演出日期
- 開場時間
- 場館
- 城市
- 地址
- 票價
- 售票時間
- 售票平台
- 主辦單位
- 活動狀態
- 官方購票連結
- 官方活動頁連結

不應抓取或操作：

- 自動購票
- 自動登入
- 自動排隊
- 自動填表
- 驗證碼辨識
- 座位選擇
- 付款流程
- 會員資料
- 使用者個資
- ticket token / session token
- queue token
- captcha token
- 任何需要登入後才可取得的非公開資料

### 1.2 不直接發布 crawler 結果

建議流程：

```text
售票平台 / 主辦單位來源
    ↓
Crawler 抓取公開活動資訊
    ↓
Parser 解析成統一格式
    ↓
Artist alias matching
    ↓
Venue alias matching
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

---

## 2. API 取得方式總覽

台灣售票網站多數沒有正式公開 API。實務上可取得資料的方式通常有四種：

```text
1. HTML parser
2. JSON-LD / structured data
3. Frontend internal API
4. Playwright render 後解析 DOM
```

建議優先順序：

```text
JSON-LD / structured data
    ↓
靜態 HTML parser
    ↓
公開 XHR / fetch API
    ↓
Playwright render 後解析 DOM
```

不建議一開始就依賴 internal API，因為 internal API 可能隨前端改版而失效。

---

## 3. 用 DevTools 找 API 的標準流程

### 3.1 手動找 API

1. 開啟活動列表頁或活動詳細頁。
2. 開啟 Chrome DevTools。
3. 進入 Network。
4. 選擇 Fetch/XHR。
5. 重新整理頁面。
6. 點選可疑 request。
7. 查看 Response 是否為 JSON。
8. 確認是否包含以下欄位：
   - title
   - event name
   - date
   - venue
   - price
   - organizer
   - ticket URL
9. 右鍵 request，選擇 Copy as cURL。
10. 轉換成 Python requests 或 Playwright request。
11. 移除不必要的 cookie / authorization / session header。
12. 測試無登入狀態是否仍可取得資料。

### 3.2 判斷 API 是否適合使用

適合使用：

- 不需要登入
- 不需要 cookie
- 不需要排隊
- 不需要驗證碼
- 不需要動態 token
- 回傳 JSON
- 欄位穩定
- request rate 低時穩定

不適合使用：

- 需要登入 cookie
- 需要 CSRF token
- 需要排隊 token
- 只在購票流程內出現
- 需要驗證碼
- endpoint 名稱明顯屬於 order / seat / payment
- 高度依賴 session
- 呼叫後會造成鎖票、選位、下單等副作用

### 3.3 API 記錄格式

建議每個來源都建立一份紀錄：

```yaml
site: kktix
page_type: event_detail
source_type: html
url_pattern: "https://*.kktix.cc/events/*"
requires_login: false
requires_cookie: false
requires_playwright: false
data_fields:
  - title
  - date
  - venue
  - organizer
  - price
risk_level: low
notes: "Prefer HTML parser and JSON-LD if available."
```

---

## 4. 建議平台優先順序

| 優先級 | 平台                       | 建議原因                                       |
| -----: | -------------------------- | ---------------------------------------------- |
|      1 | KKTIX                      | 日系演出常見，活動頁資訊清楚                   |
|      2 | Live Nation Taiwan         | 國際演唱會常見，有公開活動列表                 |
|      3 | KKLIVE / 主辦單位 KKTIX 頁 | 日系演出常見，常導向 KKTIX                     |
|      4 | OPENTIX                    | 現代化前端，可能有結構化 API                   |
|      5 | tixCraft 拓元              | 大型演唱會常見，但可能需 Playwright            |
|      6 | ibon                       | 演唱會常見，頁面較動態                         |
|      7 | 寬宏 Kham                  | 常見大型活動，但 HTML / ASP.NET parsing 較麻煩 |
|      8 | 年代售票                   | 頁面較傳統，需處理 encoding 與 HTML 結構       |
|      9 | FamiTicket 全網購票        | 可列為補充來源                                 |
|     10 | udn 售票 / udnFunLife      | 可列為補充來源                                 |
|     11 | Accupass                   | 活動較廣，不一定以演唱會為主                   |

---

# 5. 各平台爬蟲方式

---

## 5.1 KKTIX

### 平台特性

KKTIX 常見於：

- Live house 演出
- 日系樂團
- 動漫音樂活動
- 主辦單位自建活動頁
- KKLIVE 相關活動

常見 URL 型態：

```text
https://kktix.com/events
https://{organizer}.kktix.cc/events/{event-slug}
```

### 建議抓取方式

優先：

```text
1. 活動詳細頁 HTML parser
2. structured data / JSON-LD
3. organizer events list
4. KKTIX events list
```

不建議：

```text
購票流程頁
選票頁
需要登入的訂單頁
```

### 可取得欄位

| 欄位     | 取得難度 | 建議來源                       |
| -------- | -------- | ------------------------------ |
| 活動名稱 | 低       | HTML title / h1                |
| 演出日期 | 低       | activity page                  |
| 場館     | 低       | activity page                  |
| 主辦單位 | 低       | organizer page / activity page |
| 票價     | 中       | activity content               |
| 售票時間 | 中       | activity content               |
| 活動狀態 | 中       | activity page                  |
| 購票連結 | 低       | current activity URL           |

### API 取得方式

KKTIX 不應假設有穩定官方公開 API。建議以 HTML parser 為主。

DevTools 檢查重點：

```text
Network > Fetch/XHR
Network > Doc
Elements > script[type="application/ld+json"]
```

若活動頁包含 JSON-LD，可以優先解析：

```python
from bs4 import BeautifulSoup
import json


def extract_json_ld(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    result = []

    for script in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.get_text(strip=True))
            result.append(data)
        except Exception:
            continue

    return result
```

HTML parser fallback：

```python
import requests
from bs4 import BeautifulSoup


def crawl_kktix_event(url: str) -> dict:
    res = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20,
    )
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "lxml")

    title = soup.select_one("h1")
    title_text = title.get_text(" ", strip=True) if title else None

    text = soup.get_text("\n", strip=True)

    return {
        "source_platform": "kktix",
        "source_url": url,
        "title": title_text,
        "raw_text": text,
    }
```

### 建議 crawler 類型

```text
requests + BeautifulSoup
```

只有當 organizer list 或活動列表需要 JS render 時，才使用 Playwright。

### 風險

| 風險 | 說明                                                 |
| ---- | ---------------------------------------------------- |
| 中   | 票價與售票時間可能寫在自由文字中，需要 regex parsing |
| 低   | 活動詳細頁通常可公開瀏覽                             |
| 中   | organizer 子網域格式多，需要 URL normalization       |

### 實作優先級

```text
高
```

---

## 5.2 tixCraft 拓元售票

### 平台特性

tixCraft 常見於大型演唱會、國內外大型活動。活動資訊通常會出現在活動列表與活動詳細頁，但實際購票流程可能涉及排隊、驗證與登入。

常見 URL 型態：

```text
https://tixcraft.com/activity
https://tixcraft.com/activity/detail/{activity_id}
```

### 建議抓取方式

優先：

```text
1. activity list
2. activity detail page
3. detail page HTML parser
4. Playwright render 後解析 DOM
```

不應進入：

```text
ticket/area
ticket/ticket
order
payment
seat selection
```

### 可取得欄位

| 欄位     | 取得難度 | 建議來源               |
| -------- | -------- | ---------------------- |
| 活動名稱 | 低       | activity detail        |
| 演出日期 | 中       | detail page            |
| 場館     | 中       | detail page            |
| 票價     | 中       | detail content         |
| 售票時間 | 中       | detail content         |
| 售票狀態 | 中       | activity list / detail |
| 購票連結 | 低       | detail page            |

### API 取得方式

tixCraft 的前端可能會呼叫內部 endpoint，但不應假設穩定。

DevTools 搜尋方向：

```text
Network > Fetch/XHR
搜尋 keyword:
- activity
- detail
- game
- sale
```

判斷 endpoint 是否適合使用：

```text
只抓 activity / detail 類型 endpoint
不要抓 ticket / area / order / payment 類型 endpoint
```

如果 API 需要 cookie、token、驗證碼或排隊資訊，應放棄 API，改用 detail page HTML parser。

### Playwright 範例

```python
from playwright.sync_api import sync_playwright


def fetch_rendered_html(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0")
        page.goto(url, wait_until="networkidle", timeout=30000)
        html = page.content()
        browser.close()
        return html
```

### 建議 crawler 類型

```text
Playwright + BeautifulSoup
```

若 detail page 可由 requests 直接取得，則優先不用 Playwright。

### 風險

| 風險 | 說明                               |
| ---- | ---------------------------------- |
| 高   | 購票流程不能碰，容易涉及排隊與驗證 |
| 中   | 活動資訊可能散落在 HTML 文字       |
| 中   | 頁面結構可能改版                   |
| 中   | internal API 不保證穩定            |

### 實作優先級

```text
中高
```

---

## 5.3 ibon 售票系統

### 平台特性

ibon 常見於大型活動、演唱會、展演與體育活動。頁面可能較依賴前端動態載入，因此通常需要先用 DevTools 檢查是否有公開 JSON API。

常見入口：

```text
https://ticket.ibon.com.tw/
```

### 建議抓取方式

優先：

```text
1. 公開活動列表 API，如果無需登入且穩定
2. Playwright render 活動列表
3. 活動詳細頁 HTML parser
```

不建議：

```text
登入頁
訂票頁
座位選擇頁
付款頁
便利商店取票流程
```

### 可取得欄位

| 欄位     | 取得難度 | 建議來源      |
| -------- | -------- | ------------- |
| 活動名稱 | 中       | list / detail |
| 演出日期 | 中       | detail        |
| 場館     | 中       | detail        |
| 票價     | 中       | detail        |
| 售票時間 | 中       | detail        |
| 活動狀態 | 中       | list / detail |
| 購票連結 | 低       | detail URL    |

### API 取得方式

DevTools 搜尋方向：

```text
Network > Fetch/XHR
搜尋 keyword:
- event
- activity
- program
- product
- performance
- show
```

若 request 需要動態 token 或 cookie，應改用 Playwright render 後解析 DOM。

### 建議 crawler 類型

```text
Playwright first
API if publicly available
HTML fallback
```

### 風險

| 風險 | 說明                                      |
| ---- | ----------------------------------------- |
| 中高 | 前端動態載入，requests 可能拿不到完整資料 |
| 中   | endpoint 可能改版                         |
| 高   | 購票流程不能碰                            |
| 中   | 活動分類較廣，需要 artist matching 過濾   |

### 實作優先級

```text
中
```

---

## 5.4 寬宏藝術 Kham

### 平台特性

寬宏常見於大型演唱會、展演與娛樂活動。頁面可能偏傳統 ASP.NET / HTML 表單結構，欄位可能需要從頁面文字中解析。

常見入口：

```text
https://kham.com.tw/
```

### 建議抓取方式

優先：

```text
1. 活動列表 HTML parser
2. 活動詳細頁 HTML parser
3. 必要時使用 Playwright
```

不建議：

```text
訂票頁
會員頁
付款頁
任何需要 postback 的流程
```

### 可取得欄位

| 欄位     | 取得難度 | 建議來源         |
| -------- | -------- | ---------------- |
| 活動名稱 | 中       | detail page      |
| 日期     | 中       | detail page text |
| 場館     | 中       | detail page text |
| 票價     | 中       | detail page text |
| 售票時間 | 中       | detail page text |
| 主辦單位 | 中       | detail page text |
| 購票連結 | 低       | detail URL       |

### API 取得方式

寬宏不應預期有穩定公開 JSON API。建議主要依賴 HTML parser。

DevTools 檢查重點：

```text
Network > Doc
Network > Fetch/XHR
Form postback request 不建議使用
```

若看到 ASP.NET hidden fields，例如：

```text
__VIEWSTATE
__EVENTVALIDATION
```

不要使用 postback 流程抓資料，避免變成操作流程。

### 建議 crawler 類型

```text
requests + BeautifulSoup
```

若內容由 JavaScript 產生，再改用 Playwright。

### 風險

| 風險 | 說明                             |
| ---- | -------------------------------- |
| 中   | 頁面格式可能不一致               |
| 中   | 日期與票價可能在自由文字         |
| 中   | ASP.NET form 不適合作為 API 依賴 |
| 高   | 不應操作訂票表單                 |

### 實作優先級

```text
中
```

---

## 5.5 年代售票 ERA Ticket

### 平台特性

年代售票頁面可能較傳統，常見於演唱會、展演、戲劇活動等。Crawler 需要注意文字編碼、HTML 結構與活動分類。

常見入口：

```text
https://ticket.com.tw/
```

### 建議抓取方式

優先：

```text
1. 活動列表 HTML parser
2. 活動詳細頁 HTML parser
3. 處理 encoding
```

### 可取得欄位

| 欄位     | 取得難度 | 建議來源    |
| -------- | -------- | ----------- |
| 活動名稱 | 中       | detail page |
| 日期     | 中       | detail page |
| 場館     | 中       | detail page |
| 票價     | 中       | detail page |
| 售票時間 | 中       | detail page |
| 主辦單位 | 中       | detail page |
| 購票連結 | 低       | detail URL  |

### API 取得方式

年代售票不建議預設有穩定公開 API。可以用 DevTools 檢查 Fetch/XHR，但建議以 HTML parser 為主。

encoding 處理範例：

```python
import requests
from bs4 import BeautifulSoup


def fetch_era_page(url: str) -> BeautifulSoup:
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    res.raise_for_status()

    if not res.encoding or res.encoding.lower() == "iso-8859-1":
        res.encoding = res.apparent_encoding

    return BeautifulSoup(res.text, "lxml")
```

### 建議 crawler 類型

```text
requests + BeautifulSoup
```

### 風險

| 風險 | 說明                                    |
| ---- | --------------------------------------- |
| 中   | 可能需要處理 Big5 / encoding            |
| 中   | 頁面欄位可能不規則                      |
| 中   | 活動類型較廣，需要 artist matching 過濾 |

### 實作優先級

```text
中低
```

---

## 5.6 OPENTIX 兩廳院文化生活

### 平台特性

OPENTIX 是現代化票務平台，常見於藝文活動、音樂會、展演。雖然日系樂團大型演唱會不一定最多，但若有動漫音樂、管弦、劇場、跨界演出，可能會出現在 OPENTIX。

常見入口：

```text
https://www.opentix.life/
```

### 建議抓取方式

優先：

```text
1. DevTools 找公開 JSON API
2. 活動詳細頁 JSON-LD
3. Playwright render 後解析 DOM
4. HTML parser fallback
```

### 可取得欄位

| 欄位     | 取得難度 | 建議來源     |
| -------- | -------- | ------------ |
| 活動名稱 | 低~中    | API / detail |
| 日期     | 低~中    | API / detail |
| 場館     | 低~中    | API / detail |
| 票價     | 中       | API / detail |
| 節目介紹 | 中       | detail       |
| 售票狀態 | 中       | API / detail |
| 購票連結 | 低       | detail URL   |

### API 取得方式

OPENTIX 屬於較可能有前端 JSON API 的平台。建議使用 DevTools 檢查：

```text
Network > Fetch/XHR
搜尋 keyword:
- event
- program
- performance
- product
- show
```

如果 API 無需登入、無 cookie、無 token，即可考慮作為主要資料來源。但仍應建立 HTML fallback：

```text
API failed
    ↓
Playwright render page
    ↓
DOM parser
```

### 建議 crawler 類型

```text
API if available
Playwright fallback
```

### 風險

| 風險  | 說明                       |
| ----- | -------------------------- |
| 中    | internal API 可能改版      |
| 中    | 日系演出比例較低，需要篩選 |
| 低~中 | 現代化前端較適合 API 解析  |

### 實作優先級

```text
中
```

---

## 5.7 Live Nation Taiwan

### 平台特性

Live Nation Taiwan 常見於國際大型演唱會。日系大型藝人、J-pop、J-rock、國際巡迴台灣場可能出現在此。

常見入口：

```text
https://www.livenation.com.tw/
```

### 建議抓取方式

優先：

```text
1. upcoming events list
2. event detail page
3. structured data / JSON-LD
4. Playwright render
```

### 可取得欄位

| 欄位     | 取得難度 | 建議來源                    |
| -------- | -------- | --------------------------- |
| 活動名稱 | 低       | list / detail               |
| 日期     | 低       | list / detail               |
| 場館     | 低       | detail                      |
| 城市     | 低       | detail                      |
| 購票連結 | 低       | detail                      |
| 票價     | 中       | detail / linked ticket site |
| 售票時間 | 中       | detail / linked ticket site |

### API 取得方式

Live Nation 站點可能有前端資料載入或 structured data。建議檢查：

```text
Network > Fetch/XHR
Elements > script[type="application/ld+json"]
```

若 detail page 有 JSON-LD Event data，優先解析。

### 建議 crawler 類型

```text
requests + BeautifulSoup
Playwright fallback
```

### 風險

| 風險  | 說明                                 |
| ----- | ------------------------------------ |
| 低~中 | 活動資料相對規則                     |
| 中    | 售票細節可能導向其他平台             |
| 中    | 需要 artist alias 判斷是否為日系藝人 |

### 實作優先級

```text
高
```

---

## 5.8 KKLIVE / 主辦單位活動頁

### 平台特性

KKLIVE 常見於日系演出與 KKTIX 售票頁。實務上 KKLIVE 的活動常導到 KKTIX 或以 KKTIX organizer page 形式存在。

常見型態：

```text
https://kklivetw.kktix.cc/events/{event-slug}
```

### 建議抓取方式

優先：

```text
1. KKTIX organizer page
2. KKTIX event detail parser
3. 主辦單位官方公告頁
```

### API 取得方式

不建議另寫一套 KKLIVE API crawler。可視為 KKTIX crawler 的特化來源。

建議 config：

```yaml
- id: kklive_kktix
  name: KKLIVE Taiwan KKTIX
  enabled: true
  type: organizer
  crawler: kktix
  base_url: "https://kklivetw.kktix.cc"
  list_urls:
    - "https://kklivetw.kktix.cc/events"
```

### 建議 crawler 類型

```text
Reuse KKTIX crawler
```

### 風險

| 風險 | 說明                               |
| ---- | ---------------------------------- |
| 低   | 可複用 KKTIX parser                |
| 中   | 主辦公告與售票頁資訊可能不完全一致 |

### 實作優先級

```text
高
```

---

## 5.9 FamiTicket 全網購票

### 平台特性

FamiTicket / 全網購票可能出現演唱會、展演與活動售票。日系演出比例需實際觀察。

常見入口：

```text
https://www.famiticket.com.tw/
```

### 建議抓取方式

優先：

```text
1. 活動列表頁
2. 活動詳細頁
3. DevTools 查詢公開 API
4. Playwright fallback
```

### API 取得方式

DevTools 搜尋：

```text
event
activity
product
program
ticket
```

只使用公開活動資訊 API，不使用訂票流程 API。

### 建議 crawler 類型

```text
Playwright + API inspection
HTML fallback
```

### 風險

| 風險 | 說明                     |
| ---- | ------------------------ |
| 中   | 需確認活動分類與資料欄位 |
| 中   | 可能需要 JS render       |
| 中   | 內部 API 可能改版        |

### 實作優先級

```text
低~中
```

---

## 5.10 udn 售票 / udnFunLife

### 平台特性

udn 相關售票或活動平台可能包含展演、音樂、親子、藝文活動。日系演出比例不一定高，但可作為補充來源。

### 建議抓取方式

優先：

```text
1. 活動列表頁
2. 活動詳細頁
3. DevTools 找公開 JSON API
4. Playwright fallback
```

### API 取得方式

DevTools 搜尋：

```text
event
activity
product
program
performance
```

若 API 需要登入、cookie 或 token，不使用該 API。

### 建議 crawler 類型

```text
Playwright first
HTML / API fallback
```

### 風險

| 風險 | 說明                   |
| ---- | ---------------------- |
| 中   | 平台入口與頁面可能更動 |
| 中   | 活動類型較廣           |
| 中   | 日系活動比例需觀察     |

### 實作優先級

```text
低
```

---

## 5.11 Accupass

### 平台特性

Accupass 比較偏活動平台，演唱會不是唯一主軸。可能包含日系文化、動漫、音樂活動，但需大量 filtering。

常見入口：

```text
https://www.accupass.com/
```

### 建議抓取方式

優先：

```text
1. 搜尋頁
2. 活動詳細頁
3. structured data
4. DevTools 找公開 API
```

### 適合用途

比較適合作為：

- 日系文化活動補充來源
- 小型動漫音樂活動
- 主題活動
- fan event

若專案只收錄「日團演唱會」，Accupass 優先級可降低。

### 風險

| 風險 | 說明                             |
| ---- | -------------------------------- |
| 高   | 雜訊多，需要強 filtering         |
| 中   | 活動類型與專案定位可能不完全一致 |
| 中   | 可能需要搜尋關鍵字而非完整列表   |

### 實作優先級

```text
低
```

---

# 6. 欄位解析策略

## 6.1 日期解析

台灣售票網站常見日期格式：

```text
2026/05/01
2026.05.01
2026-05-01
2026/05/01（五）
2026/05/01 19:30
2026年5月1日
2026年05月01日 19:30
```

建議 parser：

```python
from dateutil import parser
from zoneinfo import ZoneInfo

TAIPEI_TZ = ZoneInfo("Asia/Taipei")


def parse_datetime(text: str):
    try:
        dt = parser.parse(text, fuzzy=True)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=TAIPEI_TZ)
        return dt.isoformat()
    except Exception:
        return None
```

注意：

- `dateutil.parser` 對中文日期不一定完美。
- 中文星期要先移除。
- 民國年格式要特別處理。
- 若只有日期沒有時間，`start_time` 可留 null，`date` 必須保留。

## 6.2 票價解析

常見格式：

```text
NT$2,800
$2800
新台幣 2,800 元
票價：2800 / 3200 / 3800
全區 1800
搖滾區 4800
```

建議 regex：

```python
import re


def parse_prices(text: str) -> list[int]:
    matches = re.findall(r"(?:NT\$|\$|新台幣)?\s*([1-9]\d{2,4})(?:\s*元)?", text)
    prices = []

    for value in matches:
        try:
            price = int(value.replace(",", ""))
            if 100 <= price <= 50000:
                prices.append(price)
        except Exception:
            continue

    return sorted(set(prices))
```

注意：

- 不要把日期誤判為票價。
- 不要把年份 2026 誤判為票價。
- 票價 parser 應搭配上下文關鍵字，如 `票價`、`NT$`、`元`。
- 若不確定，保留 `raw_price_text`，不要硬填正式欄位。

## 6.3 場館解析

建議建立 `venues.json` 作為 canonical venue dictionary。

```json
[
  {
    "id": "zepp-new-taipei",
    "name": "Zepp New Taipei",
    "aliases": ["Zepp New Taipei", "Zepp New Taipei 新北", "Zepp新北"],
    "city": "New Taipei"
  },
  {
    "id": "taipei-arena",
    "name": "臺北小巨蛋",
    "aliases": ["台北小巨蛋", "臺北小巨蛋", "Taipei Arena"],
    "city": "Taipei"
  }
]
```

場館 matching：

```text
1. exact alias match
2. normalized alias match
3. fuzzy match
4. 無法判斷則保留 raw venue text
```

## 6.4 藝人解析

以 `artists.json` 的 aliases 為核心。

比對來源：

```text
title
description
organizer text
performer field
metadata
```

信心分數：

| 情況                          |  分數 |
| ----------------------------- | ----: |
| title 完整包含 artist alias   |   100 |
| title normalized 後包含 alias |    95 |
| title fuzzy match             | 85-94 |
| description 提及 alias        | 70-84 |
| 只出現 Japan / J-pop / 日本   | 40-60 |

低於 85 的 candidate 不建議自動進入正式 review，可放到 low confidence section。

---

# 7. API 使用策略

## 7.1 不要硬編 undocumented API

若從 DevTools 找到 endpoint，例如：

```text
/api/events
/api/activity/list
/api/product/detail
```

不要直接假設它穩定。建議建立 adapter：

```python
def fetch_by_api(url: str) -> dict | None:
    try:
        ...
    except Exception:
        return None


def fetch_by_html(url: str) -> dict | None:
    ...
```

流程：

```text
try API
    ↓ failed
try HTML parser
    ↓ failed
try Playwright DOM parser
```

## 7.2 保存 API metadata

每個 API source 應記錄：

```json
{
  "source_platform": "opentix",
  "source_type": "internal_api",
  "endpoint": "redacted or documented pattern",
  "requires_login": false,
  "requires_cookie": false,
  "last_verified_at": "2026-05-11T00:00:00+08:00",
  "fallback": "html_parser"
}
```

不要在公開 repo 中保存：

- cookie
- authorization header
- token
- session id
- queue id
- captcha token
- payment related endpoint

## 7.3 Headers 建議

基本 headers 即可，不要偽裝成登入狀態。

```python
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; japan-live-taiwan-crawler/1.0; +https://github.com/xiayu0424/japan-live-taiwan)",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8,ja;q=0.7",
}
```

若站方不接受 crawler user agent，可以改成一般瀏覽器 UA，但不應加入登入 cookie 或繞過機制。

---

# 8. Rate Limit 與排程

## 8.1 頻率建議

| 場景         | 頻率           |
| ------------ | -------------- |
| 開發測試     | 手動           |
| 一般自動更新 | 每天 1 次      |
| 活動密集期   | 每天 2 次      |
| 售票日前後   | 不高頻刷新     |
| 開賣當下     | 不執行 crawler |

## 8.2 每站 request interval

| 平台               | 建議 interval |
| ------------------ | ------------: |
| KKTIX              |        3-5 秒 |
| Live Nation Taiwan |        3-5 秒 |
| OPENTIX            |        3-5 秒 |
| tixCraft           |       5-10 秒 |
| ibon               |       5-10 秒 |
| 寬宏               |       5-10 秒 |
| 年代               |       5-10 秒 |

## 8.3 GitHub Actions 排程

```yaml
on:
  schedule:
    # Taiwan 08:00
    - cron: "0 0 * * *"
  workflow_dispatch:
```

活動密集期最多：

```yaml
on:
  schedule:
    # Taiwan 08:00
    - cron: "0 0 * * *"
    # Taiwan 20:00
    - cron: "0 12 * * *"
  workflow_dispatch:
```

---

# 9. Crawler Config 範例

```yaml
sources:
  - id: kktix
    name: KKTIX
    enabled: true
    crawler: kktix
    source_type: ticket_platform
    base_url: "https://kktix.com"
    list_urls:
      - "https://kktix.com/events"
    request_interval_seconds: 3
    use_playwright: false
    strategy:
      - html
      - json_ld

  - id: kklive_kktix
    name: KKLIVE Taiwan KKTIX
    enabled: true
    crawler: kktix
    source_type: organizer
    base_url: "https://kklivetw.kktix.cc"
    list_urls:
      - "https://kklivetw.kktix.cc/events"
    request_interval_seconds: 3
    use_playwright: false
    strategy:
      - html
      - json_ld

  - id: livenation_tw
    name: Live Nation Taiwan
    enabled: true
    crawler: livenation
    source_type: organizer
    base_url: "https://www.livenation.com.tw"
    list_urls:
      - "https://www.livenation.com.tw/en/event/allevents"
    request_interval_seconds: 5
    use_playwright: true
    strategy:
      - json_ld
      - html
      - playwright

  - id: opentix
    name: OPENTIX
    enabled: false
    crawler: opentix
    source_type: ticket_platform
    base_url: "https://www.opentix.life"
    list_urls:
      - "https://www.opentix.life/"
    request_interval_seconds: 5
    use_playwright: true
    strategy:
      - api
      - json_ld
      - playwright

  - id: tixcraft
    name: tixCraft
    enabled: false
    crawler: tixcraft
    source_type: ticket_platform
    base_url: "https://tixcraft.com"
    list_urls:
      - "https://tixcraft.com/activity"
    request_interval_seconds: 8
    use_playwright: true
    strategy:
      - html
      - playwright

  - id: ibon
    name: ibon
    enabled: false
    crawler: ibon
    source_type: ticket_platform
    base_url: "https://ticket.ibon.com.tw"
    list_urls:
      - "https://ticket.ibon.com.tw/"
    request_interval_seconds: 8
    use_playwright: true
    strategy:
      - api
      - playwright

  - id: kham
    name: Kham
    enabled: false
    crawler: kham
    source_type: ticket_platform
    base_url: "https://kham.com.tw"
    list_urls:
      - "https://kham.com.tw/"
    request_interval_seconds: 8
    use_playwright: false
    strategy:
      - html

  - id: era
    name: ERA Ticket
    enabled: false
    crawler: era
    source_type: ticket_platform
    base_url: "https://ticket.com.tw"
    list_urls:
      - "https://ticket.com.tw/"
    request_interval_seconds: 8
    use_playwright: false
    strategy:
      - html
```

---

# 10. 建議新增 API Notes 文件

建議新增：

```text
docs/ticket-site-api-notes/
├── kktix.md
├── tixcraft.md
├── ibon.md
├── kham.md
├── era.md
├── opentix.md
├── livenation.md
└── kklive.md
```

每份記錄格式：

```md
# KKTIX API Notes

## Last verified

2026-05-11

## Public pages

- list:
- detail:

## Structured data

- JSON-LD: yes / no
- OpenGraph: yes / no

## XHR endpoints found

| Endpoint | Requires login | Stable  | Used |
| -------- | -------------- | ------- | ---- |
| ...      | no             | unknown | no   |

## Recommended strategy

1. HTML parser
2. JSON-LD parser
3. API fallback

## Notes

...
```

---

# 11. 各平台推薦實作方式總表

| 平台               | 首選方式                    | API 依賴程度 | 是否需要 Playwright | 優先級 |
| ------------------ | --------------------------- | -----------: | ------------------: | -----: |
| KKTIX              | HTML + JSON-LD              |           低 |                  低 |     高 |
| KKLIVE             | KKTIX organizer parser      |           低 |                  低 |     高 |
| Live Nation Taiwan | HTML + JSON-LD              |           中 |                  中 |     高 |
| OPENTIX            | API + JSON-LD + Playwright  |         中高 |                  中 |     中 |
| tixCraft           | HTML + Playwright           |           中 |                中高 |   中高 |
| ibon               | API inspection + Playwright |         中高 |                  高 |     中 |
| 寬宏 Kham          | HTML parser                 |           低 |               低~中 |     中 |
| 年代 ERA           | HTML parser                 |           低 |                  低 |   中低 |
| FamiTicket         | API inspection + Playwright |           中 |                  中 |  低~中 |
| udn                | API inspection + Playwright |           中 |                  中 |     低 |
| Accupass           | Search/API/HTML             |           中 |                  中 |     低 |

---

# 12. Candidate Output 對應正式欄位

Crawler raw candidate 最後需要對應到正式 `events.json`。

| Candidate 欄位              | events.json 欄位            |
| --------------------------- | --------------------------- |
| `title`                     | `title`                     |
| `matched_artist_ids`        | `artist_ids`                |
| `event_type`                | `event_type`                |
| `shows[].date`              | `shows[].date`              |
| `shows[].start_time`        | `shows[].start_time`        |
| `shows[].venue_name`        | `shows[].venue_name`        |
| `shows[].city`              | `shows[].city`              |
| `ticket_sales[].platform`   | `ticket_sales[].platform`   |
| `ticket_sales[].sale_start` | `ticket_sales[].sale_start` |
| `ticket_sales[].ticket_url` | `ticket_sales[].ticket_url` |
| `prices[]`                  | `prices[]`                  |
| `organizers[]`              | `organizers[]`              |
| `sources[]`                 | `sources[]`                 |

---

# 13. Candidate Confidence 分級

```text
high:
  match_confidence >= 95
  and has date
  and has venue
  and has official source_url

medium:
  match_confidence >= 85
  and has official source_url
  and has either date or venue

low:
  match_confidence >= 60
  but missing date or venue

ignored:
  match_confidence < 60
```

只有 `high` 和 `medium` 建議寫入 `candidates.json`。`low` 可以只寫入 `crawler_report.json`。

---

# 14. 風險與維護策略

## 14.1 風險

| 風險           | 解法                                |
| -------------- | ----------------------------------- |
| 平台改版       | 建立 fallback parser                |
| API 失效       | 不依賴單一 API                      |
| 票價解析錯誤   | 保留 raw text，人工 review          |
| 日期解析錯誤   | 保留 raw date text，人工 review     |
| 同活動重複     | dedupe + duplicate_event_id         |
| 抓到非日系活動 | artist alias matching               |
| 抓到非台灣活動 | venue/city matching                 |
| 資訊不完整     | candidate 不直接發布                |
| 法規或平台限制 | 只抓公開資訊，遵守 robots.txt / ToS |

## 14.2 維護策略

- 每個 crawler 都要有 source-specific parser test。
- 每個 parser 都要保留 raw text。
- 每個 candidate 都要有 source URL。
- 每次自動更新都走 PR。
- 不要在 main branch 直接自動修改正式資料。
- internal API 失效時不要讓整個 pipeline fail。
- 單一平台 fail 不應中斷所有 crawler。

---

# 15. 建議新增測試

```text
tests/
├── fixtures/
│   ├── kktix_event.html
│   ├── livenation_event.html
│   ├── tixcraft_activity.html
│   └── opentix_event.json
├── test_date_parser.py
├── test_price_parser.py
├── test_artist_matcher.py
├── test_venue_matcher.py
└── test_dedupe.py
```

測試重點：

- 日期是否解析正確。
- 票價是否解析正確。
- 藝人 alias 是否命中。
- 場館 alias 是否命中。
- duplicate 是否正確標記。
- parser 在 HTML 結構缺欄位時不會 crash。

---

# 16. 建議第一階段實作順序

建議先做：

```text
1. KKTIX crawler
2. KKLIVE as KKTIX organizer source
3. Live Nation Taiwan crawler
4. JSON-LD extractor
5. HTML text parser
6. Artist alias matching
7. Venue alias matching
8. Dedupe
9. GitHub Actions auto PR
```

第二階段再做：

```text
10. OPENTIX API / Playwright crawler
11. tixCraft detail crawler
12. ibon Playwright crawler
13. Kham HTML crawler
14. ERA HTML crawler
```

---

# 17. 結論

目前最適合的 crawler 策略是：

```text
KKTIX / KKLIVE / Live Nation 先做
    ↓
以 HTML + JSON-LD 為主
    ↓
API 只作為可選來源
    ↓
所有資料進 candidates.json
    ↓
GitHub Actions 自動開 PR
    ↓
人工 review 後再合併到正式 events.json
```

不要一開始投入太多時間 reverse engineer 各平台 API。更穩定的做法是：

```text
先抓公開頁面
保留來源
保留 raw text
人工 review
逐步擴充 parser
```

這樣能讓網站先穩定累積資料，同時降低平台改版、API 失效與資料污染的風險。
