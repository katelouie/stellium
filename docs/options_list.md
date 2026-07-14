# Stellium Options Reference

This document provides a comprehensive reference of all implemented options in Stellium. Whether you're looking for a specific house system, sidereal zodiac, fixed star, Arabic lot, or aspect type, you'll find it here.

**Summary:** Stellium supports **{{ n_objects }} celestial objects**, **{{ n_house_systems }} house systems**, **{{ n_ayanamsas }} ayanamsas**, **{{ n_fixed_stars }} fixed stars**, **{{ n_arabic_parts }} Arabic parts**, and **{{ n_aspects }} aspect types**.

---

## Celestial Objects (37 objects)

All celestial bodies and points available for chart calculation.

### Traditional Planets (The Septenary) - 7 objects

| Name | Glyph | Aliases | Description |
|------|-------|---------|-------------|
| Sun | ☉ | Sol | Life force, vitality, ego, conscious will |
| Moon | ☽ | Luna | Emotions, instincts, habits, subconscious |
| Mercury | ☿ | | Communication, intellect, learning, exchange |
| Venus | ♀ | | Love, beauty, harmony, values, relationships |
| Mars | ♂ | | Action, desire, courage, assertion, conflict |
| Jupiter | ♃ | | Expansion, growth, wisdom, fortune, philosophy |
| Saturn | ♄ | | Structure, discipline, boundaries, responsibility, time |

### Modern Planets (Outer Planets) - 3 objects

| Name | Glyph | Description |
|------|-------|-------------|
| Uranus | ♅ | Revolution, innovation, awakening, sudden change |
| Neptune | ♆ | Dreams, illusion, spirituality, dissolution |
| Pluto | ♇ | Transformation, power, death/rebirth, underworld |

### Lunar Nodes - 3 objects

| Name | Glyph | Aliases | Description |
|------|-------|---------|-------------|
| True Node | ☊ | North Node, Dragon's Head, Rahu | True lunar north node - karmic direction and soul growth |
| Mean Node | ☊ | Mean North Node | Averaged position of the lunar north node |
| South Node | ☋ | Dragon's Tail, Ketu | Opposite of North Node - past patterns and karmic release |

### Calculated Points - 3 objects

| Name | Glyph | Aliases | Description |
|------|-------|---------|-------------|
| Mean Apogee | ⚸ | Black Moon Lilith, BML | Mean lunar apogee - wild feminine, shadow work |
| True Apogee | ⚸ | True Lilith | True lunar apogee - instantaneous farthest point |
| Vertex | 🜊 | Electric Ascendant | Fated encounters and destined events |

### Main Belt Asteroids (The "Big Five") - 5 objects

| Name | Glyph | Description |
|------|-------|-------------|
| Ceres | ⚳ | Nurturing, motherhood, agriculture, sustenance |
| Pallas | ⚴ | Wisdom, creative intelligence, strategic thinking |
| Juno | ⚵ | Partnership, marriage, commitment, power dynamics |
| Vesta | ⚶ | Sacred flame, devotion, focus, sexual integrity |
| Hygiea | ⚕ | Health, hygiene, preventive medicine |

### Centaurs - 4 objects

| Name | Glyph | Description |
|------|-------|-------------|
| Chiron | ⚷ | The wounded healer - deep wounds, healing journey, mentorship |
| Pholus | ⬰ | Small cause, big effect - multigenerational patterns |
| Nessus | Nes | Abuse, boundaries violated, karmic consequences |
| Chariklo | Cha | Chiron's wife - compassionate healing, grounding wisdom |

### Trans-Neptunian Objects (TNOs) - 6 objects

| Name | Glyph | Category | Description |
|------|-------|----------|-------------|
| Eris | ⯰ | Dwarf Planet | Discord, rivalry, fierce feminine power |
| Sedna | Sed | TNO | Deep cold, isolation, victim consciousness |
| Makemake | 🝼 | Dwarf Planet | Environmental awareness, resourcefulness |
| Haumea | 🝻 | Dwarf Planet | Rebirth, fertility, connection to nature |
| Orcus | Orc | TNO | Anti-Pluto - oaths, consequences, afterlife |
| Quaoar | Qua | TNO | Creation myths, harmony, order from chaos |

