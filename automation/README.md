# automation

This folder contains the Playwright automation subsystem for the AI E-Parts project.

## Purpose

- Keep browser automation isolated from the Python agent layer.
- Record and execute real eParts workflows using Playwright.
- Expose a reusable `runLookup()` function for later integration.

## Install

```bash
cd automation
npm install
npx playwright install
```

## Run tests

```bash
cd automation
npm test
```

## Quick start

- Update `EPARTS_BASE_URL` and credentials in the root `.env`.
- Record login selectors and lookup flows with `npx playwright codegen`.
- Replace stub behavior in `src/lookup.ts` with the real eParts navigation path.
