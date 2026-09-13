# Evaluation of AI News Sources & Whitelist (Research Sandbox)

> [!NOTE]
> **Strict Separation from Production**:
> This `evaluation/` directory is strictly for evaluating new concepts, test harnesses, and candidate sources.
> No production pipeline code relies on or references files in this directory.
> The authoritative production whitelist lives in `backend/app/data/whitelist.csv` and is consumed by `backend.app.services.whitelist.WhitelistService`.

## Files in this Directory

- **`whitelist.csv`**: Experimental scratchpad of candidate source URLs.
- **`evaluation_plan.md`**: Architectural evaluation criteria (reachability, anti-bot defenses, signal-to-noise ratio, scoping).
- **`evaluate_whitelist.py`**: Automated audit runner script for diagnostic testing of new domains.
- **`whitelist_evaluated.csv`**: Evaluated output scorecard from the latest evaluation run.
- **`evaluation_report.md`**: Human-readable audit report and domain scoping guide.
- **`sync_editorial_sources.py`**: Utility to sync audit results to PostgreSQL `editorial_memories`.

## How to Run an Evaluation Experiment

To test new candidate domains without affecting production:

```bash
# Run the 4-dimensional audit across candidate domains
backend/venv/bin/python3 evaluation/evaluate_whitelist.py
```
