import path from 'node:path';
import { fileURLToPath } from 'node:url';
import dotenv from 'dotenv';

const CURRENT_FILE = fileURLToPath(import.meta.url);
const SRC_DIR = path.dirname(CURRENT_FILE);
const AUTOMATION_DIR = path.resolve(SRC_DIR, '..');
const REPO_ROOT_DIR = path.resolve(AUTOMATION_DIR, '..');
const ROOT_ENV_PATH = path.join(REPO_ROOT_DIR, '.env');
const FALSEY_ENV_VALUES = new Set(['false', '0']);

dotenv.config({ path: ROOT_ENV_PATH });

function readEnv(name: string): string {
  return process.env[name]?.trim() ?? '';
}

export function requireEnv(name: string): string {
  const value = readEnv(name);
  if (!value) {
    throw new Error(`${name} is required.`);
  }
  return value;
}

export const AUTH_FILE_RELATIVE = 'playwright/.auth/eparts.json';
export const AUTH_FILE_ABSOLUTE = path.join(AUTOMATION_DIR, AUTH_FILE_RELATIVE);
export const PORTAL_URL = readEnv('EPARTS_PORTAL_URL') || 'https://portal.cnh.com/DPLogin/';
export const BASE_URL = readEnv('EPARTS_BASE_URL');
export const APP_LINK_TEXT = readEnv('EPARTS_APP_LINK_TEXT') || 'eParts4.0';
export const DEALER_LINK_TEXT = readEnv('EPARTS_DEALER_LINK_TEXT');
export const HEADLESS = !FALSEY_ENV_VALUES.has(readEnv('EPARTS_HEADLESS').toLowerCase());
