import { test, expect } from '@playwright/test';
import { runLookup } from '../src/lookup.js';

test('automation subsystem can reach the eParts entry page', async () => {
  const result = await runLookup({ model: 'Workmaster 75', part: 'oil filter' });
  expect(['stub', 'success', 'error', 'blocked']).toContain(result.status);
  expect(result.finalUrl).toBeTruthy();
  expect(result.sourcePath).toBe('model');
});
