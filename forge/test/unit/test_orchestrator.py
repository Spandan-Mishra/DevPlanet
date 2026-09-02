from httpx import ASGITransport, AsyncClient

from src.engine.orchestrator import PlanetGenomeOrchestrator
from src.main import app
from src.models.genome import PlanetGenome
from src.models.request import LandformRepo, LanguageStat, UserPlanetProfileRequest


def test_orchestrator_synthesize_planet_genome_complete() -> None:
    """Verifies end-to-end synthesis of the unified PlanetGenome."""
    req = UserPlanetProfileRequest(
        username="spandev",
        name="Spandan Mishra",
        total_repos=12,
        total_commits=650,
        total_prs=35,
        total_issues=15,
        total_reviews=20,
        language_summary=[
            LanguageStat(name="Rust", color="#dea584", bytes=15000, percentage=60.0),
            LanguageStat(
                name="TypeScript", color="#3178c6", bytes=10000, percentage=40.0
            ),
        ],
        landforms=[
            LandformRepo(
                name="DevPlanet", stars=250, forks=45, commit_count=320, is_pinned=True
            ),
            LandformRepo(name="forge-engine", stars=80, forks=12, commit_count=180),
        ],
    )

    genome = PlanetGenomeOrchestrator.synthesize_planet_genome(req)

    assert isinstance(genome, PlanetGenome)
    assert genome.meta.username == "spandev"
    assert genome.meta.version == "1.0.0"
    assert genome.meta.master_seed == "spandev:devplanet_v1"

    # Verify math profile
    assert genome.math_profile.shannon_entropy > 0.0
    assert genome.math_profile.polyglot_diversity > 0.0

    # Verify celestial
    assert genome.celestial.radius == 100.0
    assert len(genome.celestial.moons) >= 1
    assert genome.celestial.rings.enabled is True

    # Verify topology
    assert genome.topology.base_radius == 100.0
    assert len(genome.topology.landforms) == 2

    # Verify surface material
    assert len(genome.surface_material.elevation_color_ramp) == 6
    assert len(genome.surface_material.roughness_curve) == 5

    # Verify ecosystem
    assert len(genome.ecosystem.species) >= 2
    assert genome.ecosystem.aurora_color.startswith("#")

    # Verify atmosphere
    assert genome.atmosphere.has_atmosphere is True
    assert len(genome.atmosphere.rayleigh_coefficients) == 3


async def test_generate_genome_api_endpoint() -> None:
    """Verifies the POST /api/v1/genome/generate HTTP endpoint."""
    payload = {
        "username": "octocat",
        "name": "The Octocat",
        "totalRepos": 5,
        "totalCommits": 300,
        "totalPRs": 10,
        "totalIssues": 5,
        "totalReviews": 8,
        "languageSummary": [
            {"name": "Python", "color": "#3572A5", "bytes": 5000, "percentage": 100.0}
        ],
        "landforms": [
            {
                "name": "Spoon-Knife",
                "stars": 500,
                "forks": 200,
                "commitCount": 100,
            }
        ],
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/genome/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["username"] == "octocat"
        assert data["meta"]["masterSeed"] == "octocat:devplanet_v1"
        assert "mathProfile" in data
        assert "celestial" in data
        assert "topology" in data
        assert "surfaceMaterial" in data
        assert "ecosystem" in data
        assert "atmosphere" in data
