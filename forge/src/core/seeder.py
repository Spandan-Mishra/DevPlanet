import hashlib
from typing import Self


class DeterministicSeeder:
    """Deterministic pseudo-random number generator and hierarchical seed graph.

    Uses SHA-256 for cryptographic string-to-seed derivation and SplitMix64
    for high-performance, uniform 64-bit integer and float generation.
    Supports hierarchical domain forking to prevent cross-feature state pollution.
    """

    MASK_64: int = 0xFFFFFFFFFFFFFFFF
    SPLITMIX64_INCREMENT: int = 0x9E3779B97F4A7C15
    SPLITMIX64_MUL1: int = 0xBF58476D1CE4E5B9
    SPLITMIX64_MUL2: int = 0x94D049BB133111EB

    def __init__(self, seed: int) -> None:
        self.master_seed: int = seed & self.MASK_64
        self.state: int = self.master_seed

    @classmethod
    def from_string(cls, input_str: str, salt: str = "") -> Self:
        """Derives a deterministic 64-bit seed from an input string (e.g. username + date)."""
        combined = f"{input_str}:{salt}".encode()
        digest = hashlib.sha256(combined).digest()
        # Take first 8 bytes big-endian as uint64
        seed_int = int.from_bytes(digest[:8], byteorder="big", signed=False)
        return cls(seed_int)

    def next_uint64(self) -> int:
        """Generates the next pseudo-random 64-bit unsigned integer using SplitMix64."""
        self.state = (self.state + self.SPLITMIX64_INCREMENT) & self.MASK_64
        z = self.state
        z = ((z ^ (z >> 30)) * self.SPLITMIX64_MUL1) & self.MASK_64
        z = ((z ^ (z >> 27)) * self.SPLITMIX64_MUL2) & self.MASK_64
        return (z ^ (z >> 31)) & self.MASK_64

    def next_float(self, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Generates a uniform float in the range [min_val, max_val).

        Uses 53-bit precision equivalent to standard IEEE 754 float mantissa.
        """
        if min_val >= max_val:
            raise ValueError(
                f"min_val ({min_val}) must be strictly less than max_val ({max_val})"
            )
        # 53-bit resolution float in [0.0, 1.0)
        unit = (self.next_uint64() >> 11) * (1.0 / (1 << 53))
        return min_val + unit * (max_val - min_val)

    def next_int(self, min_val: int, max_val: int) -> int:
        """Generates a uniform integer in the inclusive range [min_val, max_val]."""
        if min_val > max_val:
            raise ValueError(f"min_val ({min_val}) must be <= max_val ({max_val})")
        if min_val == max_val:
            return min_val
        span = (max_val - min_val) + 1
        return min_val + (self.next_uint64() % span)

    def fork(self, domain_tag: str) -> "DeterministicSeeder":
        """Forks an independent, deterministic child PRNG for a specific subsystem.

        Subsystems: 'topology', 'climate', 'celestial', 'ecosystem', repo names, etc.
        Guarantees that sampling from one subsystem does NOT advance the state of others.
        """
        domain_entropy = hashlib.sha256(
            f"{self.master_seed:016x}:{domain_tag}".encode()
        ).digest()
        derived_seed = int.from_bytes(domain_entropy[:8], byteorder="big", signed=False)
        return DeterministicSeeder(derived_seed)

    @property
    def hex_seed(self) -> str:
        """Returns the 64-bit master seed formatted as a 0x-prefixed 16-char hex string."""
        return f"0x{self.master_seed:016x}"
