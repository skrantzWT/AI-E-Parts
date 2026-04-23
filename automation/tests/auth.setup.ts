import { test, expect } from '@playwright/test';

test('auth setup placeholder', async ({ page }) => {
  const baseUrl = process.env.EPARTS_BASE_URL;
  expect(baseUrl).toBeTruthy();

  await page.goto(String(baseUrl), { waitUntil: 'domcontentloaded' });
  await expect(page).toHaveTitle(/eParts|Parts|Dealer|Login/i);

  // TODO: update this setup with real login selectors and saved auth state.
});
