import pytest
from backend.app.services.scoring import ScoringEngine, DEFAULT_WEIGHTS

def test_composite_score_standard():
    # S = 0.35*8 + 0.25*7 + 0.20*9 - 0.20*3 + 0.15*1 = 2.8 + 1.75 + 1.8 - 0.6 + 0.15 = 5.9
    score = ScoringEngine.compute_composite_score(
        significance=8.0,
        novelty=7.0,
        evidence=9.0,
        saturation=3.0,
        feedback_bias=1.0,
        weights=DEFAULT_WEIGHTS,
    )
    assert score == 5.9

def test_composite_score_clamping():
    # Score inputs outside [1, 10] or feedback bias outside [-3, 3] should be clamped
    score_clamped = ScoringEngine.compute_composite_score(
        significance=20.0, # clamped to 10
        novelty=0.0,      # clamped to 1
        evidence=10.0,
        saturation=1.0,
        feedback_bias=5.0, # clamped to 3
        weights=DEFAULT_WEIGHTS,
    )
    assert score_clamped > 0.0

def test_cold_start_feedback_zeroed():
    weights_cold = DEFAULT_WEIGHTS.copy()
    weights_cold["feedback_weight"] = 0.0
    score1 = ScoringEngine.compute_composite_score(8.0, 7.0, 9.0, 3.0, feedback_bias=3.0, weights=weights_cold)
    score2 = ScoringEngine.compute_composite_score(8.0, 7.0, 9.0, 3.0, feedback_bias=-3.0, weights=weights_cold)
    assert score1 == score2

def test_low_signal_day_threshold():
    # Fewer than 5 qualified candidates
    candidates = [
        {"title": "Story 1", "composite_score": 5.5, "novelty_score": 7.0, "saturation_score": 3.0, "url": "https://a.com/1"},
        {"title": "Story 2", "composite_score": 4.5, "novelty_score": 6.0, "saturation_score": 4.0, "url": "https://a.com/2"},
        {"title": "Story 3", "composite_score": 3.0, "novelty_score": 5.0, "saturation_score": 6.0, "url": "https://a.com/3"},
    ]
    selected, is_low_signal, notice = ScoringEngine.partition_portfolio(candidates, target_count=8)
    assert is_low_signal is True
    assert "Low-signal day" in notice
    assert len(selected) == 2 # only the 2 >= 4.0

def test_portfolio_partition_sufficient_candidates():
    candidates = []
    for i in range(15):
        candidates.append({
            "title": f"Story {i}",
            "composite_score": 5.0 + (i * 0.2),
            "novelty_score": 8.5 if i % 4 == 0 else (7.0 if i % 2 == 0 else 5.0),
            "saturation_score": 3.0 if i % 4 == 0 else 5.0,
            "url": f"https://example.com/story-{i}",
        })
    selected, is_low_signal, notice = ScoringEngine.partition_portfolio(candidates, target_count=8)
    assert is_low_signal is False
    assert notice == ""
    assert len(selected) == 8
