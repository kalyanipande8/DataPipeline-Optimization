# High-Performance Data Pipeline & Optimization

Real multi-core benchmarking (Python `multiprocessing`, genuine process-
level parallelism, not simulated timing) of a 340-sample CPU-bound
workload, with a real performance-regression monitor comparing run-over-
run throughput.

> Designed HPC-ready data pipelines processing a 340-sample workload;
> benchmarked real core-scaling efficiency across 1-4 cores. Implemented
> a benchmark suite and performance-regression monitor; found and fixed a
> real BLAS-thread-oversubscription issue that was hiding the pipeline's
> actual multi-core speedup during development.

## What's real vs. synthetic — read this first

**Real:** the workload (`src/workload.py`) is genuine CPU-bound work (
repeated matrix multiplication), not a `sleep()` placeholder, so the
core-scaling benchmark (`src/pipeline_benchmark.py`) measures real
process-level parallelism via Python's `multiprocessing.Pool`. The
regression monitor (`src/performance_monitoring.py`) is demonstrated to
both correctly pass on a similar run and correctly flag a real injected
3x slowdown — not a check that always passes. The debugging story is
also real: an initial benchmark run showed *no* multi-core speedup at
all, traced to numpy's own internal BLAS multithreading competing with
multiprocessing's process-level parallelism (oversubscription) — fixed by
pinning each worker to single-threaded BLAS
(`OMP_NUM_THREADS`/`MKL_NUM_THREADS`/`OPENBLAS_NUM_THREADS=1`), after
which real (if modest) speedup appeared.

**Synthetic:** there is no real HPC cluster or Databricks workspace in
this environment; the benchmark runs on this machine's available CPU
cores (up to 4 used, out of 8 detected) via standard-library
multiprocessing, honestly disclosed as a local stand-in for a true HPC
job scheduler.

## Scientific approach

1. **Workload** (`src/workload.py`): a 250×250 matrix power-iteration
   computation per sample — real, meaningful CPU work (~60ms/sample
   single-threaded).

2. **Benchmark suite** (`src/pipeline_benchmark.py`): runs the 340-sample
   workload with 1 through 4 worker processes, measuring real wall-clock
   speedup and parallel efficiency (speedup / n_cores) at each core count.

3. **Performance monitoring** (`src/performance_monitoring.py`): compares
   a new benchmark run's best throughput against a stored baseline,
   flagging a regression if throughput degrades beyond a 15% tolerance.

## Results (real, measured on this machine, 4 cores used of 8 available)

```
340-sample workload, core-scaling benchmark:
  1 core:  baseline (speedup 1.0x, 100% efficiency by definition)
  2 cores: ~1.2x speedup (~60% parallel efficiency)
  3 cores: ~1.3x speedup (~43% parallel efficiency)
  4 cores: ~1.25x speedup (~31% parallel efficiency)
```

The speedup is real but modest and actually *declines* in relative
efficiency as core count increases — an honest reflection of
multiprocessing's real overhead (process spawn, data pickling/transfer)
relative to this workload's per-task runtime, not an idealized linear-
scaling claim.

`tests/test_pipeline.py` (5 tests, all passing) checks: the benchmark
runs for every requested core count, the single-core baseline correctly
has speedup 1.0, at least one multi-core configuration shows real
measurable speedup, and the regression monitor both correctly passes on
similar runs and correctly flags a real injected slowdown.

## Usage

```bash
pip install -r requirements.txt
python3 run_all.py            # runs the core-scaling benchmark and regression check
python3 -m pytest tests/ -v    # run the test suite
```

Outputs are written to `results/summary.json`.

## Project structure

```
src/
  workload.py              # real CPU-bound per-sample computation
  pipeline_benchmark.py       # multiprocessing core-scaling benchmark
  performance_monitoring.py      # run-over-run regression detection
run_all.py                         # end-to-end pipeline
tests/test_pipeline.py               # pytest suite
```

## Tech stack

Python 3.11, numpy, multiprocessing (standard library), pytest.

## Limitations

- No real HPC cluster or Databricks workspace is used; benchmarking runs
  locally on up to 4 of this machine's available cores.
- Parallel efficiency at this task granularity is genuinely limited by
  multiprocessing overhead (not a Databricks-cluster-scale result); a
  real distributed system (Spark/Databricks) amortizes that overhead
  very differently.
