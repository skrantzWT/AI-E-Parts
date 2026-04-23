import { chromium } from 'playwright';

const BASE_URL = process.env.EPARTS_BASE_URL;
if (!BASE_URL) {
  throw new Error('EPARTS_BASE_URL is required to run automation.');
}

const HEADLESS = process.env.EPARTS_HEADLESS !== 'false' && process.env.EPARTS_HEADLESS !== '0';

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
  const browser = await chromium.launch({ headless: HEADLESS });
  const page = await browser.newPage();

  try {
    const response = await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
    const bodyText = (await page.locator('body').innerText()) ?? '';
    const entryState = classifyEntry(bodyText);

    return {
      status: 'stub',
      description: 'Playwright automation subsystem has reached the entry page; replace selectors with real eParts workflow steps.',
      sourcePath: params.serialNumber ? 'serial' : params.model ? 'model' : 'unknown',
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
      sourcePath: params.serialNumber ? 'serial' : params.model ? 'model' : 'unknown',
      warnings: ['Playwright failed before the real lookup flow could complete.'],
    };
  } finally {
    await browser.close();
  }
}
