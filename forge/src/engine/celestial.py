import math

from src.core.math_utils import clamp, round_to
from src.core.seeder import DeterministicSeeder
from src.engine.palette import OklabColorConverter
from src.models.genome import (
    CelestialGenome,
    CelestialMoon,
    CelestialRings,
    MathematicalProfile,
)
from src.models.request import UserPlanetProfileRequest


class CelestialMechanicsEngine:
    """Procedural celestial mechanics and orbital dynamics engine.

    Synthesizes:
    1. Planetary rotation velocity and axial tilt derived from circadian diurnal rhythms.
    2. Orbital moon systems parameterized by external pull requests and code reviews.
    3. Planetary asteroid rings spawned by heavy contribution and commit density.
    """

    MAX_MOONS: int = 5
    PLANET_RADIUS: float = 100.0

    @classmethod
    def generate_moons(
        cls,
        request: UserPlanetProfileRequest,
        math_profile: MathematicalProfile,
        seeder: DeterministicSeeder,
    ) -> list[CelestialMoon]:
        """Synthesizes Keplerian orbital moon systems from external contributions."""
        external_impact = request.total_prs + request.total_reviews
        if external_impact <= 0:
            return []

        # Determine number of moons: 1 to MAX_MOONS based on external collaboration
        num_moons = int(
            clamp(float(1 + external_impact // 15), 1.0, float(cls.MAX_MOONS))
        )
        moon_seeder = seeder.fork("celestial_moons")

        # Color palette choices for moons (silicate rock, icy quartz, metallic iron, obsidian)
        moon_palette = [
            "#b0b5bc",  # Silicate Lunar Gray
            "#d4e6f1",  # Icy Quartz White
            "#c08081",  # Oxidized Iron Terracotta
            "#85929e",  # Basaltic Slate
            "#f9e79f",  # Sulfur Yellow
        ]

        moons: list[CelestialMoon] = []
        base_orbit = cls.PLANET_RADIUS * 1.55  # 155.0

        for i in range(num_moons):
            sub_seeder = moon_seeder.fork(f"moon_{i}")

            # Moon radius: 4.0 to 14.0
            radius_jitter = sub_seeder.next_float(-1.5, 2.5)
            moon_radius = clamp(
                6.0 + (external_impact / 50.0) + radius_jitter, 4.0, 14.0
            )

            # Orbit radius: tiered progression so orbits never collide
            orbit_step = 35.0 + sub_seeder.next_float(5.0, 18.0)
            orbit_dist = base_orbit + (i * orbit_step)

            # Kepler's 3rd Law approximation: v ~ 1 / sqrt(r)
            keplerian_speed = 1.25 / math.sqrt(orbit_dist / cls.PLANET_RADIUS)
            orbit_speed = clamp(
                keplerian_speed * sub_seeder.next_float(0.85, 1.15), 0.15, 1.20
            )

            # Orbital plane inclination in radians: [0.02, 0.45] (~1 deg to 26 deg)
            inclination = clamp(
                0.08 * float(i + 1) + sub_seeder.next_float(-0.04, 0.06),
                0.02,
                0.45,
            )

            # Crater density: [0.15, 0.90] (higher for older accounts and lower repo resilience)
            crater_density = clamp(
                0.35
                + 0.35 * (1.0 - math_profile.repo_gini_index)
                + sub_seeder.next_float(-0.08, 0.08),
                0.15,
                0.90,
            )

            color_idx = i % len(moon_palette)
            moon_color = moon_palette[color_idx]

            moons.append(
                CelestialMoon(
                    id=f"moon-{request.username}-{i + 1}",
                    name=f"Satellite-{chr(65 + i)}",
                    radius=round_to(moon_radius, 2),
                    orbit_radius=round_to(orbit_dist, 2),
                    orbit_speed=round_to(orbit_speed, 4),
                    inclination=round_to(inclination, 4),
                    color=moon_color,
                    crater_density=round_to(crater_density, 3),
                )
            )

        return moons

    @classmethod
    def generate_rings(
        cls,
        request: UserPlanetProfileRequest,
        math_profile: MathematicalProfile,
        seeder: DeterministicSeeder,
    ) -> CelestialRings:
        """Synthesizes planetary asteroid rings if contribution volume qualifies."""
        ring_seeder = seeder.fork("celestial_rings")

        # Rings form for prolific developers: high commits or multiple repos
        qualifies_for_rings = request.total_commits >= 250 or request.total_repos >= 8

        if not qualifies_for_rings:
            return CelestialRings(
                enabled=False,
                inner_radius=0.0,
                outer_radius=0.0,
                particle_count=0,
                density=0.0,
                tint="#000000",
            )

        # Ring geometry
        inner_radius = cls.PLANET_RADIUS * clamp(
            1.35 + ring_seeder.next_float(-0.05, 0.05), 1.25, 1.45
        )
        ring_width = cls.PLANET_RADIUS * clamp(
            0.40 + 0.30 * math_profile.polyglot_diversity, 0.30, 0.85
        )
        outer_radius = inner_radius + ring_width

        # Particle density and count: 800 to 4500 particles for WebGL instancing
        commit_scale = clamp(float(request.total_commits) / 1000.0, 0.2, 1.0)
        particle_count = int(clamp(800.0 + 3500.0 * commit_scale, 800.0, 4500.0))
        density = clamp(0.40 + 0.50 * math_profile.diurnal_coherence, 0.30, 0.95)

        # Procedural ring tint derived from primary language or celestial silver
        if request.language_summary:
            top_color = request.language_summary[0].color
            L, a, b = OklabColorConverter.hex_to_oklab(top_color)
            # Desaturate slightly for celestial icy dust appearance
            ring_tint = OklabColorConverter.oklab_to_hex(
                clamp(L + 0.15, 0.55, 0.88), a * 0.5, b * 0.5
            )
        else:
            ring_tint = "#c8d6e5"

        return CelestialRings(
            enabled=True,
            inner_radius=round_to(inner_radius, 2),
            outer_radius=round_to(outer_radius, 2),
            particle_count=particle_count,
            density=round_to(density, 3),
            tint=ring_tint,
        )

    @classmethod
    def synthesize_celestial(
        cls,
        request: UserPlanetProfileRequest,
        math_profile: MathematicalProfile,
        master_seeder: DeterministicSeeder,
    ) -> CelestialGenome:
        """Synthesizes the complete CelestialGenome coupling orbital physics and dynamics."""
        celestial_seeder = master_seeder.fork("celestial_dynamics")

        # 1. Rotation speed (rad/s): [0.05, 0.35]
        # Driven by commit frequency and diurnal coherence
        speed_base = 0.08 + 0.20 * math_profile.diurnal_coherence
        speed_jitter = celestial_seeder.next_float(-0.02, 0.02)
        rotation_speed = clamp(speed_base + speed_jitter, 0.05, 0.35)

        # 2. Axial tilt (rad): [0.05, 0.45] (~3 deg to 26 deg)
        # Circadian Fourier phase modulates planetary obliquity
        tilt_base = 0.08 + 0.32 * math_profile.diurnal_phase
        tilt_jitter = celestial_seeder.next_float(-0.03, 0.03)
        axial_tilt = clamp(tilt_base + tilt_jitter, 0.05, 0.45)

        # 3. Moons and Rings
        moons = cls.generate_moons(request, math_profile, master_seeder)
        rings = cls.generate_rings(request, math_profile, master_seeder)

        return CelestialGenome(
            radius=cls.PLANET_RADIUS,
            rotation_speed=round_to(rotation_speed, 4),
            axial_tilt=round_to(axial_tilt, 4),
            moons=moons,
            rings=rings,
        )
