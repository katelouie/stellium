"""
Celestial Objects Registry

A comprehensive catalog of all celestial objects used in astrological calculations.
This centralizes metadata like names, glyphs, types, and descriptions for planets,
asteroids, nodes, points, fixed stars, and other celestial bodies.
"""

from dataclasses import dataclass, field
from typing import Any

from stellium.core.models import ObjectType


@dataclass(frozen=True)
class CelestialObjectInfo:
    """
    Complete metadata for a celestial object.

    This represents everything we know about an object - from its technical
    name and ephemeris ID to its glyph and human-readable description.
    """

    # Core Identity
    name: str  # Technical/internal name (e.g., "Mean Apogee", "True Node")
    display_name: str  # What users see (e.g., "Black Moon Lilith", "North Node")
    object_type: ObjectType  # PLANET, NODE, POINT, ASTEROID, etc.

    # Visual Representation
    glyph: str  # Unicode astrological glyph (e.g., "☽", "☊", "⚸")
    # Filename of a bundled SVG glyph, for bodies Unicode does not usefully cover
    # (centaurs, TNOs, Uranian points, named stars). Resolved against the packaged
    # glyph directory by `stellium.data.paths.find_glyph_svg` — a bare filename, NOT
    # a path. It used to be "assets/glyphs/pholus.svg", relative to the repo root,
    # which resolved to nothing at all once installed.
    glyph_svg_path: str | None = None

    # Ephemeris/Calculation Data
    swiss_ephemeris_id: int | None = None  # Swiss Ephemeris object ID (if applicable)
    avg_daily_motion: float | None = None  # Average apparent daily motion (geocentric)

    # Classification & Organization
    category: str | None = (
        None  # "Traditional Planet", "Asteroid", "Centaur", "TNO", "Fixed Star", etc.
    )
    aliases: list[str] = field(
        default_factory=list
    )  # Alternative names (e.g., ["Lilith", "BML"])

    # Documentation
    description: str = ""  # Brief explanation of what this object represents

    # Advanced/Optional Metadata
    metadata: dict[str, Any] = field(
        default_factory=dict
    )  # Extensible for future needs

    def __str__(self) -> str:
        return f"{self.display_name} ({self.name})"


# ============================================================================
# CELESTIAL OBJECTS REGISTRY
# ============================================================================

