import { expect, test } from '@playwright/test';
import { BASE_URL } from '../src/config.js';

test('authenticated session reaches the eParts catalog home', async ({ page }) => {
  test.skip(!BASE_URL, 'EPARTS_BASE_URL is not set.');

  await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
  await expect(page.locator('body')).toContainText(
    /Search in Catalog|Equipment Navigation|Working List|Parts Catalog|eParts/i,
    { timeout: 30_000 },
  );
});
