# 🌟 Stellium Development Roadmap

## Feature Implementation Recommendations

Based on analysis of the current codebase and technical astrology requirements, this document outlines recommended next features for the Stellium astrological calculation engine.

---

## ✅ **RECENTLY COMPLETED FEATURES**

### Arabic Parts Calculator ✅ 
**Status**: **COMPLETED** | **Complexity**: Medium | **Value**: High

- ✅ Implemented 15+ traditional Arabic Parts including Part of Fortune and Spirit
- ✅ Proper day/night sect handling with automatic formula switching
- ✅ Integration with existing chart object structure
- ✅ Added to main Chart class as `chart.arabic_parts` property

### Expanded House Systems ✅
**Status**: **COMPLETED** | **Complexity**: Low | **Value**: High

- ✅ Implemented support for 23+ house systems from Swiss Ephemeris
- ✅ Added comprehensive house system catalog with proper error handling
- ✅ Supports all major systems: Placidus, Koch, Whole Sign, Equal, Porphyry, etc.

---

## 🎯 **HIGH PRIORITY - Core Analysis Features**

### 1. **Aspect Pattern Detection**
**Status**: Not Implemented | **Complexity**: Medium | **Value**: Very High

Detect major aspect configurations that provide key insights into chart dynamics.

#### Patterns to Implement:
- **Grand Trine**: 3 planets in trine (120°) forming triangle
- **T-Square**: 2 planets in opposition with 3rd planet squaring both
- **Grand Cross**: 4 planets forming 2 oppositions with squares between
- **Yod (Finger of God)**: 2 planets in sextile with 3rd planet quincunx to both
- **Stellium**: 3+ planets within tight orb (8-10°)
- **Kite**: Grand trine with 4th planet opposing one corner
- **Mystic Rectangle**: 2 oppositions with sextiles and trines
- **Grand Sextile**: 6 planets forming hexagon with sextiles

#### Implementation Approach:
```python
# Add to chart.py
def get_aspect_patterns(self) -> dict:
    """Detect major aspect patterns in the chart."""
    patterns = {
        'grand_trines': [],
        't_squares': [],
        'grand_crosses': [],
        'yods': [],
        'stelliums': [],
        'kites': [],
        'mystic_rectangles': [],
        'grand_sextiles': []
    }
    
    # Use existing aspect calculation system
    aspects = self.get_all_aspects()
    
    # Pattern detection algorithms here
    return patterns
```

#### Files to Modify:
- `src/stellium/chart.py` - Add pattern detection methods
- `src/stellium/presentation.py` - Add pattern display formatting
- `tests/` - Add comprehensive pattern detection tests

---

### 2. **Element & Modality Balance Analysis**
**Status**: TODO in README | **Complexity**: Easy | **Value**: High

Analyze planetary distribution across astrological elements and modalities.

#### Features:
- **Element Balance**: Fire, Earth, Air, Water distribution
- **Modality Balance**: Cardinal, Fixed, Mutable emphasis
- **Hemispheric Analysis**: Above/below horizon, East/West emphasis
- **Temperament Analysis**: Choleric, Sanguine, Melancholic, Phlegmatic
- **Planetary Weight Scoring**: Consider planetary strength in calculations

#### Implementation Approach:
```python
# Add to chart.py
def get_element_balance(self) -> dict:
    """Calculate elemental balance with planetary weights."""
    elements = {'Fire': 0, 'Earth': 0, 'Air': 0, 'Water': 0}
    
    for planet in self.planets:
        # Get planetary weight (luminaries = 2, personal = 1.5, etc.)
        weight = self._get_planetary_weight(planet)
        element = self._get_sign_element(planet.sign)
        elements[element] += weight
    
    return elements

def get_hemispheric_emphasis(self) -> dict:
    """Analyze distribution above/below horizon and east/west."""
    # Use ASC/DSC and MC/IC to determine hemispheres
    pass
```

#### Files to Create/Modify:
- `src/stellium/analysis.py` - New module for chart analysis
- `src/stellium/chart.py` - Add balance calculation methods
- `src/stellium/presentation.py` - Add balance visualization

---

### 3. **Enhanced Retrograde Analysis**
**Status**: Partially Implemented | **Complexity**: Medium | **Value**: High

Complete retrograde detection and add advanced retrograde analysis.

#### Current State:
- Basic retrograde detection exists in `objects.py`
- Display needs improvement in presentation layer

