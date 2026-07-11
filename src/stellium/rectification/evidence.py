"""Event- and temperament-character sect signals (a priori keyword tallies).

Doctrine (all day-positive: >0 leans day, <0 leans night):

* **malefic contrary to sect** — the out-of-sect malefic is the sharper destroyer:
  Mars-flavoured hardship → day, Saturn-flavoured → night. This is the one signal
  that survived every confound in the empirical study (partial corr +0.35).
* **benefic of sect** — the in-sect benefic is the stronger helper:
  Jupiter-flavoured fortune → day, Venus-flavoured → night. (Null on its own.)
* **temperament** (soft, ~null on strangers — informative only with real first-hand
  knowledge): malefic-of-sect on character (Mars-hot → day, Saturn-cold → night)
  and sect-light (Solar → day, Lunar → night).

Keyword lists are traditional significations set a priori, not tuned to any corpus.
Operates on :class:`~stellium.data.LifeEvent` / :class:`~stellium.data.Temperament`.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from stellium.rectification._data import SIGNIFICANCE_WEIGHT

# ── event character ───────────────────────────────────────────────────────────

HARDSHIP_TYPES = {
    "health_crisis",
    "accident",
    "financial_loss",
    "bereavement_parent",
    "bereavement_other",
    "legal",
}
FORTUNE_TYPES = {
    "windfall",
    "recognition",
    "relationship",
    "career",
    "childbirth",
    "education",
    "spiritual",
}

MARS_WORDS = (
    "accident",
    "crash",
    "collision",
    "shot",
    "gunshot",
    "gun ",
    "stabbed",
    "knife",
    "killed",
    "murder",
    "assassin",
    "war",
    "battle",
    "combat",
    "fight",
    "assault",
    "violence",
    "violent",
    "wound",
    "injury",
    "injured",
    "surgery",
    "operation",
    "amputat",
    "fire",
    "burned",
    "burns",
    "explosion",
    "blood",
    "acute",
    "overdose",
    "beaten",
    "shooting",
    "duel",
)
SATURN_WORDS = (
    "illness",
    "disease",
    "cancer",
    "tuberculosis",
    "chronic",
    "ill health",
    "prison",
    "jail",
    "imprison",
    "incarcerat",
    "bankruptcy",
    "bankrupt",
    "ruin",
    "poverty",
    "debt",
    "exile",
    "banish",
    "decline",
    "paralysis",
    "stroke",
    "depression",
    "melancholy",
    "old age",
    "natural causes",
    "starv",
    "foreclosure",
    "lingering",
    "confined",
    "arthritis",
    "polio",
    "dementia",
    "alzheimer",
)
_HARDSHIP_TYPE_LEAN = {
    "accident": "mars",
    "financial_loss": "saturn",
    "bereavement_parent": "saturn",
    "bereavement_other": "saturn",
    "legal": "saturn",
    "health_crisis": None,
}

JUPITER_WORDS = (
    "award",
    "prize",
    "nobel",
    "medal",
    "honor",
    "honour",
    "knighthood",
    "title",
    "throne",
    "crown",
    "coronation",
    "elected",
    "president",
    "minister",
    "governor",
    "professor",
    "doctorate",
    "degree",
    "graduat",
    "published",
    "book",
    "bestseller",
    "founded",
    "company",
    "fortune",
    "wealth",
    "millionaire",
    "billionaire",
    "championship",
    "champion",
    "gold medal",
    "victory",
    "world cup",
    "religion",
    "ordained",
    "guru",
    "philosophy",
    "discovery",
    "patent",
    "empire",
    "abroad",
    "pilgrimage",
    "knighted",
    "peerage",
    "record deal",
)
VENUS_WORDS = (
    "married",
    "marriage",
    "wed",
    "engaged",
    "engagement",
    "romance",
    "love affair",
    "affair",
    "mistress",
    "lover",
    "art",
    "painting",
    "exhibition",
    "gallery",
    "sculpture",
    "music",
    "album",
    "song",
    "sang",
    "opera",
    "ballet",
    "dance",
    "actress",
    "beauty",
    "fashion",
    "muse",
    "portrait",
    "aesthetic",
    "debut",
    "modelling",
    "model ",
)
_BENEFIC_TYPE_LEAN = {
    "relationship": "venus",
    "windfall": "jupiter",
    "recognition": "jupiter",
    "career": "jupiter",
    "childbirth": "jupiter",
    "education": "jupiter",
    "spiritual": "jupiter",
}


def _flavor(text: str, etype: str, hot: tuple, cold: tuple, lean: dict) -> str | None:
    t = text.lower()
    is_hot = any(w in t for w in hot)
    is_cold = any(w in t for w in cold)
    if is_hot and not is_cold:
        return "hot"
    if is_cold and not is_hot:
        return "cold"
    if is_hot and is_cold:
        return None  # mixed — abstain
    v = lean.get(etype)
    if v is None:
        return None
    return {"mars": "hot", "jupiter": "hot", "saturn": "cold", "venus": "cold"}.get(v)


def malefic_tally(events: Iterable) -> tuple[float, float]:
    """(Mars-flavoured, Saturn-flavoured) weight over hardship events."""
    mars = saturn = 0.0
    for e in events:
        if e.type not in HARDSHIP_TYPES:
            continue
        flav = _flavor(
            e.description, e.type, MARS_WORDS, SATURN_WORDS, _HARDSHIP_TYPE_LEAN
        )
        w = SIGNIFICANCE_WEIGHT.get(e.significance, 0.5)
        if flav == "hot":
            mars += w
        elif flav == "cold":
            saturn += w
    return mars, saturn


def benefic_tally(events: Iterable) -> tuple[float, float]:
    """(Jupiter-flavoured, Venus-flavoured) weight over fortune events."""
    jup = ven = 0.0
    for e in events:
        if e.type not in FORTUNE_TYPES:
            continue
        flav = _flavor(
            e.description, e.type, JUPITER_WORDS, VENUS_WORDS, _BENEFIC_TYPE_LEAN
        )
        w = SIGNIFICANCE_WEIGHT.get(e.significance, 0.5)
        if flav == "hot":
            jup += w
        elif flav == "cold":
            ven += w
    return jup, ven


def malefic_event_score(events: Iterable) -> float:
    """Day-positive malefic-of-sect score over hardship events (Mars − Saturn)."""
    mars, saturn = malefic_tally(events)
    return mars - saturn


# ── temperament character (soft) ──────────────────────────────────────────────

MARS_TEMPER_WORDS = (
    "aggressive",
    "angry",
    "anger",
    "hot-tempered",
    "hot temper",
    "quick-tempered",
    "temper",
    "irritable",
    "combative",
    "confrontational",
    "belligerent",
    "violent",
    "violence",
    "impulsive",
    "reckless",
    "rash",
    "brash",
    "daring",
    "fearless",
    "competitive",
    "aggression",
    "forceful",
    "fierce",
    "fiery",
    "restless",
    "energetic",
    "volatile",
    "explosive",
    "abrasive",
    "ruthless",
    "domineering",
    "pugnacious",
    "hostile",
    "sharp-tongued",
    "brave",
    "courageous",
    "audacious",
)
SATURN_TEMPER_WORDS = (
    "cold",
    "aloof",
    "detached",
    "disciplined",
    "restrained",
    "reserved",
    "serious",
    "austere",
    "stern",
    "grave",
    "dour",
    "rigid",
    "controlled",
    "cautious",
    "guarded",
    "methodical",
    "patient",
    "frugal",
    "miserly",
    "melancholic",
    "melancholy",
    "pessimistic",
    "fearful",
    "anxious",
    "inhibited",
    "withdrawn",
    "solitary",
    "stoic",
    "calculating",
    "hard-working",
    "industrious",
    "persevering",
    "duty",
    "dutiful",
    "responsible",
    "rigorous",
    "unyielding",
    "brooding",
)
SOLAR_WORDS = (
    "proud",
    "pride",
    "ambitious",
    "ambition",
    "authoritative",
    "authority",
    "dominant",
    "domineering",
    "commanding",
    "willful",
    "strong-willed",
    "confident",
    "self-assured",
    "leader",
    "leadership",
    "ego",
    "bold",
    "assertive",
    "magnanimous",
    "charismatic",
    "driven",
    "forceful",
    "imperious",
    "grandiose",
    "vain",
    "flamboyant",
    "regal",
    "self-confident",
)
LUNAR_WORDS = (
    "private",
    "reserved",
    "receptive",
    "nurturing",
    "caring",
    "moody",
    "sensitive",
    "emotional",
    "adaptable",
    "adaptive",
    "retiring",
    "shy",
    "introverted",
    "gentle",
    "empathetic",
    "empathic",
    "changeable",
    "insecure",
    "withdrawn",
    "melancholic",
    "melancholy",
    "quiet",
    "tender",
    "domestic",
    "vulnerable",
    "fluid",
    "self-effacing",
    "humble",
)


def _temper_text(trait: Any) -> str:
    text: str = (
        trait.trait + " " + " ".join(trait.tags) + " " + trait.evidence
    ).lower()
    return text


def malefic_temperament_score(temperament: Iterable) -> float:
    """Mars-hot − Saturn-cold character (day-positive). Soft — trust real knowledge."""
    mars = saturn = 0.0
    for tr in temperament:
        text = _temper_text(tr)
        mars += sum(w in text for w in MARS_TEMPER_WORDS)
        saturn += sum(w in text for w in SATURN_TEMPER_WORDS)
    return float(mars - saturn)


def sect_light_temperament_score(temperament: Iterable) -> float:
    """Solar − Lunar character (day-positive). Soft — trust real knowledge."""
    solar = lunar = 0.0
    for tr in temperament:
        text = _temper_text(tr)
        solar += sum(w in text for w in SOLAR_WORDS)
        lunar += sum(w in text for w in LUNAR_WORDS)
    return float(solar - lunar)