### Uranian / Hamburg School Planets - 8 objects

Hypothetical points used in Uranian astrology.

| Name | Glyph | Description |
|------|-------|-------------|
| Cupido | Cup | Family, groups, art, community |
| Hades | Had | Decay, the past, poverty, what's hidden |
| Zeus | Zeu | Leadership, fire, machines, directed energy |
| Kronos | Kro | Authority, expertise, high position |
| Apollon | Apo | Expansion, science, commerce, success |
| Admetos | Adm | Depth, stagnation, raw materials, earth |
| Vulkanus | Vul | Immense power, force, intensity |
| Poseidon | Pos | Spirituality, enlightenment, clarity |

### Example: Selecting Celestial Objects

```python
from stellium import ChartBuilder
from stellium.core.native import Native
from datetime import datetime

native = Native(datetime(1994, 1, 6, 11, 47), "Palo Alto, CA")

# Default: Traditional + Modern planets, Nodes, Chiron
chart = ChartBuilder.from_native(native).calculate()

# Access any object
sun = chart.get_object("Sun")
chiron = chart.get_object("Chiron")
lilith = chart.get_object("Mean Apogee")  # or "Black Moon Lilith"
```
---

## House Systems (18 systems)

Stellium implements all major house systems via the Swiss Ephemeris. You can use multiple house systems simultaneously.

### Popular Systems

| Name | Code | Description |
|------|------|-------------|
| Placidus | P | Most popular modern system. Time-based division of diurnal arc. |
| Whole Sign | W | Ancient system where each house equals one zodiac sign. |
| Koch | K | Popular refinement based on birthplace latitude. |
| Equal | A | Each house is exactly 30° starting from the Ascendant. |

### Traditional Systems

| Name | Code | Description |
|------|------|-------------|
| Porphyry | O | Ancient quadrant system dividing each quarter into thirds. |
| Regiomontanus | R | Renaissance system based on celestial equator divisions. |
| Campanus | C | Medieval system using prime vertical divisions. |
| Alcabitius | B | Ancient Hellenistic semi-arc system. |

### Modern Systems

| Name | Code | Description |
|------|------|-------------|
| Topocentric | T | Modern system emphasizing local horizon. |
| Morinus | M | Equator-based system ignoring the ecliptic. |
| Krusinski | U | Alternative mathematical division system. |

### Equal House Variants

| Name | Code | Description |
|------|------|-------------|
| Equal (MC) | D | Equal 30° houses centered on MC instead of ASC. |
| Vehlow Equal | V | Equal houses with ASC at middle of 1st house. |
| Equal (Vertex) | E | Equal houses calculated from the Vertex point. |

### Specialized Systems

| Name | Code | Description |
|------|------|-------------|
| Horizontal | H | Based on horizontal coordinate system. |
| Axial Rotation | X | Based on Earth's axial rotation. |
| APC | Y | Ascendant-Precedent-Consequent houses. |

### Example: Using House Systems

```python
from stellium import ChartBuilder
from stellium.core.native import Native
from stellium.engines.houses import PlacidusHouses, WholeSignHouses, KochHouses
from datetime import datetime

native = Native(datetime(1994, 1, 6, 11, 47), "Palo Alto, CA")

# Single house system
chart = ChartBuilder.from_native(native).with_house_systems([PlacidusHouses()]).calculate()

# Multiple house systems for comparison
chart = (ChartBuilder.from_native(native)
    .with_house_systems([PlacidusHouses(), WholeSignHouses(), KochHouses()])
    .calculate())

# Access house cusps
placidus_cusps = chart.get_houses("Placidus")
whole_sign_cusps = chart.get_houses("Whole Sign")
```
---

## Ayanamsas / Sidereal Zodiacs (9 systems)

