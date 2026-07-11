"""Event-character sect signals: malefic-of-sect + benefic-of-sect.

Doctrine (both directions point the same way — positive = day):
  * malefic out of sect is the sharper destroyer:
      Mars-flavoured hardship  -> day,  Saturn-flavoured -> night
  * benefic in sect is the stronger benefic:
      Jupiter-flavoured fortune -> day, Venus-flavoured  -> night

Keyword lists are a priori (traditional significations), not tuned to the corpus.
The malefic side is imported from ``probe_malefic_sect`` (already validated).
"""

from __future__ import annotations

from probe_malefic_sect import SIGNIFICANCE_WEIGHT
from probe_malefic_sect import tally as malefic_tally

# Growth / good-fortune events inform the benefic-of-sect.
FORTUNE_TYPES = {
    "windfall",
    "recognition",
    "relationship",
    "career",
    "childbirth",
    "education",
    "spiritual",
}

# Jupiter: honour, wealth, expansion, law, religion, wisdom, travel, fame.
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
# Venus: love, marriage, art, beauty, music, pleasure, charm, women.
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
# Per-type fallback lean when no keyword matches.
BENEFIC_TYPE_LEAN = {
    "relationship": "venus",
    "windfall": "jupiter",
    "recognition": "jupiter",
    "career": "jupiter",
    "childbirth": "jupiter",  # children = Jupiter (5th)
    "education": "jupiter",
    "spiritual": "jupiter",
}


def _benefic_flavor(description: str, etype: str) -> str | None:
    text = description.lower()
    jup = any(w in text for w in JUPITER_WORDS)
    ven = any(w in text for w in VENUS_WORDS)
    if jup and not ven:
        return "jupiter"
    if ven and not jup:
        return "venus"
    if jup and ven:
        return None  # mixed — abstain
    return BENEFIC_TYPE_LEAN.get(etype)


def benefic_tally(person) -> tuple[float, float]:
    """(jupiter_score, venus_score) over the person's fortune events."""
    jup = ven = 0.0
    for e in person.events:
        if e.type not in FORTUNE_TYPES:
            continue
        flav = _benefic_flavor(e.description, e.type)
        w = SIGNIFICANCE_WEIGHT.get(e.significance, 0.5)
        if flav == "jupiter":
            jup += w
        elif flav == "venus":
            ven += w
    return jup, ven


def sect_score(person, *, use_malefic: bool = True, use_benefic: bool = True) -> float:
    """Day-positive score. >0 predicts day, <0 predicts night, 0 = undecided."""
    score = 0.0
    if use_malefic:
        mars, saturn = malefic_tally(person)
        score += mars - saturn
    if use_benefic:
        jup, ven = benefic_tally(person)
        score += jup - ven
    return score
