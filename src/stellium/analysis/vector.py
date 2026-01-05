"""Generate embedding vectors to represent individual charts for fast comparison."""

import numpy as np

from stellium.core.models import CalculatedChart
from stellium.core.registry import get_object_info

# Define the standard bodies to guarantee vector alignment
VECTOR_BODIES = [
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
    "True Node",
]


class ChartVectorizer:
    """Transforms a stellium CalculatedChart into a dense vector embedding."""

    def __init__(self, include_speed: bool = True, include_houses: bool = True):
        self.include_speed = include_speed
        self.include_houses = include_houses

        # Calculate expected dimension (sanity check)
        self.dim = len(VECTOR_BODIES) * (3 if include_speed else 2) + 4  # 4 angles
        if include_houses:
            self.dim += 24  # sin, cos of position = * 2

    def encode(self, chart: CalculatedChart) -> np.ndarray:
        features = []

        # Body encoding
        for name in VECTOR_BODIES:
            obj = chart.get_object(name)
            # Cyclic encoding (0..1 range not needed, -1..1 is better for ML)
            rads = np.deg2rad(obj.longitude)
            features.extend([np.sin(rads), np.cos(rads)])

            if self.include_speed:
                avg_daily_motion = get_object_info(name).avg_daily_motion
                norm_speed = obj.speed / avg_daily_motion
                features.append(norm_speed)

        # Angles (AC, MC) - Important for house matching
        for angle in ["AC", "MC"]:
            obj = chart.get_object(angle)
            rads = np.deg2rad(obj.longitude)
            features.extend([np.sin(rads), np.cos(rads)])

        # House cusps (optional)
        if self.include_houses:
            cusps = chart.get_houses().cusps
            for cusp in cusps:
                rads = np.deg2rad(cusp)
                features.extend([np.sin(rads), np.cos(rads)])

        return np.array(features, dtype=np.float32)

    def similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """Cosine similarity between two charts."""
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        return np.dot(vec_a, vec_b) / (norm_a * norm_b)