Stellium supports sidereal zodiac calculations with multiple ayanamsa options across Vedic and Western traditions.

### Vedic Tradition

| Name | Registry Key | Description |
|------|--------------|-------------|
| Lahiri | `lahiri` | Indian government standard. Chitrapaksha ayanamsa. Most widely used. |
| Raman | `raman` | B.V. Raman's ayanamsa. Popular in South India. |
| Krishnamurti | `krishnamurti` | Used in KP (Krishnamurti Paddhati) system. |
| Yukteshwar | `yukteshwar` | Sri Yukteshwar's ayanamsa from *The Holy Science*. |
| J.N. Bhasin | `jn_bhasin` | North Indian variant by J.N. Bhasin. |

### Vedic Star-Based

| Name | Registry Key | Description |
|------|--------------|-------------|
| True Chitrapaksha | `true_citra` | Spica (Chitra) fixed at exactly 0° Libra. |
| True Revati | `true_revati` | Revati fixed at exactly 0° Aries. |

### Western Sidereal

| Name | Registry Key | Description |
|------|--------------|-------------|
| Fagan-Bradley | `fagan_bradley` | Primary Western sidereal ayanamsa. |
| De Luce | `deluce` | De Luce's Western sidereal calculation. |

### Example: Sidereal Charts

```python
from stellium import ChartBuilder
from stellium.core.native import Native
from datetime import datetime

native = Native(datetime(1994, 1, 6, 11, 47), "Palo Alto, CA")

# Vedic chart with Lahiri ayanamsa
chart = ChartBuilder.from_native(native).with_sidereal("lahiri").calculate()

# Western sidereal
chart = ChartBuilder.from_native(native).with_sidereal("fagan_bradley").calculate()

# KP astrology
chart = ChartBuilder.from_native(native).with_sidereal("krishnamurti").calculate()
```
---

## Fixed Stars (26 stars)

Stellium includes 26 major fixed stars organized into three tiers based on astrological significance.

### Tier 1: Royal Stars of Persia (4 stars)

The four Watchers of the Heavens - the most significant traditional fixed stars.

| Name | Constellation | Mag | Nature | Keywords |
|------|---------------|-----|--------|----------|
| Aldebaran | Taurus | 0.85 | Mars | Integrity, eloquence, courage, guardian, military honors |
| Regulus | Leo | 1.35 | Mars/Jupiter | Royalty, success, fame, ambition, leadership |
| Antares | Scorpio | 1.09 | Mars/Jupiter | Intensity, obsession, strategy, self-destruction |
| Fomalhaut | Piscis Austrinus | 1.16 | Venus/Mercury | Idealism, dreams, magic, immortality through art |

### Tier 2: Major Stars (11 stars)

High-significance stars commonly used in astrological interpretation.

| Name | Constellation | Mag | Nature | Keywords |
|------|---------------|-----|--------|----------|
| Algol | Perseus | 2.12 | Saturn/Jupiter | Intensity, transformation, female power |
| Sirius | Canis Major | -1.46 | Jupiter/Mars | Brilliance, ambition, fame, devotion |
| Spica | Virgo | 0.97 | Venus/Mars | Brilliance, talent, gifts, skill |
| Arcturus | Bootes | -0.05 | Mars/Jupiter | Pathfinding, pioneering, prosperity |
| Vega | Lyra | 0.03 | Venus/Mercury | Charisma, artistic talent, magic |
| Capella | Auriga | 0.08 | Mars/Mercury | Curiosity, learning, civic honors |
| Rigel | Orion | 0.13 | Jupiter/Saturn | Education, teaching, lasting fame |
| Betelgeuse | Orion | 0.42 | Mars/Mercury | Success, fame, martial honors |
| Procyon | Canis Minor | 0.34 | Mercury/Mars | Quick success, sudden rise, sudden fall |
| Pollux | Gemini | 1.14 | Mars | Courage, athletics, craftiness |
| Alcyone | Taurus | 2.87 | Moon/Mars | Ambition, eminence, sorrow (Pleiades) |

