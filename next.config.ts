import type { NextConfig } from 'next';

// actions/configure-pages gives the Pages base path: "/<repo>" for a project site, "" for a
// user site or a custom domain. The workflow passes it in, so no repo name is hard-coded here.
const basePath = process.env.PAGES_BASE_PATH ?? '';

const config: NextConfig = {
  output: 'export',
  basePath,
  trailingSlash: true,
  images: { unoptimized: true },
};

export default config;
