# Frontend — Smart Certificate Generator

React 18 + Vite + Tailwind CSS + React Router + Axios + Recharts.

## Setup

```bash
cd frontend
npm install
cp .env.example .env      # set VITE_API_URL if backend isn't on localhost:8000
```

## Run

```bash
npm run dev
```

Opens on http://localhost:5173. Requires the backend to be running.

## Build

```bash
npm run build
```

Outputs to `dist/`.

## Structure

- `src/pages` — one file per route (admin and employee views).
- `src/layouts/AppLayout.jsx` — sidebar/navbar shell, swaps nav items by role.
- `src/context` — auth state and toast notifications.
- `src/services` — Axios client (JWT auto-attached) + per-resource API calls.
- `src/components` — shared UI primitives (cards, modals, form inputs).
