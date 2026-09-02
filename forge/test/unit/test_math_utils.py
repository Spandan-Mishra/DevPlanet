import pytest

from src.core.math_utils import cbrt, clamp, lerp, round_to


def test_clamp() -> None:
    """Verifies strict scalar clamping within bounds."""
    assert clamp(5.0, 0.0, 10.0) == 5.0
    assert clamp(-5.0, 0.0, 10.0) == 0.0
    assert clamp(15.0, 0.0, 10.0) == 10.0
    assert clamp(0.0, 0.0, 0.0) == 0.0


def test_round_to() -> None:
    """Verifies rounding to arbitrary decimal precisions."""
    assert round_to(3.14159265, 2) == 3.14
    assert round_to(3.14159265, 4) == 3.1416
    assert round_to(10.0, 2) == 10.0


def test_lerp() -> None:
    """Verifies linear interpolation and factor clamping."""
    assert lerp(0.0, 10.0, 0.5) == 5.0
    assert lerp(0.0, 10.0, 0.0) == 0.0
    assert lerp(0.0, 10.0, 1.0) == 10.0
    assert lerp(0.0, 10.0, -1.0) == 0.0  # Clamped below
    assert lerp(0.0, 10.0, 2.0) == 10.0  # Clamped above


def test_cbrt() -> None:
    """Verifies cube root for positive, negative, and zero inputs."""
    assert cbrt(8.0) == pytest.approx(2.0)
    assert cbrt(0.0) == pytest.approx(0.0)
    assert cbrt(-8.0) == pytest.approx(-2.0)
    assert cbrt(27.0) == pytest.approx(3.0)
