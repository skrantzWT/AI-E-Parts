# eParts Workflow Notes

This note summarizes the vendor training PDFs currently located in `C:\Users\skrantz\Downloads\` and the runtime behavior observed against the configured storefront URL on April 22, 2026.

## Documented workflow

- `Search Overview` lists the main entry paths as search per equipment, search per part, equipment navigation, and latest search.
- `Equipment Search & Model Overview` documents the main equipment flow as search by model or serial number, then Product List Page, then Model Page, then Figure Page, then Part Detail Page.
- `Search per Part and Part List Page` documents part-number / description search, landing on Part Detail Page, and the Part List Page with upper section, results list, and check boxes.
- `Model Page` documents search by model, search by serial number, search in model, related models, notes, and technical/marketing materials.
- `Figure Page` documents figure landing, part list details, serial-number filtering, the serial number window, and the ability to open Part Detail Page from a selected part number.

## Automation implications

- A good first deterministic automation path is:
  1. Open the storefront
  2. Search by model or serial number
  3. Land on Product List Page / Model Page
  4. Open the target Figure Page
  5. Select the part and capture Part Detail Page data
- Serial-number flows appear to add SN-specific filters on both Model Page and Figure Page.
- Model and Figure pages both mention "Search in Model", which is likely a strong candidate for part-name lookup once selectors are available.

## Current runtime finding

- The configured `EPARTS_BASE_URL` currently returns HTTP `403` with an `Access Denied` page when accessed through Playwright automation from this environment.
- Because of that, the automation code now reports a `blocked` result with screenshot evidence instead of incorrectly assuming a login page or a successful catalog session.
- The next practical step is to record selectors from a browser session the site accepts, or to use a storefront endpoint/session that allows automation access.

