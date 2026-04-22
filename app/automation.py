import os
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import Browser, Page, sync_playwright

from .models import LookupResult, ParsedRequest

load_dotenv()

ARTIFACTS_DIR = Path("data/artifacts")


def _headless_mode() -> bool:
    return os.getenv("EPARTS_HEADLESS", "true").lower() not in {"0", "false", "no"}


def login(page: Page) -> None:
    page.goto(os.environ["EPARTS_BASE_URL"])

    # Replace these selectors with real ones from your eParts instance.
    page.fill('input[name="username"]', os.environ["EPARTS_USERNAME"])
    page.fill('input[name="password"]', os.environ["EPARTS_PASSWORD"])
    page.click('button[type="submit"]')


def _build_stub_result(parsed: ParsedRequest) -> LookupResult:
    warnings = ["Replace placeholder selectors and search steps with recorded eParts flows."]
    if parsed.lookup_type == "unknown":
        warnings.append("Parser could not confidently classify the request yet.")

    return LookupResult(
        status="stub",
        description="Login completed, but the lookup path is still a scaffold.",
        source_path=parsed.lookup_type,
        warnings=warnings,
    )


def _save_failure_screenshot(page: Page) -> str:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    screenshot_path = ARTIFACTS_DIR / "lookup_failure.png"
    page.screenshot(path=str(screenshot_path), full_page=True)
    return str(screenshot_path)


def lookup_part(parsed: ParsedRequest | dict) -> LookupResult:
    parsed_request = parsed if isinstance(parsed, ParsedRequest) else ParsedRequest.model_validate(parsed)

    with sync_playwright() as playwright:
        browser: Browser = playwright.chromium.launch(headless=_headless_mode())
        context = browser.new_context()
        page = context.new_page()

        try:
            login(page)
            return _build_stub_result(parsed_request)
        except Exception as exc:
            screenshot_path = _save_failure_screenshot(page)
            return LookupResult(
                status="error",
                description=str(exc),
                source_path=parsed_request.lookup_type,
                warnings=["Lookup failed before a real search flow could complete."],
                screenshot_path=screenshot_path,
            )
        finally:
            browser.close()

