from src.core.math_utils import clamp, round_to
from src.core.seeder import DeterministicSeeder
from src.engine.palette import OklabColorConverter
from src.models.genome import (
    BoidPhysics,
    EcosystemGenome,
    InhabitantSpecies,
    MathematicalProfile,
    SurfaceMaterialGenome,
    TopologyGenome,
)
from src.models.request import UserPlanetProfileRequest


class EcosystemEngine:
    """Procedural inhabitant boids ecosystem and atmospheric aurora synthesizer.

    Calculates:
    1. Inhabitant boid flock populations and Craig Reynolds (1987) steering dynamics
       parameterized by community engagement metrics (stars, forks, PRs).
    2. Distinct species archetypes (Avian Gliders, Pelagic Swarms, Luminescent Wisps).
    3. Planetary aurora borealis field intensity, harmonic pulse frequency, and Oklab hue.
    """

    @classmethod
    def _synthesize_avian_species(
        cls,
        request: UserPlanetProfileRequest,
        math_profile: MathematicalProfile,
        seeder: DeterministicSeeder,
    ) -> InhabitantSpecies:
        """Synthesizes high-altitude atmospheric avian gliders driven by repository stars."""
        total_stars = sum(repo.stars for repo in request.landforms)
        pop_base = 15.0 + 4.0 * math_profile.polyglot_diversity * 10.0 + min(float(total_stars) * 0.5, 80.0)
        pop_jitter = seeder.next_float(-3.0, 3.0)
        population = int(clamp(pop_base + pop_jitter, 12.0, 150.0))

        # Color: Primary language chromatic tint or radiant solar gold
        if request.language_summary:
            prim_hex = request.language_summary[0].color
            L, a, b = OklabColorConverter.hex_to_oklab(prim_hex)
            color = OklabColorConverter.oklab_to_hex(clamp(L + 0.1, 0.70, 0.95), a, b)
        else:
            color = "#f9ca24"

        scale = clamp(1.0 + float(total_stars) / 200.0, 0.8, 2.5)

        physics = BoidPhysics(
            max_speed=round_to(clamp(6.0 + 3.0 * math_profile.diurnal_coherence, 4.5, 9.5), 3),
            max_force=round_to(clamp(0.25 + 0.15 * math_profile.repo_gini_index, 0.15, 0.45), 3),
            separation_dist=round_to(clamp(8.0 + 4.0 * scale, 6.0, 16.0), 2),
            neighbor_radius=round_to(clamp(25.0 + 10.0 * scale, 18.0, 45.0), 2),
            cohesion_weight=round_to(clamp(1.0 + 0.5 * math_profile.diurnal_coherence, 0.8, 1.8), 3),
            alignment_weight=round_to(clamp(1.2 + 0.4 * (1.0 - math_profile.repo_gini_index), 0.9, 1.9), 3),
            separation_weight=round_to(clamp(1.5 + 0.5 * scale, 1.2, 2.4), 3),
            terrain_avoidance_altitude=round_to(clamp(20.0 + 10.0 * math_profile.shannon_entropy, 18.0, 38.0), 2),
        )

        return InhabitantSpecies(
            type="avian_glider",
            population=population,
            mesh_archetype="avian_glider",
            scale=round_to(scale, 2),
            boid_physics=physics,
            bioluminescence_color=color,
            pulse_frequency=round_to(clamp(0.8 + 0.6 * math_profile.diurnal_phase, 0.5, 2.0), 3),
        )

    @classmethod
    def _synthesize_pelagic_species(
        cls,
        request: UserPlanetProfileRequest,
        math_profile: MathematicalProfile,
        topology: TopologyGenome,
        seeder: DeterministicSeeder,
    ) -> InhabitantSpecies | None:
        """Synthesizes oceanic / aquatic pelagic swarms driven by repository forks."""
        # Only spawn pelagic species if planet has substantial water bodies
        if topology.sea_level < 0.25:
            return None

        total_forks = sum(repo.forks for repo in request.landforms)
        pop_base = 10.0 + min(float(total_forks) * 0.8, 70.0) + (topology.sea_level * 25.0)
        pop_jitter = seeder.next_float(-2.0, 2.0)
        population = int(clamp(pop_base + pop_jitter, 8.0, 120.0))

        # Color: Secondary language tint or oceanic bioluminescent cyan
        if len(request.language_summary) > 1:
            sec_hex = request.language_summary[1].color
            L, a, b = OklabColorConverter.hex_to_oklab(sec_hex)
            color = OklabColorConverter.oklab_to_hex(clamp(L + 0.15, 0.65, 0.90), a, b)
        else:
            color = "#00e5ff"

        scale = clamp(0.9 + float(total_forks) / 150.0, 0.7, 2.2)

        physics = BoidPhysics(
            max_speed=round_to(clamp(3.5 + 2.0 * math_profile.diurnal_coherence, 2.5, 6.0), 3),
            max_force=round_to(clamp(0.18 + 0.10 * math_profile.repo_gini_index, 0.10, 0.35), 3),
            separation_dist=round_to(clamp(6.0 + 3.0 * scale, 5.0, 12.0), 2),
            neighbor_radius=round_to(clamp(18.0 + 8.0 * scale, 14.0, 32.0), 2),
            cohesion_weight=round_to(clamp(1.4 + 0.4 * math_profile.diurnal_coherence, 1.0, 2.0), 3),
            alignment_weight=round_to(clamp(1.3 + 0.3 * (1.0 - math_profile.repo_gini_index), 1.0, 1.8), 3),
            separation_weight=round_to(clamp(1.4 + 0.3 * scale, 1.1, 2.0), 3),
            terrain_avoidance_altitude=round_to(clamp(3.0 + 4.0 * topology.sea_level, 2.5, 8.0), 2),
        )

        return InhabitantSpecies(
            type="pelagic_swimmer",
            mesh_archetype="pelagic_manta",
            population=population,
            scale=round_to(scale, 2),
            boid_physics=physics,
            bioluminescence_color=color,
            pulse_frequency=round_to(clamp(0.4 + 0.4 * math_profile.diurnal_phase, 0.3, 1.4), 3),
        )

    @classmethod
    def _synthesize_wisp_species(
        cls,
        request: UserPlanetProfileRequest,
        math_profile: MathematicalProfile,
        seeder: DeterministicSeeder,
    ) -> InhabitantSpecies:
        """Synthesizes ground/lowland crystalline roamers driven by PRs and code activity."""
        activity_mass = float(request.total_prs + request.total_issues + request.total_reviews)
        pop_base = 20.0 + min(activity_mass * 0.7, 80.0) + (math_profile.polyglot_diversity * 30.0)
        pop_jitter = seeder.next_float(-3.0, 3.0)
        population = int(clamp(pop_base + pop_jitter, 15.0, 160.0))

        # Color: Prismatic violet/emerald tint
        color = "#a29bfe" if math_profile.diurnal_phase < 0.4 else "#00cec9"

        scale = clamp(0.6 + activity_mass / 200.0, 0.5, 1.8)

        physics = BoidPhysics(
            max_speed=round_to(clamp(4.0 + 2.5 * math_profile.diurnal_coherence, 3.0, 7.5), 3),
            max_force=round_to(clamp(0.30 + 0.15 * math_profile.repo_gini_index, 0.20, 0.50), 3),
            separation_dist=round_to(clamp(5.0 + 3.0 * scale, 4.0, 10.0), 2),
            neighbor_radius=round_to(clamp(15.0 + 6.0 * scale, 12.0, 26.0), 2),
            cohesion_weight=round_to(clamp(1.1 + 0.3 * math_profile.diurnal_coherence, 0.9, 1.6), 3),
            alignment_weight=round_to(clamp(1.1 + 0.3 * (1.0 - math_profile.repo_gini_index), 0.8, 1.6), 3),
            separation_weight=round_to(clamp(1.8 + 0.4 * scale, 1.4, 2.5), 3),
            terrain_avoidance_altitude=round_to(clamp(4.0 + 3.0 * math_profile.polyglot_diversity, 3.0, 9.0), 2),
        )

        return InhabitantSpecies(
            type="luminescent_wisp",
            mesh_archetype="luminescent_wisp",
            population=population,
            scale=round_to(scale, 2),
            boid_physics=physics,
            bioluminescence_color=color,
            pulse_frequency=round_to(clamp(1.0 + 1.2 * math_profile.diurnal_phase, 0.8, 2.5), 3),
        )

    @classmethod
    def synthesize_ecosystem(
        cls,
        request: UserPlanetProfileRequest,
        math_profile: MathematicalProfile,
        topology: TopologyGenome,
        surface_material: SurfaceMaterialGenome,
        master_seeder: DeterministicSeeder,
    ) -> EcosystemGenome:
        """Synthesizes the complete EcosystemGenome coupling boids and aurora dynamics."""
        eco_seeder = master_seeder.fork("ecosystem_synthesis")

        # 1. Inhabitant Species Synthesis
        species_list: list[InhabitantSpecies] = []

        # Avian species (always present)
        avian = cls._synthesize_avian_species(request, math_profile, eco_seeder.fork("avian"))
        species_list.append(avian)

        # Pelagic species (if aquatic bodies exist)
        pelagic = cls._synthesize_pelagic_species(request, math_profile, topology, eco_seeder.fork("pelagic"))
        if pelagic is not None:
            species_list.append(pelagic)

        # Luminescent wisps (always present)
        wisp = cls._synthesize_wisp_species(request, math_profile, eco_seeder.fork("wisp"))
        species_list.append(wisp)

        # 2. Planetary Aurora Borealis Field
        # Aurora intensity higher for night-owl developers (low diurnal phase) and high entropy
        night_bonus = (1.0 - math_profile.diurnal_phase) * 0.4
        aurora_intensity = clamp(
            0.25 + 0.35 * math_profile.polyglot_diversity + night_bonus,
            0.15,
            0.95,
        )

        # Aurora harmonic oscillation frequency in Hz: [0.20, 1.80]
        aurora_freq = clamp(0.35 + 1.10 * math_profile.diurnal_coherence, 0.20, 1.80)

        # Aurora color: Oklab synthesis
        if math_profile.diurnal_phase < 0.35:
            # Ethereal violet-cyan polar ribbon
            aurora_color = "#81ecec"
        elif math_profile.diurnal_phase > 0.70:
            # High-noon solar aurora: shimmering emerald
            aurora_color = "#55efc4"
        else:
            # Twilight magenta-indigo
            aurora_color = "#a29bfe"

        return EcosystemGenome(
            species=species_list,
            aurora_intensity=round_to(aurora_intensity, 4),
            aurora_frequency=round_to(aurora_freq, 4),
            aurora_color=aurora_color,
        )
