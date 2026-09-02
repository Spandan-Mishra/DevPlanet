import math

from src.core.math_utils import clamp, round_to
from src.core.seeder import DeterministicSeeder
from src.models.genome import LandformNode, MathematicalProfile, TopologyGenome
from src.models.request import LandformRepo, UserPlanetProfileRequest


class SphericalTopologyEngine:
    """Procedural spherical topology engine for 3D planetary surfaces on S^2.

    Calculates:
    1. Spherical Voronoi tectonic plate distributions using a golden-ratio Fibonacci
       lattice perturbed by seeded organic jitter.
    2. Adaptive Landform node parameterization (elevation, roughness, resilience).
    3. Global fractal noise parameters (FBM octaves, persistence, domain warping)
       coupled to Shannon information entropy and repo concentration.
    """

    MAX_PRIMARY_LANDFORMS: int = 12

    @staticmethod
    def _rank_and_filter_repos(
        repos: list[LandformRepo],
    ) -> list[LandformRepo]:
        """Filters and ranks repositories to select the top significant landforms.

        Scoring formula: Stars * 3 + Forks * 2 + Commits + (100 if pinned else 0).
        """
        if not repos:
            return []

        def repo_score(r: LandformRepo) -> float:
            pinned_bonus = 100.0 if r.is_pinned else 0.0
            return (
                float(r.stars * 3 + r.forks * 2 + r.commit_count) + pinned_bonus
            )

        sorted_repos = sorted(repos, key=repo_score, reverse=True)
        return sorted_repos[: SphericalTopologyEngine.MAX_PRIMARY_LANDFORMS]

    @staticmethod
    def _compute_fibonacci_sphere_points(
        n: int, seeder: DeterministicSeeder, jitter_scale: float = 0.18
    ) -> list[tuple[float, float, float]]:
        """Distributes n points quasi-uniformly on S^2 with deterministic seeded jitter.

        Uses golden spiral (Fibonacci sphere) with randomized global orientation
        and individual angular perturbation.
        """
        if n <= 0:
            return []
        if n == 1:
            # Single continent: derive location from seeded polar tilt and azimuth
            tilt_theta = seeder.next_float(0.35, 1.25)
            rot_phi = seeder.next_float(0.0, 2.0 * math.pi)
            x = math.sin(tilt_theta) * math.cos(rot_phi)
            y = math.sin(tilt_theta) * math.sin(rot_phi)
            z = math.cos(tilt_theta)
            norm = math.sqrt(x * x + y * y + z * z)
            return [(x / norm, y / norm, z / norm)]

        points: list[tuple[float, float, float]] = []
        golden_ratio = (1.0 + math.sqrt(5.0)) / 2.0
        golden_angle = 2.0 * math.pi * (1.0 - 1.0 / golden_ratio)

        # Global rotational offset for this planet's seed
        rot_offset = seeder.next_float(0.0, 2.0 * math.pi)

        for i in range(n):
            # Base spherical coordinates
            # y goes from 1 - 1/n to -1 + 1/n
            y_base = 1.0 - (2.0 * float(i) + 1.0) / float(n)
            # Clamp to [-1.0, 1.0] to guard against numerical float precision drift
            y_base = clamp(y_base, -1.0, 1.0)
            theta_base = math.acos(y_base)
            phi_base = float(i) * golden_angle + rot_offset

            # Seeded organic jitter per plate
            jitter_seeder = seeder.fork(f"plate_jitter_{i}")
            theta_jitter = jitter_seeder.next_float(-jitter_scale, jitter_scale)
            phi_jitter = jitter_seeder.next_float(-jitter_scale, jitter_scale)

            theta = clamp(theta_base + theta_jitter, 0.01, math.pi - 0.01)
            phi = (phi_base + phi_jitter) % (2.0 * math.pi)

            # Convert to Cartesian coordinate on S^2 (unit sphere)
            x = math.sin(theta) * math.cos(phi)
            y = math.sin(theta) * math.sin(phi)
            z = math.cos(theta)

            # Normalize to guarantee exact unit sphere norm: ||P|| = 1.0
            norm = math.sqrt(x * x + y * y + z * z)
            points.append((x / norm, y / norm, z / norm))

        return points

    @staticmethod
    def _classify_tectonic_type(repo: LandformRepo, resilience: float) -> str:
        """Classifies the geological archetype of a repository landform."""
        if repo.stars >= 100 or repo.is_pinned:
            return "orogenic_belt"  # Towering mountain ridge system
        if resilience >= 0.65 and repo.commit_count > 50:
            return "shield_craton"  # Vast, ancient stable continental mass
        if repo.stars > 10 or repo.forks > 5:
            return "volcanic_archipelago"  # Dynamic volcanic island chain
        if repo.commit_count > 10:
            return "rift_valley"  # Fissured continental rift
        return "oceanic_trench"  # Submerged oceanic rise / nascent sea mount

    @classmethod
    def generate_landforms(
        cls,
        repos: list[LandformRepo],
        math_profile: MathematicalProfile,
        seeder: DeterministicSeeder,
    ) -> list[LandformNode]:
        """Generates parameterized tectonic landform nodes on S^2."""
        primary_repos = cls._rank_and_filter_repos(repos)
        if not primary_repos:
            return []

        n = len(primary_repos)
        plate_seeder = seeder.fork("tectonics_plates")
        points = cls._compute_fibonacci_sphere_points(n, plate_seeder)

        # Calculate total mass for relative plate scaling
        masses = [
            float(r.stars * 3 + r.forks * 2 + r.commit_count + 1)
            for r in primary_repos
        ]
        max_mass = max(masses) if masses else 1.0

        landform_nodes: list[LandformNode] = []

        for i, repo in enumerate(primary_repos):
            repo_mass = masses[i]
            mass_ratio = repo_mass / max_mass

            # Resilience index [0.1, 1.0]
            impact_score = float(
                repo.stars * 3 + repo.forks * 2 + repo.commit_count + 1
            )
            resilience = clamp(impact_score / (impact_score + 25.0), 0.1, 1.0)

            # Plate radius in radians on S^2: [0.15, 0.85]
            # Higher mass = wider continental plate
            base_radius = 0.25 + 0.50 * math.sqrt(mass_ratio)
            plate_radius = clamp(base_radius, 0.15, 0.85)

            # Elevation factor [0.25, 1.0]
            elevation = clamp(0.30 + 0.70 * mass_ratio, 0.25, 1.0)

            # Roughness [0.15, 0.85] influenced by diurnal coherence and commit density
            roughness_base = 0.50 + 0.35 * (1.0 - math_profile.diurnal_coherence)
            roughness = clamp(roughness_base, 0.15, 0.85)

            tectonic_type = cls._classify_tectonic_type(repo, resilience)

            landform_nodes.append(
                LandformNode(
                    repo_name=repo.name,
                    plate_center=points[i],
                    plate_radius=round_to(plate_radius, 4),
                    elevation_factor=round_to(elevation, 4),
                    roughness=round_to(roughness, 4),
                    tectonic_type=tectonic_type,
                    resilience_index=round_to(resilience, 4),
                )
            )

        return landform_nodes

    @classmethod
    def synthesize_topology(
        cls,
        request: UserPlanetProfileRequest,
        math_profile: MathematicalProfile,
        master_seeder: DeterministicSeeder,
    ) -> TopologyGenome:
        """Synthesizes the complete TopologyGenome."""
        topology_seeder = master_seeder.fork("topology_noise")

        # 1. Fractal noise octaves: 4 (simple) to 8 (complex, high entropy)
        entropy = math_profile.shannon_entropy
        octaves = int(clamp(float(4 + int(entropy * 1.5)), 4.0, 8.0))

        # 2. Persistence & Lacunarity with seeded micro-variance
        pers_noise = topology_seeder.next_float(-0.02, 0.02)
        persistence = clamp(0.45 + 0.05 * entropy + pers_noise, 0.40, 0.60)

        lac_noise = topology_seeder.next_float(-0.05, 0.05)
        lacunarity = clamp(
            2.0 + 0.10 * (1.0 - math_profile.repo_gini_index) + lac_noise,
            1.85,
            2.40,
        )

        # 3. Domain Warping
        warp_freq = clamp(0.35 + 0.40 * math_profile.polyglot_diversity, 0.20, 1.20)
        warp_amp = clamp(8.0 + 12.0 * math_profile.polyglot_diversity, 4.0, 25.0)

        # 4. Sea Level [0.30, 0.68]
        # Low entropy = Pangaea supercontinent (lower sea level)
        # High entropy = Archipelago chain (higher sea level)
        sea_level = clamp(0.38 + 0.12 * entropy, 0.30, 0.68)

        # 5. Planetary Altitude & Radius
        base_radius = 100.0  # Standard Three.js unit sphere radius
        max_altitude = clamp(
            20.0 + 15.0 * (1.0 - math_profile.repo_gini_index), 15.0, 35.0
        )

        # 6. Generate Landforms
        landforms = cls.generate_landforms(
            request.landforms, math_profile, master_seeder
        )

        return TopologyGenome(
            base_radius=base_radius,
            sea_level=round_to(sea_level, 4),
            max_altitude=round_to(max_altitude, 4),
            octaves=octaves,
            persistence=round_to(persistence, 4),
            lacunarity=round_to(lacunarity, 4),
            domain_warp_frequency=round_to(warp_freq, 4),
            domain_warp_amplitude=round_to(warp_amp, 4),
            landforms=landforms,
        )
