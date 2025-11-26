# Interactive HTML Reports with Jinja2 + Pico.css + Alpine.js

**Status:** Planned for future implementation
**Created:** November 26, 2025
**Goal:** Transform HTML reports from static PDFs-in-HTML to interactive web experiences

---

## Vision

Create beautiful, interactive HTML reports that take advantage of the web platform while still printing perfectly to PDF. Think: **collapsible sections, tabbed house systems, filterable aspects, dark mode, search** - all the things that make web reports BETTER than static PDFs.

---

## Technology Stack

### Jinja2 (Template Engine)
- **Why:** Composable templates, same pattern as our Typst renderer
- **Size:** ~200KB (dev dependency, not runtime)
- **Features:** Template inheritance, includes, macros, filters
- **Already familiar:** Widely used in Python ecosystem

### Pico.css (Classless CSS Framework)
- **Why:** Beautiful semantic HTML styling, no class names needed
- **Size:** ~13KB minified
- **Features:**
  - Dark/light themes built-in
  - Excellent print styles (still works as PDF!)
  - Responsive by default
  - Beautiful typography out of the box
- **Inlined:** No external dependencies, bundle it into base template

### Alpine.js (Lightweight JavaScript Framework)
- **Why:** Tiny, declarative, no build step, works great with Jinja2
- **Size:** ~15KB minified
- **Features:**
  - Reactive data binding
  - Directives in HTML (`x-show`, `x-model`, `x-transition`)
  - No virtual DOM overhead
- **Loading:** CDN for now, can inline later

**Total overhead:** ~28KB (CSS + JS) - less than a single image!

---

## Interactive Features to Implement

### 1. Collapsible Sections
**Use case:** Long reports with many sections - let users collapse what they don't need

```html
<section x-data="{ open: true }">
    <h2 @click="open = !open" style="cursor: pointer">
        <span x-show="!open">▶</span>
        <span x-show="open">▼</span>
        {{ section_name }}
    </h2>
    <div x-show="open" x-transition>
        {{ content }}
    </div>
</section>
```

**Benefits:**
- Save screen space on long reports
- Focus on relevant sections
- Smooth transitions with `x-transition`

---

### 2. Tabbed Multi-System House Views
**Use case:** Charts calculated with multiple house systems (Placidus + Whole Sign + Koch)

**Current approach:** Side-by-side columns - cramped on narrow screens
**New approach:** Tabs - show one system at a time

```html
<div x-data="{ activeSystem: 'Placidus' }">
    <nav>
        <button @click="activeSystem = 'Placidus'"
                :class="{ 'contrast': activeSystem === 'Placidus' }">
            Placidus
        </button>
        <button @click="activeSystem = 'Whole Sign'"
                :class="{ 'contrast': activeSystem === 'Whole Sign' }">
            Whole Sign
        </button>
        <button @click="activeSystem = 'Koch'"
                :class="{ 'contrast': activeSystem === 'Koch' }">
            Koch
        </button>
    </nav>

    <table x-show="activeSystem === 'Placidus'" x-transition>
        <!-- Placidus data -->
    </table>
    <table x-show="activeSystem === 'Whole Sign'" x-transition>
        <!-- Whole Sign data -->
    </table>
    <table x-show="activeSystem === 'Koch'" x-transition>
        <!-- Koch data -->
    </table>
</div>
```

**Benefits:**
- Clean, uncluttered view
- Easy system comparison
- Works great on mobile
- Still shows all systems when printed!

---

### 3. Aspect Filtering by Type
**Use case:** Filter aspects by major/minor/harmonic without regenerating report

```html
<div x-data="{ types: { major: true, minor: true, harmonic: false } }">
    <fieldset>
        <label>
            <input type="checkbox" x-model="types.major">
            Major Aspects
        </label>
        <label>
            <input type="checkbox" x-model="types.minor">
            Minor Aspects
        </label>
        <label>
            <input type="checkbox" x-model="types.harmonic">
            Harmonic Aspects
        </label>
    </fieldset>

    <table>
        {% for aspect in aspects %}
        <tr x-show="types.{{ aspect.category }}" data-category="{{ aspect.category }}">
            <td>{{ aspect.planet1 }}</td>
            <td>{{ aspect.aspect_name }}</td>
            <td>{{ aspect.planet2 }}</td>
            <td>{{ aspect.orb }}</td>
        </tr>
        {% endfor %}
    </table>
</div>
```

