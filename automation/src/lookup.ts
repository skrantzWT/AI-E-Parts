import fs from 'node:fs';
import { chromium } from 'playwright';
import { AUTH_FILE_ABSOLUTE, BASE_URL, HEADLESS } from './config.js';

export type LookupParams = {
  model?: string;
  part?: string;
  serialNumber?: string;
};

export type LookupResult = {
  status: 'stub' | 'success' | 'error' | 'blocked';
  partNumber?: string;
  description?: string;
  sourcePath?: string;
  warnings?: string[];
  finalUrl?: string;
  entryState?: string;
  httpStatus?: number;
  screenshotPath?: string;
};

function resolveSourcePath(params: LookupParams): string {
  if (params.serialNumber) {
    return 'serial';
  }
  if (params.model) {
    return 'model';
  }
  return 'unknown';
}

function classifyEntry(bodyText: string): string {
  const normalized = bodyText.toLowerCase();
  if (normalized.includes('access denied') || normalized.includes('403') || normalized.includes('forbidden')) {
    return 'blocked';
  }
  if (normalized.includes('sign in') || normalized.includes('login') || normalized.includes('username')) {
    return 'login_required';
  }
  return 'public';
}

export async function runLookup(params: LookupParams): Promise<LookupResult> {
  if (!BASE_URL) {
    return {
      status: 'error',
      description: 'EPARTS_BASE_URL is required to run catalog lookup.',
      sourcePath: resolveSourcePath(params),
      warnings: ['Set EPARTS_BASE_URL in the repo root .env before running lookup automation.'],
    };
  }

  const browser = await chromium.launch({ headless: HEADLESS });
  const context = await browser.newContext(
    fs.existsSync(AUTH_FILE_ABSOLUTE) ? { storageState: AUTH_FILE_ABSOLUTE } : {},
  );
  const page = await context.newPage();

  try {
    const response = await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
    const bodyText = (await page.locator('body').innerText()) ?? '';
    const entryState = classifyEntry(bodyText);

    return {
      status: 'stub',
      description: 'Playwright automation subsystem has reached the entry page; replace selectors with real eParts workflow steps.',
      sourcePath: resolveSourcePath(params),
      warnings: [
        'This automation path is currently a scaffold. Update selectors and page flow for your real dealer portal.',
      ],
      finalUrl: page.url(),
      entryState,
      httpStatus: response?.status(),
    };
  } catch (error) {
    return {
      status: 'error',
      description: String(error),
      sourcePath: resolveSourcePath(params),
      warnings: ['Playwright failed before the real lookup flow could complete.'],
    };
  } finally {
    await context.close();
    await browser.close();
  }
}
