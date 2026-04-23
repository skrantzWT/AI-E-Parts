import { defineConfig, devices } from '@playwright/test';
import { AUTH_FILE_RELATIVE, BASE_URL, HEADLESS } from './src/config.js';

const authSetupPattern = /.*auth\.setup(\.spec)?\.ts/;

export default defineConfig({
  testDir: './tests',
  timeout: 120_000,
  expect: {
    timeout: 10_000,
  },
  outputDir: 'test-results',
  use: {
    headless: HEADLESS,
    viewport: { width: 1280, height: 800 },
    actionTimeout: 30_000,
    baseURL: BASE_URL || undefined,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'setup',
      testMatch: authSetupPattern,
      use: {
        ...devices['Desktop Chrome'],
      },
    },
    {
      name: 'chromium',
      dependencies: ['setup'],
      testIgnore: authSetupPattern,
      use: {
        ...devices['Desktop Chrome'],
        storageState: AUTH_FILE_RELATIVE,
      },
    },
  ],
});
