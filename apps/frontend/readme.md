This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```


The frontend provides a clinical-facing web interface for interacting with the health_vitals backend. Planned pages include:

- **Dashboard** — overview of recent patient vitals, active alert summaries, and key health statistics at a glance
- **User Management** — admin interface for creating and managing accounts, assigning roles (admin, doctor, patient), and controlling access permissions
- **Patient Management** — doctor-facing view of assigned patients, their profiles, and linked wearable devices
- **Sensor Data** — browseable recording history per patient, filterable by time range, device, or vital type (heart rate, SpO2, etc.)
- **Alerts** — list of triggered alerts with severity levels, timestamps, and acknowledgement status; doctors can review and dismiss alerts
- **Device Management** — register and manage wearable devices, link them to individual patients

---

## Admin dashboard

A client-rendered admin console for inspecting devices, sensor recordings, alerts, and the Consumer Delivery Layer (CDL) lives under the `app/(admin)/` route group.

### Routes

| Path | Purpose |
|---|---|
| `/dashboard` | Stat cards (devices, 24-h recordings, alerts, live stress prediction) and a 7-day heart-rate chart from CDL `/overview`. |
| `/devices` | Devices CRUD for the signed-in user (`/api/v1/device`). |
| `/sensor-recordings` | Filter raw recordings by sensor type and date range; table + line chart. |
| `/alerts` | List of backend alerts (`/api/v1/alert/user/{id}`). |
| `/adapters` | Pretty-printed preview of CDL's per-consumer adapter outputs (`/api/v1/data/{consumer_type}/{user_id}`). |

### Running locally

```bash
# from the repo root
docker compose -f infra/docker-compose.yml up -d   # backend :8000, CDL :8001, postgres, redis, mlflow

cd apps/frontend
npm install
npm run dev                                        # http://localhost:3000
```

Open <http://localhost:3000/dashboard>. The login modal appears immediately — sign in with any account registered against the backend (`POST /api/v1/auth/login`).

### Configuration

The frontend talks to the backend and CDL through **same-origin Next.js rewrites** declared in `next.config.ts`:

```
/backend/*  →  $NEXT_PUBLIC_BACKEND_BASE_URL/api/v1/*  (default http://localhost:8000)
/cdl/ping   →  $NEXT_PUBLIC_CDL_BASE_URL/ping          (default http://localhost:8001)
/cdl/*      →  $NEXT_PUBLIC_CDL_BASE_URL/api/v1/*
```

To point at a remote backend/CDL, copy `.env.local.example` to `.env.local` and override the two `NEXT_PUBLIC_*` variables. Because of the rewrites, the browser never makes a cross-origin request — no CORS preflight is required.

### Authentication

- JWT issued by the backend is stored in `localStorage` under the key `hv.token`.
- The token's `sub` claim carries the user UUID; the frontend decodes it client-side with `jwt-decode` to call the user-scoped endpoints (`/device/user/{id}`, `/sensor_recordings/user/{id}`, `/alert/user/{id}`).
- The Zustand store at `store/authStore.ts` handles hydrate / login / logout / handle401 and schedules a `setTimeout` to auto-logout at the token's `exp`.
- A `mounted` guard inside `<AuthGate>` ensures SSR and the first client render produce the same `<PageSkeleton />`, so reading `localStorage` later doesn't cause a hydration mismatch.

### Design tokens

The medical-SaaS palette lives in `app/globals.css` under the `@theme inline` block (Tailwind v4). Custom tokens added by this work:

- `--color-vital` — `#00D4AA` (health indicators, accent line on charts)
- `--color-danger` — `#FF4D4F` (destructive actions, alert badges)
- `--color-sidebar` — `#0A1628` (deep sea blue)
- `--color-sidebar-hover` — `#1E3A5F`
- `--color-app-bg` — `#F8FAFC` (body background)

Fonts are loaded via `next/font/google`: `DM_Sans` for body and `JetBrains_Mono` for UUIDs/timestamps.

### Known limitations

1. **Alerts schema is minimal.** Backend `AlertResponse` only exposes `id`, `user_id`, `content`, `created_at`. Severity, threshold, and resolved-state columns will appear once the backend schema is extended.
2. **No Backend ↔ CDL toggle on Sensor Recordings.** CDL doesn't expose an equivalent raw-recordings list; only Dashboard's 7-day chart uses CDL (`/overview`).
3. **Single-tenant.** Scoped to the JWT-decoded user_id. The backend has no list-users endpoint, so there's no admin user picker yet.
4. **No dark mode.** Tokens are light-only; the sidebar stays dark regardless.
5. **Desktop-first.** Sidebar is fixed; below ~1024 px it overlaps content.
6. **No request retries / no client cache.** Failed requests show a toast; the user refreshes. The `useApi` interface is close to TanStack Query so swapping it in later is mechanical.
7. **Token in localStorage** (XSS-exposed). To harden, move issuance to a Next.js Route Handler and switch to an `httpOnly` cookie.
8. **JWT signature not verified client-side** — only the `exp` claim is checked. Every protected call still hits the backend, which re-verifies.
9. **No optimistic updates on device CRUD** — each mutation awaits the round-trip, then refetches.
10. **Recordings chart only renders numeric `data.value`** (or ACC `{x,y,z}` magnitude). The backend stores arbitrary JSON under `data`.
11. **Font swap may visually affect `/home`.** The landing page now uses DM Sans globally (the old Geist registrations were removed). If `/home` typography needs to stay Geist, scope DM Sans to the admin layout via `className={dmSans.className}` instead of putting it on `<html>`.

### Verification checklist

- `npx tsc --noEmit` — type-clean.
- `npm run build` — production build succeeds.
- Logged-out visit to `/dashboard` → skeleton + non-dismissible login modal.
- After signing in, refresh `/dashboard` → no modal flash, data loads.
- Corrupt the `hv.token` in DevTools → next API call triggers toast + modal reopens.
- Devices CRUD: add → edit → delete round-trip works; 422s surface as toasts.
- Sensor Recordings: change sensor_type and date range → table + chart refetch.
- Adapters: each of `smart_watch`, `web_dashboard`, `ml`, `researcher` returns JSON.
- DevTools Network: every backend/CDL call lands on `localhost:3000/backend/*` or `/cdl/*` (no cross-origin requests, no preflights).
