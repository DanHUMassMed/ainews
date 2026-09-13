"""Unit and regression test for Golden Evaluation Benchmark."""

import pytest
from agents.tests.eval.eval_runner import run_evaluation_benchmark

def test_golden_eval_benchmark_thresholds():
    """Verify precision, recall, and fluff rejection meet PRD 2.0 Section 33 targets."""
    res = run_evaluation_benchmark()
    m = res["metrics"]

    assert m["total_cases"] >= 15, "Golden dataset must contain at least 15 cases"
    assert m["precision"] >= 0.85, f"Precision {m['precision']:.2f} below 0.85 threshold"
    assert m["recall"] >= 0.85, f"Recall {m['recall']:.2f} below 0.85 threshold"
    assert m["fluff_rejection_rate"] >= 0.95, f"Fluff rejection {m['fluff_rejection_rate']:.2f} below 0.95 threshold"
    assert m["passed"] is True
