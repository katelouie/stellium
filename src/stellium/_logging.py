"""Internal logging setup for Stellium.

Library code emits operational diagnostics through :func:`get_logger`, a child
of the ``stellium`` root logger. Following the standard library-author pattern,
the root logger gets a :class:`~logging.NullHandler` at import, so Stellium is
**silent by default** -- nothing is printed unless the application opts in.

Applications configure output themselves (their choice of handlers/levels/
formatters), or use the :func:`configure_logging` convenience re-exported at the
top level as ``stellium.configure_logging``.

Diagnostics vs. warnings: use this logger for internal operational detail (cache
writes, file setup) the app opts into. Use :mod:`stellium.exceptions` warnings
for conditions the *caller* should see by default. See
``docs/development/specs/STRUCTURED_LOGGING_SPEC.md``.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import IO

_ROOT = "stellium"

# Silent by default: absorb records unless the application adds a real handler.
logging.getLogger(_ROOT).addHandler(logging.NullHandler())


def get_logger(name: str = "") -> logging.Logger:
    """Return the ``stellium`` logger, or a named child of it.

    Library code should call this with the module's dotted name relative to the
    package, e.g.::

        from stellium._logging import get_logger

        log = get_logger(__name__.removeprefix("stellium."))  # "utils.cache"
        log.warning("Could not write to cache: %s", exc)      # lazy formatting

    Args:
        name: Dotted suffix under the ``stellium`` root (``""`` for the root).

    Returns:
        The corresponding :class:`logging.Logger`.
    """
    return logging.getLogger(f"{_ROOT}.{name}" if name else _ROOT)


def configure_logging(
    level: int | str = "INFO",
    *,
    stream: IO[str] | None = None,
    fmt: str | None = None,
) -> logging.Logger:
    """Attach a stream handler to Stellium's logger -- one-call setup for apps.

    This is a convenience for scripts and applications that just want Stellium's
    logs on screen. Libraries embedding Stellium should generally configure the
    root logger themselves instead of calling this.

    Args:
        level: Log level for the ``stellium`` logger (name or numeric).
        stream: Destination stream (defaults to ``sys.stderr`` per
            :class:`logging.StreamHandler`).
        fmt: Optional :class:`logging.Formatter` format string. Defaults to
            ``"%(name)s %(levelname)s %(message)s"``.

    Returns:
        The configured ``stellium`` root logger.
    """
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter(fmt or "%(name)s %(levelname)s %(message)s"))
    root = logging.getLogger(_ROOT)
    root.addHandler(handler)
    root.setLevel(level)
    return root