**Benefits:**
- Instant filtering (no page reload)
- Explore different aspect subsets
- Reduces visual clutter

---

### 4. Planet Search/Filter
**Use case:** Quickly find specific planets in long position tables

```html
<div x-data="{ search: '' }">
    <input type="search"
           x-model="search"
           placeholder="Search planets...">

    <table>
        {% for planet in planets %}
        <tr x-show="search === '' || '{{ planet.name|lower }}'.includes(search.toLowerCase())">
            <td>{{ planet.glyph }} {{ planet.name }}</td>
            <td>{{ planet.position }}</td>
            <td>{{ planet.house }}</td>
        </tr>
        {% endfor %}
    </table>
</div>
```

**Benefits:**
- Quick navigation in large tables
- No backend search needed
- Instant results

---

### 5. Dark/Light Theme Toggle
**Use case:** User preference for reading environment

```html
<div x-data="{ theme: 'light' }"
     x-init="$watch('theme', val => document.documentElement.setAttribute('data-theme', val))">
    <button @click="theme = (theme === 'light' ? 'dark' : 'light')"
            class="outline">
        <span x-show="theme === 'light'">🌙 Dark Mode</span>
        <span x-show="theme === 'dark'">☀️ Light Mode</span>
    </button>
</div>
```

**Benefits:**
- Eye comfort in different environments
- Pico.css handles theme colors automatically
- Persists across page loads (with localStorage)

---

### 6. Dignity Tooltips/Popovers
**Use case:** Show detailed dignity breakdown on hover without cluttering table

```html
<td x-data="{ showTooltip: false }"
    @mouseenter="showTooltip = true"
    @mouseleave="showTooltip = false"
    style="position: relative">

    +9 <!-- Dignity score -->

    <div x-show="showTooltip"
         x-transition
         class="tooltip">
        <strong>Traditional Dignities:</strong>
        <ul>
            <li>Domicile (Leo) +5</li>
            <li>Exaltation +4</li>
        </ul>
    </div>
</td>
```

**Benefits:**
- Detailed info without table bloat
- Progressive disclosure
- Clean, scannable tables

---

### 7. Expandable Aspect Patterns
**Use case:** Show pattern details on demand

```html
{% for pattern in aspect_patterns %}
<details x-data="{ open: false }" :open="open">
    <summary @click="open = !open">
        {{ pattern.name }} — {{ pattern.planets|join(', ') }}
    </summary>
    <div>
        <p><strong>Element:</strong> {{ pattern.element }}</p>
        <p><strong>Quality:</strong> {{ pattern.quality }}</p>
        <p><strong>Aspects involved:</strong></p>
        <ul>
            {% for aspect in pattern.aspects %}
            <li>{{ aspect }}</li>
            {% endfor %}
        </ul>
    </div>
</details>
{% endfor %}
```

**Benefits:**
- Compact overview, detailed on click
- Native HTML `<details>` element
- No JavaScript required (but can enhance with Alpine)

---

## Template Structure

```
src/stellium/templates/
├── base.html                        # Main layout with Pico + Alpine
├── components/
│   ├── table.html                   # Basic table
│   ├── table_filterable.html        # Table with Alpine filters
│   ├── table_tabbed.html            # Multi-system tabbed view
│   ├── key_value.html               # Key-value pairs
│   ├── text.html                    # Text content
│   ├── collapsible_section.html     # Section with collapse/expand
│   ├── tooltip.html                 # Tooltip component
│   └── chart_svg.html               # SVG embed (maybe with zoom/pan?)
├── sections/
│   ├── chart_overview.html          # Chart overview rendering
│   ├── planet_positions.html        # Planet table with search
│   ├── house_cusps.html             # Tabbed house systems
│   ├── aspects.html                 # Filterable aspects
│   ├── dignities.html               # Dignity table with tooltips
│   └── aspect_patterns.html         # Expandable patterns
└── assets/
    ├── pico.min.css                 # Inlined into base.html (~13KB)
    └── alpine.min.js                # Loaded from CDN or inlined (~15KB)
```

---

## Renderer Architecture

### Same Composable Pattern as Typst!

