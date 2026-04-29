# Japan Live Taiwan

日系藝人來台演出資訊整理平台。第一版以 GitHub Pages、Next.js static export、靜態 JSON 資料與前端搜尋篩選為核心，不需要後端或資料庫。

目前資料為 sample catalog，用於驗證 UI、資料結構與部署流程；正式上線前請以官方售票頁、主辦公告或藝人官方來源補齊真實資料。

## Features

- 首頁重點區塊：即將開賣、即將演出、最新新增活動。
- 活動列表：關鍵字搜尋，並可依城市、平台、狀態、場館、藝人類型與票價篩選。
- 活動詳細頁：演出時間、場館、票價、售票資訊、來源與最後更新時間。
- 藝人與場館頁：整理已收錄藝人、演出紀錄與場館活動數。
- 日曆頁：切換演出日與售票日。
- 統計頁：每月演出、平台分布、城市分布、場館排名與藝人類型比例。
- 資料驗證：使用 Zod 檢查 JSON 格式與跨檔案 ID 關聯。

## Tech Stack

- Next.js App Router
- React 19
- TypeScript
- Tailwind CSS
- Fuse.js
- Recharts
- Zod
- Vitest
- Husky + commitlint

## Project Structure

```text
src/app/               App Router routes
src/components/        UI components and component tests
src/lib/               data loading, schema, date, statistics, event utilities
src/types/             TypeScript domain types
public/data/           static JSON catalog
scripts/validate-data.ts
.github/workflows/     GitHub Pages deployment
```

## Getting Started

This project uses Node.js 24. On Windows PowerShell, use `npm.cmd` if direct `npm` execution is blocked by execution policy.

```bash
npm install
npm run dev
```

Open the local URL printed by Next.js, usually `http://localhost:3000`.

## Available Scripts

```bash
npm run dev            # Start local development server
npm run build          # Build static export into out/
npm run lint           # Run ESLint
npm run typecheck      # Run TypeScript checks
npm test               # Run Vitest tests
npm run format:check   # Check Prettier formatting
npm run validate:data  # Validate JSON catalog and references
```

## Data Maintenance

Edit static data under `public/data/`:

- `events.json`
- `artists.json`
- `venues.json`
- `platforms.json`
- `organizers.json`

Every event must include at least one source URL. Before committing data changes, run:

```bash
npm run validate:data
```

Do not publish rumors or unofficial scraped personal data. Use official ticketing, organizer, artist official, news, or social sources that users can verify.

## Deployment

Production builds use `output: "export"` and GitHub Pages base path `/japan-live-taiwan`. The workflow in `.github/workflows/deploy.yml` runs:

```text
npm ci -> validate:data -> typecheck -> lint -> test -> build -> deploy Pages
```

In the GitHub repository settings, configure Pages source as GitHub Actions.

## Commit Convention

Use AngularJS-style commit messages:

```text
<type>(<scope>): <subject>
```

Allowed types are `feat`, `fix`, `docs`, `style`, `refactor`, `test`, and `chore`.

Example:

```text
docs(readme): add project setup guide
```

Pre-commit hooks run data validation, typecheck, lint, format check, and tests. The commit message hook enforces the convention above.

## License

Code is licensed under the repository license. Event data should be maintained with source attribution and may need separate licensing rules before production use.
