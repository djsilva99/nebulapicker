import type { NextConfig } from "next";

// Force the default to be the Docker service name 'api'
const API_DESTINATION = process.env.API_URL || "http://api:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${API_DESTINATION}/:path*`,
      },
    ];
  },
};

export default nextConfig;
