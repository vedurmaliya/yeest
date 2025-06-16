/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    BACKEND_URL: 'https://yeest-backend-830732726616.asia-south1.run.app',
  },
}

module.exports = nextConfig
