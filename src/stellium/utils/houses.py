"""House calculation utilities."""


def find_house_for_longitude(longitude: float, cusps: tuple[float, ...]) -> int:
    """
    Find which house a longitude falls into.

    This function determines which of the 12 houses a given ecliptic longitude
    occupies, based on the house cusp positions. It correctly handles houses
    that wrap around the 360°/0° boundary.

    Args:
        longitude: Ecliptic longitude in degrees (0-360°)
        cusps: Tuple of 12 house cusp longitudes (in degrees)

    Returns:
        House number (1-12)

    Example:
        >>> cusps = (0.0, 30.0, 60.0, 90.0, 120.0, 150.0,
        ...          180.0, 210.0, 240.0, 270.0, 300.0, 330.0)
        >>> find_house_for_longitude(45.0, cusps)
        2
        >>> find_house_for_longitude(355.0, cusps)  # Wraps around
        12

    Note:
        A planet at the exact cusp belongs to the house it's entering,
        not the one it's leaving. The logic uses cusp_start <= longitude < cusp_end.
    """
    for i in range(12):
        cusp_start = cusps[i]
        cusp_end = cusps[(i + 1) % 12]

        # Handle houses that wrap around 360°/0°
        if cusp_start < cusp_end:
            # Normal case: cusp doesn't wrap (e.g., 30° to 60°)
            if cusp_start <= longitude < cusp_end:
                return i + 1
        else:
            # Wraps around 0° (e.g., 350° to 10°)
            if longitude >= cusp_start or longitude < cusp_end:
                return i + 1

    # Fallback (should never happen with valid cusps)
    # If we get here, return house 1 as a safe default
    return 1
