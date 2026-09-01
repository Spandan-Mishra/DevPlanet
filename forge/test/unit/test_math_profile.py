import pytest

from src.engine.math_profile import MathProfileEngine
from src.models.request import (
    ContributionDay,
    LandformRepo,
    LanguageStat,
    UserPlanetProfileRequest,
)


def test_shannon_entropy_calculation() -> None:
    """Verifies Shannon entropy for known theoretical distributions."""
    engine = MathProfileEngine()

    # Empty languages
    assert engine.compute_shannon_entropy([]) == 0.0

    # Single language -> 0 bits of entropy
    single_lang = [
        LanguageStat(name="Rust", color="#dea584", bytes=10000, percentage=100.0)
    ]
    assert engine.compute_shannon_entropy(single_lang) == 0.0

    # 2 equal languages (50% / 50%) -> - (0.5 * log2(0.5) + 0.5 * log2(0.5)) = 1.0 bit
    two_equal = [
        LanguageStat(name="Go", color="#00ADD8", bytes=5000, percentage=50.0),
        LanguageStat(name="Python", color="#3572A5", bytes=5000, percentage=50.0),
    ]
    assert engine.compute_shannon_entropy(two_equal) == pytest.approx(1.0, abs=1e-3)

    # 4 equal languages (25% each) -> log2(4) = 2.0 bits
    four_equal = [
        LanguageStat(name="Go", color="#00ADD8", bytes=2500, percentage=25.0),
        LanguageStat(name="Python", color="#3572A5", bytes=2500, percentage=25.0),
        LanguageStat(name="TypeScript", color="#3178c6", bytes=2500, percentage=25.0),
        LanguageStat(name="Rust", color="#dea584", bytes=2500, percentage=25.0),
    ]
    assert engine.compute_shannon_entropy(four_equal) == pytest.approx(2.0, abs=1e-3)


def test_polyglot_diversity_index() -> None:
    """Verifies Gini-Simpson diversity metric."""
    engine = MathProfileEngine()

    assert engine.compute_polyglot_diversity([]) == 0.0

    # Single language -> 1 - 1.0^2 = 0.0
    single = [LanguageStat(name="C++", color="#f34b7d", bytes=1000, percentage=100.0)]
    assert engine.compute_polyglot_diversity(single) == 0.0

    # 2 equal languages -> 1 - (0.5^2 + 0.5^2) = 0.5
    two_equal = [
        LanguageStat(name="Go", color="#00ADD8", bytes=500, percentage=50.0),
        LanguageStat(name="Python", color="#3572A5", bytes=500, percentage=50.0),
    ]
    assert engine.compute_polyglot_diversity(two_equal) == pytest.approx(0.5, abs=1e-3)


def test_diurnal_metrics_fourier_analysis() -> None:
    """Verifies circadian Fourier harmonic phase and coherence."""
    engine = MathProfileEngine()

    # Empty profile
    empty_req = UserPlanetProfileRequest(username="test")
    phase, coherence = engine.compute_diurnal_metrics(empty_req)
    assert phase == 0.5
    assert coherence == 0.0

    # All commits on Wednesday (2026-01-07 was a Wednesday)
    wed_commits = [
        ContributionDay(date="2026-01-07", contribution_count=10),
        ContributionDay(date="2026-01-14", contribution_count=10),
    ]
    req_wed = UserPlanetProfileRequest(username="wed_dev", activity_heatmap=wed_commits)
    _, coherence_wed = engine.compute_diurnal_metrics(req_wed)
    # Perfect single-day concentration should yield maximum coherence = 1.0
    assert coherence_wed == pytest.approx(1.0, abs=1e-3)

    # Uniform daily commits across a full 7-day week
    uniform_week = [
        ContributionDay(date=f"2026-01-0{i}", contribution_count=5) for i in range(1, 8)
    ]
    req_uniform = UserPlanetProfileRequest(
        username="daily_dev", activity_heatmap=uniform_week
    )
    _, coherence_uniform = engine.compute_diurnal_metrics(req_uniform)
    # Uniform spread across all 7 days cancels out harmonic vector sum -> coherence near 0.0
    assert coherence_uniform == pytest.approx(0.0, abs=1e-2)


def test_repo_gini_index() -> None:
    """Verifies Gini concentration coefficient across landforms."""
    engine = MathProfileEngine()

    # <= 1 repo returns 0.0
    assert engine.compute_repo_gini_index([]) == 0.0
    assert (
        engine.compute_repo_gini_index(
            [LandformRepo(name="solo", stars=100, forks=10, commit_count=50)]
        )
        == 0.0
    )

    # Equal repos -> Gini = 0.0
    equal_repos = [
        LandformRepo(name=f"repo_{i}", stars=10, forks=5, commit_count=20)
        for i in range(5)
    ]
    assert engine.compute_repo_gini_index(equal_repos) == pytest.approx(0.0, abs=1e-3)

    # Skewed distribution (1 mega-popular repo, 9 empty repos)
    skewed_repos = [
        LandformRepo(name="mega_star", stars=100000, forks=50000, commit_count=1000)
    ] + [
        LandformRepo(name=f"tiny_{i}", stars=0, forks=0, commit_count=0)
        for i in range(9)
    ]
    gini_skewed = engine.compute_repo_gini_index(skewed_repos)
    # Extreme inequality approaches ~ 0.9 for n=10
    assert gini_skewed > 0.80


def test_repo_resilience_factor() -> None:
    """Verifies individual repository geological resilience calculation."""
    engine = MathProfileEngine()

    new_repo = LandformRepo(name="brand_new", stars=0, forks=0, commit_count=0)
    resilience_new = engine.compute_repo_resilience(new_repo)
    assert 0.0 < resilience_new < 0.2

    veteran_repo = LandformRepo(
        name="linux", stars=180000, forks=55000, commit_count=120000
    )
    resilience_vet = engine.compute_repo_resilience(veteran_repo)
    assert resilience_vet == pytest.approx(1.0, abs=1e-2)


def test_full_profile_generation() -> None:
    """Verifies that generate_profile constructs a complete MathematicalProfile."""
    req = UserPlanetProfileRequest(
        username="spandev",
        language_summary=[
            LanguageStat(name="Go", color="#00ADD8", bytes=8000, percentage=80.0),
            LanguageStat(name="Python", color="#3572A5", bytes=2000, percentage=20.0),
        ],
        landforms=[
            LandformRepo(name="devplanet", stars=50, forks=10, commit_count=30),
            LandformRepo(name="dotfiles", stars=2, forks=0, commit_count=10),
        ],
        activity_heatmap=[
            ContributionDay(date="2026-01-05", contribution_count=4),
            ContributionDay(date="2026-01-06", contribution_count=6),
        ],
    )

    profile = MathProfileEngine.generate_profile(req)
    assert profile.shannon_entropy > 0.0
    assert 0.0 <= profile.polyglot_diversity <= 1.0
    assert 0.0 <= profile.diurnal_phase <= 1.0
    assert 0.0 <= profile.diurnal_coherence <= 1.0
    assert 0.0 <= profile.repo_gini_index <= 1.0
