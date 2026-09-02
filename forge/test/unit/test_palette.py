import pytest

from src.core.seeder import DeterministicSeeder
from src.engine.palette import OklabColorConverter, SurfaceMaterialEngine
from src.models.genome import (
    ElevationRampNode,
    MathematicalProfile,
    SurfaceMaterialGenome,
    TopologyGenome,
)
from src.models.request import LanguageStat, UserPlanetProfileRequest


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


def test_elevation_ramp_generation_with_languages() -> None:
    """Verifies synthesis of a 6-stop monotonic elevation color ramp driven by languages."""
    languages = [
        LanguageStat(name="Rust", color="#dea584", bytes=7000, percentage=70.0),
        LanguageStat(name="Go", color="#00ADD8", bytes=3000, percentage=30.0),
    ]
    math_profile = MathematicalProfile(
        shannon_entropy=0.88,
        diurnal_phase=0.80,  # Day developer
        diurnal_coherence=0.90,
        repo_gini_index=0.45,
        polyglot_diversity=0.42,
    )
    seeder = DeterministicSeeder.from_string("test_dev")

    ramp = SurfaceMaterialEngine.generate_elevation_ramp(
        languages, math_profile, sea_level=0.45, seeder=seeder
    )

    assert len(ramp) == 6
    for node in ramp:
        assert isinstance(node, ElevationRampNode)
        assert 0.0 <= node.elevation <= 1.0
        assert 0.0 <= node.oklab[0] <= 1.0
        assert node.hex.startswith("#") and len(node.hex) == 7
        # Ensure node.oklab matches hex_to_oklab exactly
        expected_oklab = OklabColorConverter.hex_to_oklab(node.hex)
        assert node.oklab == expected_oklab

    # Verify strictly monotonic elevation stops
    elevations = [node.elevation for node in ramp]
    assert elevations == sorted(elevations)
    assert len(elevations) == len(set(elevations))
    assert elevations[0] == 0.00
    assert elevations[-1] == 1.00


def test_elevation_ramp_boundary_sea_levels() -> None:
    """Verifies strictly increasing unique elevation keys at extreme boundary sea levels (0.0 and 1.0)."""
    math_profile = MathematicalProfile(
        shannon_entropy=0.5,
        diurnal_phase=0.5,
        diurnal_coherence=0.5,
        repo_gini_index=0.5,
        polyglot_diversity=0.5,
    )
    seeder = DeterministicSeeder.from_string("boundary_dev")

    for sea_level in [0.0, 1.0]:
        ramp = SurfaceMaterialEngine.generate_elevation_ramp(
            [], math_profile, sea_level=sea_level, seeder=seeder
        )
        assert len(ramp) == 6
        elevations = [node.elevation for node in ramp]
        # Must be strictly increasing without duplicates
        assert elevations == sorted(elevations)
        assert len(elevations) == len(set(elevations))
        assert elevations[0] == 0.0
        assert elevations[-1] == 1.0


def test_elevation_ramp_fallback_no_languages() -> None:
    """Verifies elevation ramp fallback generation when no languages are provided."""
    math_profile = MathematicalProfile(
        shannon_entropy=0.0,
        diurnal_phase=0.15,  # Night owl developer
        diurnal_coherence=0.50,
        repo_gini_index=0.0,
        polyglot_diversity=0.0,
    )
    seeder = DeterministicSeeder.from_string("empty_lang_dev")

    ramp = SurfaceMaterialEngine.generate_elevation_ramp(
        [], math_profile, sea_level=0.50, seeder=seeder
    )

    assert len(ramp) == 6
    assert ramp[0].elevation == 0.0
    assert ramp[-1].elevation == 1.0


def test_synthesize_surface_material_genome() -> None:
    """Verifies full synthesis of SurfaceMaterialGenome coupled with Whittaker climate."""
    req = UserPlanetProfileRequest(
        username="spandev",
        language_summary=[
            LanguageStat(
                name="Python", color="#3572A5", bytes=8000, percentage=80.0
            ),
            LanguageStat(name="Go", color="#00ADD8", bytes=2000, percentage=20.0),
        ],
    )
    math_profile = MathematicalProfile(
        shannon_entropy=0.72,
        diurnal_phase=0.65,
        diurnal_coherence=0.85,
        repo_gini_index=0.35,
        polyglot_diversity=0.32,
    )
    topology = TopologyGenome(
        base_radius=100.0,
        sea_level=0.48,
        max_altitude=25.0,
        octaves=6,
        persistence=0.48,
        lacunarity=2.05,
        domain_warp_frequency=0.45,
        domain_warp_amplitude=12.0,
        landforms=[],
    )
    seeder = DeterministicSeeder.from_string("spandev")

    material = SurfaceMaterialEngine.synthesize_material(
        req, math_profile, topology, seeder
    )

    assert isinstance(material, SurfaceMaterialGenome)
    assert -15.0 <= material.temperature_base <= 35.0
    assert 10.0 <= material.equator_heat <= 30.0
    assert -40.0 <= material.polar_cooling <= -10.0
    assert 0.0 <= material.moisture_base <= 1.0
    assert 0.0 <= material.ocean_evaporation <= 1.0
    assert len(material.roughness_curve) == 5
    for r in material.roughness_curve:
        assert 0.0 <= r <= 1.0
    assert 0.0 <= material.metallic_factor <= 1.0
    assert 0.0 <= material.crystalline_facetting <= 1.0
    assert len(material.elevation_color_ramp) == 6


def test_synthesize_surface_material_determinism() -> None:
    """Verifies that separate seeders created from the same seed produce identical SurfaceMaterialGenomes."""
    req = UserPlanetProfileRequest(
        username="spandev",
        language_summary=[
            LanguageStat(name="Rust", color="#dea584", bytes=5000, percentage=50.0),
            LanguageStat(name="Python", color="#3572a5", bytes=5000, percentage=50.0),
        ],
    )
    math_profile = MathematicalProfile(
        shannon_entropy=1.0,
        diurnal_phase=0.5,
        diurnal_coherence=0.7,
        repo_gini_index=0.2,
        polyglot_diversity=0.5,
    )
    topology = TopologyGenome(
        base_radius=100.0,
        sea_level=0.45,
        max_altitude=20.0,
        octaves=6,
        persistence=0.5,
        lacunarity=2.0,
        domain_warp_frequency=0.5,
        domain_warp_amplitude=10.0,
        landforms=[],
    )

    seeder1 = DeterministicSeeder.from_string("reproducible_dev")
    seeder2 = DeterministicSeeder.from_string("reproducible_dev")

    mat1 = SurfaceMaterialEngine.synthesize_material(req, math_profile, topology, seeder1)
    mat2 = SurfaceMaterialEngine.synthesize_material(req, math_profile, topology, seeder2)

    assert mat1.model_dump() == mat2.model_dump()