#### Features to Add:
- **Retrograde Stations**: Calculate exact station dates
- **Shadow Periods**: Pre/post shadow calculations
- **Cazimi Detection**: Exact Sun conjunction (< 17' orb)
- **Combust Detection**: Close Sun proximity (< 8.5°)
- **Under the Beams**: Moderate Sun proximity (8.5° - 15°)

#### Implementation Approach:
```python
# Enhance objects.py
class Planet(Object):
    def get_solar_condition(self, sun_position: float) -> str:
        """Determine planet's condition relative to Sun."""
        distance = abs(self.long - sun_position)
        if distance > 180:
            distance = 360 - distance
            
        if distance < 0.28:  # 17 arcminutes
            return "cazimi"
        elif distance < 8.5:
            return "combust"
        elif distance < 15:
            return "under_beams"
        return "free"
```

#### Files to Modify:
- `src/stellium/objects.py` - Enhance retrograde/solar methods
- `src/stellium/chart.py` - Add retrograde analysis
- `src/stellium/presentation.py` - Improve retrograde display

---

### 4. **Moon Phase Calculator**
**Status**: TODO in README | **Complexity**: Easy-Medium | **Value**: High

Complete lunar phase analysis using existing phase foundation.

#### Current State:
- Basic phase calculation exists in `Planet._get_phase()`
- Needs expansion and proper integration

#### Features:
- **Phase Type**: New, Waxing Crescent, First Quarter, etc.
- **Illumination Percentage**: Exact illumination fraction
- **Lunation Cycle**: Days since New Moon
- **Void of Course Detection**: Moon's last aspect before sign change
- **Moon Mansions**: 28 lunar mansions (Nakshatras)

#### Implementation Approach:
```python
# Add to chart.py or new lunar.py module
def get_moon_phase_info(self) -> dict:
    """Complete moon phase analysis."""
    moon = self.objects_dict["Moon"]
    sun = self.objects_dict["Sun"]
    
    # Calculate Sun-Moon angle
    phase_angle = (moon.long - sun.long) % 360
    
    phase_names = {
        (0, 45): "New Moon",
        (45, 90): "Waxing Crescent",
        (90, 135): "First Quarter",
        (135, 180): "Waxing Gibbous",
        (180, 225): "Full Moon",
        (225, 270): "Waning Gibbous",
        (270, 315): "Last Quarter",
        (315, 360): "Waning Crescent"
    }
    
    return {
        'phase_name': self._get_phase_name(phase_angle),
        'illumination': moon.phase_frac,
        'phase_angle': phase_angle,
        'void_of_course': self._is_void_of_course()
    }
```

---

## 🚀 **MEDIUM PRIORITY - Advanced Technical Features**

### 5. **Dispositor Chain Analysis**
**Status**: TODO in README | **Complexity**: Medium-High | **Value**: High

Analyze planetary rulership chains and mutual reception patterns.

#### Features:
- **Dispositor Trees**: Map complete rulership chains
- **Final Dispositor**: Identify chart's ultimate ruler
- **Mutual Reception**: Planets in each other's signs
- **Dispositorship Strength**: Weight based on dignity scores

#### Implementation Approach:
```python
# Add to chart.py
def get_dispositor_chains(self) -> dict:
    """Calculate complete dispositor analysis."""
    from stellium.signs import DIGNITIES
    
    dispositors = {}
    for planet in self.planets:
        ruler = DIGNITIES[planet.sign]["traditional"]["ruler"]
        dispositors[planet.name] = ruler
    
    # Find chains and final dispositors
    chains = self._trace_dispositor_chains(dispositors)
    mutual_receptions = self._find_mutual_receptions(dispositors)
    
    return {
        'chains': chains,
        'final_dispositors': self._find_final_dispositors(chains),
        'mutual_receptions': mutual_receptions
    }
```

---

### 6. **Arabic Parts/Lots Calculator**
**Status**: Foundation Exists | **Complexity**: Medium | **Value**: Medium-High

Expand the existing `calc_arabic_part()` method into a comprehensive system.

#### Current State:
- Basic Part of Fortune calculation exists
- Needs expansion to full lot system

#### Parts to Implement:
- **Part of Fortune**: ☽ + ASC - ☉ (day) / ☉ + ASC - ☽ (night)
- **Part of Spirit**: ☉ + ASC - ☽ (day) / ☽ + ASC - ☉ (night)
- **Part of Love**: ♀ + ASC - ☉
- **Part of Career**: ♂ + ASC - ☽
- **Part of Marriage**: ♀ + DSC - ♃
- **Part of Death**: 8th cusp + ♄ - ☽
- **Hermetic Lots**: 97 traditional Arabic Parts

#### Implementation Approach:
```python
# Expand chart.py
ARABIC_PARTS = {
    'fortune': {
        'day': lambda c: (c.objects_dict["Moon"].long + c.objects_dict["ASC"].long - c.objects_dict["Sun"].long) % 360,
        'night': lambda c: (c.objects_dict["Sun"].long + c.objects_dict["ASC"].long - c.objects_dict["Moon"].long) % 360
    },
    'spirit': {
        'day': lambda c: (c.objects_dict["Sun"].long + c.objects_dict["ASC"].long - c.objects_dict["Moon"].long) % 360,
        'night': lambda c: (c.objects_dict["Moon"].long + c.objects_dict["ASC"].long - c.objects_dict["Sun"].long) % 360
    }
    # ... more parts
}

def calculate_all_arabic_parts(self) -> dict:
    """Calculate all configured Arabic Parts."""
    sect = self.get_sect().lower()
    parts = {}
    
    for part_name, formulas in ARABIC_PARTS.items():
        if sect in formulas:
            parts[part_name] = formulas[sect](self)
        else:
            # Use day formula as default
            parts[part_name] = formulas['day'](self)
    
    return parts
```

---

### 7. **Advanced House Analysis**
**Status**: Basic Implementation | **Complexity**: Medium | **Value**: High

Enhance house system analysis beyond current basic implementation.

#### Features:
- **House Rulers**: Identify ruling planets of each house
- **House Ruler Positions**: Analyze where house rulers are placed
- **Planetary Joy**: Classical planetary house joy positions
- **Intercepted Signs**: Signs contained within houses
- **House Emphasis**: Planetary distribution analysis
- **Multiple House Systems**: Side-by-side comparison

#### Implementation Approach:
```python
# Add to chart.py
def get_house_analysis(self) -> dict:
    """Comprehensive house system analysis."""
    from stellium.signs import DIGNITIES
    
    house_rulers = {}
    for i, cusp_degree in enumerate(self.cusps):
        cusp_sign = self._get_sign_from_degree(cusp_degree)
        ruler = DIGNITIES[cusp_sign]["traditional"]["ruler"]
        house_rulers[i + 1] = {
            'sign': cusp_sign,
            'ruler': ruler,
            'ruler_house': self._find_planet_house(ruler),
            'ruler_sign': self._find_planet_sign(ruler)
        }
    
    return {
        'house_rulers': house_rulers,
        'planetary_joys': self._check_planetary_joys(),
        'house_emphasis': self._calculate_house_emphasis(),
        'intercepted_signs': self._find_intercepted_signs()
    }
```

---

### 8. **Professional Chart Drawing**
**Status**: Broken Implementation | **Complexity**: High | **Value**: Critical

Complete rewrite of the chart drawing system for professional output.

#### Current Issues:
- `drawing.py` notes "NOTHING in this file works properly"
- Basic SVG structure exists but needs major fixes

#### Features Needed:
- **Proper Chart Wheel**: 12 houses with correct proportions
- **Planet Placement**: Accurate positioning with collision detection
- **Aspect Lines**: Configurable aspect line drawing
- **House System Support**: Both Placidus and Whole Sign
- **Customizable Styling**: Colors, fonts, symbols
- **Multiple Output Formats**: SVG, PNG, PDF
- **Responsive Sizing**: Various chart sizes

#### Implementation Strategy:
```python
# Rewrite drawing.py with proper architecture
class ChartDrawer:
    def __init__(self, chart: Chart, style_config: dict = None):
        self.chart = chart
        self.style = style_config or DEFAULT_STYLE
        
    def draw_wheel(self) -> svgwrite.Drawing:
        """Draw complete chart wheel."""
        # 1. Draw house divisions
        # 2. Draw zodiac ring
        # 3. Place planets with collision detection
        # 4. Draw aspect lines
        # 5. Add labels and decorations
        
    def _calculate_planet_positions(self) -> dict:
        """Smart planet placement avoiding overlaps."""
        
    def _draw_aspect_lines(self, dwg: svgwrite.Drawing):
        """Draw aspect lines with proper styling."""
```

#### Recommended Libraries:
- **svgwrite**: Primary SVG generation (already imported)
- **cairo** or **skia-python**: For high-quality rasterization
- **reportlab**: For PDF output
- **matplotlib**: Alternative for scientific-style charts

---

## ⭐ **ADVANCED FEATURES - Specialized Techniques**

### 9. **Heliacal Rising/Setting Calculator**
**Complexity**: Very High | **Value**: Specialized

Ancient astronomical visibility calculations for stars and planets.

#### Features:
- **Heliacal Rising**: First visibility after conjunction with Sun
- **Heliacal Setting**: Last visibility before conjunction with Sun
- **Star Phases**: Rising, culmination, setting times
- **Synodic Cycles**: Planet visibility cycles

### 10. **Harmonic Charts**
**Complexity**: High | **Value**: Specialized

Generate harmonic divisional charts for advanced analysis.

#### Common Harmonics:
- **4th Harmonic**: Stress and tension patterns
- **5th Harmonic**: Creative and artistic talents
- **7th Harmonic**: Spiritual and inspirational themes
- **9th Harmonic**: Completion and fulfillment

### 11. **Solar Arc Directions**
**Complexity**: High | **Value**: Predictive

Predictive technique using solar arc progressions.

#### Features:
- **Solar Arc Positions**: Future planetary positions
- **Solar Arc Aspects**: Progressed aspects to natal
- **Configurable Arc Rates**: Various progression methods

### 12. **Fixed Stars Integration**
**Complexity**: Very High | **Value**: Traditional

Integration with major fixed star positions and influences.

#### Stars to Include:
- **Royal Stars**: Aldebaran, Regulus, Antares, Fomalhaut
- **Major Stars**: Sirius, Vega, Spica, Algol, etc.
- **Star Aspects**: Conjunctions within tight orbs (1-2°)
- **Parans**: Rising/setting simultaneously

---

## 🛠 **INFRASTRUCTURE & UX IMPROVEMENTS**

### 13. **Chart Comparison Tools**
Synastry, composite, and relationship chart analysis.

### 14. **Export & Reporting System**
Professional report generation in multiple formats.

### 15. **Configuration Management**
User preferences for orbs, aspects, house systems, etc.

### 16. **Performance Optimizations**
Caching expansion, parallel processing, memory optimization.

---

## 📊 **RECOMMENDED IMPLEMENTATION ORDER**

### Phase 1: Core Analysis (Immediate - 2-4 weeks)
1. **Element & Modality Balance** - Quick win, high value
2. **Enhanced Retrograde Analysis** - Complete existing feature
3. **Aspect Pattern Detection** - Build on solid aspect foundation
4. **Moon Phase Calculator** - Standalone valuable feature

### Phase 2: Advanced Analysis (1-2 months)
5. **Dispositor Chain Analysis** - Complex but high-value
6. **Arabic Parts Expansion** - Build on existing foundation
7. **Advanced House Analysis** - Enhance current house system

### Phase 3: Visualization (2-3 months)
8. **Professional Chart Drawing** - Critical rewrite needed
9. **Export & Reporting System** - User experience focus

### Phase 4: Specialized Features (3-6 months)
10. **Chart Comparison Tools** - Relationship analysis
11. **Harmonic Charts** - Advanced techniques
12. **Fixed Stars Integration** - Traditional techniques

---

## 🏗 **Architecture Recommendations**

### New Module Structure:
```
src/stellium/
├── analysis/           # New analysis modules
│   ├── __init__.py
│   ├── patterns.py     # Aspect pattern detection
│   ├── balance.py      # Element/modality analysis
│   ├── dispositors.py  # Dispositor chain analysis
│   └── arabic_parts.py # Arabic parts calculator
├── drawing/            # Enhanced drawing system
│   ├── __init__.py
│   ├── wheel.py        # Chart wheel drawing
│   ├── styling.py      # Style configuration
│   └── export.py       # Export utilities
└── traditional/        # Traditional techniques
    ├── __init__.py
    ├── fixed_stars.py  # Fixed star calculations
    └── heliacal.py     # Heliacal calculations
```

### Configuration System:
```python
# config.py
DEFAULT_CONFIG = {
    'orbs': {
        'conjunction': 8,
        'opposition': 8,
        'trine': 8,
        'square': 8,
        'sextile': 6,
        'quincunx': 3
    },
    'aspects': ['conjunction', 'opposition', 'trine', 'square', 'sextile'],
    'house_system': 'Placidus',
    'ayanamsa': 'Lahiri',  # For future sidereal support
    'dignity_system': 'traditional'
}
```

---

## 🧪 **Testing Strategy**

### Test Categories:
1. **Unit Tests**: Individual calculation methods
2. **Integration Tests**: Complete chart analysis workflows
3. **Accuracy Tests**: Compare with established astrological software
4. **Performance Tests**: Large dataset processing
5. **Visual Tests**: Chart drawing output validation

### Test Data:
- **Historical Charts**: Well-documented birth data
- **Edge Cases**: Polar locations, unusual configurations
- **Validation Charts**: Cross-reference with professional software

---

This roadmap provides a structured approach to expanding Stellium into a comprehensive professional astrological calculation engine while maintaining code quality and architectural integrity.