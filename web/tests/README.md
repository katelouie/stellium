# Web app tests

In-process tests for the NiceGUI web app — **no browser required**. They run
under their own pytest config so the library's `pytest` run (which only
collects top-level `tests/`) stays free of web/async dependencies.

## Running locally

```bash
# from the repo root, with stellium installed (pip install -e ".[dev]")
pip install nicegui pytest-asyncio
pytest web/tests -c web/tests/pytest.ini
```

CI runs the same command in a standalone `web-tests` job.

## What's here (the testing tiers)

Most webapp bugs are *logic that happens to live in UI files*, not visual
rendering — so the bulk of the value is browser-free:

| File | Tier | What it covers |
|---|---|---|
| `test_imports.py` | 1 — import smoke | Every page/component module imports (catches syntax errors, bad imports, `_`-translator shadowing). |
| `test_state.py` | 2 — pure logic | `is_valid()` rules on the state dataclasses. |
| `test_i18n.py` | 2 — pure logic | `wt()` translation/passthrough, `wt_list()` feature lookup, `report_locale()` mapping (locale is monkeypatched). |
| `test_code_preview.py` | 2 — pure logic | "View as Python" generators produce valid, runnable Python (`ast.parse`) and reflect the selected locale. |
| `test_smoke.py` | 3 — interaction | NiceGUI `user` fixture drives the element tree in-process (page loads, empty-form validation). Keep this tier small. |

There is intentionally **no Selenium/browser (Tier 4)** here — it's slow and
flaky. If you ever need it, NiceGUI's `screen` fixture provides it; gate it
behind a marker and run it locally rather than in the default CI job.

## Adding tests

- New pure function (generator, helper, validation)? Add a Tier-2 unit test —
  call it and assert on the return value.
- New page/component module? Add it to `MODULES` in `test_imports.py`.
- New critical user flow? Add a small Tier-3 `user`-fixture test. Reach for the
  `user` fixture (in-process), not a real browser.
