import re

import numpy as np

from src.core.seeder import DeterministicSeeder
from src.models.genome import (
    ElevationRampNode,
    MathematicalProfile,
    SurfaceMaterialGenome,
    TopologyGenome,
)
from src.models.request import LanguageStat, UserPlanetProfileRequest


class OklabColorConverter:
    """Perceptually uniform Oklab color space converter and interpolator (Björn Ottosson, 2020).

    Guarantees monotonic lightness scaling and uniform perceptual distance (Delta E)
    without color-muddying artifacts during procedural palette generation.
    """

    @staticmethod
    def hex_to_srgb(hex_str: str) -> tuple[float, float, float]:
        """Converts standard #RRGGBB or #RGB hex string to normalized sRGB [0.0, 1.0]."""
        cleaned = hex_str.strip().lstrip("#")
        if len(cleaned) == 3:
            cleaned = "".join(c * 2 for c in cleaned)
        if len(cleaned) != 6 or not re.fullmatch(r"[0-9a-fA-F]{6}", cleaned):
            # Fallback to neutral obsidian gray
            return (0.2, 0.2, 0.2)

        r = int(cleaned[0:2], 16) / 255.0
        g = int(cleaned[2:4], 16) / 255.0
        b = int(cleaned[4:6], 16) / 255.0
        return (r, g, b)

    @staticmethod
    def srgb_to_linear(c: float) -> float:
        """Converts standard gamma-compressed sRGB channel to linear sRGB."""
        if c <= 0.04045:
            return c / 12.92
        return float(((c + 0.055) / 1.055) ** 2.4)

    @staticmethod
    def linear_to_srgb(c_lin: float) -> float:
        """Converts linear sRGB channel back to gamma-compressed standard sRGB."""
        if c_lin <= 0.0031308:
            return float(12.92 * c_lin)
        return float(1.055 * (c_lin ** (1.0 / 2.4)) - 0.055)

    @classmethod
    def hex_to_oklab(cls, hex_str: str) -> tuple[float, float, float]:
        """Converts hex color code directly to Oklab (L, a, b) coordinates."""
        r_srgb, g_srgb, b_srgb = cls.hex_to_srgb(hex_str)

        r_lin = cls.srgb_to_linear(r_srgb)
        g_lin = cls.srgb_to_linear(g_srgb)
        b_lin = cls.srgb_to_linear(b_srgb)

        # 1. Linear sRGB to cone response LMS
        l_cone = 0.4122214708 * r_lin + 0.5363325363 * g_lin + 0.0514459929 * b_lin
        m_cone = 0.2119034982 * r_lin + 0.6806995451 * g_lin + 0.1073969566 * b_lin
        s_cone = 0.0883024619 * r_lin + 0.2817188376 * g_lin + 0.6299787005 * b_lin

        # 2. Non-linear cube root compression
        l_prime = float(np.cbrt(l_cone))
        m_prime = float(np.cbrt(m_cone))
        s_prime = float(np.cbrt(s_cone))

        # 3. LMS' to Oklab coordinates (L, a, b)
        L = 0.2104542553 * l_prime + 0.7936177850 * m_prime - 0.0040720468 * s_prime
        a = 1.9779984951 * l_prime - 2.4285922050 * m_prime + 0.4505937099 * s_prime
        b = 0.0259040371 * l_prime + 0.7827717662 * m_prime - 0.8086757660 * s_prime

        return (
            float(np.round(L, 5)),
            float(np.round(a, 5)),
            float(np.round(b, 5)),
        )

    @classmethod
    def oklab_to_hex(cls, L: float, a: float, b: float) -> str:
        """Converts Oklab (L, a, b) coordinates back to clamped #RRGGBB hex string."""
        # 1. Oklab to LMS'
        l_prime = L + 0.3963377774 * a + 0.2158037573 * b
        m_prime = L - 0.1055613458 * a - 0.0638541728 * b
        s_prime = L - 0.0894841775 * a - 1.2914855480 * b

        # 2. Cube
        l_cone = l_prime**3
        m_cone = m_prime**3
        s_cone = s_prime**3

        # 3. LMS to Linear sRGB
        r_lin = 4.0767439362 * l_cone - 3.3077115913 * m_cone + 0.2309699292 * s_cone
        g_lin = -1.2684380046 * l_cone + 2.6097574011 * m_cone - 0.3413193965 * s_cone
        b_lin = -0.0041960863 * l_cone - 0.7034186147 * m_cone + 1.7076147010 * s_cone

        # 4. Linear to gamma sRGB and clamp [0, 1]
        r_srgb = np.clip(cls.linear_to_srgb(r_lin), 0.0, 1.0)
        g_srgb = np.clip(cls.linear_to_srgb(g_lin), 0.0, 1.0)
        b_srgb = np.clip(cls.linear_to_srgb(b_lin), 0.0, 1.0)

        # 5. Format to 8-bit hex
        r_byte = int(np.round(r_srgb * 255.0))
        g_byte = int(np.round(g_srgb * 255.0))
        b_byte = int(np.round(b_srgb * 255.0))

        return f"#{r_byte:02x}{g_byte:02x}{b_byte:02x}"

    @classmethod
    def lerp_oklab(
        cls,
        oklab_1: tuple[float, float, float],
        oklab_2: tuple[float, float, float],
        t: float,
    ) -> tuple[float, float, float]:
        """Performs perceptually uniform linear interpolation between two Oklab colors."""
        t_clamped = float(np.clip(t, 0.0, 1.0))
        L = oklab_1[0] + (oklab_2[0] - oklab_1[0]) * t_clamped
        a = oklab_1[1] + (oklab_2[1] - oklab_1[1]) * t_clamped
        b = oklab_1[2] + (oklab_2[2] - oklab_1[2]) * t_clamped
        return (
            float(np.round(L, 5)),
            float(np.round(a, 5)),
            float(np.round(b, 5)),
        )


