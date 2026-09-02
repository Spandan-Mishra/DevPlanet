from datetime import date

import numpy as np

from src.models.genome import MathematicalProfile
from src.models.request import (
    LandformRepo,
    LanguageStat,
    UserPlanetProfileRequest,
)


class MathProfileEngine:
    """Vectorized mathematical engine for extracting high-dimensional developer profiles.

    Computes Shannon entropy, Gini concentration, diurnal Fourier phase & coherence,
    and repository resilience without categorical AI heuristics.
    """

    @staticmethod
    def compute_shannon_entropy(languages: list[LanguageStat]) -> float:
        """Calculates the Shannon information entropy of the language distribution.

        H = - sum(p_i * log2(p_i)) where p_i is the byte proportion.
        Higher entropy represents polyglot diversity; lower entropy represents specialization.
        """
        if not languages:
            return 0.0

        byte_counts = np.array(
            [lang.bytes for lang in languages if lang.bytes > 0],
            dtype=np.float64,
        )
        if len(byte_counts) <= 1:
            return 0.0

        total_bytes = np.sum(byte_counts)
        if total_bytes <= 0:
            return 0.0

        probabilities = byte_counts / total_bytes
        # Filter out 0 probabilities to prevent log2(0)
        probabilities = probabilities[probabilities > 0]
        entropy = -np.sum(probabilities * np.log2(probabilities))
        return float(np.round(entropy, 4))

    @staticmethod
    def compute_polyglot_diversity(languages: list[LanguageStat]) -> float:
        """Calculates the Gini-Simpson diversity index: 1 - sum(p_i^2).

        Bounded strictly in [0.0, 1.0).
        0.0 = pure single language; approaching 1.0 = infinite uniformly distributed languages.
        """
        if not languages:
            return 0.0

        byte_counts = np.array(
            [lang.bytes for lang in languages if lang.bytes > 0],
            dtype=np.float64,
        )
        if len(byte_counts) <= 1:
            return 0.0

        total_bytes = np.sum(byte_counts)
        if total_bytes <= 0:
            return 0.0

        probabilities = byte_counts / total_bytes
        simpson_index = 1.0 - np.sum(probabilities**2)
        return float(np.clip(np.round(simpson_index, 4), 0.0, 1.0))

    @staticmethod
    def compute_diurnal_metrics(
        profile: UserPlanetProfileRequest,
    ) -> tuple[float, float]:
        """Performs 1D Discrete Fourier Transform (DFT) harmonic analysis on activity heatmap.

        Extracts:
        1. Diurnal Phase (Phi in [0.0, 1.0]): Circadian / weekly harmonic peak.
           0.0 = Sunday / Weekend peak, ~0.43 = Midweek Wednesday peak.
        2. Diurnal Coherence (R in [0.0, 1.0]): Measure of rhythmic consistency.
           1.0 = strictly concentrated on exact same days; 0.0 = completely uniform / random.
        """
        if not profile.activity_heatmap:
            return (0.0, 0.0)

        days_of_week: list[int] = []
        weights: list[int] = []

        for item in profile.activity_heatmap:
            if item.contribution_count > 0:
                try:
                    # ISO date format: YYYY-MM-DD
                    dt = date.fromisoformat(item.date)
                    # Python weekday: Monday=0, Sunday=6 -> map Sunday=0, Saturday=6
                    dow = (dt.weekday() + 1) % 7
                    days_of_week.append(dow)
                    weights.append(item.contribution_count)
                except (ValueError, TypeError):
                    continue

        if not weights or sum(weights) == 0:
            return (0.0, 0.0)

        w_arr = np.array(weights, dtype=np.float64)
        d_arr = np.array(days_of_week, dtype=np.float64)

        # 7-day period fundamental frequency
        angles = 2.0 * np.pi * d_arr / 7.0
        sin_sum = np.sum(w_arr * np.sin(angles))
        cos_sum = np.sum(w_arr * np.cos(angles))
        total_weight = np.sum(w_arr)

        raw_phase = np.arctan2(sin_sum, cos_sum)  # in [-pi, pi]
        # Circular modulo normalization aligned with dow: Sunday (dow=0) -> 0.0
        norm_phase = (raw_phase % (2.0 * np.pi)) / (2.0 * np.pi)

        # Coherence (resultant vector length normalized by total mass)
        coherence = np.sqrt(sin_sum**2 + cos_sum**2) / total_weight

        return (
            float(np.clip(np.round(norm_phase, 4), 0.0, 1.0)),
            float(np.clip(np.round(coherence, 4), 0.0, 1.0)),
        )

    @staticmethod
    def compute_repo_gini_index(landforms: list[LandformRepo]) -> float:
        """Calculates the Gini concentration coefficient of repository mass.

        Measures whether the developer's work is concentrated in a single monolithic
        repo (Gini ~ 1.0) or evenly balanced across many repos (Gini ~ 0.0).
        """
        if not landforms or len(landforms) <= 1:
            return 0.0

        # Repository mass formula: Stars * 3 + Forks * 2 + Commits + 1
        masses = np.array(
            [
                repo.stars * 3 + repo.forks * 2 + repo.commit_count + 1
                for repo in landforms
            ],
            dtype=np.float64,
        )

        n = len(masses)
        total_mass = np.sum(masses)
        if total_mass <= 0:
            return 0.0

        sorted_masses = np.sort(masses)
        # Vectorized Gini formula: (2 * sum(i * y_i)) / (n * sum(y_i)) - (n + 1) / n
        index = np.arange(1, n + 1)
        gini = (2.0 * np.sum(index * sorted_masses)) / (n * total_mass) - (
            n + 1.0
        ) / n
        return float(np.clip(np.round(gini, 4), 0.0, 1.0))

    @staticmethod
    def compute_repo_resilience(repo: LandformRepo) -> float:
        """Calculates the geological resilience/age factor for a single repository landmass.

        Psi in [0.1, 1.0]:
        High resilience = mature, established continental craton (high stars/forks/commits).
        Low resilience = youthful, sharp volcanic island / archipelago.
        """
        impact_score = (
            repo.stars * 3.0 + repo.forks * 2.0 + repo.commit_count + 1.0
        )
        # Normalization with soft saturation
        resilience = impact_score / (impact_score + 25.0)
        return float(np.clip(np.round(resilience, 4), 0.1, 1.0))

    @classmethod
    def generate_profile(
        cls, request: UserPlanetProfileRequest
    ) -> MathematicalProfile:
        """Synthesizes the complete mathematical profile from the ingestion request."""
        shannon_entropy = cls.compute_shannon_entropy(request.language_summary)
        polyglot_diversity = cls.compute_polyglot_diversity(
            request.language_summary
        )
        diurnal_phase, diurnal_coherence = cls.compute_diurnal_metrics(request)
        repo_gini = cls.compute_repo_gini_index(request.landforms)

        return MathematicalProfile(
            shannon_entropy=shannon_entropy,
            diurnal_phase=diurnal_phase,
            diurnal_coherence=diurnal_coherence,
            repo_gini_index=repo_gini,
            polyglot_diversity=polyglot_diversity,
        )