CELESTIAL_REGISTRY: dict[str, CelestialObjectInfo] = {
    # ========================================================================
    # TRADITIONAL PLANETS (The Septenary)
    # ========================================================================
    "Sun": CelestialObjectInfo(
        name="Sun",
        display_name="Sun",
        object_type=ObjectType.PLANET,
        glyph="☉",
        swiss_ephemeris_id=0,
        avg_daily_motion=0.986,
        category="Traditional Planet",
        aliases=["Sol"],
        description="The luminary representing life force, vitality, ego, and conscious will.",
    ),
    "Moon": CelestialObjectInfo(
        name="Moon",
        display_name="Moon",
        object_type=ObjectType.PLANET,
        glyph="☽",
        swiss_ephemeris_id=1,
        avg_daily_motion=13.177,
        category="Traditional Planet",
        aliases=["Luna"],
        description="The luminary representing emotions, instincts, habits, and the subconscious.",
    ),
    "Mercury": CelestialObjectInfo(
        name="Mercury",
        display_name="Mercury",
        object_type=ObjectType.PLANET,
        glyph="☿",
        swiss_ephemeris_id=2,
        avg_daily_motion=1.383,
        category="Traditional Planet",
        description="The planet of communication, intellect, learning, and exchange.",
    ),
    "Venus": CelestialObjectInfo(
        name="Venus",
        display_name="Venus",
        object_type=ObjectType.PLANET,
        glyph="♀",
        swiss_ephemeris_id=3,
        avg_daily_motion=1.2,
        category="Traditional Planet",
        description="The planet of love, beauty, harmony, values, and relationships.",
    ),
    "Mars": CelestialObjectInfo(
        name="Mars",
        display_name="Mars",
        object_type=ObjectType.PLANET,
        glyph="♂",
        swiss_ephemeris_id=4,
        avg_daily_motion=0.524,
        category="Traditional Planet",
        description="The planet of action, desire, courage, assertion, and conflict.",
    ),
    "Jupiter": CelestialObjectInfo(
        name="Jupiter",
        display_name="Jupiter",
        object_type=ObjectType.PLANET,
        glyph="♃",
        swiss_ephemeris_id=5,
        avg_daily_motion=0.083,
        category="Traditional Planet",
        description="The planet of expansion, growth, wisdom, fortune, and philosophy.",
    ),
    "Saturn": CelestialObjectInfo(
        name="Saturn",
        display_name="Saturn",
        object_type=ObjectType.PLANET,
        glyph="♄",
        swiss_ephemeris_id=6,
        avg_daily_motion=0.034,
        category="Traditional Planet",
        description="The planet of structure, discipline, boundaries, responsibility, and time.",
    ),
    # ========================================================================
    # MODERN PLANETS (Outer Planets)
    # ========================================================================
    "Uranus": CelestialObjectInfo(
        name="Uranus",
        display_name="Uranus",
        object_type=ObjectType.PLANET,
        glyph="♅",
        swiss_ephemeris_id=7,
        avg_daily_motion=0.012,
        category="Modern Planet",
        description="The planet of revolution, innovation, awakening, and sudden change.",
    ),
    "Neptune": CelestialObjectInfo(
        name="Neptune",
        display_name="Neptune",
        object_type=ObjectType.PLANET,
        glyph="♆",
        swiss_ephemeris_id=8,
        avg_daily_motion=0.006,
        category="Modern Planet",
        description="The planet of dreams, illusion, spirituality, dissolution, and the unconscious.",
    ),
    "Pluto": CelestialObjectInfo(
        name="Pluto",
        display_name="Pluto",
        object_type=ObjectType.PLANET,
        glyph="♇",
        swiss_ephemeris_id=9,
        avg_daily_motion=0.004,
        category="Modern Planet",
        description="The planet of transformation, power, death/rebirth, and the underworld.",
    ),
    # ========================================================================
    # LUNAR NODES
    # ========================================================================
    "True Node": CelestialObjectInfo(
        name="True Node",
        display_name="North Node",
        object_type=ObjectType.NODE,
        glyph="☊",
        swiss_ephemeris_id=11,
        avg_daily_motion=-0.053,
        category="Lunar Node",
        aliases=["North Node", "Dragon's Head", "Rahu"],
        description="The true (osculating) lunar north node - the Moon's ascending node, representing karmic direction and soul growth.",
    ),
    "Mean Node": CelestialObjectInfo(
        name="Mean Node",
        display_name="Mean North Node",
        object_type=ObjectType.NODE,
        glyph="☊",
        swiss_ephemeris_id=10,
        avg_daily_motion=-0.053,
        category="Lunar Node",
        aliases=["Mean North Node"],
        description="The mean lunar north node - averaged position of the Moon's ascending node.",
    ),
    "South Node": CelestialObjectInfo(
        name="South Node",
        display_name="South Node",
        object_type=ObjectType.NODE,
        glyph="☋",
        swiss_ephemeris_id=None,  # Calculated as opposite of North Node
        avg_daily_motion=-0.053,
        category="Lunar Node",
        aliases=["Dragon's Tail", "Ketu"],
        description="The lunar south node - opposite the North Node, representing past patterns and karmic release.",
    ),
    # ========================================================================
    # CALCULATED POINTS
    # ========================================================================
    "Mean Apogee": CelestialObjectInfo(
        name="Mean Apogee",
        display_name="Black Moon Lilith",
        object_type=ObjectType.POINT,
        glyph="⚸",
        swiss_ephemeris_id=12,
        avg_daily_motion=0.111,
        category="Lunar Apogee",
        aliases=["Lilith", "BML", "Black Moon", "Mean Lilith"],
        description="The mean lunar apogee - the point where the Moon is farthest from Earth. Represents the wild, untamed feminine, shadow work, and rejection of patriarchal norms.",
    ),
    "True Apogee": CelestialObjectInfo(
        name="True Apogee",
        display_name="True Black Moon Lilith",
        object_type=ObjectType.POINT,
        glyph="⚸",
        swiss_ephemeris_id=13,
        avg_daily_motion=0.111,
        category="Lunar Apogee",
        aliases=["True Lilith", "Osculating Lilith"],
        description="The true (osculating) lunar apogee - the actual, instantaneous farthest point of the Moon's orbit.",
    ),
    "Vertex": CelestialObjectInfo(
        name="Vertex",
        display_name="Vertex",
        object_type=ObjectType.POINT,
        glyph="🜊",
        swiss_ephemeris_id=-5,  # Calculated by swe.houses()
        category="Calculated Point",
        aliases=["Electric Ascendant"],
        description="A sensitive point on the western horizon, often associated with fated encounters and destined events.",
    ),
    # ========================================================================
    # ASTEROIDS (The "Big Four")
    # ========================================================================
    "Ceres": CelestialObjectInfo(
        name="Ceres",
        display_name="Ceres",
        object_type=ObjectType.ASTEROID,
        glyph="⚳",
        swiss_ephemeris_id=17,
        avg_daily_motion=0.214,
        category="Main Belt Asteroid",
        description="The largest asteroid, representing nurturing, motherhood, agriculture, and sustenance.",
    ),
    "Pallas": CelestialObjectInfo(
        name="Pallas",
        display_name="Pallas Athena",
        object_type=ObjectType.ASTEROID,
        glyph="⚴",
        swiss_ephemeris_id=18,
        avg_daily_motion=0.214,
        category="Main Belt Asteroid",
        aliases=["Pallas Athene"],
        description="The warrior asteroid representing wisdom, creative intelligence, and strategic thinking.",
    ),
    "Juno": CelestialObjectInfo(
        name="Juno",
        display_name="Juno",
        object_type=ObjectType.ASTEROID,
        glyph="⚵",
        swiss_ephemeris_id=19,
        avg_daily_motion=0.226,
        category="Main Belt Asteroid",
        description="The asteroid of partnership, marriage, commitment, and power dynamics in relationships.",
    ),
    "Vesta": CelestialObjectInfo(
        name="Vesta",
        display_name="Vesta",
        object_type=ObjectType.ASTEROID,
        glyph="⚶",
        swiss_ephemeris_id=20,
        avg_daily_motion=0.272,
        category="Main Belt Asteroid",
        description="The asteroid of the sacred flame, devotion, focus, and sexual integrity.",
    ),
    "Hygiea": CelestialObjectInfo(
        name="Hygiea",
        display_name="Hygiea",
        object_type=ObjectType.ASTEROID,
        glyph="⚕",
        glyph_svg_path="hygiea.svg",
        swiss_ephemeris_id=10010,  # AST_OFFSET (10000) + asteroid number (10)
        category="Main Belt Asteroid",
        aliases=["Hygeia"],
        description="The asteroid of health, hygiene, and preventive medicine. Named for the goddess of cleanliness and sanitation.",
    ),
    # ========================================================================
    # CENTAURS
    # ========================================================================
    "Chiron": CelestialObjectInfo(
        name="Chiron",
        display_name="Chiron",
        object_type=ObjectType.ASTEROID,  # Note: Often treated as honorary planet
        glyph="⚷",
        swiss_ephemeris_id=15,
        avg_daily_motion=0.019,
        category="Centaur",
        aliases=["The Wounded Healer"],
        description="The wounded healer - represents deep wounds, healing journey, mentorship, and bridging worlds.",
    ),
    "Pholus": CelestialObjectInfo(
        name="Pholus",
        display_name="Pholus",
        object_type=ObjectType.ASTEROID,
        glyph="⬰",
        glyph_svg_path="pholus.svg",
        swiss_ephemeris_id=16,
        category="Centaur",
        description="Small cause, big effect - represents multigenerational patterns and catalyst events.",
    ),
    "Nessus": CelestialObjectInfo(
        name="Nessus",
        display_name="Nessus",
        object_type=ObjectType.ASTEROID,
        glyph="Nes",
        glyph_svg_path="nessus.svg",
        swiss_ephemeris_id=17066,  # MPC 7066 + AST_OFFSET
        category="Centaur",
        description="Represents abuse, boundaries violated, karmic consequences, and the poison that becomes medicine.",
    ),
    "Chariklo": CelestialObjectInfo(
        name="Chariklo",
        display_name="Chariklo",
        object_type=ObjectType.ASTEROID,
        glyph="Cha",
        glyph_svg_path="chariklo.svg",
        swiss_ephemeris_id=20199,  # MPC 10199 + AST_OFFSET
        category="Centaur",
        description="Chiron's wife - represents compassionate healing, devotion, and grounding spiritual wisdom.",
    ),
    # ========================================================================
    # TRANS-NEPTUNIAN OBJECTS (TNOs)
    # ========================================================================
    "Eris": CelestialObjectInfo(
        name="Eris",
        display_name="Eris",
        object_type=ObjectType.ASTEROID,
        glyph="⯰",
        glyph_svg_path="eris.svg",
        swiss_ephemeris_id=146199,  # MPC 136199 + AST_OFFSET
        category="Dwarf Planet (TNO)",
        aliases=["Xena"],
        description="The dwarf planet of discord, rivalry, and fierce feminine power. Larger than Pluto.",
    ),
    "Sedna": CelestialObjectInfo(
        name="Sedna",
        display_name="Sedna",
        object_type=ObjectType.ASTEROID,
        glyph="Sed",
        glyph_svg_path="sedna.svg",
        swiss_ephemeris_id=100377,  # MPC 90377 + AST_OFFSET
        category="Trans-Neptunian Object",
        description="Represents deep cold, isolation, victim consciousness, and the slow thaw of healing.",
    ),
    "Makemake": CelestialObjectInfo(
        name="Makemake",
        display_name="Makemake",
        object_type=ObjectType.ASTEROID,
        glyph="🝼",
        swiss_ephemeris_id=146472,  # MPC 136472 + AST_OFFSET
        category="Dwarf Planet (TNO)",
        description="Represents environmental awareness, resourcefulness, and manifestation.",
    ),
    "Haumea": CelestialObjectInfo(
        name="Haumea",
        display_name="Haumea",
        object_type=ObjectType.ASTEROID,
        glyph="🝻",
        swiss_ephemeris_id=146108,  # MPC 136108 + AST_OFFSET
        category="Dwarf Planet (TNO)",
        description="Represents rebirth, fertility, connection to nature, and rapid transformation.",
    ),
    "Orcus": CelestialObjectInfo(
        name="Orcus",
        display_name="Orcus",
        object_type=ObjectType.ASTEROID,
        glyph="Orc",
        glyph_svg_path="orcus.svg",
        swiss_ephemeris_id=100482,  # MPC 90482 + AST_OFFSET
        category="Trans-Neptunian Object",
        aliases=["Anti-Pluto"],
        description="The anti-Pluto - represents oaths, consequences, and the afterlife.",
    ),
    "Quaoar": CelestialObjectInfo(
        name="Quaoar",
        display_name="Quaoar",
        object_type=ObjectType.ASTEROID,
        glyph="Qua",
        glyph_svg_path="quaoar.svg",
        swiss_ephemeris_id=60000,  # MPC 50000 + AST_OFFSET
        category="Trans-Neptunian Object",
        description="Represents creation myths, harmony, and finding order in chaos.",
    ),
    "Gonggong": CelestialObjectInfo(
        name="Gonggong",
        display_name="Gonggong",
        object_type=ObjectType.ASTEROID,
        glyph="Gon",
        glyph_svg_path="gonggong.svg",
        swiss_ephemeris_id=235088,  # MPC 225088 + AST_OFFSET
        category="Trans-Neptunian Object",
        aliases=("2007 OR10",),
        description=(
            "Chinese water god of floods and chaos. Read for disruption that clears "
            "ground, and for what will not stay contained."
        ),
    ),
    # ========================================================================
    # NAMED ASTEROIDS
    #
    # The personal-name asteroids, used in modern practice for relationship and
    # vocation work. Each needs its own .se1 file:
    #     stellium ephemeris download-asteroid <mpc>
    # ========================================================================
    "Psyche": CelestialObjectInfo(
        name="Psyche",
        display_name="Psyche",
        object_type=ObjectType.ASTEROID,
        glyph="Psy",
        glyph_svg_path="psyche.svg",
        swiss_ephemeris_id=10016,  # MPC 16 + AST_OFFSET
        category="Asteroid",
        description="The soul, and the wound in it. Where you were broken open, and what that made possible.",
    ),
    "Sappho": CelestialObjectInfo(
        name="Sappho",
        display_name="Sappho",
        object_type=ObjectType.ASTEROID,
        glyph="Sap",
        glyph_svg_path="sappho.svg",
        swiss_ephemeris_id=10080,  # MPC 80 + AST_OFFSET
        category="Asteroid",
        description="Poetic and erotic sensibility; artistic friendship, and love that does not fit a category.",
    ),
    "Pandora": CelestialObjectInfo(
        name="Pandora",
        display_name="Pandora",
        object_type=ObjectType.ASTEROID,
        glyph="Pan",
        glyph_svg_path="pandora.svg",
        swiss_ephemeris_id=10055,  # MPC 55 + AST_OFFSET
        category="Asteroid",
        description="Curiosity that cannot be un-satisfied. The question you had to ask, and its consequences.",
    ),
    "Amor": CelestialObjectInfo(
        name="Amor",
        display_name="Amor",
        object_type=ObjectType.ASTEROID,
        glyph="Amo",
        glyph_svg_path="amor.svg",
        swiss_ephemeris_id=11221,  # MPC 1221 + AST_OFFSET
        category="Asteroid",
        description="Love given freely and without condition — compassion rather than desire.",
    ),
    "Astraea": CelestialObjectInfo(
        name="Astraea",
        display_name="Astraea",
        object_type=ObjectType.ASTEROID,
        glyph="Ast",
        glyph_svg_path="astraea.svg",
        swiss_ephemeris_id=10005,  # MPC 5 + AST_OFFSET
        category="Asteroid",
        description="Justice, and the return of it. Discernment; the refusal to look away.",
    ),
    "Hebe": CelestialObjectInfo(
        name="Hebe",
        display_name="Hebe",
        object_type=ObjectType.ASTEROID,
        glyph="Heb",
        glyph_svg_path="hebe.svg",
        swiss_ephemeris_id=10006,  # MPC 6 + AST_OFFSET
        category="Asteroid",
        description="Youth, service, and the cup that is refilled. Vitality offered to others.",
    ),
    "Iris": CelestialObjectInfo(
        name="Iris",
        display_name="Iris",
        object_type=ObjectType.ASTEROID,
        glyph="Iri",
        glyph_svg_path="iris.svg",
        swiss_ephemeris_id=10007,  # MPC 7 + AST_OFFSET
        category="Asteroid",
        description="The messenger between worlds. Communication that crosses a threshold.",
    ),
    "Flora": CelestialObjectInfo(
        name="Flora",
        display_name="Flora",
        object_type=ObjectType.ASTEROID,
        glyph="Flo",
        glyph_svg_path="flora.svg",
        swiss_ephemeris_id=10008,  # MPC 8 + AST_OFFSET
        category="Asteroid",
        description="Flowering, sensual pleasure, and the health of the body.",
    ),
    "Metis": CelestialObjectInfo(
        name="Metis",
        display_name="Metis",
        object_type=ObjectType.ASTEROID,
        glyph="Met",
        glyph_svg_path="metis.svg",
        swiss_ephemeris_id=10009,  # MPC 9 + AST_OFFSET
        category="Asteroid",
        description="Practical wisdom and counsel — the intelligence that was swallowed.",
    ),
    "Fortuna": CelestialObjectInfo(
        name="Fortuna",
        display_name="Fortuna",
        object_type=ObjectType.ASTEROID,
        glyph="For",
        glyph_svg_path="fortuna.svg",
        swiss_ephemeris_id=10019,  # MPC 19 + AST_OFFSET
        category="Asteroid",
        description="Luck, chance, and the turning of the wheel. What is not earned.",
    ),
    "Diana": CelestialObjectInfo(
        name="Diana",
        display_name="Diana",
        object_type=ObjectType.ASTEROID,
        glyph="Dia",
        glyph_svg_path="diana.svg",
        swiss_ephemeris_id=10078,  # MPC 78 + AST_OFFSET
        category="Asteroid",
        description="The wild and the untouched. Sovereignty, and the refusal to be domesticated.",
    ),
    "Hidalgo": CelestialObjectInfo(
        name="Hidalgo",
        display_name="Hidalgo",
        object_type=ObjectType.ASTEROID,
        glyph="Hid",
        glyph_svg_path="hidalgo.svg",
        swiss_ephemeris_id=10944,  # MPC 944 + AST_OFFSET
        category="Asteroid",
        description="Self-assertion and the crusade; standing up on behalf of others.",
    ),
    "Icarus": CelestialObjectInfo(
        name="Icarus",
        display_name="Icarus",
        object_type=ObjectType.ASTEROID,
        glyph="Ica",
        glyph_svg_path="icarus.svg",
        swiss_ephemeris_id=11566,  # MPC 1566 + AST_OFFSET
        category="Asteroid",
        description="Recklessness, escape, and the flight too near the sun.",
    ),
    "Toro": CelestialObjectInfo(
        name="Toro",
        display_name="Toro",
        object_type=ObjectType.ASTEROID,
        glyph="Tor",
        glyph_svg_path="toro.svg",
        swiss_ephemeris_id=11685,  # MPC 1685 + AST_OFFSET
        category="Asteroid",
        description="Raw strength and the use of force — power, and its restraint.",
    ),
    "Bacchus": CelestialObjectInfo(
        name="Bacchus",
        display_name="Bacchus",
        object_type=ObjectType.ASTEROID,
        glyph="Bac",
        glyph_svg_path="bacchus.svg",
        swiss_ephemeris_id=12063,  # MPC 2063 + AST_OFFSET
        category="Asteroid",
        description="Ecstasy, intoxication, and release from the ordinary self.",
    ),
    "Eros": CelestialObjectInfo(
        name="Eros",
        display_name="Eros",
        object_type=ObjectType.ASTEROID,
        glyph="Ero",
        glyph_svg_path="eros.svg",
        swiss_ephemeris_id=10433,  # MPC 433 + AST_OFFSET
        category="Asteroid",
        description="Desire that will not be reasoned with — passion, and what it costs to want.",
    ),
    "Urania": CelestialObjectInfo(
        name="Urania",
        display_name="Urania",
        object_type=ObjectType.ASTEROID,
        glyph="Ura",
        glyph_svg_path="urania.svg",
        swiss_ephemeris_id=10030,  # MPC 30 + AST_OFFSET
        category="Asteroid",
        description="Astronomy and astrology themselves; the study of the sky, and pattern-sense.",
    ),
    "Apollo": CelestialObjectInfo(
        name="Apollo",
        display_name="Apollo",
        object_type=ObjectType.ASTEROID,
        glyph="Apo",
        glyph_svg_path="apollo.svg",
        swiss_ephemeris_id=11862,  # MPC 1862 + AST_OFFSET
        category="Asteroid",
        description="The masculine principle in its bright form: aim, ambition, and the pursuit.",
    ),
    "Asbolus": CelestialObjectInfo(
        name="Asbolus",
        display_name="Asbolus",
        object_type=ObjectType.ASTEROID,
        glyph="Asb",
        glyph_svg_path="asbolus.svg",
        swiss_ephemeris_id=18405,  # MPC 8405 + AST_OFFSET
        category="Centaur",
        description="The seer who reads the omens and is not believed. Intuition under threat.",
    ),
    "Hylonome": CelestialObjectInfo(
        name="Hylonome",
        display_name="Hylonome",
        object_type=ObjectType.ASTEROID,
        glyph="Hyl",
        glyph_svg_path="hylonome.svg",
        swiss_ephemeris_id=20370,  # MPC 10370 + AST_OFFSET
        category="Centaur",
        description="Grief, and the dignity in it. Mourning, and love that outlives its object.",
    ),
    "Echeclus": CelestialObjectInfo(
        name="Echeclus",
        display_name="Echeclus",
        object_type=ObjectType.ASTEROID,
        glyph="Ech",
        glyph_svg_path="echeclus.svg",
        swiss_ephemeris_id=70558,  # MPC 60558 + AST_OFFSET
        category="Centaur",
        description="What was suppressed and erupts anyway. Sudden, unlooked-for release.",
    ),
    "Elatus": CelestialObjectInfo(
        name="Elatus",
        display_name="Elatus",
        object_type=ObjectType.ASTEROID,
        glyph="Ela",
        glyph_svg_path="elatus.svg",
        swiss_ephemeris_id=41824,  # MPC 31824 + AST_OFFSET
        category="Centaur",
        description="The voice, and its power to wound or to carry. Speech as an act.",
    ),
    "Bienor": CelestialObjectInfo(
        name="Bienor",
        display_name="Bienor",
        object_type=ObjectType.ASTEROID,
        glyph="Bie",
        glyph_svg_path="bienor.svg",
        swiss_ephemeris_id=64598,  # MPC 54598 + AST_OFFSET
        category="Centaur",
        description="Strength held collectively — what a group can do that a person cannot.",
    ),
    "Ixion": CelestialObjectInfo(
        name="Ixion",
        display_name="Ixion",
        object_type=ObjectType.ASTEROID,
        glyph="Ixi",
        glyph_svg_path="ixion.svg",
        swiss_ephemeris_id=38978,  # MPC 28978 + AST_OFFSET
        category="TNO",
        description="The one given a second chance who squandered it. Transgression, and what follows.",
    ),
    "Huya": CelestialObjectInfo(
        name="Huya",
        display_name="Huya",
        object_type=ObjectType.ASTEROID,
        glyph="Huy",
        glyph_svg_path="huya.svg",
        swiss_ephemeris_id=48628,  # MPC 38628 + AST_OFFSET
        category="TNO",
        description="Rain-bringer. What arrives from elsewhere to end a drought.",
    ),
    "Chaos": CelestialObjectInfo(
        name="Chaos",
        display_name="Chaos",
        object_type=ObjectType.ASTEROID,
        glyph="Cha",
        glyph_svg_path="chaos.svg",
        swiss_ephemeris_id=29521,  # MPC 19521 + AST_OFFSET
        category="TNO",
        description="The formless state before order — potential that has not yet chosen a shape.",
    ),
    "Deucalion": CelestialObjectInfo(
        name="Deucalion",
        display_name="Deucalion",
        object_type=ObjectType.ASTEROID,
        glyph="Deu",
        glyph_svg_path="deucalion.svg",
        swiss_ephemeris_id=63311,  # MPC 53311 + AST_OFFSET
        category="TNO",
        description="The one who survives the flood, and begins again. Continuity through catastrophe.",
    ),
    "Altjira": CelestialObjectInfo(
        name="Altjira",
        display_name="Altjira",
        object_type=ObjectType.ASTEROID,
        glyph="Alt",
        glyph_svg_path="altjira.svg",
        swiss_ephemeris_id=158780,  # MPC 148780 + AST_OFFSET
        category="TNO",
        description="The dreamtime: the world as it was made, and is still being made.",
    ),
    # ========================================================================
    # URANIAN / HAMBURG SCHOOL PLANETS
    # ========================================================================
    "Cupido": CelestialObjectInfo(
        name="Cupido",
        display_name="Cupido",
        object_type=ObjectType.ASTEROID,
        glyph="Cup",
        glyph_svg_path="cupido.svg",
        swiss_ephemeris_id=40,
        category="Uranian Planet",
        description="Hypothetical planet representing family, groups, art, and community.",
    ),
    "Hades": CelestialObjectInfo(
        name="Hades",
        display_name="Hades",
        object_type=ObjectType.ASTEROID,
        glyph="Had",
        glyph_svg_path="hades.svg",
        swiss_ephemeris_id=41,
        category="Uranian Planet",
        description="Hypothetical planet representing decay, the past, poverty, and what's hidden.",
    ),
    "Zeus": CelestialObjectInfo(
        name="Zeus",
        display_name="Zeus",
        object_type=ObjectType.ASTEROID,
        glyph="Zeu",
        glyph_svg_path="zeus.svg",
        swiss_ephemeris_id=42,
        category="Uranian Planet",
        description="Hypothetical planet representing leadership, fire, machines, and directed energy.",
    ),
    "Kronos": CelestialObjectInfo(
        name="Kronos",
        display_name="Kronos",
        object_type=ObjectType.ASTEROID,
        glyph="Kro",
        glyph_svg_path="kronos.svg",
        swiss_ephemeris_id=43,
        category="Uranian Planet",
        description="Hypothetical planet representing authority, expertise, and high position.",
    ),
    "Apollon": CelestialObjectInfo(
        name="Apollon",
        display_name="Apollon",
        object_type=ObjectType.ASTEROID,
        glyph="Apo",
        glyph_svg_path="apollon.svg",
        swiss_ephemeris_id=44,
        category="Uranian Planet",
        description="Hypothetical planet representing expansion, science, commerce, and success.",
    ),
    "Admetos": CelestialObjectInfo(
        name="Admetos",
        display_name="Admetos",
        object_type=ObjectType.ASTEROID,
        glyph="Adm",
        glyph_svg_path="admetos.svg",
        swiss_ephemeris_id=45,
        category="Uranian Planet",
        description="Hypothetical planet representing depth, stagnation, raw materials, and the earth.",
    ),
    "Vulkanus": CelestialObjectInfo(
        name="Vulkanus",
        display_name="Vulkanus",
        object_type=ObjectType.ASTEROID,
        glyph="Vul",
        glyph_svg_path="vulcanus.svg",
        swiss_ephemeris_id=46,
        category="Uranian Planet",
        aliases=["Vulcanus"],
        description="Hypothetical planet representing immense power, force, and intensity.",
    ),
    "Poseidon": CelestialObjectInfo(
        name="Poseidon",
        display_name="Poseidon",
        object_type=ObjectType.ASTEROID,
        glyph="Pos",
        glyph_svg_path="poseidon.svg",
        swiss_ephemeris_id=47,
        category="Uranian Planet",
        description="Hypothetical planet representing spirituality, enlightenment, and clarity.",
    ),
    # ========================================================================
    # URANIAN REFERENCE POINTS
    # ========================================================================
    "Aries Point": CelestialObjectInfo(
        name="Aries Point",
        display_name="Aries Point",
        object_type=ObjectType.POINT,
        glyph="♈",
        swiss_ephemeris_id=None,  # Fixed at 0° longitude, no ephemeris calculation needed
        category="Uranian Point",
        aliases=["AP", "Aries 0", "Vernal Point", "Spring Equinox"],
        description="The first degree of Aries (0° longitude). A fundamental reference point in Uranian astrology representing public events, worldly manifestation, and the intersection of personal and collective.",
    ),
    # ========================================================================
    # FIXED STARS (Selected Notable Stars)
    # ========================================================================
    "Algol": CelestialObjectInfo(
        name="Algol",
        display_name="Algol",
        object_type=ObjectType.FIXED_STAR,
        glyph="★",
        glyph_svg_path="algol.svg",
        swiss_ephemeris_id=None,  # Fixed stars calculated differently
        category="Fixed Star",
        aliases=["Beta Persei", "The Demon Star"],
        description="The most infamous fixed star - represents the Medusa's head, transformation through crisis, and facing the shadow.",
        metadata={
            "constellation": "Perseus",
            "magnitude": 2.1,
            "approx_longitude_2000": 26.0,
        },  # ~26° Taurus
    ),
    "Regulus": CelestialObjectInfo(
        name="Regulus",
        display_name="Regulus",
        object_type=ObjectType.FIXED_STAR,
        glyph="★",
        glyph_svg_path="regulus.svg",
        swiss_ephemeris_id=None,
        category="Fixed Star",
        aliases=["Alpha Leonis", "The Heart of the Lion"],
        description="Royal star representing glory, success, nobility, and leadership. One of the four Royal Stars of Persia.",
        metadata={
            "constellation": "Leo",
            "magnitude": 1.4,
            "approx_longitude_2000": 29.5,
        },  # ~29° Leo
    ),
    "Spica": CelestialObjectInfo(
        name="Spica",
        display_name="Spica",
        object_type=ObjectType.FIXED_STAR,
        glyph="★",
        swiss_ephemeris_id=None,
        category="Fixed Star",
        aliases=["Alpha Virginis"],
        description="The gift of the harvest - represents talent, brilliance, protection, and divine favor. One of the four Royal Stars.",
        metadata={
            "constellation": "Virgo",
            "magnitude": 1.0,
            "approx_longitude_2000": 23.5,
        },  # ~23° Libra
    ),
    "Antares": CelestialObjectInfo(
        name="Antares",
        display_name="Antares",
        object_type=ObjectType.FIXED_STAR,
        glyph="★",
        swiss_ephemeris_id=None,
        category="Fixed Star",
        aliases=["Alpha Scorpii", "The Rival of Mars"],
        description="The heart of the Scorpion - represents courage, obsession, confrontation, and intensity. One of the four Royal Stars.",
        metadata={
            "constellation": "Scorpius",
            "magnitude": 1.0,
            "approx_longitude_2000": 9.5,
        },  # ~9° Sagittarius
    ),
    "Aldebaran": CelestialObjectInfo(
        name="Aldebaran",
        display_name="Aldebaran",
        object_type=ObjectType.FIXED_STAR,
        glyph="★",
        swiss_ephemeris_id=None,
        category="Fixed Star",
        aliases=["Alpha Tauri", "The Eye of the Bull"],
        description="The follower of the Pleiades - represents integrity, eloquence, courage, and the warrior spirit. One of the four Royal Stars.",
        metadata={
            "constellation": "Taurus",
            "magnitude": 0.9,
            "approx_longitude_2000": 9.5,
        },  # ~9° Gemini
    ),
    "Fomalhaut": CelestialObjectInfo(
        name="Fomalhaut",
        display_name="Fomalhaut",
        object_type=ObjectType.FIXED_STAR,
        glyph="★",
        swiss_ephemeris_id=None,
        category="Fixed Star",
        aliases=["Alpha Piscis Austrini"],
        description="The mouth of the fish - represents idealism, utopianism, and the fall from grace. One of the four Royal Stars.",
        metadata={
            "constellation": "Piscis Austrinus",
            "magnitude": 1.2,
            "approx_longitude_2000": 3.5,
        },  # ~3° Pisces
    ),
    "Sirius": CelestialObjectInfo(
        name="Sirius",
        display_name="Sirius",
        object_type=ObjectType.FIXED_STAR,
        glyph="★",
        swiss_ephemeris_id=None,
        category="Fixed Star",
        aliases=["Alpha Canis Majoris", "The Dog Star"],
        description="The brightest star in the sky - represents fame, honor, devotion, passion, and the guardianship of the sacred.",
        metadata={
            "constellation": "Canis Major",
            "magnitude": -1.5,
            "approx_longitude_2000": 14.0,
        },  # ~14° Cancer
    ),
    "Pleiades": CelestialObjectInfo(
        name="Pleiades",
        display_name="Pleiades",
        object_type=ObjectType.FIXED_STAR,
        glyph="★",
        swiss_ephemeris_id=None,
        category="Fixed Star",
        aliases=["The Seven Sisters", "M45"],
        description="The weeping sisters - represents ambition, brilliance, love of learning, but also sorrow and loss.",
        metadata={
            "constellation": "Taurus",
            "magnitude": 1.6,
            "approx_longitude_2000": 0.0,
        },  # ~0° Gemini
    ),
    # ========================================================================
    # OTHER NOTABLE POINTS/BODIES
    # ========================================================================
    "Earth": CelestialObjectInfo(
        name="Earth",
        display_name="Earth",
        object_type=ObjectType.PLANET,
        glyph="♁",
        swiss_ephemeris_id=14,
        category="Planet",
        description="Our home planet. Rarely used in geocentric charts but relevant in heliocentric calculations.",
    ),
}


