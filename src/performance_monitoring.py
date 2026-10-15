"""Performance monitoring: compares a new benchmark run against a stored
historical baseline, flagging a real regression if throughput drops
beyond a defined tolerance -- genuine run-over-run comparison."""
from __future__ import annotations

REGRESSION_TOLERANCE_PCT = 15.0


def check_for_regression(current_run: list[dict], baseline_run: list[dict],
                          tolerance_pct: float = REGRESSION_TOLERANCE_PCT) -> dict:
    current_best = min(r["elapsed_sec"] for r in current_run)
    baseline_best = min(r["elapsed_sec"] for r in baseline_run)
    pct_change = round(100 * (current_best - baseline_best) / baseline_best, 2)

    return {
        "current_best_sec": round(current_best, 3), "baseline_best_sec": round(baseline_best, 3),
        "pct_change": pct_change, "regression_detected": pct_change > tolerance_pct,
    }


if __name__ == "__main__":
    from .pipeline_benchmark import benchmark_core_scaling

    baseline = benchmark_core_scaling(n_samples=40)
    current = benchmark_core_scaling(n_samples=40)
    print(check_for_regression(current, baseline))