```python
class Jinja2Renderer:
    """
    Beautiful, interactive HTML renderer using Jinja2 + Pico.css + Alpine.js.

    Features:
    - Collapsible sections
    - Tabbed multi-system views
    - Filterable tables
    - Dark mode toggle
    - Search functionality
    - Tooltips for detailed info
    - Still prints beautifully to PDF!
    """

    def __init__(self, interactive: bool = True, theme: str = "light"):
        """
        Initialize Jinja2 renderer.

        Args:
            interactive: Enable Alpine.js features (default True)
            theme: Default theme ("light" or "dark")
        """
        self.interactive = interactive
        self.theme = theme

        # Setup Jinja2 environment
        self.env = Environment(
            loader=PackageLoader('stellium', 'templates'),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Register custom filters
        self.env.filters['glyph'] = self._format_glyph
        self.env.filters['degree'] = self._format_degree

        # Load CSS once (will be inlined into every HTML file)
        self.pico_css = self._load_pico_css()

    def render_report(
        self,
        sections: list[tuple[str, dict[str, Any]]],
        chart_svg_path: str | None = None,
        title: str | None = None,
    ) -> str:
        """
        Render complete HTML report.

        Args:
            sections: List of (section_name, section_data) tuples
            chart_svg_path: Optional path to chart SVG
            title: Report title

        Returns:
            Complete HTML document as string
        """
        # Load SVG if provided
        chart_svg = None
        if chart_svg_path:
            with open(chart_svg_path, 'r') as f:
                chart_svg = f.read()

        # Render each section using appropriate template
        rendered_sections = []
        for section_name, section_data in sections:
            rendered = self._render_section(section_name, section_data)
            rendered_sections.append(rendered)

        # Render base template
        template = self.env.get_template('base.html')
        return template.render(
            title=title or "Astrological Report",
            pico_css=self.pico_css,
            chart_svg=chart_svg,
            sections=rendered_sections,
            interactive=self.interactive,
            theme=self.theme,
        )

    def _render_section(self, name: str, data: dict[str, Any]) -> str:
        """
        Render a single section using appropriate template.

        Same composable pattern as TypstRenderer!
        """
        section_type = data.get("type")

        if section_type == "table":
            # Check if this is a multi-system table
            if "systems" in data and self.interactive:
                # Use tabbed template
                template = self.env.get_template('components/table_tabbed.html')
            else:
                # Use regular table
                template = self.env.get_template('components/table.html')

        elif section_type == "key_value":
            template = self.env.get_template('components/key_value.html')

        elif section_type == "text":
            template = self.env.get_template('components/text.html')

        else:
            raise ValueError(f"Unknown section type: {section_type}")

        # Wrap in collapsible section if interactive mode
        content = template.render(title=name, **data)

        if self.interactive:
            wrapper = self.env.get_template('components/collapsible_section.html')
            return wrapper.render(title=name, content=content, default_open=True)
        else:
            return content

    def _load_pico_css(self) -> str:
        """Load Pico.css from assets directory."""
        css_path = Path(__file__).parent / 'templates' / 'assets' / 'pico.min.css'
        with open(css_path, 'r') as f:
            return f.read()

    def _format_glyph(self, text: str) -> str:
        """Format text with glyph class."""
        return f'<span class="glyph">{text}</span>'

    def _format_degree(self, value: float) -> str:
        """Format degree value."""
        deg = int(value)
        min = int((value % 1) * 60)
        return f"{deg}°{min:02d}'"
```

---

## Base Template Example