### Tier 3: Extended Stars (11 stars)

Additional stars for detailed analysis.

| Name | Constellation | Mag | Nature | Keywords |
|------|---------------|-----|--------|----------|
| Castor | Gemini | 1.58 | Mercury | Intellect, writing, sudden fame/loss |
| Deneb | Cygnus | 1.25 | Venus/Mercury | Idealism, intelligence, artistic talent |
| Altair | Aquila | 0.77 | Mars/Jupiter | Boldness, ambition, sudden wealth |
| Canopus | Carina | -0.74 | Saturn/Jupiter | Voyages, navigation, education |
| Polaris | Ursa Minor | 1.98 | Saturn/Venus | Direction, guidance, spiritual focus |
| Achernar | Eridanus | 0.46 | Jupiter | Success, happiness, high office |
| Hamal | Aries | 2.00 | Mars/Saturn | Independence, headstrong |
| Alkaid | Ursa Major | 1.86 | Mars | Mourning, danger, leadership |
| Vindemiatrix | Virgo | 2.83 | Saturn/Mercury | Widowhood, falsity, harvest |
| Zubeneschamali | Libra | 2.61 | Jupiter/Mercury | Good fortune, honor, riches |
| Zubenelgenubi | Libra | 2.75 | Saturn/Mars | Negative, social unrest, ill health |

### Example: Including Fixed Stars

```python
from stellium import ChartBuilder
from stellium.core.native import Native
from stellium.components import FixedStarsComponent
from datetime import datetime

native = Native(datetime(1994, 1, 6, 11, 47), "Palo Alto, CA")

# All fixed stars
chart = ChartBuilder.from_native(native).add_component(FixedStarsComponent()).calculate()

# Royal stars only (Tier 1)
chart = ChartBuilder.from_native(native).add_component(FixedStarsComponent(royal_only=True)).calculate()

# Major stars (Tiers 1 and 2)
chart = ChartBuilder.from_native(native).add_component(FixedStarsComponent(tier=2, include_higher_tiers=True)).calculate()

# Specific stars
chart = ChartBuilder.from_native(native).add_component(FixedStarsComponent(stars=["Regulus", "Algol", "Spica"])).calculate()

# Access results
fixed_stars = chart.get_component_result("Fixed Stars")
for star in fixed_stars:
    print(f"{star.name}: {star.longitude:.2f}° {star.sign}")
```
<!--pytest-codeblocks:expected-output-->
```
Regulus: 149.75° Leo
Algol: 56.09° Taurus
Spica: 203.76° Libra
```

---

## Arabic Parts / Lots (28 parts)

Stellium implements the traditional Hellenistic lots with proper sect-based calculations.

**Formula:** `Lot = ASC + Point2 - Point3` (day) or `Lot = ASC + Point3 - Point2` (night, when sect flip applies)

### Core Hermetic Lots (8 parts)

The seven Hermetic lots plus one variant.

| Name | Formula (Day) | Sect Flip | Theme |
|------|---------------|-----------|-------|
| Part of Fortune | ASC + Moon - Sun | Yes | Body, health, material wellbeing |
| Part of Spirit | ASC + Sun - Moon | Yes | Soul, intellect, purpose, career |
| Part of Eros | ASC + Venus - Spirit | Yes | Love, desire, affection |
| Part of Eros (Planetary) | ASC + Venus - Sun | No | Ptolemaic love variant |
| Part of Necessity | ASC + Mercury - Fortune | Yes | Constraints, fate, struggles |
| Part of Courage | ASC + Mars - Fortune | Yes | Boldness, action, treachery |
| Part of Victory | ASC + Jupiter - Fortune | Yes | Victory, faith, success |
| Part of Nemesis | ASC + Saturn - Fortune | Yes | Subconscious, endings, karma |

### Family & Relationship Lots (5 parts)