class SurfaceMaterialEngine:
    """Procedural surface material and elevation color ramp synthesizer.

    Maps developer language distributions, circadian diurnal phase, and Whittaker
    climate gradients into continuous PBR surface materials and Oklab elevation ramps.
    """

    @classmethod
    def generate_elevation_ramp(
        cls,
        languages: list[LanguageStat],
        math_profile: MathematicalProfile,
        sea_level: float,
        seeder: DeterministicSeeder,
    ) -> list[ElevationRampNode]:
        """Synthesizes a 6-stop continuous elevation color ramp in Oklab space."""
        palette_seeder = seeder.fork("elevation_palette")

        # 1. Determine primary and secondary chromatic signatures
        if languages:
            sorted_langs = sorted(languages, key=lambda lang: lang.bytes, reverse=True)
            primary_hex = sorted_langs[0].color
            secondary_hex = (
                sorted_langs[1].color
                if len(sorted_langs) > 1
                else sorted_langs[0].color
            )
        else:
            # Deterministic procedural default colors if no languages
            hue_a = palette_seeder.next_float(0.0, 1.0)
            primary_hex = "#3572a5" if hue_a > 0.5 else "#00add8"
            secondary_hex = "#dea584"

        _, prim_a, prim_b = OklabColorConverter.hex_to_oklab(primary_hex)
        _, sec_a, sec_b = OklabColorConverter.hex_to_oklab(secondary_hex)

        # 2. Diurnal albedo modulation
        # High diurnal phase (daylight) increases surface lightness; low phase (night) deepens tones
        albedo_mod = 0.05 * (math_profile.diurnal_phase - 0.5)

        # 3. Synthesize 6 elevation ramp stops from 0.0 (trench) to 1.0 (alpine peak)
        stops: list[tuple[float, float, float, float]] = []

        # Stop 0: Deep Oceanic Trench (elev = 0.00)
        # Deep dark basalt/abyssal tone with subtle secondary chromatic reflection
        trench_L = float(np.clip(0.14 + albedo_mod, 0.08, 0.22))
        trench_a = float(sec_a * 0.3)
        trench_b = float(sec_b * 0.3 - 0.05)  # slight oceanic cool shift
        stops.append((0.00, trench_L, trench_a, trench_b))

        # Stop 1: Continental Shelf / Shallow Ocean (elev = sea_level * 0.70)
        shelf_elev = float(np.round(sea_level * 0.70, 4))
        shelf_L = float(np.clip(0.32 + albedo_mod, 0.22, 0.42))
        shelf_a = float(prim_a * 0.5)
        shelf_b = float(prim_b * 0.5 - 0.03)
        stops.append((shelf_elev, shelf_L, shelf_a, shelf_b))

        # Stop 2: Coastline & Beach Strand (elev = sea_level)
        coast_elev = float(np.round(sea_level, 4))
        coast_L = float(np.clip(0.50 + albedo_mod, 0.40, 0.60))
        coast_a = float((prim_a + sec_a) * 0.4)
        coast_b = float((prim_b + sec_b) * 0.4 + 0.02)  # warm sand/strand tint
        stops.append((coast_elev, coast_L, coast_a, coast_b))

        # Stop 3: Lowlands & Vegetative Valleys (elev = sea_level + (1 - sea_level) * 0.35)
        lowland_elev = float(np.round(sea_level + (1.0 - sea_level) * 0.35, 4))
        lowland_L = float(np.clip(0.60 + albedo_mod, 0.48, 0.72))
        lowland_a = float(prim_a * 0.85)
        lowland_b = float(prim_b * 0.85)
        stops.append((lowland_elev, lowland_L, lowland_a, lowland_b))

        # Stop 4: Mountain Plateaus & Mineral Strata (elev = sea_level + (1 - sea_level) * 0.75)
        plateau_elev = float(np.round(sea_level + (1.0 - sea_level) * 0.75, 4))
        plateau_L = float(np.clip(0.74 + albedo_mod, 0.62, 0.84))
        plateau_a = float(sec_a * 0.90)
        plateau_b = float(sec_b * 0.90)
        stops.append((plateau_elev, plateau_L, plateau_a, plateau_b))

        # Stop 5: Alpine Spires / Crystalline Summit (elev = 1.00)
        # Night-owl devs get bioluminescent mineral glow; day devs get radiant glacial quartz
        if math_profile.diurnal_phase < 0.35:
            # Bioluminescent aurora summit
            summit_L = float(np.clip(0.85 + albedo_mod, 0.75, 0.92))
            summit_a = -0.08  # ethereal cyan/green
            summit_b = -0.04
        else:
            # High-albedo glacial summit
            summit_L = float(np.clip(0.94 + albedo_mod, 0.88, 0.99))
            summit_a = 0.00
            summit_b = 0.01
        stops.append((1.00, summit_L, summit_a, summit_b))

        nodes: list[ElevationRampNode] = []
        for elev, L, a, b in stops:
            hex_code = OklabColorConverter.oklab_to_hex(L, a, b)
            nodes.append(
                ElevationRampNode(
                    elevation=elev,
                    oklab=(
                        float(np.round(L, 5)),
                        float(np.round(a, 5)),
                        float(np.round(b, 5)),
                    ),
                    hex=hex_code,
                )
            )

        return nodes

    @classmethod
    def synthesize_material(
        cls,
        request: UserPlanetProfileRequest,
        math_profile: MathematicalProfile,
        topology: TopologyGenome,
        master_seeder: DeterministicSeeder,
    ) -> SurfaceMaterialGenome:
        """Synthesizes the complete SurfaceMaterialGenome coupling Whittaker climate and Oklab palette."""
        material_seeder = master_seeder.fork("surface_material")

        # 1. Base Temperature (°C): modulated by diurnal phase
        # Day developers (phase ~0.7-1.0) have warmer baseline; night developers cooler
        temp_base = float(
            np.clip(
                -5.0 + 25.0 * math_profile.diurnal_phase,
                -10.0,
                28.0,
            )
        )

        # 2. Equator Heat and Polar Cooling gradients
        equator_heat = float(
            np.clip(
                14.0 + 10.0 * math_profile.diurnal_coherence,
                10.0,
                26.0,
            )
        )
        polar_cooling = float(
            np.clip(
                -30.0 + 8.0 * (1.0 - math_profile.diurnal_coherence),
                -35.0,
                -15.0,
            )
        )

        # 3. Moisture Base and Ocean Evaporation
        # Coupled to sea level and Shannon language entropy (polyglots have higher atmospheric moisture)
        moisture_base = float(
            np.clip(
                0.25
                + 0.50 * topology.sea_level
                + 0.10 * math_profile.polyglot_diversity,
                0.15,
                0.90,
            )
        )
        ocean_evaporation = float(
            np.clip(
                0.35 + 0.45 * topology.sea_level + 0.10 * (math_profile.diurnal_phase),
                0.25,
                0.90,
            )
        )

        # 4. PBR Roughness Curve across 5 elevation stops:
        # [0.0 (trench), 0.25 (shelf), 0.50 (coast/lowland), 0.75 (plateau), 1.0 (summit)]
        # Oceanic stops are smoother; high plateaus and rocky crags are rougher
        r_noise = material_seeder.next_float(-0.03, 0.03)
        roughness_curve = [
            float(np.clip(0.12 + r_noise, 0.05, 0.25)),  # Abyssal ocean bed
            float(np.clip(0.22 + r_noise, 0.15, 0.35)),  # Submerged shelf
            float(np.clip(0.55 + r_noise, 0.40, 0.70)),  # Lowland / vegetative
            float(np.clip(0.78 + r_noise, 0.65, 0.90)),  # Rugged mountain crag
            float(np.clip(0.35 + r_noise, 0.20, 0.50)),  # Glacial / crystalline summit
        ]

        # 5. Metallic Factor & Crystalline Facetting
        # Repo resilience & star mass increase metallic sheen; diversity increases crystal facets
        metallic_factor = float(
            np.clip(
                0.08 + 0.45 * (1.0 - math_profile.repo_gini_index),
                0.05,
                0.65,
            )
        )
        crystalline_facetting = float(
            np.clip(
                0.15 + 0.65 * math_profile.polyglot_diversity,
                0.10,
                0.90,
            )
        )

        # 6. Generate 6-stop Elevation Color Ramp
        elevation_ramp = cls.generate_elevation_ramp(
            request.language_summary,
            math_profile,
            topology.sea_level,
            master_seeder,
        )

        return SurfaceMaterialGenome(
            temperature_base=float(np.round(temp_base, 2)),
            equator_heat=float(np.round(equator_heat, 2)),
            polar_cooling=float(np.round(polar_cooling, 2)),
            moisture_base=float(np.round(moisture_base, 4)),
            ocean_evaporation=float(np.round(ocean_evaporation, 4)),
            roughness_curve=[float(np.round(r, 4)) for r in roughness_curve],
            metallic_factor=float(np.round(metallic_factor, 4)),
            crystalline_facetting=float(np.round(crystalline_facetting, 4)),
            elevation_color_ramp=elevation_ramp,
        )