```html
<!DOCTYPE html>
<html lang="en" data-theme="{{ theme }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ title }}</title>

    <!-- Pico.css (inlined for no external dependencies) -->
    <style>
        {{ pico_css }}
    </style>

    <!-- Custom CSS for astrology aesthetics -->
    <style>
        :root {
            --primary: #4a5568;           /* Cosmic blue-grey */
            --primary-hover: #2d3748;
            --primary-focus: rgba(74, 85, 104, 0.125);
        }

        /* Glyphs look better slightly larger */
        .glyph {
            font-size: 1.2em;
            font-family: "Noto Sans Symbols 2", sans-serif;
        }

        /* Tooltip styles */
        .tooltip {
            position: absolute;
            z-index: 10;
            background: var(--card-background-color);
            border: 1px solid var(--muted-border-color);
            padding: 0.5rem;
            border-radius: 0.25rem;
            box-shadow: var(--card-box-shadow);
            max-width: 20rem;
        }

        /* Print styles */
        @media print {
            /* Show all collapsed sections when printing */
            [x-show] {
                display: block !important;
            }

            /* Hide interactive controls */
            button, input[type="search"], input[type="checkbox"] {
                display: none !important;
            }

            /* Ensure tabs show all content */
            [x-show] {
                display: block !important;
            }
        }
    </style>

    {% if interactive %}
    <!-- Alpine.js for interactivity -->
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    {% endif %}
</head>
<body>
    <main class="container">
        {% if interactive %}
        <!-- Theme toggle -->
        <div x-data="{ theme: '{{ theme }}' }"
             x-init="$watch('theme', val => document.documentElement.setAttribute('data-theme', val))"
             style="text-align: right; margin-bottom: 1rem;">
            <button @click="theme = (theme === 'light' ? 'dark' : 'light')"
                    class="outline secondary"
                    role="button">
                <span x-show="theme === 'light'">🌙 Dark</span>
                <span x-show="theme === 'dark'">☀️ Light</span>
            </button>
        </div>
        {% endif %}

        <header>
            <h1>{{ title }}</h1>
        </header>

        {% if chart_svg %}
        <figure>
            {{ chart_svg | safe }}
        </figure>
        {% endif %}

        <!-- Rendered sections -->
        {% for section in sections %}
            {{ section | safe }}
        {% endfor %}

        <footer style="margin-top: 3rem; text-align: center; color: var(--muted-color);">
            <small>
                Generated with <a href="https://github.com/yourusername/stellium">Stellium</a>
                — Computational Astrology with Python
            </small>
        </footer>
    </main>
</body>
</html>
```

---

## Implementation Phases

### Phase 1: Foundation
- [ ] Add Jinja2 dependency to `pyproject.toml`
- [ ] Create `src/stellium/templates/` directory structure
- [ ] Download and inline Pico.css into `assets/pico.min.css`
- [ ] Create `base.html` template
- [ ] Create basic component templates (table, key_value, text)

### Phase 2: Basic Renderer
- [ ] Implement `Jinja2Renderer` class in `renderers.py`
- [ ] Wire up template loading and rendering
- [ ] Test with simple reports (no interactivity yet)
- [ ] Ensure print-to-PDF works beautifully

### Phase 3: Interactive Features (Alpine.js)
- [ ] Add Alpine.js to base template (CDN)
- [ ] Implement collapsible sections
- [ ] Implement dark/light theme toggle
- [ ] Test interactivity + print compatibility

### Phase 4: Advanced Components
- [ ] Tabbed multi-system house view
- [ ] Filterable aspect tables (major/minor/harmonic)
- [ ] Planet search/filter
- [ ] Dignity tooltips

### Phase 5: Polish & Documentation
- [ ] Add custom CSS for astrology aesthetics
- [ ] Optimize print styles
- [ ] Write usage docs
- [ ] Create examples
- [ ] Add tests

---

## Future Enhancements

### SVG Chart Interactivity
- Zoom/pan controls with Alpine.js or simple JS
- Highlight planet when hovering table row
- Click planet in chart to jump to details

### Advanced Filtering
- Combine filters (e.g., "Major aspects to Sun")
- Save filter presets

### Export Options
- "Copy to clipboard" buttons for tables
- Download individual tables as CSV
- Print-optimized view (hide controls)

### Accessibility
- ARIA labels for interactive elements
- Keyboard navigation for tabs
- Screen reader friendly

### Progressive Enhancement
- Works without JavaScript (static HTML)
- Enhanced with Alpine.js when available
- Degrades gracefully

---

## Benefits Summary

✨ **For Users:**
- Beautiful, modern reports that look great on any screen
- Interactive exploration without regenerating charts
- Dark mode for comfortable reading
- Prints perfectly to PDF
- Works on mobile, tablet, desktop

✨ **For Developers:**
- Same composable pattern as Typst renderer
- Clean separation of logic and presentation
- Easy to add new features
- Minimal dependencies (~28KB CSS + JS)
- No build step required

✨ **For the Project:**
- Differentiates from other astrology libraries
- Showcases modern web capabilities
- Still maintains PDF workflow (Typst)
- Opens door to future web app possibilities

---

## References

- [Pico.css Documentation](https://picocss.com/)
- [Alpine.js Documentation](https://alpinejs.dev/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)

---

**Next Steps:** Pick up in next session and start with Phase 1! 🎉

*Written during session November 26, 2025 with excitement and vision for the future!*
