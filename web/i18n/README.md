# Web app i18n

Localization for the Stellium NiceGUI web app (separate from the library's
`stellium.i18n`, which translates report/chart content).

## Scheme: English source string is the key

`_("Create Your Birth Chart")` looks up the **English text itself** in the
active locale file. English is the identity locale (zero-overhead passthrough);
unknown keys fall back to the English text. This keeps the source readable and
new strings cheap to add — there are no semantic key names to invent or govern.

```python
from i18n import wt

def create_natal_page():
    _ = wt()                       # translator for the current user's locale
    ui.label(_("Create Your Birth Chart"))
    ui.button(_("CREATE CHART"))
    ui.notify(f"{_('Error:')} {err}")          # translate the static prefix only
    ui.label(f"☆  {_('CHART OPTIONS')}")        # translate text, keep the glyph
```

Call `_ = wt()` as the first line of **every function** that renders text
(nested inner functions can use the enclosing `_`).

> ⚠️ `_` is the translator here, so do **not** use `_` as a throwaway loop
> variable in these functions (`for name, _ in HOUSE_SYSTEMS`). Use `_code` etc.

### Selects / radios

Translate the display text, keep the internal value/key:

```python
ui.select({"outer": _("Outer planets only"), "all": _("All planets")}, ...)
```

If a control's logic compares against the *displayed* string, switch it to a
stable `key -> _(display)` dict and compare against the key, so translation
can't break the logic.

### Don't wrap

CSS classes, `.style()`/`.props()` strings, icon names, internal state values,
format hints (`"YYYY-MM-DD"`), URLs, filenames, and config-driven dropdown
option names that are technical astrology terms / proper nouns (house systems,
themes, palettes, ayanamsas, aspect sets).

## The home `features` array

The home feature cards are a nested list, translated by position via
`wt_list("features", ENGLISH_FEATURES)` (see `pages/home.py`). The translated
list lives under `home.features` in each locale file.

## Coverage check

`check_coverage.py` extracts every `_("...")` string from `web/` via the AST and
verifies each one has a translation in every locale file. Run it after editing:

```bash
python web/i18n/check_coverage.py
```

It exits non-zero on any **missing** key (used in code, no translation) and
lists **orphaned** keys (in a locale, unused in code) as a pruning hint. Wire it
into CI to make copy drift loud instead of a silent fall-back to English.

## Adding a language

1. Copy `zh_CN.json` to `web/i18n/{locale}.json`, keep the same English keys,
   translate the values (and the nested `home.features` list).
2. Add a display name in `get_available_locales()` in `__init__.py`.
3. Run `python web/i18n/check_coverage.py` to confirm full coverage.

The header language dropdown picks up new locale files automatically.
