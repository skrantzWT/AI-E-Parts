import os
from datetime import datetime
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from playwright.sync_api import Browser, Page, sync_playwright

from .models import LookupResult, ParsedRequest

load_dotenv()

ARTIFACTS_DIR = Path("data/artifacts")
ENTRY_STATE = Literal["public", "login_required", "blocked", "unknown"]

USERNAME_SELECTORS = (
    'input[name="username"]',
    'input[name="email"]',
    'input[name="login"]',
    'input[type="email"]',
    'input[id*="user"]',
)
PASSWORD_SELECTORS = (
    'input[name="password"]',
    'input[type="password"]',
)
ACCESS_DENIED_MARKERS = (
    "access denied",
    "you don't have permission",
    "forbidden",
)


def _headless_mode() -> bool:
    return os.getenv("EPARTS_HEADLESS", "true").lower() not in {"0", "false", "no"}


def _first_available_selector(page: Page, selectors: tuple[str, ...]) -> str | None:
    for selector in selectors:
        if page.locator(selector).count() > 0:
            return selector
    return None


def _safe_page_text(page: Page) -> str:
    return page.locator("body").inner_text()[:4000] if page.locator("body").count() else ""


def classify_catalog_entry(
    *,
    status_code: int | None,
    title: str,
    body_text: str,
    has_username_input: bool,
    has_password_input: bool,
) -> ENTRY_STATE:
    combined_text = f"{title}\n{body_text}".lower()
    if status_code == 403 or any(marker in combined_text for marker in ACCESS_DENIED_MARKERS):
        return "blocked"
    if has_password_input or (has_username_input and "sign in" in combined_text):
        return "login_required"
    if title.strip() or body_text.strip():
        return "public"
    return "unknown"


def inspect_catalog_entry(page: Page) -> dict[str, str | int | ENTRY_STATE | None]:
    title = page.title()
    body_text = _safe_page_text(page)
    username_selector = _first_available_selector(page, USERNAME_SELECTORS)
    password_selector = _first_available_selector(page, PASSWORD_SELECTORS)

    return {
        "title": title,
        "body_text": body_text,
        "entry_state": classify_catalog_entry(
            status_code=None,
            title=title,
            body_text=body_text,
            has_username_input=username_selector is not None,
            has_password_input=password_selector is not None,
        ),
        "username_selector": username_selector,
        "password_selector": password_selector,
    }


def open_catalog(page: Page) -> dict[str, str | int | ENTRY_STATE | None]:
    response = page.goto(os.environ["EPARTS_BASE_URL"], wait_until="domcontentloaded", timeout=60000)
    details = inspect_catalog_entry(page)
    status_code = response.status if response else None
    details["http_status"] = status_code
    details["final_url"] = page.url
    details["entry_state"] = classify_catalog_entry(
        status_code=status_code,
        title=str(details["title"] or ""),
        body_text=str(details["body_text"] or ""),
        has_username_input=details["username_selector"] is not None,
        has_password_input=details["password_selector"] is not None,
    )
    return details


def login(page: Page, entry_details: dict[str, str | int | ENTRY_STATE | None]) -> dict[str, str | int | ENTRY_STATE | None]:
    username = os.getenv("EPARTS_USERNAME")
    password = os.getenv("EPARTS_PASSWORD")
    username_selector = entry_details.get("username_selector")
    password_selector = entry_details.get("password_selector")

    if not username or not password:
        raise RuntimeError("The catalog requires login, but EPARTS_USERNAME or EPARTS_PASSWORD is missing.")
    if not username_selector or not password_selector:
        raise RuntimeError("The catalog appears to require login, but login inputs could not be identified.")

    page.fill(str(username_selector), username)
    page.fill(str(password_selector), password)
    page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")')
    page.wait_for_load_state("domcontentloaded")
    return inspect_catalog_entry(page)


def _build_stub_result(parsed: ParsedRequest, entry_details: dict[str, str | int | ENTRY_STATE | None]) -> LookupResult:
    warnings = [
        "Documented eParts flow is Home/Search -> Product List -> Model Page -> Figure Page -> Part Detail Page.",
        "Search paths are still stubbed until we record working selectors from an allowed browser session.",
    ]
    if parsed.lookup_type == "unknown":
        warnings.append("Parser could not confidently classify the request yet.")

    return LookupResult(
        status="stub",
        description="Catalog entry succeeded, but the lookup path is still a scaffold.",
        source_path=parsed.lookup_type,
        warnings=warnings,
        entry_state=str(entry_details.get("entry_state") or "unknown"),
        page_title=str(entry_details.get("title") or ""),
        final_url=str(entry_details.get("final_url") or page_url_fallback()),
        http_status=int(entry_details["http_status"]) if entry_details.get("http_status") is not None else None,
    )


def page_url_fallback() -> str:
    return os.getenv("EPARTS_BASE_URL", "")


def _save_failure_screenshot(page: Page, prefix: str = "lookup_failure") -> str:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = ARTIFACTS_DIR / f"{prefix}_{timestamp}.png"
    page.screenshot(path=str(screenshot_path), full_page=True)
    return str(screenshot_path)


def _build_blocked_result(parsed: ParsedRequest, entry_details: dict[str, str | int | ENTRY_STATE | None], screenshot_path: str) -> LookupResult:
    return LookupResult(
        status="blocked",
        description="The configured eParts URL returned an Access Denied/403 response to automation.",
        source_path=parsed.lookup_type,
        warnings=[
            "The storefront is reachable, but automated browser access is currently blocked.",
            "Capture selectors from a browser session the site accepts, or use an allowlisted automation path.",
        ],
        screenshot_path=screenshot_path,
        entry_state="blocked",
        page_title=str(entry_details.get("title") or ""),
        final_url=str(entry_details.get("final_url") or page_url_fallback()),
        http_status=int(entry_details["http_status"]) if entry_details.get("http_status") is not None else None,
    )


def lookup_part(parsed: ParsedRequest | dict) -> LookupResult:
    parsed_request = parsed if isinstance(parsed, ParsedRequest) else ParsedRequest.model_validate(parsed)

    with sync_playwright() as playwright:
        browser: Browser = playwright.chromium.launch(headless=_headless_mode())
        context = browser.new_context()
        page = context.new_page()

        try:
            entry_details = open_catalog(page)
            if entry_details["entry_state"] == "blocked":
                screenshot_path = _save_failure_screenshot(page, prefix="access_denied")
                return _build_blocked_result(parsed_request, entry_details, screenshot_path)

            if entry_details["entry_state"] == "login_required":
                entry_details = login(page, entry_details)
                entry_details["final_url"] = page.url
                entry_details["http_status"] = entry_details.get("http_status")
                if entry_details["entry_state"] == "blocked":
                    screenshot_path = _save_failure_screenshot(page, prefix="access_denied")
                    return _build_blocked_result(parsed_request, entry_details, screenshot_path)
                if entry_details["entry_state"] == "login_required":
                    raise RuntimeError("Login flow completed, but the catalog still presents a login screen.")

            return _build_stub_result(parsed_request, entry_details)
        except Exception as exc:
            screenshot_path = _save_failure_screenshot(page)
            return LookupResult(
                status="error",
                description=str(exc),
                source_path=parsed_request.lookup_type,
                warnings=["Lookup failed before a real search flow could complete."],
                screenshot_path=screenshot_path,
                final_url=page.url if page.url else page_url_fallback(),
            )
        finally:
            browser.close()
