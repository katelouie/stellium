"""
Stellium Web - Configuration & Theming

Color palette and styling constants matching the PDF report output.
"""

# =============================================================================
# COLOR PALETTE (from Typst PDF template)
# =============================================================================

COLORS = {
    # Core purple family
    "primary": "#4a3353",  # Deep warm purple - headers, primary buttons
    "secondary": "#6b4d6e",  # Medium purple - table headers, accents
    "accent": "#8e6b8a",  # Light mauve - hover states, borders
    # Highlight
    "gold": "#b8953d",  # Antique gold - links, stars, interactive
    # Backgrounds
    "cream": "#faf8f5",  # Main background
    "cream_dark": "#f3efe9",  # Alt section background
    # Text
    "text": "#2d2330",  # Primary text (warm near-black)
    "text_muted": "#5a4d5e",  # Secondary text (muted purple-gray)
    # Utility
    "border": "#d4cdc4",  # Subtle borders
    "white": "#ffffff",
}

# =============================================================================
# TYPOGRAPHY
# =============================================================================

# Toggle this to switch between Cinzel and Cinzel Decorative for display font
USE_DECORATIVE_FONT = True  # Set to False for regular Cinzel

FONTS = {
    "display": "Cinzel Decorative" if USE_DECORATIVE_FONT else "Cinzel",
    "body": "Crimson Pro",  # Body text, form labels
    "mono": "JetBrains Mono",  # Code blocks
}

# Google Fonts URL - includes both Cinzel variants so switching is instant
GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Cinzel:wght@400;500;600;700&"
    "family=Cinzel+Decorative:wght@400;700&"
    "family=Crimson+Pro:ital,wght@0,400;0,500;0,600;1,400&"
    "family=JetBrains+Mono:wght@400;500&"
    "display=swap"
)

# =============================================================================
# HOUSE SYSTEMS (all 18 available in Stellium)
# =============================================================================

HOUSE_SYSTEMS = [
    # Most popular
    ("Placidus", "PlacidusHouses"),
    ("Whole Sign", "WholeSignHouses"),
    ("Koch", "KochHouses"),
    ("Equal", "EqualHouses"),
    # Traditional
    ("Porphyry", "PorphyryHouses"),
    ("Regiomontanus", "RegiomontanusHouses"),
    ("Campanus", "CampanusHouses"),
    ("Alcabitius", "AlcabitiusHouses"),
    # Modern
    ("Topocentric", "TopocentricHouses"),
    ("Morinus", "MorinusHouses"),
    ("Krusinski", "KrusinskiHouses"),
    # Equal variants
    ("Equal (MC)", "EqualMCHouses"),
    ("Vehlow Equal", "VehlowEqualHouses"),
    ("Equal (Vertex)", "EqualVertexHouses"),
    # Specialized
    ("Gauquelin", "GauquelinHouses"),
    ("Horizontal", "HorizontalHouses"),
    ("Axial Rotation", "AxialRotationHouses"),
    ("APC", "APCHouses"),
]

# =============================================================================
# AYANAMSA SYSTEMS (all 9 available in Stellium)
# =============================================================================

AYANAMSAS = [
    # Vedic tradition
    ("Lahiri", "lahiri"),
    ("Raman", "raman"),
    ("Krishnamurti", "krishnamurti"),
    ("Yukteshwar", "yukteshwar"),
    ("J.N. Bhasin", "jn_bhasin"),
    ("True Chitrapaksha", "true_citra"),
    ("True Revati", "true_revati"),
    # Western sidereal
    ("Fagan-Bradley", "fagan_bradley"),
    ("De Luce", "deluce"),
]

# =============================================================================
# THEMES (all 13 available in Stellium)
# =============================================================================

CHART_THEMES = [
    # Classic themes
    "classic",
    "dark",
    "midnight",
    "celestial",
    "sepia",
    "pastel",
    "neon",
    # Data science themes
    "viridis",
    "plasma",
    "inferno",
    "magma",
    "cividis",
    "turbo",
]

# =============================================================================
# ZODIAC PALETTES (all available in Stellium)
# =============================================================================

ZODIAC_PALETTES = [
    # Base palettes
    "grey",
    "rainbow",
    "elemental",
    "cardinality",
    # Theme-coordinated rainbow variants
    "rainbow_dark",
    "rainbow_midnight",
    "rainbow_celestial",
    "rainbow_neon",
    "rainbow_sepia",
    # Theme-coordinated elemental variants
    "elemental_dark",
    "elemental_midnight",
    "elemental_neon",
    "elemental_sepia",
    # Data science palettes
    "viridis",
    "plasma",
    "inferno",
    "magma",
    "cividis",
    "turbo",
    "coolwarm",
    "spectral",
]

# =============================================================================
# ASPECT MODES
# =============================================================================

ASPECT_MODES = [
    ("Major (Ptolemaic)", "major"),
    ("All Aspects", "all"),
    ("Minor Only", "minor"),
    ("Harmonic", "harmonic"),
]

# =============================================================================
# MOON PHASE POSITIONS
# =============================================================================

MOON_PHASE_POSITIONS = [
    ("Bottom Right", "bottom-right"),
    ("Bottom Left", "bottom-left"),
    ("Top Right", "top-right"),
    ("Top Left", "top-left"),
    ("Center", "center"),
]

# =============================================================================
# TABLE POSITIONS
# =============================================================================

TABLE_POSITIONS = [
    ("Right", "right"),
    ("Left", "left"),
    ("Below", "below"),
]

# =============================================================================
# ASPECT PALETTES (for aspect line colors)
# =============================================================================

ASPECT_PALETTES = [
    # Theme-based
    "classic",
    "dark",
    "midnight",
    "neon",
    "sepia",
    "pastel",
    "celestial",
    # Monochromatic
    "greyscale",
    "blues",
    "purples",
    "earth_tones",
    # Data science
    "viridis",
    "plasma",
    "inferno",
    "magma",
    "cividis",
    "turbo",
]

# =============================================================================
# PLANET GLYPH PALETTES (for planet symbol colors)
# =============================================================================

PLANET_GLYPH_PALETTES = [
    ("Default (Theme)", "default"),
    ("By Element", "element"),
    ("By Rulership", "sign_ruler"),
    ("By Planet Type", "planet_type"),
    ("Luminaries Accent", "luminaries"),
    ("Rainbow", "rainbow"),
    ("Chakra", "chakra"),
    # Data science
    ("Viridis", "viridis"),
    ("Plasma", "plasma"),
    ("Inferno", "inferno"),
    ("Turbo", "turbo"),
]

# =============================================================================
# TIMING CHART TYPES
# =============================================================================

TIMING_CHART_TYPES = [
    ("transits", "Transits", "Current sky positions compared to natal"),
    ("progressions", "Secondary Progressions", "1 day = 1 year symbolic progression"),
    ("solar_return", "Solar Return", "Annual chart when Sun returns to natal position"),
    (
        "lunar_return",
        "Lunar Return",
        "Monthly chart when Moon returns to natal position",
    ),
    (
        "planetary_return",
        "Planetary Return",
        "Chart when a planet returns to natal position",
    ),
]

# =============================================================================
# RETURN PLANETS (for planetary returns)
# =============================================================================

RETURN_PLANETS = [
    ("Saturn", "Saturn Return (~29 years)"),
    ("Jupiter", "Jupiter Return (~12 years)"),
    ("Mars", "Mars Return (~2 years)"),
    ("Venus", "Venus Return (~1 year)"),
    ("Mercury", "Mercury Return (~1 year)"),
]
