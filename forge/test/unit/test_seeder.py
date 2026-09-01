import pytest

from src.core.seeder import DeterministicSeeder


def test_deterministic_seeder_reproducibility() -> None:
    """Verifies that the same seed and input string yield identical random sequences."""
    seeder_a = DeterministicSeeder.from_string("octocat", salt="2026-09-01")
    seeder_b = DeterministicSeeder.from_string("octocat", salt="2026-09-01")

    assert seeder_a.master_seed == seeder_b.master_seed
    assert seeder_a.hex_seed == seeder_b.hex_seed

    # Sequence of 10 values must match 1:1
    seq_a = [seeder_a.next_uint64() for _ in range(10)]
    seq_b = [seeder_b.next_uint64() for _ in range(10)]
    assert seq_a == seq_b


def test_deterministic_seeder_distinct_inputs() -> None:
    """Verifies that different usernames produce completely different master seeds."""
    seeder_a = DeterministicSeeder.from_string("octocat")
    seeder_b = DeterministicSeeder.from_string("torvalds")

    assert seeder_a.master_seed != seeder_b.master_seed
    assert seeder_a.next_uint64() != seeder_b.next_uint64()


def test_hierarchical_domain_forking_isolation() -> None:
    """Verifies that domain forking provides deterministic, isolated sub-PRNGs."""
    master = DeterministicSeeder.from_string("octocat")

    terrain_seeder_1 = master.fork("topology")
    climate_seeder = master.fork("climate")

    # Sample from terrain
    t1 = terrain_seeder_1.next_float(0.0, 100.0)
    t2 = terrain_seeder_1.next_float(0.0, 100.0)

    # Sample from climate
    c1 = climate_seeder.next_float(0.0, 100.0)

    # Climate must not match terrain
    assert t1 != c1

    # Re-forking terrain from master produces identical initial sequence
    terrain_seeder_2 = master.fork("topology")
    assert terrain_seeder_2.next_float(0.0, 100.0) == t1
    assert terrain_seeder_2.next_float(0.0, 100.0) == t2


def test_next_float_bounds() -> None:
    """Verifies that next_float respects min_val and max_val bounds."""
    seeder = DeterministicSeeder.from_string("test_bounds")

    for _ in range(100):
        val = seeder.next_float(10.0, 20.0)
        assert 10.0 <= val < 20.0

    with pytest.raises(ValueError, match="strictly less"):
        seeder.next_float(20.0, 10.0)


def test_next_int_bounds() -> None:
    """Verifies that next_int produces values within [min_val, max_val] inclusive."""
    seeder = DeterministicSeeder.from_string("test_int")

    samples = [seeder.next_int(1, 6) for _ in range(200)]
    assert min(samples) >= 1
    assert max(samples) <= 6
    assert len(set(samples)) == 6  # All faces of die rolled

    # Single value range
    assert seeder.next_int(5, 5) == 5

    with pytest.raises(ValueError, match="must be <="):
        seeder.next_int(10, 2)
