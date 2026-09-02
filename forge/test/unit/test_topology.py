import numpy as np
import pytest

from src.core.seeder import DeterministicSeeder
from src.engine.math_profile import MathProfileEngine
from src.engine.topology import SphericalTopologyEngine
from src.models.genome import TopologyGenome
from src.models.request import (
    LandformRepo,
    LanguageStat,
    UserPlanetProfileRequest,
)


def test_repo_filtering_and_ranking() -> None:
    """Verifies that repos are ranked by significance and capped at MAX_PRIMARY_LANDFORMS."""
    repos = [
        LandformRepo(name=f"tiny_{i}", stars=1, forks=0, commit_count=5)
        for i in range(20)
    ]
    # Add a prominent pinned repo
    repos.append(
        LandformRepo(
            name="mega_pinned",
            stars=500,
            forks=200,
            commit_count=1000,
            is_pinned=True,
        )
    )

    filtered = SphericalTopologyEngine._rank_and_filter_repos(repos)
    assert len(filtered) == SphericalTopologyEngine.MAX_PRIMARY_LANDFORMS
    assert filtered[0].name == "mega_pinned"


def test_fibonacci_sphere_points_unit_norm() -> None:
    """Verifies that all generated Fibonacci points lie precisely on the unit sphere S^2."""
    seeder = DeterministicSeeder.from_string("octocat")
    points = SphericalTopologyEngine._compute_fibonacci_sphere_points(
        12, seeder
    )

    assert len(points) == 12
    for x, y, z in points:
        norm = np.sqrt(x * x + y * y + z * z)
        assert norm == pytest.approx(1.0, abs=1e-5)


def test_single_landform_point_determinism_and_divergence() -> None:
    """Verifies that single-landform generation derives non-static unit vectors with seed variance."""
    seeder_a1 = DeterministicSeeder.from_string("octocat", salt="single")
    seeder_a2 = DeterministicSeeder.from_string("octocat", salt="single")
    seeder_b = DeterministicSeeder.from_string("torvalds", salt="single")

    pts_a1 = SphericalTopologyEngine._compute_fibonacci_sphere_points(
        1, seeder_a1
    )
    pts_a2 = SphericalTopologyEngine._compute_fibonacci_sphere_points(
        1, seeder_a2
    )
    pts_b = SphericalTopologyEngine._compute_fibonacci_sphere_points(1, seeder_b)

    assert len(pts_a1) == 1
    # Unit norm check
    x, y, z = pts_a1[0]
    assert np.sqrt(x * x + y * y + z * z) == pytest.approx(1.0, abs=1e-5)

    # Identical seeds match
    assert pts_a1 == pts_a2

    # Different seeds diverge
    assert pts_a1[0] != pts_b[0]


def test_fibonacci_sphere_jitter_and_determinism() -> None:
    """Verifies that seeded jitter is deterministic for identical seeds and distinct across different seeds."""
    seeder_a1 = DeterministicSeeder.from_string("octocat", salt="2026")
    seeder_a2 = DeterministicSeeder.from_string("octocat", salt="2026")
    seeder_b = DeterministicSeeder.from_string("torvalds", salt="2026")

    pts_a1 = SphericalTopologyEngine._compute_fibonacci_sphere_points(
        8, seeder_a1
    )
    pts_a2 = SphericalTopologyEngine._compute_fibonacci_sphere_points(
        8, seeder_a2
    )
    pts_b = SphericalTopologyEngine._compute_fibonacci_sphere_points(8, seeder_b)

    # Identical seeds must yield exact same coordinates
    assert pts_a1 == pts_a2

    # Different seeds must yield different coordinates due to rotational and jitter divergence
    assert pts_a1[0] != pts_b[0]


def test_tectonic_type_classification() -> None:
    """Verifies geological archetype mapping based on repo stats and resilience."""
    engine = SphericalTopologyEngine()

    pinned_repo = LandformRepo(name="core", stars=200, is_pinned=True)
    assert engine._classify_tectonic_type(pinned_repo, 0.9) == "orogenic_belt"

    shield_repo = LandformRepo(name="old_engine", stars=5, commit_count=150)
    assert engine._classify_tectonic_type(shield_repo, 0.8) == "shield_craton"

    volcanic_repo = LandformRepo(name="hot_new_lib", stars=25, commit_count=5)
    assert (
        engine._classify_tectonic_type(volcanic_repo, 0.4)
        == "volcanic_archipelago"
    )

    trench_repo = LandformRepo(name="empty_test", stars=0, commit_count=1)
    assert engine._classify_tectonic_type(trench_repo, 0.1) == "oceanic_trench"


def test_synthesize_topology_full_generation() -> None:
    """Verifies complete synthesis of TopologyGenome with mathematical profile coupling."""
    req = UserPlanetProfileRequest(
        username="spandev",
        language_summary=[
            LanguageStat(
                name="Go", color="#00ADD8", bytes=6000, percentage=60.0
            ),
            LanguageStat(
                name="Python", color="#3572A5", bytes=4000, percentage=40.0
            ),
        ],
        landforms=[
            LandformRepo(
                name="devplanet",
                stars=150,
                forks=40,
                commit_count=120,
                is_pinned=True,
            ),
            LandformRepo(name="dotfiles", stars=10, forks=2, commit_count=35),
            LandformRepo(name="sandbox", stars=0, forks=0, commit_count=2),
        ],
    )

    math_profile = MathProfileEngine.generate_profile(req)
    seeder = DeterministicSeeder.from_string(req.username)

    topology = SphericalTopologyEngine.synthesize_topology(
        req, math_profile, seeder
    )

    assert isinstance(topology, TopologyGenome)
    assert topology.base_radius == 100.0
    assert 0.30 <= topology.sea_level <= 0.70
    assert 4 <= topology.octaves <= 8
    assert 0.0 < topology.persistence < 1.0
    assert topology.lacunarity > 1.0
    assert len(topology.landforms) == 3

    # Primary repo should have highest elevation and largest plate radius
    primary_plate = topology.landforms[0]
    assert primary_plate.repo_name == "devplanet"
    assert primary_plate.tectonic_type == "orogenic_belt"
    assert (
        primary_plate.elevation_factor
        >= topology.landforms[2].elevation_factor
    )
    assert primary_plate.plate_radius >= topology.landforms[2].plate_radius