# ============================================================================
# FIXED STARS REGISTRY
# ============================================================================


@dataclass(frozen=True)
class FixedStarInfo:
    """
    Complete metadata for a fixed star.

    This contains everything needed to look up and interpret a fixed star,
    from its Swiss Ephemeris name to its traditional astrological meanings.
    """

    # Core Identity
    name: str  # Display name (e.g., "Regulus")
    swe_name: str  # Swiss Ephemeris lookup name

    # Visual
    glyph: str = "★"  # Unicode glyph
    glyph_svg_path: str | None = None  # Path to SVG for stars with custom glyphs

    # Classification
    constellation: str = ""  # Traditional constellation (e.g., "Leo")
    bayer: str = ""  # Bayer designation (e.g., "Alpha Leonis")
    tier: int = 2  # 1=Royal, 2=Major, 3=Extended
    is_royal: bool = False  # One of the four Royal Stars of Persia

    # Physical Properties
    magnitude: float = 0.0  # Apparent magnitude (lower = brighter)

    # Astrological Properties
    nature: str = ""  # Planetary nature (e.g., "Mars/Jupiter")
    keywords: tuple[str, ...] = field(default_factory=tuple)
    description: str = ""

    def __str__(self) -> str:
        return f"{self.name} ({self.constellation})"


