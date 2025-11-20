import type { NextConfig } from "next";

const API_DESTINATION = process.env.API_URL || "http://127.0.0.1:8081";

const nextConfig: NextConfig = {
  env: {
    API_URL: process.env.API_URL,
  },

  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${API_DESTINATION}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
