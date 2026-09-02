from src.core.seeder import DeterministicSeeder
from src.engine.ecosystem import EcosystemEngine
from src.models.genome import (
    EcosystemGenome,
    ElevationRampNode,
    MathematicalProfile,
    SurfaceMaterialGenome,
    TopologyGenome,
)
from src.models.request import LandformRepo, LanguageStat, UserPlanetProfileRequest


def _sample_topology(sea_level: float = 0.45) -> TopologyGenome:
    return TopologyGenome(
        base_radius=100.0,
        sea_level=sea_level,
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


def test_synthesize_ecosystem_full() -> None:
    """Verifies complete ecosystem synthesis with all 3 species present."""
    req = UserPlanetProfileRequest(
        username="ecosystem_dev",
        total_prs=20,
        total_issues=10,
        total_reviews=15,
        landforms=[
            LandformRepo(name="core_lib", stars=120, forks=45, commit_count=200),
            LandformRepo(name="web_ui", stars=40, forks=12, commit_count=80),
        ],
        language_summary=[
            LanguageStat(
                name="TypeScript", color="#3178C6", bytes=8000, percentage=80.0
            ),
            LanguageStat(name="Rust", color="#dea584", bytes=2000, percentage=20.0),
        ],
    )
    math_profile = MathematicalProfile(
        shannon_entropy=0.72,
        diurnal_phase=0.3,
        diurnal_coherence=0.85,
        repo_gini_index=0.4,
        polyglot_diversity=0.35,
    )
    topology = _sample_topology(sea_level=0.50)
    surface_mat = _sample_surface_material()
    seeder = DeterministicSeeder.from_string("ecosystem_dev")

    eco = EcosystemEngine.synthesize_ecosystem(
        req, math_profile, topology, surface_mat, seeder
    )

    assert isinstance(eco, EcosystemGenome)
    assert len(eco.species) == 3

    # Check species types
    types = [s.type for s in eco.species]
    assert "avian_glider" in types
    assert "pelagic_swimmer" in types
    assert "luminescent_wisp" in types

    for s in eco.species:
        assert s.population >= 8
        assert s.scale >= 0.5
        assert s.bioluminescence_color.startswith("#")
        assert 0.3 <= s.pulse_frequency <= 3.0

        # Check Boid physics sanity
        p = s.boid_physics
        assert 2.0 <= p.max_speed <= 12.0
        assert 0.1 <= p.max_force <= 0.6
        assert 4.0 <= p.separation_dist <= 20.0
        assert 10.0 <= p.neighbor_radius <= 50.0
        assert p.cohesion_weight > 0.0
        assert p.alignment_weight > 0.0
        assert p.separation_weight > 0.0
        assert p.terrain_avoidance_altitude >= 2.0

    # Aurora parameters
    assert 0.15 <= eco.aurora_intensity <= 0.95
    assert 0.20 <= eco.aurora_frequency <= 1.80
    assert eco.aurora_color.startswith("#")


def test_ecosystem_low_sea_level_skips_pelagic() -> None:
    """Verifies that arid planets with negligible ocean coverage omit pelagic swimmers."""
    req = UserPlanetProfileRequest(username="arid_dev")
    math_profile = MathematicalProfile(
        shannon_entropy=0.2,
        diurnal_phase=0.8,
        diurnal_coherence=0.5,
        repo_gini_index=0.1,
        polyglot_diversity=0.1,
    )
    topology = _sample_topology(sea_level=0.15)  # < 0.25 threshold
    surface_mat = _sample_surface_material()
    seeder = DeterministicSeeder.from_string("arid_dev")

    eco = EcosystemEngine.synthesize_ecosystem(
        req, math_profile, topology, surface_mat, seeder
    )

    types = [s.type for s in eco.species]
    assert "avian_glider" in types
    assert "luminescent_wisp" in types
    assert "pelagic_swimmer" not in types


def test_ecosystem_determinism() -> None:
    """Verifies seeded reproducibility of ecosystem generation."""
    req = UserPlanetProfileRequest(
        username="seeded_eco",
        landforms=[LandformRepo(name="engine", stars=50, forks=20, commit_count=100)],
    )
    math_profile = MathematicalProfile(
        shannon_entropy=0.5,
        diurnal_phase=0.6,
        diurnal_coherence=0.7,
        repo_gini_index=0.2,
        polyglot_diversity=0.3,
    )
    topology = _sample_topology()
    surface_mat = _sample_surface_material()

    seeder_1 = DeterministicSeeder.from_string("eco_seed")
    seeder_2 = DeterministicSeeder.from_string("eco_seed")

    e1 = EcosystemEngine.synthesize_ecosystem(
        req, math_profile, topology, surface_mat, seeder_1
    )
    e2 = EcosystemEngine.synthesize_ecosystem(
        req, math_profile, topology, surface_mat, seeder_2
    )

    assert e1.model_dump() == e2.model_dump()
