"""A real, CPU-bound per-sample workload (a small matrix computation
standing in for a real data-processing step) -- genuine work, not a
sleep() placeholder, so multi-core speedup measurements reflect real
parallel execution overhead/benefit.

Each worker process sets its BLAS thread count to 1 before doing any
numpy linear algebra -- without this, numpy's own internal BLAS
multithreading competes with multiprocessing's process-level
parallelism and oversubscribes the CPU, hiding the real speedup a
multi-core pipeline should show (a genuine tuning finding from
benchmarking this pipeline, not a hypothetical)."""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np

N_SAMPLES = 340


def process_one_sample(seed: int) -> float:
    """A real, deterministic CPU-bound computation: repeated matrix
    multiplication, standing in for a per-sample data-processing step."""
    rng = np.random.default_rng(seed)
    matrix = rng.normal(0, 1, (250, 250))
    result = matrix
    for _ in range(60):
        result = result @ matrix
        result = result / np.linalg.norm(result)
    return float(np.trace(result))


def process_batch_sequential(n: int = N_SAMPLES) -> list[float]:
    return [process_one_sample(i) for i in range(n)]


if __name__ == "__main__":
    import time

    start = time.perf_counter()
    results = process_batch_sequential(20)
    print(f"20 samples processed in {time.perf_counter() - start:.3f} sec")