FIXED_STARS_REGISTRY: dict[str, FixedStarInfo] = {
    # ========================================================================
    # TIER 1: ROYAL STARS (The Four Watchers of Persia)
    # ========================================================================
    "Aldebaran": FixedStarInfo(
        name="Aldebaran",
        swe_name="Aldebaran",
        glyph_svg_path="aldebaran.svg",
        constellation="Taurus",
        bayer="Alpha Tauri",
        tier=1,
        is_royal=True,
        magnitude=0.85,
        nature="Mars",
        keywords=("integrity", "eloquence", "courage", "guardian", "military honors"),
        description="Eye of the Bull. Watcher of the East. Success only through integrity.",
    ),
    "Regulus": FixedStarInfo(
        name="Regulus",
        swe_name="Regulus",
        glyph_svg_path="regulus.svg",
        constellation="Leo",
        bayer="Alpha Leonis",
        tier=1,
        is_royal=True,
        magnitude=1.35,
        nature="Mars/Jupiter",
        keywords=("royalty", "success", "fame", "ambition", "leadership"),
        description="Heart of the Lion. Watcher of the North. Most royal of all stars.",
    ),
    "Antares": FixedStarInfo(
        name="Antares",
        swe_name="Antares",
        constellation="Scorpio",
        bayer="Alpha Scorpii",
        tier=1,
        is_royal=True,
        magnitude=1.09,
        nature="Mars/Jupiter",
        keywords=("intensity", "obsession", "strategy", "self-destruction"),
        description="Heart of the Scorpion. Watcher of the West. Rival of Mars.",
    ),
    "Fomalhaut": FixedStarInfo(
        name="Fomalhaut",
        swe_name="Fomalhaut",
        constellation="Piscis Austrinus",
        bayer="Alpha Piscis Austrini",
        tier=1,
        is_royal=True,
        magnitude=1.16,
        nature="Venus/Mercury",
        keywords=("idealism", "dreams", "magic", "immortality through art"),
        description="Mouth of the Fish. Watcher of the South. Most mystical Royal Star.",
    ),
    # ========================================================================
    # TIER 2: MAJOR STARS
    # ========================================================================
    "Algol": FixedStarInfo(
        name="Algol",
        swe_name="Algol",
        glyph_svg_path="algol.svg",
        constellation="Perseus",
        bayer="Beta Persei",
        tier=2,
        magnitude=2.12,
        nature="Saturn/Jupiter",
        keywords=("intensity", "transformation", "female power", "losing one's head"),
        description="The Demon Star. Medusa's head. Raw transformative power.",
    ),
    "Sirius": FixedStarInfo(
        name="Sirius",
        swe_name="Sirius",
        glyph_svg_path="sirius.svg",
        constellation="Canis Major",
        bayer="Alpha Canis Majoris",
        tier=2,
        magnitude=-1.46,
        nature="Jupiter/Mars",
        keywords=("brilliance", "ambition", "fame", "devotion", "burning"),
        description="The Dog Star. Brightest star in the sky. Great honor but danger of burnout.",
    ),
    "Spica": FixedStarInfo(
        name="Spica",
        swe_name="Spica",
        constellation="Virgo",
        bayer="Alpha Virginis",
        tier=2,
        magnitude=0.97,
        nature="Venus/Mars",
        keywords=("brilliance", "talent", "gifts", "skill", "potential"),
        description="Ear of Wheat. One of the most fortunate stars. Great talent.",
    ),
    "Arcturus": FixedStarInfo(
        name="Arcturus",
        swe_name="Arcturus",
        constellation="Bootes",
        bayer="Alpha Bootis",
        tier=2,
        magnitude=-0.05,
        nature="Mars/Jupiter",
        keywords=("pathfinding", "pioneering", "different path", "prosperity"),
        description="Bear Watcher. Success through a different approach.",
    ),
    "Vega": FixedStarInfo(
        name="Vega",
        swe_name="Vega",
        constellation="Lyra",
        bayer="Alpha Lyrae",
        tier=2,
        magnitude=0.03,
        nature="Venus/Mercury",
        keywords=("charisma", "artistic talent", "magic", "fleeting success"),
        description="Falling Eagle. Lyre of Orpheus. Magical and artistic gifts.",
    ),
    "Capella": FixedStarInfo(
        name="Capella",
        swe_name="Capella",
        glyph_svg_path="capella.svg",
        constellation="Auriga",
        bayer="Alpha Aurigae",
        tier=2,
        magnitude=0.08,
        nature="Mars/Mercury",
        keywords=("curiosity", "learning", "civic honors", "wealth", "independence"),
        description="Little She-Goat. Civic and military honors.",
    ),
    "Rigel": FixedStarInfo(
        name="Rigel",
        swe_name="Rigel",
        constellation="Orion",
        bayer="Beta Orionis",
        tier=2,
        magnitude=0.13,
        nature="Jupiter/Saturn",
        keywords=("education", "teaching", "benevolence", "lasting fame"),
        description="Left Foot of Orion. Good fortune and teaching ability.",
    ),
    "Betelgeuse": FixedStarInfo(
        name="Betelgeuse",
        swe_name="Betelgeuse",
        constellation="Orion",
        bayer="Alpha Orionis",
        tier=2,
        magnitude=0.42,
        nature="Mars/Mercury",
        keywords=("success", "fame", "martial honors", "acute mind"),
        description="Armpit of the Giant. Everlasting fame and military success.",
    ),
    "Procyon": FixedStarInfo(
        name="Procyon",
        swe_name="Procyon",
        glyph_svg_path="procyon.svg",
        constellation="Canis Minor",
        bayer="Alpha Canis Minoris",
        tier=2,
        magnitude=0.34,
        nature="Mercury/Mars",
        keywords=("quick success", "activity", "sudden rise", "sudden fall"),
        description="Before the Dog. Quick rise to prominence, danger of quick fall.",
    ),
    "Pollux": FixedStarInfo(
        name="Pollux",
        swe_name="Pollux",
        constellation="Gemini",
        bayer="Beta Geminorum",
        tier=2,
        magnitude=1.14,
        nature="Mars",
        keywords=("courage", "athletics", "cruelty", "craftiness"),
        description="The Immortal Twin. Athletic ability but potential for cunning.",
    ),
    # ========================================================================
    # TIER 3: EXTENDED STARS
    # ========================================================================
    "Castor": FixedStarInfo(
        name="Castor",
        swe_name="Castor",
        constellation="Gemini",
        bayer="Alpha Geminorum",
        tier=3,
        magnitude=1.58,
        nature="Mercury",
        keywords=("intellect", "writing", "sudden fame", "sudden loss"),
        description="The Mortal Twin. Intellectual gifts but instability.",
    ),
    "Deneb": FixedStarInfo(
        name="Deneb",
        swe_name="Deneb",
        constellation="Cygnus",
        bayer="Alpha Cygni",
        tier=3,
        magnitude=1.25,
        nature="Venus/Mercury",
        keywords=("idealism", "intelligence", "artistic talent", "psychic ability"),
        description="Tail of the Swan. Artistic and intellectual gifts.",
    ),
    "Altair": FixedStarInfo(
        name="Altair",
        swe_name="Altair",
        constellation="Aquila",
        bayer="Alpha Aquilae",
        tier=3,
        magnitude=0.77,
        nature="Mars/Jupiter",
        keywords=("boldness", "ambition", "sudden wealth", "confidence"),
        description="Flying Eagle. Bold action brings success.",
    ),
    "Canopus": FixedStarInfo(
        name="Canopus",
        swe_name="Canopus",
        constellation="Carina",
        bayer="Alpha Carinae",
        tier=3,
        magnitude=-0.74,
        nature="Saturn/Jupiter",
        keywords=("voyages", "navigation", "education", "changing evil to good"),
        description="Second brightest star. Travel and turning bad situations around.",
    ),
    "Polaris": FixedStarInfo(
        name="Polaris",
        swe_name="Polaris",
        constellation="Ursa Minor",
        bayer="Alpha Ursae Minoris",
        tier=3,
        magnitude=1.98,
        nature="Saturn/Venus",
        keywords=("direction", "guidance", "sickness", "spiritual focus"),
        description="North Star. Spiritual guidance but chronic troubles.",
    ),
    "Achernar": FixedStarInfo(
        name="Achernar",
        swe_name="Achernar",
        constellation="Eridanus",
        bayer="Alpha Eridani",
        tier=3,
        magnitude=0.46,
        nature="Jupiter",
        keywords=("success", "happiness", "high office"),
        description="End of the River. Royal and ecclesiastical preferment.",
    ),
    "Hamal": FixedStarInfo(
        name="Hamal",
        swe_name="Hamal",
        constellation="Aries",
        bayer="Alpha Arietis",
        tier=3,
        magnitude=2.00,
        nature="Mars/Saturn",
        keywords=("independence", "cruelty", "headstrong"),
        description="Head of the Ram. Independent but potentially violent.",
    ),
    "Alkaid": FixedStarInfo(
        name="Alkaid",
        swe_name="Alkaid",
        glyph_svg_path="alkaid.svg",
        constellation="Ursa Major",
        bayer="Eta Ursae Majoris",
        tier=3,
        magnitude=1.86,
        nature="Mars",
        keywords=("mourning", "death", "danger", "leadership"),
        description="End of Big Dipper's handle. Danger but also leadership.",
    ),
    "Vindemiatrix": FixedStarInfo(
        name="Vindemiatrix",
        swe_name="Vindemiatrix",
        constellation="Virgo",
        bayer="Epsilon Virginis",
        tier=3,
        magnitude=2.83,
        nature="Saturn/Mercury",
        keywords=("widowhood", "falsity", "disgrace", "harvest"),
        description="Grape Gatherer. Difficult partnerships.",
    ),
    "Zubeneschamali": FixedStarInfo(
        name="Zubeneschamali",
        swe_name="Zuben Eschamali",
        constellation="Libra",
        bayer="Beta Librae",
        tier=3,
        magnitude=2.61,
        nature="Jupiter/Mercury",
        keywords=("good fortune", "high ambition", "honor", "riches"),
        description="Northern Claw. One of the most fortunate stars.",
    ),
    "Zubenelgenubi": FixedStarInfo(
        name="Zubenelgenubi",
        swe_name="Zuben Elgenubi",
        constellation="Libra",
        bayer="Alpha Librae",
        tier=3,
        magnitude=2.75,
        nature="Saturn/Mars",
        keywords=("negative", "malevolent", "social unrest", "ill health"),
        description="Southern Claw. Difficulties and potential for social problems.",
    ),
    "Alcyone": FixedStarInfo(
        name="Alcyone",
        swe_name="Alcyone",
        glyph_svg_path="alcyone.svg",
        constellation="Taurus",
        bayer="Eta Tauri",
        tier=2,
        magnitude=2.87,
        nature="Moon/Mars",
        keywords=("ambition", "eminence", "sorrow", "blindness", "the weeping sisters"),
        description="Brightest star of the Pleiades (Seven Sisters). Ambition but also loss.",
    ),
}