| Name | Formula (Day) | Sect Flip | Theme |
|------|---------------|-----------|-------|
| Part of Father | ASC + Sun - Saturn | Yes | Father figure relationship |
| Part of Mother | ASC + Moon - Venus | Yes | Mother figure relationship |
| Part of Marriage | ASC + Venus - Saturn | Yes | Partnership, commitment |
| Part of Children | ASC + Jupiter - Saturn | Yes | Fertility, children |
| Part of Siblings | ASC + Mercury - Saturn | Yes | Brothers, sisters, kin |

### Life Topic Lots (7 parts)

| Name | Formula (Day) | Sect Flip | Theme |
|------|---------------|-----------|-------|
| Part of Action | ASC + Mars - Sun | Yes | Career, vocation, will |
| Part of Profession | ASC + MC - Sun | No | Public standing |
| Part of Passion | ASC + Venus - Mars | No | Passion, sexual attraction |
| Part of Illness | ASC + Mars - Saturn | Yes | Health issues |
| Part of Death | ASC + Saturn - Moon | Yes | Endings, nature of death |
| Part of Travel | ASC + Mars - Mercury | Yes | Journeys, movement |
| Part of Friends | ASC + Mercury - Moon | Yes | Friendships, alliances |

### Planetary Exaltation Lots (8 parts)

Based on each planet's exaltation sign ruler.

| Name | Formula (Day) | Sect Flip | Theme |
|------|---------------|-----------|-------|
| Part of the Sun | ASC + Sun - Mars | Yes | Glory, recognition |
| Part of the Moon | ASC + Moon - Venus | Yes | Nurturing, protection |
| Part of Mercury | ASC + Mercury - Mercury | No | Intellect, communication |
| Part of Venus | ASC + Venus - Jupiter | Yes | Beauty, art, grace |
| Part of Mars | ASC + Mars - Saturn | Yes | Strategy, endurance |
| Part of Jupiter | ASC + Jupiter - Moon | Yes | Growth, good fortune |
| Part of Saturn | ASC + Saturn - Venus | Yes | Structure, discipline |

### Example: Calculating Arabic Parts

```python
from stellium import ChartBuilder
from stellium.core.native import Native
from stellium.components import ArabicPartsCalculator
from datetime import datetime

native = Native(datetime(1994, 1, 6, 11, 47), "Palo Alto, CA")

# All Arabic parts
chart = ChartBuilder.from_native(native).add_component(ArabicPartsCalculator()).calculate()

# Specific parts only
chart = ChartBuilder.from_native(native).add_component(
    ArabicPartsCalculator(["Part of Fortune", "Part of Spirit"])
).calculate()

# Access results
fortune = chart.get_object("Part of Fortune")
print(f"Part of Fortune: {fortune.longitude:.2f}° {fortune.sign}")
```
<!--pytest-codeblocks:expected-output-->
```
Part of Fortune: 311.26° Aquarius
```

---

## Aspects (26 aspects)

Stellium supports major, minor, harmonic, and declination aspects with configurable orbs.

### Major Aspects (Ptolemaic) - 5 aspects

| Name | Angle | Glyph | Default Orb | Description |
|------|-------|-------|-------------|-------------|
| Conjunction | 0° | ☌ | 8.0° | Blending and merging of energies |
| Sextile | 60° | ⚹ | 6.0° | Harmonious opportunity and cooperation |
| Square | 90° | □ | 8.0° | Tension, friction, motivation to act |
| Trine | 120° | △ | 8.0° | Harmony, talent, natural ability |
| Opposition | 180° | ☍ | 8.0° | Awareness through contrast and balance |

### Minor Aspects - 4 aspects

| Name | Angle | Glyph | Default Orb | Description |
|------|-------|-------|-------------|-------------|
| Semisextile | 30° | ⚺ | 3.0° | Subtle friction requiring adjustments |
| Semisquare | 45° | ∠ | 3.0° | Irritation and need for action |
| Sesquisquare | 135° | ⚼ | 3.0° | Tension and restlessness |
| Quincunx | 150° | ⚻ | 3.0° | Requires adjustment and integration |

