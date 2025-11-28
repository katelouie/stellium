import os
import sys

sys.path.insert(0, os.path.abspath(".."))
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Stellium"
copyright = "2025, Kate Louie"
author = "Kate Louie"
release = "0.3.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # Auto-generate docs from docstrings
    "sphinx.ext.napoleon",  # Support Google/NumPy docstrings
    "sphinx.ext.viewcode",  # Add links to source code
    "sphinx.ext.intersphinx",  # Link to other docs
    "sphinx_autodoc_typehints",  # Better type hints
    "myst_parser",  # MARKDOWN SUPPORT!
]

# MyST configuration
myst_enable_extensions = [
    "colon_fence",  # ::: fences
    "deflist",  # Definition lists
    "tasklist",  # Task lists
]

# Source file suffixes
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"

# Warm mystical purple theme matching PDF reports
html_theme_options = {
    "light_css_variables": {
        # Primary colors - warm mystical purple
        "color-brand-primary": "#4a3353",  # Deep warm purple
        "color-brand-content": "#6b4d6e",  # Medium warm purple
        # Background colors - warm cream
        "color-background-primary": "#faf8f5",  # Warm cream
        "color-background-secondary": "#f3efe8",  # Slightly darker cream
        "color-background-hover": "#ebe5dd",  # Hover state
        "color-background-border": "#d4cdc3",  # Subtle borders
        # Foreground/text colors
        "color-foreground-primary": "#2d2330",  # Warm near-black text
        "color-foreground-secondary": "#4a3353",  # Deep purple for secondary text
        "color-foreground-muted": "#6b4d6e",  # Medium purple for muted text
        # Links
        "color-link": "#6b4d6e",  # Medium purple links
        "color-link--hover": "#4a3353",  # Darker on hover
        "color-link-underline": "#8e6b8a",  # Light mauve underline
        "color-link-underline--hover": "#6b4d6e",  # Medium purple underline on hover
        # Code blocks
        "color-code-background": "#f3efe8",  # Warm cream for code
        "color-code-foreground": "#4a3353",  # Purple code text
        # Admonitions (notes, warnings, etc)
        "color-admonition-background": "#f9f5f0",
        "color-admonition-title-background": "#8e6b8a",  # Light mauve
        "color-admonition-title": "#faf8f5",
        # Sidebar
        "color-sidebar-background": "#faf8f5",
        "color-sidebar-background-border": "#d4cdc3",
        "color-sidebar-brand-text": "#4a3353",
        "color-sidebar-link-text": "#2d2330",
        "color-sidebar-link-text--top-level": "#4a3353",
        # API documentation
        "color-api-background": "#f9f5f0",
        "color-api-background-hover": "#f3efe8",
        "color-api-name": "#4a3353",
        "color-api-pre-name": "#6b4d6e",
        # Highlights
        "color-highlighted-background": "#fff9e6",
        "color-highlighted-text": "#2d2330",
        # Typography - more readable for docs
        "font-stack": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif",
        "font-stack--monospace": "'JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', monospace",
        "font-size--normal": "16px",
        "font-size--small": "14px",
        "font-size--small--2": "12px",
    },
    "dark_css_variables": {
        # Dark mode - mystical night sky
        "color-brand-primary": "#a78bfa",  # Light purple
        "color-brand-content": "#c4b5fd",  # Lighter purple
        # Dark backgrounds
        "color-background-primary": "#1a1625",  # Deep purple-black
        "color-background-secondary": "#221c2e",  # Slightly lighter
        "color-background-hover": "#2d2640",  # Hover state
        "color-background-border": "#3d3450",  # Borders
        # Dark foreground
        "color-foreground-primary": "#e9e4f0",  # Light cream text
        "color-foreground-secondary": "#d4c5e8",  # Muted cream
        "color-foreground-muted": "#b8a5d0",  # Very muted
        # Dark links
        "color-link": "#c4b5fd",  # Light purple
        "color-link--hover": "#a78bfa",  # Medium purple
        "color-link-underline": "#8e6b8a",
        "color-link-underline--hover": "#a78bfa",
        # Dark code
        "color-code-background": "#2d2640",
        "color-code-foreground": "#c4b5fd",
        # Dark admonitions
        "color-admonition-background": "#2d2640",
        "color-admonition-title-background": "#6b4d6e",
        "color-admonition-title": "#faf8f5",
        # Dark sidebar
        "color-sidebar-background": "#1a1625",
        "color-sidebar-background-border": "#3d3450",
        "color-sidebar-brand-text": "#c4b5fd",
        "color-sidebar-link-text": "#e9e4f0",
        "color-sidebar-link-text--top-level": "#a78bfa",
        # Dark API
        "color-api-background": "#2d2640",
        "color-api-background-hover": "#3d3450",
        "color-api-name": "#c4b5fd",
        "color-api-pre-name": "#a78bfa",
    },
    # Additional theme options
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_button": "edit",
    # Footer content
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/yourusername/stellium",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
}

html_title = "Stellium"
html_short_title = "Stellium"

html_static_path = ["_static"]
html_css_files = [
    "custom.css",
]
html_js_files = [
    "force_light_default.js",
]

# Intersphinx
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# Pygments style for code highlighting
pygments_style = "autumn"  # Warm colors matching your theme
pygments_dark_style = "dracula"  # For dark mode