# ============================================================================
# FIXED STARS HELPER FUNCTIONS
# ============================================================================


def get_fixed_star_info(name: str) -> FixedStarInfo | None:
    """
    Get fixed star info by name.

    Args:
        name: The name of the star (e.g., "Regulus", "Algol")

    Returns:
        FixedStarInfo if found, None otherwise
    """
    return FIXED_STARS_REGISTRY.get(name)


def get_royal_stars() -> list[FixedStarInfo]:
    """
    Get the four Royal Stars of Persia.

    Returns:
        List of the four royal stars (Aldebaran, Regulus, Antares, Fomalhaut)
    """
    return [star for star in FIXED_STARS_REGISTRY.values() if star.is_royal]


def get_stars_by_tier(tier: int) -> list[FixedStarInfo]:
    """
    Get all fixed stars of a specific tier.

    Args:
        tier: The tier level (1=Royal, 2=Major, 3=Extended)

    Returns:
        List of FixedStarInfo matching the tier
    """
    return [star for star in FIXED_STARS_REGISTRY.values() if star.tier == tier]


def get_all_fixed_stars() -> list[FixedStarInfo]:
    """
    Get all fixed stars in the registry.

    Returns:
        List of all FixedStarInfo objects
    """
    return list(FIXED_STARS_REGISTRY.values())


