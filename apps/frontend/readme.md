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
