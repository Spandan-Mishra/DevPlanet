from datetime import UTC, datetime

from src.core.seeder import DeterministicSeeder
from src.engine.atmosphere import AtmosphereEngine
from src.engine.celestial import CelestialMechanicsEngine
from src.engine.ecosystem import EcosystemEngine
from src.engine.math_profile import MathProfileEngine
from src.engine.palette import SurfaceMaterialEngine
from src.engine.topology import SphericalTopologyEngine
from src.models.genome import MetaGenome, PlanetGenome
from src.models.request import UserPlanetProfileRequest


class PlanetGenomeOrchestrator:
    """Master procedural orchestrator for The Forge.

    Executes the deterministic synthesis pipeline:
    1. Seed Initialization: Deterministic PRNG initialized from username & salt.
    2. Mathematical Profiling: High-dimensional entropy, Gini concentration, diurnal harmonic analysis.
    3. Spherical Topology: S^2 Voronoi tectonic plate distribution & FBM fractal terrain.
    4. Surface Material & Climate: Continuous Oklab color space palette & Whittaker thermal matrix.
    5. Celestial Mechanics: Keplerian moon systems, asteroid dust rings & planetary tilt/rotation.
    6. Atmospheric Scattering: Rayleigh wavelength dispersion, Mie particulate & cloud circulation.
    7. Inhabitant Ecosystem: Multi-species Craig Reynolds flocking boids & polar aurora field.
    """

    GENOME_VERSION: str = "1.0.0"

    @classmethod
    def synthesize_planet_genome(
        cls,
        request: UserPlanetProfileRequest,
        salt: str = "devplanet_v1",
    ) -> PlanetGenome:
        """Synthesizes the complete, unified PlanetGenome from the user GitHub request."""
        # 1. Deterministic Seeder Initialization
        master_seeder = DeterministicSeeder.from_string(request.username, salt=salt)

        # 2. Mathematical Profile
        math_profile = MathProfileEngine.generate_profile(request)

        # 3. Spherical Topology Genome
        topology = SphericalTopologyEngine.synthesize_topology(
            request, math_profile, master_seeder
        )

        # 4. Surface Material & Climate Genome
        surface_material = SurfaceMaterialEngine.synthesize_material(
            request, math_profile, topology, master_seeder
        )

        # 5. Celestial Mechanics Genome
        celestial = CelestialMechanicsEngine.synthesize_celestial(
            request, math_profile, master_seeder
        )

        # 6. Planetary Atmosphere Genome
        atmosphere = AtmosphereEngine.synthesize_atmosphere(
            request, math_profile, topology, surface_material, master_seeder
        )

        # 7. Inhabitant Boids Ecosystem Genome
        ecosystem = EcosystemEngine.synthesize_ecosystem(
            request, math_profile, topology, surface_material, master_seeder
        )

        # 8. Meta Information (stores exact material used for cryptographic seed derivation)
        meta = MetaGenome(
            username=request.username,
            master_seed=f"{request.username}:{salt}",
            generated_at=datetime.now(UTC).isoformat(),
            version=cls.GENOME_VERSION,
        )

        return PlanetGenome(
            meta=meta,
            math_profile=math_profile,
            celestial=celestial,
            topology=topology,
            surface_material=surface_material,
            ecosystem=ecosystem,
            atmosphere=atmosphere,
        )
