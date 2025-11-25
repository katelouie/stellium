# Chart Types

## Composite vs Davison Charts

### What Are Relationship Charts?

Relationship charts create a single chart representing the relationship as its own entity - not the interaction between two people (that's synastry), but the relationship itself as a third thing that emerges from the union.

### Composite Charts

**Method:** Calculate the midpoint of each planet pair between two natal charts.

```text
Composite Sun = midpoint(Person A's Sun, Person B's Sun)
Composite Moon = midpoint(Person A's Moon, Person B's Moon)
... and so on for all planets
```

**Characteristics:**

- Mathematical construct (no actual moment in time)
- Typically rendered house-less (no meaningful Ascendant)
- Focuses on planetary aspects within the composite
- Popular in modern psychological astrology

**Schools of Thought:**

- Hand/Arroyo School: Pure midpoints, no houses, aspect-focused
- Davison-derivative School: Use derived angles from midpoint ASC/MC
- Reference Location School: Calculate houses for a meaningful location

### Davison Charts

**Method:** Find the midpoint in both time and space between two birth events, then cast a real chart for that moment and place.

```text
Davison DateTime = midpoint(Person A's birth time, Person B's birth time)
Davison Location = midpoint(Person A's birth place, Person B's birth place)
```

**Characteristics:**

- Represents an actual astronomical moment
- Has a real Ascendant and house system
- Can be progressed like any natal chart
- Developed by Ronald Davison in the 1970s

**Geographic Midpoint Methods:**

- Simple Average: `(lat1 + lat2) / 2, (lon1 + lon2) / 2` — fast but inaccurate for distant points
- Great Circle Midpoint: True geodesic midpoint on Earth's surface — accurate for any distance