def search_fixed_stars(query: str) -> list[FixedStarInfo]:
    """
    Search for fixed stars by name, constellation, or keywords.

    Args:
        query: Search string (case-insensitive)

    Returns:
        List of matching FixedStarInfo objects
    """
    query_lower = query.lower()
    results = []

    for star in FIXED_STARS_REGISTRY.values():
        if (
            query_lower in star.name.lower()
            or query_lower in star.constellation.lower()
            or query_lower in star.description.lower()
            or any(query_lower in kw.lower() for kw in star.keywords)
        ):
            results.append(star)

    return results


# ============================================================================
# REGISTRY HELPER FUNCTIONS
# ============================================================================


def get_object_info(name: str) -> CelestialObjectInfo | None:
    """
    Get celestial object info by name.

    Args:
        name: The technical name of the object (e.g., "Mean Apogee", "Sun")

    Returns:
        CelestialObjectInfo if found, None otherwise
    """
    return CELESTIAL_REGISTRY.get(name)


def get_by_alias(alias: str) -> CelestialObjectInfo | None:
    """
    Get celestial object info by any of its aliases.

    Args:
        alias: An alias for the object (e.g., "Lilith", "BML", "North Node")

    Returns:
        CelestialObjectInfo if found, None otherwise
    """
    alias_lower = alias.lower()

    for obj_info in CELESTIAL_REGISTRY.values():
        # Check if alias matches any of the object's aliases
        if any(a.lower() == alias_lower for a in obj_info.aliases):
            return obj_info
        # Also check display name
        if obj_info.display_name.lower() == alias_lower:
            return obj_info

    return None


