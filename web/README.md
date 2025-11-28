# Stellium Webapp

## Code Structure

```text
stellium/
├── src/stellium/              # Existing library
├── tests/
├── examples/
├── docs/
├── web/                       # 👈 New web app
│   ├── main.py               # Entry point
│   ├── config.py             # Colors, fonts, constants
│   ├── state.py              # Reactive state management
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── home.py           # Landing/home page
│   │   ├── natal.py          # Natal chart builder
│   │   ├── synastry.py       # Synastry/comparison charts
│   │   └── explore.py        # Notable births browser
│   ├── components/
│   │   ├── __init__.py
│   │   ├── header.py         # Site header/nav
│   │   ├── birth_input.py    # Birth data form
│   │   ├── chart_options.py  # House systems, components, etc.
│   │   ├── chart_display.py  # SVG chart viewer
│   │   └── code_preview.py   # "View as Python" panel
│   ├── static/
│   │   └── .gitkeep
│   └── requirements.txt
├── pyproject.toml
└── README.md
```
