"""Pytest config for the web app test suite.

Runs in-process (no browser) using NiceGUI's `user` fixture for interaction
tests plus plain pytest for the pure-logic tests. Put `web/` on the import
path so the app's top-level imports (`config`, `i18n`, `pages`, ...) resolve.
"""

import os
import sys

WEB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WEB_DIR not in sys.path:
    sys.path.insert(0, WEB_DIR)

# NiceGUI's in-process user-simulation fixture (no Selenium).
pytest_plugins = ["nicegui.testing.user_plugin"]
