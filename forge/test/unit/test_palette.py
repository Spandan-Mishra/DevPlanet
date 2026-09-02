import pytest

from src.engine.palette import OklabColorConverter


def test_hex_to_srgb_parsing() -> None:
    """Verifies standard and short hex string parsing to normalized sRGB."""
    converter = OklabColorConverter()

    # White
    assert converter.hex_to_srgb("#ffffff") == (1.0, 1.0, 1.0)
    # Black
    assert converter.hex_to_srgb("#000000") == (0.0, 0.0, 0.0)
    # Short hex #f00 -> #ff0000
    r, g, b = converter.hex_to_srgb("#f00")
    assert r == pytest.approx(1.0)
    assert g == pytest.approx(0.0)
    assert b == pytest.approx(0.0)
    # Invalid fallback
    assert converter.hex_to_srgb("invalid") == (0.2, 0.2, 0.2)


def test_oklab_roundtrip_color_accuracy() -> None:
    """Verifies that converting Hex -> Oklab -> Hex preserves color within 1-byte delta."""
    converter = OklabColorConverter()

    test_colors = [
        "#00add8",  # Go Cyan
        "#3572a5",  # Python Blue
        "#dea584",  # Rust Terracotta
        "#f34b7d",  # C++ Red
        "#3178c6",  # TypeScript Blue
        "#ffffff",  # Pure White
        "#000000",  # Pure Black
        "#808080",  # Mid Gray
    ]

    for orig_hex in test_colors:
        L, a, b = converter.hex_to_oklab(orig_hex)
        res_hex = converter.oklab_to_hex(L, a, b)

        orig_r, orig_g, orig_b = converter.hex_to_srgb(orig_hex)
        res_r, res_g, res_b = converter.hex_to_srgb(res_hex)

        # Difference in any RGB channel must be less than 2/255 (quantization boundary)
        assert abs(orig_r - res_r) <= (2.0 / 255.0)
        assert abs(orig_g - res_g) <= (2.0 / 255.0)
        assert abs(orig_b - res_b) <= (2.0 / 255.0)


def test_oklab_lerp_monotonic_lightness() -> None:
    """Verifies that lerping between black and white in Oklab produces strictly monotonic lightness."""
    converter = OklabColorConverter()

    black_oklab = converter.hex_to_oklab("#000000")
    white_oklab = converter.hex_to_oklab("#ffffff")

    prev_L = -1.0
    for step in range(11):
        t = step / 10.0
        lerped = converter.lerp_oklab(black_oklab, white_oklab, t)
        assert lerped[0] > prev_L
        prev_L = lerped[0]

    assert prev_L == pytest.approx(white_oklab[0], abs=1e-4)
