"""Web app routes Stellium warnings into the logging system.

Importing ``main`` runs the app's logging setup, which calls
``logging.captureWarnings(True)`` so ``StelliumWarning`` diagnostics (bad
import rows, geocoding failures, invalid config) land in the app log instead
of being lost to stderr. See docs/development/specs/STRUCTURED_LOGGING_SPEC.md
(Phase 6).
"""

import importlib
import logging
import warnings

from stellium.exceptions import DataQualityWarning


def test_stellium_warnings_captured_into_logging():
    # Importing main runs the module-level logging config (captureWarnings).
    importlib.import_module("main")

    records: list[logging.LogRecord] = []
    handler = logging.Handler()
    handler.emit = records.append  # type: ignore[method-assign]

    pyw = logging.getLogger("py.warnings")
    pyw.addHandler(handler)
    old_level = pyw.level
    pyw.setLevel(logging.WARNING)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            warnings.warn("skipped a row", DataQualityWarning, stacklevel=1)
    finally:
        pyw.removeHandler(handler)
        pyw.setLevel(old_level)

    assert any("DataQualityWarning" in r.getMessage() for r in records), (
        "expected the StelliumWarning to be captured on the py.warnings logger"
    )
