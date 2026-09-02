import math


def clamp(val: float, min_val: float, max_val: float) -> float:
    """Clamps scalar float value strictly between min_val and max_val with zero Any return type."""
    if val < min_val:
        return min_val
    if val > max_val:
        return max_val
    return val


def round_to(val: float, decimals: int = 4) -> float:
    """Rounds scalar float value to specified decimal precision."""
    return round(val, decimals)


def lerp(a: float, b: float, t: float) -> float:
    """Performs linear interpolation between a and b by factor t clamped in [0.0, 1.0]."""
    t_clamped = clamp(t, 0.0, 1.0)
    return a + (b - a) * t_clamped


def cbrt(val: float) -> float:
    """Computes real cube root handling negative floats cleanly without complex numbers."""
    if val < 0.0:
        return -math.pow(-val, 1.0 / 3.0)
    return math.pow(val, 1.0 / 3.0)
