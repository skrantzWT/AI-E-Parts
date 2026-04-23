import fs from 'node:fs';
import path from 'node:path';
import { expect, type Page, test as setup } from '@playwright/test';
import {
  APP_LINK_TEXT,
  AUTH_FILE_ABSOLUTE,
  DEALER_LINK_TEXT,
  PORTAL_URL,
  requireEnv,
} from '../src/config.js';

const CATALOG_HOME_SIGNAL = /Search in Catalog|Equipment Navigation|Working List|Parts Catalog|eParts/i;

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

async function clickLinkMaybePopup(page: Page, linkText: string, timeout = 60_000): Promise<Page> {
  const popupPromise = page.waitForEvent('popup', { timeout: 5_000 }).catch(() => null);
  const link = page.getByRole('link', { name: new RegExp(escapeRegExp(linkText), 'i') }).first();
  await link.waitFor({ state: 'visible', timeout });
  await link.click();

  const popup = await popupPromise;
  const targetPage = popup ?? page;
  await targetPage.waitForLoadState('domcontentloaded', { timeout: 30_000 }).catch(() => undefined);
  return targetPage;
}

async function maybeClickButton(page: Page, label: string): Promise<boolean> {
  const button = page.getByRole('button', { name: new RegExp(`^${escapeRegExp(label)}$`, 'i') }).first();
  const isVisible = await button
    .waitFor({ state: 'visible', timeout: 5_000 })
    .then(() => true)
    .catch(() => false);

  if (!isVisible) {
    return false;
  }

  await button.click();
  await page.waitForLoadState('domcontentloaded', { timeout: 30_000 }).catch(() => undefined);
  return true;
}

async function maybeSelectDealer(page: Page): Promise<Page> {
  if (!DEALER_LINK_TEXT) {
    return page;
  }

  const dealerLink = page.getByRole('link', {
    name: new RegExp(escapeRegExp(DEALER_LINK_TEXT), 'i'),
  }).first();
  const isVisible = await dealerLink
    .waitFor({ state: 'visible', timeout: 10_000 })
    .then(() => true)
    .catch(() => false);

  if (!isVisible) {
    return page;
  }

  return clickLinkMaybePopup(page, DEALER_LINK_TEXT, 10_000);
}

async function waitForCatalogHome(page: Page): Promise<void> {
  await expect(page.locator('body')).toContainText(CATALOG_HOME_SIGNAL, { timeout: 60_000 });
}

setup('login to eParts', async ({ page }) => {
  const username = requireEnv('EPARTS_USERNAME');
  const password = requireEnv('EPARTS_PASSWORD');

  await page.goto(PORTAL_URL, { waitUntil: 'domcontentloaded' });
  await page.getByPlaceholder('User Id').fill(username);
  await page.getByPlaceholder('Password').fill(password);
  await page.getByRole('button', { name: /log in/i }).click();

  const appPage = await clickLinkMaybePopup(page, APP_LINK_TEXT);
  const dealerPage = await maybeSelectDealer(appPage);

  await maybeClickButton(dealerPage, 'Continue');
  await maybeClickButton(dealerPage, 'Yes');
  await waitForCatalogHome(dealerPage);

  fs.mkdirSync(path.dirname(AUTH_FILE_ABSOLUTE), { recursive: true });
  await dealerPage.context().storageState({ path: AUTH_FILE_ABSOLUTE });
});
