import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from src.pipeline_benchmark import benchmark_core_scaling
from src.performance_monitoring import check_for_regression


@pytest.fixture(scope="module")
def benchmark():
    return benchmark_core_scaling(n_samples=60)


def test_benchmark_runs_for_every_core_count(benchmark):
    assert len(benchmark) >= 2


def test_single_core_baseline_has_speedup_of_one(benchmark):
    assert benchmark[0]["n_cores"] == 1
    assert benchmark[0]["speedup"] == 1.0


def test_multi_core_shows_measurable_speedup(benchmark):
    """At least one multi-core configuration should show a real speedup
    over the single-core baseline -- not a trivial 1.0 everywhere."""
    assert any(r["speedup"] > 1.0 for r in benchmark[1:])


def test_regression_check_correctly_passes_on_similar_runs(benchmark):
    result = check_for_regression(benchmark, benchmark)
    assert result["regression_detected"] is False


def test_regression_check_correctly_flags_a_real_slowdown(benchmark):
    slow_run = [{**r, "elapsed_sec": r["elapsed_sec"] * 3} for r in benchmark]
    result = check_for_regression(slow_run, benchmark)
    assert result["regression_detected"] is True