### Harmonic Aspects - Quintile Family (H5) - 2 aspects

| Name | Angle | Glyph | Default Orb | Description |
|------|-------|-------|-------------|-------------|
| Quintile | 72° | Q | 1.0° | Creative talent, skill, unique gifts |
| Biquintile | 144° | bQ | 1.0° | Artistic expression and innovation |

### Harmonic Aspects - Septile Family (H7) - 3 aspects

| Name | Angle | Glyph | Default Orb | Description |
|------|-------|-------|-------------|-------------|
| Septile | 51.43° | S | 1.0° | Mystical fate, destiny, spiritual purpose |
| Biseptile | 102.86° | bS | 1.0° | Karmic patterns and destiny |
| Triseptile | 154.29° | tS | 1.0° | Fated encounters, spiritual gifts |

### Harmonic Aspects - Novile Family (H9) - 3 aspects

| Name | Angle | Glyph | Default Orb | Description |
|------|-------|-------|-------------|-------------|
| Novile | 40° | N | 1.0° | Completion, perfection, higher wisdom |
| Binovile | 80° | bN | 1.0° | Joy, bliss, divine connection |
| Quadnovile | 160° | qN | 1.0° | Spiritual mastery, enlightenment |

### Declination Aspects - 2 aspects

| Name | Angle | Glyph | Default Orb | Description |
|------|-------|-------|-------------|-------------|
| Parallel | 0° | ∥ | 1.0° | Same declination (both N or S), like conjunction |
| Contraparallel | 180° | ⋕ | 1.0° | Opposite declination, like opposition |

### Example: Aspect Configuration

```python
from stellium import ChartBuilder
from stellium.core.native import Native
from stellium.engines.aspects import ModernAspectEngine, HarmonicAspectEngine
from datetime import datetime

native = Native(datetime(1994, 1, 6, 11, 47), "Palo Alto, CA")

# Major aspects only (default: Conjunction, Sextile, Square, Trine, Opposition)
chart = ChartBuilder.from_native(native).with_aspects().calculate()

# Custom aspect selection via AspectConfig
from stellium.core.config import AspectConfig

config = AspectConfig(aspects=["Conjunction", "Sextile", "Square", "Trine", "Opposition", "Semi-Sextile", "Quincunx"])
chart = ChartBuilder.from_native(native).with_aspects(ModernAspectEngine(config)).calculate()

# Harmonic aspects (e.g., Quintile = 5th harmonic)
chart = (ChartBuilder.from_native(native)
    .with_aspects(HarmonicAspectEngine(harmonic=5))  # Quintiles (72°)
    .calculate())

# Access aspects
for aspect in chart.aspects[:5]:
    print(f"{aspect.object1.name} {aspect.aspect_name} {aspect.object2.name} (orb: {aspect.orb:.2f}°)")
```
<!--pytest-codeblocks:expected-output-->
```
Moon H5 Uranus (orb: 0.26°)
Moon H5 Neptune (orb: 1.50°)
Jupiter H5 Uranus (orb: 0.70°)
Jupiter H5 Neptune (orb: 1.94°)
```

---

## Summary Statistics

| Category | Count | Description |
|----------|-------|-------------|
| Celestial Objects | 37 | Planets (10) + Nodes (3) + Points (3) + Asteroids (5) + Centaurs (4) + TNOs (6) + Uranian (8) |
| House Systems | 18 | All major systems from ancient to modern |
| Ayanamsas | 9 | Vedic and Western sidereal options |
| Fixed Stars | 26 | Royal (4) + Major (11) + Extended (11) |
| Arabic Parts | 28 | Hermetic (8) + Family (5) + Life (7) + Planetary (8) |
| Aspects | 26 | Major (5) + Minor (4) + Harmonic (8) + Declination (2) |
| **Total Options** | **144** | Comprehensive astrological toolkit |

---

*For more detailed documentation, see the individual module docstrings and the [README](https://github.com/katelouie/stellium/blob/main/README.md).*