def get_all_by_type(object_type: ObjectType) -> list[CelestialObjectInfo]:
    """
    Get all celestial objects of a specific type.

    Args:
        object_type: The ObjectType to filter by

    Returns:
        List of CelestialObjectInfo matching the type
    """
    return [
        obj_info
        for obj_info in CELESTIAL_REGISTRY.values()
        if obj_info.object_type == object_type
    ]


def get_all_by_category(category: str) -> list[CelestialObjectInfo]:
    """
    Get all celestial objects in a specific category.

    Args:
        category: The category to filter by (e.g., "Centaur", "Fixed Star")

    Returns:
        List of CelestialObjectInfo matching the category
    """
    return [
        obj_info
        for obj_info in CELESTIAL_REGISTRY.values()
        if obj_info.category == category
    ]


def search_objects(query: str) -> list[CelestialObjectInfo]:
    """
    Search for objects by name, display name, alias, or description.

    Args:
        query: Search string (case-insensitive)

    Returns:
        List of matching CelestialObjectInfo objects
    """
    query_lower = query.lower()
    results = []

    for obj_info in CELESTIAL_REGISTRY.values():
        # Check name, display name
        if (
            query_lower in obj_info.name.lower()
            or query_lower in obj_info.display_name.lower()
        ):
            results.append(obj_info)
            continue

        # Check aliases
        if any(query_lower in alias.lower() for alias in obj_info.aliases):
            results.append(obj_info)
            continue

        # Check description
        if query_lower in obj_info.description.lower():
            results.append(obj_info)

    return results


# ============================================================================
# ASPECT REGISTRY
# ============================================================================


@dataclass(frozen=True)
class AspectInfo:
    """
    Complete metadata for an astrological aspect.

    This represents everything we know about an aspect - from its technical
    name and exact angle to its glyph, color, and visualization metadata.
    """

    # Core Identity
    name: str  # Primary canonical name (e.g., "Conjunction", "Trine")
    angle: float  # Exact angle in degrees (0, 60, 90, 120, 180, etc.)

    # Classification
    category: str  # "Major", "Minor", "Harmonic"
    family: str | None = None  # "Ptolemaic", "Quintile Series", "Septile Series", etc.

    # Visual Representation
    glyph: str = ""  # Unicode astrological symbol (e.g., "☌", "□", "△")
    color: str = "#CCCCCC"  # Default hex color for visualization

    # Default Orb Settings
    default_orb: float = 2.0  # Default orb allowance in degrees

    # Alternative Names & Documentation
    aliases: list[str] = field(
        default_factory=list
    )  # Alternative names (e.g., ["Inconjunct"] for Quincunx)
    description: str = ""  # Human-readable explanation

    # Visualization Settings (Optional/Advanced)
    metadata: dict[str, Any] = field(
        default_factory=dict
    )  # Extensible for line_width, dash_pattern, opacity, etc.

    def __str__(self) -> str:
        return f"{self.name} ({self.angle}°)"


