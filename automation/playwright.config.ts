import type { PlaywrightTestConfig } from '@playwright/test';

const config: PlaywrightTestConfig = {
  testDir: './tests',
  timeout: 120_000,
  expect: {
    timeout: 10_000,
  },
  use: {
    headless: process.env.EPARTS_HEADLESS !== 'false' && process.env.EPARTS_HEADLESS !== '0',
    viewport: { width: 1280, height: 800 },
    actionTimeout: 30_000,
    baseURL: process.env.EPARTS_BASE_URL,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
};

export default config;
