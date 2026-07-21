# GeoVault frontend

React + Vite UI for the GeoVault API.

## Run (development)

1. Start the FastAPI backend on port **8000** (see `backend/README.md`).
2. Install and start Vite:

```bash
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173

With the default empty `VITE_API_BASE_URL`, requests go to the same origin and **Vite proxies** `/auth` and `/video` to `http://127.0.0.1:8000` (see `vite.config.ts`).

## Production build

Set `VITE_API_BASE_URL` to your API’s public URL when building, then serve the `dist/` folder behind your web server (or use a reverse proxy so API and app share one origin).

```bash
set VITE_API_BASE_URL=https://your-api.example.com
npm run build
npm run preview
```

## Preferences

**Theme** (light / dark / system) and **accent color** are stored in `localStorage` and apply instantly across the app.
