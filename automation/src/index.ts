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

export { runLookup } from './lookup.js';
