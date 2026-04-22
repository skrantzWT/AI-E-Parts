from app.automation import classify_catalog_entry


def test_classify_catalog_entry_detects_blocked() -> None:
    state = classify_catalog_entry(
        status_code=403,
        title="Access Denied",
        body_text="You don't have permission to access this server.",
        has_username_input=False,
        has_password_input=False,
    )
    assert state == "blocked"


def test_classify_catalog_entry_detects_login_required() -> None:
    state = classify_catalog_entry(
        status_code=200,
        title="Sign in",
        body_text="Please sign in to continue.",
        has_username_input=True,
        has_password_input=True,
    )
    assert state == "login_required"


def test_classify_catalog_entry_detects_public_catalog() -> None:
    state = classify_catalog_entry(
        status_code=200,
        title="Parts Catalog",
        body_text="Search by model or serial number.",
        has_username_input=False,
        has_password_input=False,
    )
    assert state == "public"