ASPECT_REGISTRY: dict[str, AspectInfo] = {
    # ========================================================================
    # MAJOR ASPECTS (Ptolemaic)
    # ========================================================================
    "Conjunction": AspectInfo(
        name="Conjunction",
        angle=0.0,
        category="Major",
        family="Ptolemaic",
        glyph="☌",
        color="#34495E",
        default_orb=8.0,
        aliases=["Conjunct"],  # Legacy compatibility
        description="Two planets in the same zodiacal position, blending and merging their energies.",
        metadata={"line_width": 2.0, "dash_pattern": "1,0", "opacity": 0.8},
    ),
    "Sextile": AspectInfo(
        name="Sextile",
        angle=60.0,
        category="Major",
        family="Ptolemaic",
        glyph="⚹",
        color="#27AE60",
        default_orb=6.0,
        description="A harmonious 60° aspect indicating opportunity, cooperation, and ease.",
        metadata={"line_width": 1.5, "dash_pattern": "6,2", "opacity": 0.7},
    ),
    "Square": AspectInfo(
        name="Square",
        angle=90.0,
        category="Major",
        family="Ptolemaic",
        glyph="□",
        color="#F39C12",
        default_orb=8.0,
        description="A challenging 90° aspect creating tension, friction, and motivation to act.",
        metadata={"line_width": 1.5, "dash_pattern": "4,2", "opacity": 0.8},
    ),
    "Trine": AspectInfo(
        name="Trine",
        angle=120.0,
        category="Major",
        family="Ptolemaic",
        glyph="△",
        color="#3498DB",
        default_orb=8.0,
        description="A flowing 120° aspect indicating harmony, talent, and natural ability.",
        metadata={"line_width": 2.0, "dash_pattern": "1,0", "opacity": 0.8},
    ),
    "Opposition": AspectInfo(
        name="Opposition",
        angle=180.0,
        category="Major",
        family="Ptolemaic",
        glyph="☍",
        color="#E74C3C",
        default_orb=8.0,
        description="A polarizing 180° aspect representing awareness through contrast and balance.",
        metadata={"line_width": 2.0, "dash_pattern": "1,0", "opacity": 0.8},
    ),
    # ========================================================================
    # MINOR ASPECTS
    # ========================================================================
    "Semisextile": AspectInfo(
        name="Semisextile",
        angle=30.0,
        category="Minor",
        glyph="⚺",
        color="#95A5A6",
        default_orb=3.0,
        aliases=["Semi-Sextile"],  # Hyphenated variant
        description="A subtle 30° aspect indicating slight friction requiring minor adjustments.",
        metadata={"line_width": 0.8, "dash_pattern": "3,3", "opacity": 0.6},
    ),
    "Semisquare": AspectInfo(
        name="Semisquare",
        angle=45.0,
        category="Minor",
        glyph="∠",
        color="#E67E22",
        default_orb=3.0,
        aliases=["Semi-Square", "Octile"],
        description="A mildly challenging 45° aspect creating irritation and the need for action.",
        metadata={"line_width": 0.8, "dash_pattern": "3,3", "opacity": 0.6},
    ),
    "Sesquisquare": AspectInfo(
        name="Sesquisquare",
        angle=135.0,
        category="Minor",
        glyph="⚼",
        color="#D68910",
        default_orb=3.0,
        aliases=["Sesquiquadrate", "Trioctile"],
        description="A moderately challenging 135° aspect creating tension and restlessness.",
        metadata={"line_width": 0.8, "dash_pattern": "3,3", "opacity": 0.6},
    ),
    "Quincunx": AspectInfo(
        name="Quincunx",
        angle=150.0,
        category="Minor",
        glyph="⚻",
        color="#9B59B6",
        default_orb=3.0,
        aliases=["Inconjunct"],
        description="A complex 150° aspect requiring adjustment, adaptation, and integration.",
        metadata={"line_width": 1.0, "dash_pattern": "2,2", "opacity": 0.7},
    ),
    # ========================================================================
    # QUINTILE FAMILY (Harmonic 5)
    # ========================================================================
    "Quintile": AspectInfo(
        name="Quintile",
        angle=72.0,
        category="Harmonic",
        family="Quintile Series",
        glyph="Q",
        color="#16A085",
        default_orb=1.0,
        description="A creative 72° aspect (H5) indicating talent, skill, and unique gifts.",
        metadata={"line_width": 0.8, "dash_pattern": "2,4", "opacity": 0.5},
    ),
    "Biquintile": AspectInfo(
        name="Biquintile",
        angle=144.0,
        category="Harmonic",
        family="Quintile Series",
        glyph="bQ",
        color="#138D75",
        default_orb=1.0,
        description="A creative 144° aspect (H5) emphasizing artistic expression and innovation.",
        metadata={"line_width": 0.8, "dash_pattern": "2,4", "opacity": 0.5},
    ),
    # ========================================================================
    # SEPTILE FAMILY (Harmonic 7)
    # ========================================================================
    "Septile": AspectInfo(
        name="Septile",
        angle=51.42857,  # 360/7
        category="Harmonic",
        family="Septile Series",
        glyph="S",
        color="#8E44AD",
        default_orb=1.0,
        description="A mystical 51.43° aspect (H7) indicating fate, destiny, and spiritual purpose.",
        metadata={"line_width": 0.6, "dash_pattern": "1,5", "opacity": 0.4},
    ),
    "Biseptile": AspectInfo(
        name="Biseptile",
        angle=102.85714,  # 360*2/7
        category="Harmonic",
        family="Septile Series",
        glyph="bS",
        color="#7D3C98",
        default_orb=1.0,
        description="A mystical 102.86° aspect (H7) emphasizing karmic patterns and destiny.",
        metadata={"line_width": 0.6, "dash_pattern": "1,5", "opacity": 0.4},
    ),
    "Triseptile": AspectInfo(
        name="Triseptile",
        angle=154.28571,  # 360*3/7
        category="Harmonic",
        family="Septile Series",
        glyph="tS",
        color="#6C3483",
        default_orb=1.0,
        description="A mystical 154.29° aspect (H7) indicating fated encounters and spiritual gifts.",
        metadata={"line_width": 0.6, "dash_pattern": "1,5", "opacity": 0.4},
    ),
    # ========================================================================
    # NOVILE FAMILY (Harmonic 9)
    # ========================================================================
    "Novile": AspectInfo(
        name="Novile",
        angle=40.0,
        category="Harmonic",
        family="Novile Series",
        glyph="N",
        color="#2980B9",
        default_orb=1.0,
        description="A spiritual 40° aspect (H9) indicating completion, perfection, and higher wisdom.",
        metadata={"line_width": 0.6, "dash_pattern": "1,5", "opacity": 0.4},
    ),
    "Binovile": AspectInfo(
        name="Binovile",
        angle=80.0,
        category="Harmonic",
        family="Novile Series",
        glyph="bN",
        color="#21618C",
        default_orb=1.0,
        aliases=["Seminovile"],
        description="A spiritual 80° aspect (H9) emphasizing joy, bliss, and divine connection.",
        metadata={"line_width": 0.6, "dash_pattern": "1,5", "opacity": 0.4},
    ),
    "Quadnovile": AspectInfo(
        name="Quadnovile",
        angle=160.0,
        category="Harmonic",
        family="Novile Series",
        glyph="qN",
        color="#1A5276",
        default_orb=1.0,
        description="A spiritual 160° aspect (H9) indicating spiritual mastery and enlightenment.",
        metadata={"line_width": 0.6, "dash_pattern": "1,5", "opacity": 0.4},
    ),
    # ========================================================================
    # DECLINATION ASPECTS
    # ========================================================================
    "Parallel": AspectInfo(
        name="Parallel",
        angle=0.0,  # Conceptually similar to conjunction
        category="Declination",
        family="Declination",
        glyph="∥",  # U+2225 - Parallel to
        color="#34495E",  # Same as conjunction (blending)
        default_orb=1.0,
        description="Two planets at the same declination (both north or both south of celestial equator), interpreted like a conjunction.",
        metadata={"line_width": 1.5, "dash_pattern": "3,1", "opacity": 0.7},
    ),
    "Contraparallel": AspectInfo(
        name="Contraparallel",
        angle=180.0,  # Conceptually similar to opposition
        category="Declination",
        family="Declination",
        glyph="⋕",  # U+22D5 - Equal and parallel to
        color="#E74C3C",  # Same as opposition (polarity)
        default_orb=1.0,
        aliases=["Contra-parallel"],
        description="Two planets at equal declination magnitude but opposite hemispheres, interpreted like an opposition.",
        metadata={"line_width": 1.5, "dash_pattern": "3,1", "opacity": 0.7},
    ),
}


# ============================================================================
# ASPECT REGISTRY — DERIVED VIEWS
# ============================================================================
#
# Declination aspects live in ASPECT_REGISTRY alongside the ecliptic ones so that
# looking an aspect up *by name* stays uniform: a caller holding an Aspect with
# `aspect_name="Parallel"` just wants its glyph and should not have to know which
# family it belongs to (see `get_aspect_display`, and OrbEngine's default map).
#
# But the two families are not interchangeable, because declination aspects do not
# have a meaningful ecliptic angle — Parallel is recorded at 0° and Contraparallel
# at 180° purely by analogy with Conjunction and Opposition. That means **angle is
# not a unique key across the whole registry**: an angle-keyed map built over all
# of it silently lets Parallel overwrite Conjunction (∥ replacing ☌).
#
# So anything keying on *angle* — or reasoning about ecliptic geometry at all —
# should build over ECLIPTIC_ASPECT_REGISTRY, where angle is unique.

ECLIPTIC_ASPECT_REGISTRY: dict[str, AspectInfo] = {
    name: info
    for name, info in ASPECT_REGISTRY.items()
    if info.category != "Declination"
}

DECLINATION_ASPECT_REGISTRY: dict[str, AspectInfo] = {
    name: info
    for name, info in ASPECT_REGISTRY.items()
    if info.category == "Declination"
}


# ============================================================================
# ASPECT REGISTRY HELPER FUNCTIONS
# ============================================================================


def get_aspect_info(name: str) -> AspectInfo | None:
    """
    Get aspect information by name.

    Args:
        name: The aspect name to look up (e.g., "Conjunction", "Trine")

    Returns:
        AspectInfo object if found, None otherwise
    """
    return ASPECT_REGISTRY.get(name)


def get_aspect_by_alias(alias: str) -> AspectInfo | None:
    """
    Get aspect information by alias.

    Args:
        alias: An alternative name for the aspect (e.g., "Conjunct", "Inconjunct")

    Returns:
        AspectInfo object if found, None otherwise
    """
    alias_lower = alias.lower()
    for aspect_info in ASPECT_REGISTRY.values():
        if alias_lower in [a.lower() for a in aspect_info.aliases]:
            return aspect_info
    return None


def get_aspects_by_category(category: str) -> list[AspectInfo]:
    """
    Get all aspects in a specific category.

    Args:
        category: The category to filter by ("Major", "Minor", "Harmonic")

    Returns:
        List of AspectInfo matching the category
    """
    return [
        aspect_info
        for aspect_info in ASPECT_REGISTRY.values()
        if aspect_info.category == category
    ]


def get_aspects_by_family(family: str) -> list[AspectInfo]:
    """
    Get all aspects in a specific family.

    Args:
        family: The family to filter by (e.g., "Ptolemaic", "Quintile Series", "Septile Series")

    Returns:
        List of AspectInfo matching the family
    """
    return [
        aspect_info
        for aspect_info in ASPECT_REGISTRY.values()
        if aspect_info.family == family
    ]


def search_aspects(query: str) -> list[AspectInfo]:
    """
    Search for aspects by name, alias, or description.

    Args:
        query: Search string (case-insensitive)

    Returns:
        List of matching AspectInfo objects
    """
    query_lower = query.lower()
    results = []

    for aspect_info in ASPECT_REGISTRY.values():
        # Check name
        if query_lower in aspect_info.name.lower():
            results.append(aspect_info)
            continue

        # Check aliases
        if any(query_lower in alias.lower() for alias in aspect_info.aliases):
            results.append(aspect_info)
            continue

        # Check description
        if query_lower in aspect_info.description.lower():
            results.append(aspect_info)

    return results
