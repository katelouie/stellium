"""Phase 2: internal operational diagnostics use the stellium logger, not print.

Covers the migration of the remaining non-render library prints to the
``stellium`` logger (``docs/development/specs/STRUCTURED_LOGGING_SPEC.md``
Phase 2):

- ``utils/cache.py`` cache-write failure -> ``log.warning`` (tested here).
- ``data/paths.py`` ephemeris file-copy failure -> ``log.warning``, custom-path
  missing -> ``log.warning``, first-run init -> ``log.info``. These share the
  same logging channel proven here; they're not unit-tested directly because
  triggering them mutates global Swiss Ephemeris path state for the session.

The logging channel itself (NullHandler-by-default silence, logger naming,
``configure_logging``) is covered in ``test_logging_infra``.
"""

import logging


def test_cache_write_failure_logs_warning(tmp_path, caplog):
    from stellium.utils.cache import Cache

    cache = Cache(cache_dir=str(tmp_path / "cache"))

    # A lambda cannot be pickled, so the write raises inside set() -- the cache
    # must swallow it and log a warning, not crash or print.
    with caplog.at_level(logging.WARNING, logger="stellium"):
        cache.set("general", "unpicklable", lambda x: x)

    records = [r for r in caplog.records if r.name == "stellium.utils.cache"]
    assert records, "expected a log record on the stellium.utils.cache logger"
    assert records[0].levelno == logging.WARNING
    assert "Could not write to cache" in records[0].getMessage()


def test_cache_write_failure_does_not_print(tmp_path, capsys):
    """The failure is logged, never printed to stdout/stderr."""
    from stellium.utils.cache import Cache

    cache = Cache(cache_dir=str(tmp_path / "cache"))
    cache.set("general", "unpicklable", lambda x: x)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
