from src.core.seeder import DeterministicSeeder
from src.engine.atmosphere import AtmosphereEngine
from src.models.genome import (
    AtmosphereGenome,
    ElevationRampNode,
    MathematicalProfile,
    SurfaceMaterialGenome,
    TopologyGenome,
)
from src.models.request import LanguageStat, UserPlanetProfileRequest


def _sample_topology() -> TopologyGenome:
    return TopologyGenome(
        base_radius=100.0,
        sea_level=0.45,
        max_altitude=22.0,
        octaves=6,
        persistence=0.48,
        lacunarity=2.05,
        domain_warp_frequency=0.45,
        domain_warp_amplitude=12.0,
        landforms=[],
    )


def _sample_surface_material() -> SurfaceMaterialGenome:
    return SurfaceMaterialGenome(
        temperature_base=15.0,
        equator_heat=20.0,
        polar_cooling=-25.0,
        moisture_base=0.55,
        ocean_evaporation=0.60,
        roughness_curve=[0.12, 0.22, 0.55, 0.78, 0.35],
        metallic_factor=0.25,
        crystalline_facetting=0.40,
        elevation_color_ramp=[
            ElevationRampNode(elevation=0.0, oklab=(0.14, 0.0, 0.0), hex="#1a1a1a"),
            ElevationRampNode(elevation=1.0, oklab=(0.95, 0.0, 0.0), hex="#f0f0f0"),
        ],
    )


def test_synthesize_atmosphere_default() -> None:
    """Verifies atmospheric synthesis bounds without specific language overrides."""
    req = UserPlanetProfileRequest(username="test_atmos_user")
    math_profile = MathematicalProfile(
        shannon_entropy=0.6,
        diurnal_phase=0.5,
        diurnal_coherence=0.7,
        repo_gini_index=0.3,
        polyglot_diversity=0.4,
    )
    topology = _sample_topology()
    surface_material = _sample_surface_material()
    seeder = DeterministicSeeder.from_string("test_atmos_user")

    atmos = AtmosphereEngine.synthesize_atmosphere(
        req, math_profile, topology, surface_material, seeder
    )

    assert isinstance(atmos, AtmosphereGenome)
    assert atmos.has_atmosphere is True
    assert 6.0 <= atmos.density_scale_height <= 14.0
    assert len(atmos.rayleigh_coefficients) == 3
    for r in atmos.rayleigh_coefficients:
        assert 0.001 <= r <= 0.080
    assert 0.001 <= atmos.mie_coefficient <= 0.020
    assert 0.70 <= atmos.mie_directional_g <= 0.88
    assert 0.05 <= atmos.cloud_cover <= 0.85
    assert 0.01 <= atmos.cloud_speed <= 0.12


def test_atmosphere_language_rayleigh_modulation() -> None:
    """Verifies that primary developer language shifts Rayleigh scattering coefficients."""
    req_blue = UserPlanetProfileRequest(
        username="blue_dev",
        language_summary=[
            LanguageStat(name="Go", color="#00ADD8", bytes=5000, percentage=100.0)
        ],
    )
    req_red = UserPlanetProfileRequest(
        username="red_dev",
        language_summary=[
            LanguageStat(name="Ruby", color="#CC342D", bytes=5000, percentage=100.0)
        ],
    )
    math_profile = MathematicalProfile(
        shannon_entropy=0.0,
        diurnal_phase=0.5,
        diurnal_coherence=0.8,
        repo_gini_index=0.0,
        polyglot_diversity=0.0,
    )
    topology = _sample_topology()
    surface_material = _sample_surface_material()
    seeder = DeterministicSeeder.from_string("lang_atmos_test")

    atmos_blue = AtmosphereEngine.synthesize_atmosphere(
        req_blue, math_profile, topology, surface_material, seeder
    )
    atmos_red = AtmosphereEngine.synthesize_atmosphere(
        req_red, math_profile, topology, surface_material, seeder
    )

    # Red developer atmosphere should have higher red Rayleigh scattering than blue developer
    assert atmos_red.rayleigh_coefficients[0] > atmos_blue.rayleigh_coefficients[0]


def test_atmosphere_determinism() -> None:
    """Verifies seeded reproducibility of atmospheric parameters."""
    req = UserPlanetProfileRequest(username="reproducible_atmos")
    math_profile = MathematicalProfile(
        shannon_entropy=0.8,
        diurnal_phase=0.6,
        diurnal_coherence=0.75,
        repo_gini_index=0.25,
        polyglot_diversity=0.5,
    )
    topology = _sample_topology()
    surface_material = _sample_surface_material()

    seeder_1 = DeterministicSeeder.from_string("atmos_seed")
    seeder_2 = DeterministicSeeder.from_string("atmos_seed")

    a1 = AtmosphereEngine.synthesize_atmosphere(
        req, math_profile, topology, surface_material, seeder_1
    )
    a2 = AtmosphereEngine.synthesize_atmosphere(
        req, math_profile, topology, surface_material, seeder_2
    )

    assert a1.model_dump() == a2.model_dump()
