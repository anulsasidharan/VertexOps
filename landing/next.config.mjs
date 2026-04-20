/** @type {import('next').NextConfig} */
const apiProxyTarget =
  process.env.VERTEXOPS_API_PROXY_TARGET?.replace(/\/$/, "") ?? "http://127.0.0.1:8000";

const nextConfig = {
  images: {
    unoptimized: true,
  },
  /** Same-origin ``/api/*`` → FastAPI (port 8000) for optional client-side calls from the marketing site. */
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${apiProxyTarget}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
