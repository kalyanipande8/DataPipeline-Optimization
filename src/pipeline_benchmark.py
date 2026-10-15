"""Real benchmark suite: processes the 340-sample workload with Python's
multiprocessing across varying core counts, measuring genuine wall-clock
speedup and parallel efficiency (speedup / n_cores) -- real parallelism,
not simulated timing delays."""
from __future__ import annotations

import multiprocessing as mp
import time

from .workload import process_one_sample, N_SAMPLES

MAX_CORES = min(4, mp.cpu_count())


def run_with_n_cores(n_cores: int, n_samples: int = N_SAMPLES) -> float:
    start = time.perf_counter()
    if n_cores == 1:
        for i in range(n_samples):
            process_one_sample(i)
    else:
        with mp.Pool(n_cores) as pool:
            pool.map(process_one_sample, range(n_samples))
    return time.perf_counter() - start


def benchmark_core_scaling(n_samples: int = N_SAMPLES, max_cores: int = MAX_CORES) -> list[dict]:
    results = []
    baseline_time = None
    for n_cores in range(1, max_cores + 1):
        elapsed = run_with_n_cores(n_cores, n_samples)
        if baseline_time is None:
            baseline_time = elapsed
        speedup = round(baseline_time / elapsed, 3)
        efficiency_pct = round(100 * speedup / n_cores, 2)
        results.append({"n_cores": n_cores, "elapsed_sec": round(elapsed, 3),
                         "speedup": speedup, "parallel_efficiency_pct": efficiency_pct})
    return results


if __name__ == "__main__":
    for r in benchmark_core_scaling():
        print(r)
