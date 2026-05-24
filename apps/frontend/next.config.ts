import type { NextConfig } from "next";

const backend = process.env.NEXT_PUBLIC_BACKEND_BASE_URL ?? "http://localhost:8000";
const cdl = process.env.NEXT_PUBLIC_CDL_BASE_URL ?? "http://localhost:8001";

const nextConfig: NextConfig = {
  reactStrictMode: true,

  async rewrites() {
    return [
      // Landing page lives under /home
      { source: "/", destination: "/home" },

      // Same-origin proxies so the browser never makes a cross-origin call.
      // Frontend code uses axios with baseURL "/backend" and "/cdl".
      { source: "/backend/:path*", destination: `${backend}/api/v1/:path*` },
      // CDL has /ping at the root and the rest under /api/v1 — match /ping first.
      { source: "/cdl/ping", destination: `${cdl}/ping` },
      { source: "/cdl/:path*", destination: `${cdl}/api/v1/:path*` },
    ];
  },
};

export default nextConfig;
