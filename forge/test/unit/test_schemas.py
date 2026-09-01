from httpx import ASGITransport, AsyncClient

from src.main import app
from src.models.genome import (
    AtmosphereGenome,
    CelestialGenome,
    CelestialRings,
    EcosystemGenome,
    MathematicalProfile,
    MetaGenome,
    PlanetGenome,
    SurfaceMaterialGenome,
    TopologyGenome,
)
from src.models.request import UserPlanetProfileRequest


async def test_health_check_endpoint() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "devplanet-forge"


def test_user_planet_profile_request_alias_parsing() -> None:
    payload = {
        "username": "octocat",
        "name": "The Octocat",
        "avatarUrl": "https://avatars.githubusercontent.com/u/583231",
        "accountAgeDays": 365,
        "followers": 100,
        "following": 10,
        "totalRepos": 8,
        "totalCommits": 150,
        "totalPRs": 20,
        "totalIssues": 10,
        "totalReviews": 5,
        "languageSummary": [
            {"name": "Go", "color": "#00ADD8", "bytes": 50000, "percentage": 70.0},
            {"name": "Python", "color": "#3572A5", "bytes": 21428, "percentage": 30.0},
        ],
        "landforms": [
            {
                "name": "Spoon-Knife",
                "description": "Repurposed spoon-knife testing",
                "stars": 1200,
                "forks": 500,
                "commitCount": 42,
                "isPinned": True,
            }
        ],
        "activityHeatmap": [
            {"date": "2026-01-01", "contributionCount": 5, "color": "#216e39"}
        ],
    }

    model = UserPlanetProfileRequest.model_validate(payload)
    assert model.username == "octocat"
    assert model.avatar_url == "https://avatars.githubusercontent.com/u/583231"
    assert model.account_age_days == 365
    assert len(model.language_summary) == 2
    assert model.language_summary[0].name == "Go"
    assert len(model.landforms) == 1
    assert model.landforms[0].commit_count == 42
    assert model.landforms[0].is_pinned is True


def test_planet_genome_schema_serialization() -> None:
    genome = PlanetGenome(
        meta=MetaGenome(
            username="octocat",
            master_seed="0x123456789abcdef0",
            generated_at="2026-09-01T12:00:00Z",
            version="1.0.0",
        ),
        math_profile=MathematicalProfile(
            shannon_entropy=1.42,
            diurnal_phase=0.85,
            diurnal_coherence=0.78,
            repo_gini_index=0.35,
            polyglot_diversity=0.68,
        ),
        celestial=CelestialGenome(
            radius=100.0,
            rotation_speed=0.002,
            axial_tilt=23.5,
            moons=[],
            rings=CelestialRings(
                enabled=True,
                inner_radius=140.0,
                outer_radius=220.0,
                particle_count=5000,
                density=0.8,
                tint="#64ffda",
            ),
        ),
        topology=TopologyGenome(
            base_radius=100.0,
            sea_level=0.45,
            max_altitude=25.0,
            octaves=6,
            persistence=0.5,
            lacunarity=2.0,
            domain_warp_frequency=0.5,
            domain_warp_amplitude=10.0,
            landforms=[],
        ),
        surface_material=SurfaceMaterialGenome(
            temperature_base=0.5,
            equator_heat=0.8,
            polar_cooling=0.9,
            moisture_base=0.4,
            ocean_evaporation=0.6,
            roughness_curve=[0.2, 0.4, 0.6, 0.8, 0.3],
            metallic_factor=0.1,
            crystalline_facetting=0.25,
            elevation_color_ramp=[],
        ),
        ecosystem=EcosystemGenome(
            species=[],
            aurora_intensity=0.5,
            aurora_frequency=1.2,
            aurora_color="#64ffda",
        ),
        atmosphere=AtmosphereGenome(
            has_atmosphere=True,
            density_scale_height=0.25,
            rayleigh_coefficients=[0.0058, 0.0135, 0.0331],
            mie_coefficient=0.004,
            mie_directional_g=0.76,
            cloud_cover=0.5,
            cloud_speed=0.001,
        ),
    )

    dumped = genome.model_dump(by_alias=True)
    assert dumped["meta"]["masterSeed"] == "0x123456789abcdef0"
    assert dumped["mathProfile"]["shannonEntropy"] == 1.42
    assert dumped["celestial"]["rings"]["innerRadius"] == 140.0
    assert dumped["atmosphere"]["hasAtmosphere"] is True
