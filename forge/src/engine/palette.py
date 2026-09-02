import re

import numpy as np


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
