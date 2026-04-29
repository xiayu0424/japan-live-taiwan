# Repository Guidelines

## Project Structure & Module Organization

This repository contains planning material for a static site that catalogs Japanese artists' live events in Taiwan. Use `japan_live_taiwan_readme_plan.md` as the product and architecture reference.

Planned structure should follow the MVP described there:

- `src/` or `app/`: Next.js/React application code.
- `public/`: static assets served by the site.
- `data/`: static JSON event records consumed by the frontend.
- `tests/` or colocated `*.test.*` files: automated tests.
- `.github/workflows/`: GitHub Actions for build and Pages deployment.

Keep event data separate from presentation code so validation, search, and future crawler updates remain straightforward.

## Build, Test, and Development Commands

No package manifest exists yet. After the frontend is scaffolded, keep this section in sync with `package.json`. Expected commands for a Next.js MVP are:

- `npm install`: install dependencies.
- `npm run dev`: run the local development server.
- `npm run build`: create the production static build.
- `npm test`: run the test suite once tests are configured.
- `npm run lint`: run linting and formatting checks.

Do not document commands until they work in the repository.

## Coding Style & Naming Conventions

Prefer TypeScript for application code and JSON for manually maintained event data. Use 2-space indentation for JavaScript, TypeScript, JSON, and Markdown. Name React components in `PascalCase`, hooks in `useCamelCase`, utilities in `camelCase`, and route or data files with descriptive lowercase names such as `events.json`.

For event records, use stable machine-readable IDs and ISO-style dates, for example `2026-05-30`.

## Testing Guidelines

When tests are added, cover data validation, filtering/search behavior, date sorting, and event rendering. Prefer deterministic fixtures in `tests/fixtures/` or near the relevant test file. Name tests as `*.test.ts` or `*.test.tsx`.

Run the full test and lint suite before opening a pull request.

## Commit & Pull Request Guidelines

Use AngularJS-style commit messages: `<type>(<scope>): <subject>`. Allowed types are `feat`, `fix`, `docs`, `style`, `refactor`, `test`, and `chore`. Keep the subject imperative, lowercase where natural, and without a trailing period, for example `feat(events): add event list filters`.

Pull requests should include a short summary, testing notes, linked issue when applicable, and screenshots for UI changes. For data updates, include the official source URL for each new or changed event.

## Security & Configuration Tips

Do not commit `.env` files, credentials, private API tokens, or unofficial scraped personal data. Keep official ticketing and organizer links in event records so users can verify details.
