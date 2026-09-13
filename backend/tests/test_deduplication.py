import pytest
from backend.app.services.deduplication import DeduplicationService

def test_url_normalization():
    raw_url = "https://www.theverge.com/2026/9/8/ai-breakthrough/?utm_source=twitter&utm_medium=social&ref=tech#section2"
    clean_url = DeduplicationService.normalize_url(raw_url)
    assert clean_url == "https://theverge.com/2026/9/8/ai-breakthrough"

def test_jaccard_similarity():
    t1 = "OpenAI Announces GPT-5 with Enhanced Reasoning Architecture"
    t2 = "OpenAI Releases GPT-5 Featuring Advanced Reasoning Capabilities"
    sim = DeduplicationService.jaccard_similarity(t1, t2)
    assert sim >= 0.25

    t3 = "NVIDIA Reports Record Blackwell GPU Production for Data Centers"
    sim_diff = DeduplicationService.jaccard_similarity(t1, t3)
    assert sim_diff < 0.10

def test_cluster_candidates():
    candidates = [
        {"title": "DeepSeek Releases Open-Weights Reasoning Model V3", "url": "https://techcrunch.com/deepseek-v3?ref=rss", "evidence_score": 6.0},
        {"title": "DeepSeek Launches V3 Open Reasoning Model Weights", "url": "https://venturebeat.com/deepseek-v3-weights?utm_source=feed", "evidence_score": 8.5},
        {"title": "Cerebras Files for IPO Highlighting Giant AI Chips", "url": "https://bloomberg.com/cerebras-ipo", "evidence_score": 7.0},
    ]
    clusters = DeduplicationService.cluster_candidates(candidates, threshold=0.40)
    assert len(clusters) == 2
    # The higher evidence candidate should represent the cluster
    rep_titles = [c["title"] for c in clusters]
    assert "DeepSeek Launches V3 Open Reasoning Model Weights" in rep_titles
