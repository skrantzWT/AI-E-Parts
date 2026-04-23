import { test as setup } from '@playwright/test';
import 'dotenv/config';

const authFile = 'playwright/.auth/eparts.json';

setup('login to eParts', async ({ page }) => {
  await page.goto(process.env.EPARTS_BASE_URL || 'https://portal.cnh.com/DPLogin/');

  await page.getByPlaceholder('User Id').fill(process.env.EPARTS_USERNAME || '');
  await page.getByPlaceholder('Password').fill(process.env.EPARTS_PASSWORD || '');

  await page.getByRole('button', { name: 'Log In' }).click();

  await page.getByRole('link', { name: 'eParts4.0 (NGPC Replacement)' }).first().click();

  const page1Promise = page.waitForEvent('popup');
  await page.getByRole('link', { name: 'Springdale Wt Transfer' }).first().click();
  const page1 = await page1Promise;

  await page1.getByRole('button', { name: 'Continue' }).click();
  await page1.getByRole('button', { name: 'Yes' }).click();

  await page1.context().storageState({ path: authFile });
});