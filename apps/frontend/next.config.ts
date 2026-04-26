import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactStrictMode: true,

  async rewrites() {
    const rewrites = [];

    rewrites.push({
        source: '/',
        destination: '/home'
      })

    return rewrites;
  }
};

export default nextConfig;
