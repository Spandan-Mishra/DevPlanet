from src.core.seeder import DeterministicSeeder
from src.engine.celestial import CelestialMechanicsEngine
from src.models.genome import CelestialGenome, MathematicalProfile
from src.models.request import LanguageStat, UserPlanetProfileRequest


def test_celestial_synthesis_no_external_contributions() -> None:
    """Verifies celestial genome synthesis for users with 0 PRs and low commits."""
    req = UserPlanetProfileRequest(
        username="solo_coder",
        total_commits=50,
        total_repos=2,
        total_prs=0,
        total_reviews=0,
    )
    math_profile = MathematicalProfile(
        shannon_entropy=0.5,
        diurnal_phase=0.4,
        diurnal_coherence=0.6,
        repo_gini_index=0.2,
        polyglot_diversity=0.3,
    )
    seeder = DeterministicSeeder.from_string("solo_coder")

    celestial = CelestialMechanicsEngine.synthesize_celestial(req, math_profile, seeder)

    assert isinstance(celestial, CelestialGenome)
    assert celestial.radius == 100.0
    assert 0.05 <= celestial.rotation_speed <= 0.35
    assert 0.05 <= celestial.axial_tilt <= 0.45
    # No PRs -> 0 moons
    assert len(celestial.moons) == 0
    # Low commits -> no rings
    assert not celestial.rings.enabled
    assert celestial.rings.particle_count == 0


def test_celestial_moons_generation_with_prs() -> None:
    """Verifies that external PRs spawn tiered, non-colliding Keplerian moons."""
    req = UserPlanetProfileRequest(
        username="oss_maintainer",
        total_commits=800,
        total_repos=15,
        total_prs=45,
        total_reviews=30,
        language_summary=[
            LanguageStat(name="Rust", color="#dea584", bytes=10000, percentage=100.0)
        ],
    )
    math_profile = MathematicalProfile(
        shannon_entropy=1.2,
        diurnal_phase=0.8,
        diurnal_coherence=0.9,
        repo_gini_index=0.4,
        polyglot_diversity=0.5,
    )
    seeder = DeterministicSeeder.from_string("oss_maintainer")

    celestial = CelestialMechanicsEngine.synthesize_celestial(req, math_profile, seeder)

    assert len(celestial.moons) >= 2
    assert len(celestial.moons) <= CelestialMechanicsEngine.MAX_MOONS

    # Check strictly increasing orbital distances (non-colliding orbits)
    prev_orbit = 0.0
    for moon in celestial.moons:
        assert moon.orbit_radius > prev_orbit
        assert moon.radius >= 4.0
        assert 0.15 <= moon.orbit_speed <= 1.20
        assert 0.02 <= moon.inclination <= 0.45
        assert 0.15 <= moon.crater_density <= 0.90
        assert moon.color.startswith("#")
        prev_orbit = moon.orbit_radius

    # Prolific dev -> rings enabled
    assert celestial.rings.enabled
    assert celestial.rings.inner_radius > celestial.radius
    assert celestial.rings.outer_radius > celestial.rings.inner_radius
    assert celestial.rings.particle_count >= 800
    assert celestial.rings.density > 0.0
    assert celestial.rings.tint.startswith("#")


def test_celestial_determinism() -> None:
    """Verifies seeded reproducibility for celestial dynamics."""
    req = UserPlanetProfileRequest(
        username="deterministic_dev",
        total_commits=400,
        total_repos=10,
        total_prs=25,
        total_reviews=10,
    )
    math_profile = MathematicalProfile(
        shannon_entropy=0.8,
        diurnal_phase=0.5,
        diurnal_coherence=0.7,
        repo_gini_index=0.3,
        polyglot_diversity=0.4,
    )

    seeder_1 = DeterministicSeeder.from_string("same_seed")
    seeder_2 = DeterministicSeeder.from_string("same_seed")

    c1 = CelestialMechanicsEngine.synthesize_celestial(req, math_profile, seeder_1)
    c2 = CelestialMechanicsEngine.synthesize_celestial(req, math_profile, seeder_2)

    assert c1.model_dump() == c2.model_dump()
