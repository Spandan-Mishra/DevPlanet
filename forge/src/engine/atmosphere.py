from src.core.math_utils import clamp, round_to
from src.core.seeder import DeterministicSeeder
from src.engine.palette import OklabColorConverter
from src.models.genome import (
    AtmosphereGenome,
    MathematicalProfile,
    SurfaceMaterialGenome,
    TopologyGenome,
)
from src.models.request import UserPlanetProfileRequest


class AtmosphereEngine:
    """Procedural atmospheric physics and optical scattering engine.

    Synthesizes:
    1. Rayleigh wavelength-dependent optical scattering (R, G, B).
    2. Mie aerosol particulate forward scattering and directional asymmetry (g).
    3. Cloud deck coverage, circulation velocity, and density scale heights
       coupled to planetary moisture and diurnal commit dynamics.
    """

    # Earth-standard normalized Rayleigh scattering base (inverse lambda^4)
    # Scaled for real-time WebGL atmospheric rim shaders
    BASE_RAYLEIGH: tuple[float, float, float] = (0.0058, 0.0135, 0.0331)

    @classmethod
    def synthesize_atmosphere(
        cls,
        request: UserPlanetProfileRequest,
        math_profile: MathematicalProfile,
        topology: TopologyGenome,
        surface_material: SurfaceMaterialGenome,
        master_seeder: DeterministicSeeder,
    ) -> AtmosphereGenome:
        """Synthesizes the complete AtmosphereGenome."""
        atmos_seeder = master_seeder.fork("planetary_atmosphere")

        # 1. Density Scale Height: [6.0, 14.0]
        # Thicker atmospheres correlate with higher planetary moisture & sea level
        moisture_factor = surface_material.moisture_base
        scale_height_base = 6.5 + 6.0 * moisture_factor
        scale_height_jitter = atmos_seeder.next_float(-0.5, 0.5)
        density_scale_height = clamp(scale_height_base + scale_height_jitter, 6.0, 14.0)

        # 2. Rayleigh Optical Scattering Coefficients (R, G, B)
        # Primary developer language tint subtly shifts atmospheric sunset/sky hue
        if request.language_summary:
            top_color = request.language_summary[0].color
            r_lin, g_lin, b_lin = OklabColorConverter.hex_to_srgb(top_color)

            # Modulate baseline Rayleigh scattering by chromatic signature
            # Higher red in language increases red rayleigh; higher blue increases blue
            rayleigh_r = clamp(cls.BASE_RAYLEIGH[0] * (0.6 + 0.8 * r_lin), 0.0020, 0.0250)
            rayleigh_g = clamp(cls.BASE_RAYLEIGH[1] * (0.6 + 0.8 * g_lin), 0.0050, 0.0300)
            rayleigh_b = clamp(cls.BASE_RAYLEIGH[2] * (0.6 + 0.8 * b_lin), 0.0100, 0.0550)
        else:
            rayleigh_r, rayleigh_g, rayleigh_b = cls.BASE_RAYLEIGH

        # 3. Mie Aerosol Scattering & Directional Asymmetry (g)
        # Particulate density rises with landmass roughness and repository concentration
        roughness_avg = sum(surface_material.roughness_curve) / len(surface_material.roughness_curve)
        mie_base = 0.002 + 0.010 * roughness_avg
        mie_jitter = atmos_seeder.next_float(-0.001, 0.001)
        mie_coeff = clamp(mie_base + mie_jitter, 0.001, 0.020)

        # Henyey-Greenstein phase function asymmetry g in [0.70, 0.88] (strong forward scattering)
        mie_g = clamp(0.72 + 0.14 * (1.0 - math_profile.diurnal_coherence), 0.70, 0.88)

        # 4. Cloud Cover [0.05, 0.85] and Circulation Velocity [0.01, 0.12]
        # Ocean evaporation and sea level drive vapor concentration
        evaporation = surface_material.ocean_evaporation
        cloud_base = 0.10 + 0.65 * (evaporation * 0.6 + topology.sea_level * 0.4)
        cloud_jitter = atmos_seeder.next_float(-0.04, 0.04)
        cloud_cover = clamp(cloud_base + cloud_jitter, 0.05, 0.85)

        # Cloud speed driven by diurnal coherence & temperature gradients
        temp_delta = surface_material.equator_heat - surface_material.polar_cooling
        cloud_speed = clamp(0.02 + 0.0015 * temp_delta, 0.01, 0.12)

        return AtmosphereGenome(
            has_atmosphere=True,
            density_scale_height=round_to(density_scale_height, 2),
            rayleigh_coefficients=(
                round_to(rayleigh_r, 5),
                round_to(rayleigh_g, 5),
                round_to(rayleigh_b, 5),
            ),
            mie_coefficient=round_to(mie_coeff, 5),
            mie_directional_g=round_to(mie_g, 4),
            cloud_cover=round_to(cloud_cover, 4),
            cloud_speed=round_to(cloud_speed, 4),
        )
