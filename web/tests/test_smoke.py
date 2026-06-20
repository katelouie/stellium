"""Tier 3 — in-process interaction tests via NiceGUI's `user` fixture.

These exercise real page rendering and event handlers without a browser
(no Selenium): the fixture drives the element tree in-process. Keep this
tier small — a few critical-path smoke checks, not feature coverage.
"""

from nicegui.testing import User


async def test_home_page_loads(user: User) -> None:
    await user.open("/")
    await user.should_see("Stellium")


async def test_natal_page_loads(user: User) -> None:
    await user.open("/natal")
    await user.should_see("Create Your Birth Chart")


async def test_natal_create_chart_validates_empty_form(user: User) -> None:
    # Clicking "CREATE CHART" with no birth data should surface a validation notice.
    await user.open("/natal")
    user.find("CREATE CHART").click()
    await user.should_see("Please fill in all required fields")
