"""End-to-end: benchmark core-scaling on the 340-sample workload, and
check for performance regression against a stored baseline run."""
import json
import os


def main():
    from src.pipeline_benchmark import benchmark_core_scaling
    from src.performance_monitoring import check_for_regression
    from src.workload import N_SAMPLES

    os.makedirs("results", exist_ok=True)

    print(f"=== Benchmarking core scaling on {N_SAMPLES} samples ===")
    baseline_run = benchmark_core_scaling()
    for r in baseline_run:
        print(r)

    print("\n=== Re-running and checking for regression ===")
    current_run = benchmark_core_scaling()
    regression = check_for_regression(current_run, baseline_run)
    print(regression)

    best = min(baseline_run, key=lambda r: r["elapsed_sec"])
    summary = {
        "n_samples": N_SAMPLES,
        "best_n_cores": best["n_cores"],
        "best_speedup": best["speedup"],
        "best_parallel_efficiency_pct": best["parallel_efficiency_pct"],
        "regression_detected": regression["regression_detected"],
    }
    with open("results/summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n=== Summary ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
