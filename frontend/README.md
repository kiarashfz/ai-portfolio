# PortfolioGPT frontend

Next.js App Router application for PortfolioGPT, with React, TypeScript,
Tailwind CSS, Radix UI and Framer Motion.

See the [project README](../README.md) for architecture, backend prerequisites,
configuration, API routes and current limitations.

## Local development

Use Node.js 20.9+ (Node.js 24 is configured in `.nvmrc`).

```bash
npm ci
cp .env.example .env.local
npm run dev
```

Open http://localhost:3000. Set `NEXT_PUBLIC_API_BASE_URL` to the running backend
(default: http://localhost:8080). This variable is public and must contain no secrets.

```bash
npx tsc --noEmit
npm run lint
npm run build
npm start
```

Routes: `/`, `/login`, `/signup`, `/dashboard`, and `/<username>`.
