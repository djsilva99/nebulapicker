import type { NextConfig } from "next";

// Force the default to be the Docker service name 'api'
const API_DESTINATION = "http://localhost:8080";

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
