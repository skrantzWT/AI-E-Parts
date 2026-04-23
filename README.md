# AI E-Parts

Starter scaffold for an eParts lookup service with four layers:

- FastAPI for the `/lookup` endpoint
- OpenAI parsing for structured lookup intent
- Playwright for deterministic browser automation
- Codex CLI as the local agentic coding layer

## Project layout

```text
AI E-Parts/
  app/                 ← your intelligence layer (LLM + parsing)
    __init__.py
    automation.py
    logging_utils.py
    main.py
    models.py
    parser.py
    prompts.py
  automation/          ← Playwright subsystem for browser execution
    README.md
    package.json
    playwright.config.ts
    src/
      index.ts
      lookup.ts
    tests/
      auth.setup.ts
      lookup.spec.ts
  data/
    eval_cases.json
    eparts_workflow_notes.md
    logs/
  scripts/
    smoke_test.py
  tests/
    test_parser.py
  .env.example
  .gitignore
  README.md
  requirements.txt
  package.json
```

## Prerequisites

- Python 3.11+
- Node.js 20+
- Git
- An OpenAI API key

## Setup

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Mac/Linux:

```bash
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
python -m playwright install
```

Install Codex CLI:

```bash
npm install -g @openai/codex
```

## Environment

Copy `.env.example` to `.env` and fill in your real credentials:

```env
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-5
EPARTS_BASE_URL=https://your-eparts-url
EPARTS_USERNAME=your_username
EPARTS_PASSWORD=your_password
EPARTS_HEADLESS=true
```

## Automation subsystem

The Playwright automation lives in `automation/` as a separate subsystem within the same repo. This keeps the browser executor isolated while allowing the Python agent to remain the intelligence layer.

Install and run it from the repo root:

```bash
npm install
npm run automation:install
npm run automation:test
```

Then record real eParts selectors with:

```bash
cd automation
npx playwright codegen
```

## Run the API

```bash
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Lookup request:

```bash
curl -X POST http://127.0.0.1:8000/lookup \
  -H "Content-Type: application/json" \
  -d "{\"user_text\":\"I need an oil filter for my Workmaster 75\"}"
```

## Run parser tests

```bash
pytest
```

The parser unit tests mock the OpenAI call so they stay fast and deterministic.

## Run the smoke test

```bash
python scripts/smoke_test.py
```

This loads `data/eval_cases.json`, calls the parser, and prints the resulting structured intents.

## Current eParts findings

- The training workflow summary is captured in [data/eparts_workflow_notes.md](data/eparts_workflow_notes.md).
- The currently configured `EPARTS_BASE_URL` returns an `Access Denied` / HTTP `403` page to Playwright from this environment.
- The automation layer now reports that blocked state explicitly and saves a screenshot artifact instead of assuming a login page.

## Recording eParts flows

Use Playwright code generation to capture real selectors:

```bash
playwright codegen https://your-eparts-url
```

Recommended flows to record:

- Login
- Model lookup for `Workmaster 75`
- Serial-number lookup for a known machine
- Oil filter lookup
- Air filter lookup

Then replace the placeholder selectors in `app/automation.py` with the locators from your real eParts environment.

## Suggested Codex tasks

Start Codex CLI in the repo root and feed it bounded prompts like:

- `Read this repo and summarize what is missing for a first end-to-end lookup.`
- `Add parser edge-case tests for ambiguous model vs serial requests.`
- `Refactor automation.py to use traced Playwright sessions and screenshot-on-failure.`
- `Implement the Workmaster 75 model-search path using recorded selectors.`
