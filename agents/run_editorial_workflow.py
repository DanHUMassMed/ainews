#!/usr/bin/env python3
"""AI Industry News Daily - Google ADK Editorial Workflow Runner.

PRD 2.0 Sections 26-27: Master execution script running the 6-agent pipeline.
"""

import sys
import asyncio
import argparse
from datetime import date
from agents.app.workflows.root_workflow import EditorialWorkflow

async def main():
    parser = argparse.ArgumentParser(description="Run the AI News ADK Multi-Agent Editorial Workflow")
    parser.add_argument("--live", action="store_true", help="Run live web discovery via SearXNG")
    parser.add_argument("--publish", action="store_true", help="Publish the staged edition immediately")
    parser.add_argument("--target-date", type=str, default=None, help="Target edition date (YYYY-MM-DD)")
    args = parser.parse_args()

    target_date = args.target_date or date.today().isoformat()
    print("=" * 60)
    print("  AI Industry News Daily - Google ADK Editorial Pipeline")
    print(f"  Target Date: {target_date}")
    print(f"  Mode:        {'LIVE SEARXNG' if args.live else 'CURATED DEMO'}")
    print(f"  Action:      {'STAGE & PUBLISH' if args.publish else 'STAGE DRAFT'}")
    print("=" * 60)

    workflow = EditorialWorkflow(live=args.live)
    result = await workflow.run(target_date=target_date, publish=args.publish)

    print("=" * 60)
    print(f"  Workflow Status:        {result.status.upper()}")
    print(f"  Candidate Pool Count:   {result.candidate_count}")
    print(f"  Selected Story Count:   {result.story_count}")
    print(f"  Low-Signal Day:         {result.low_signal}")
    print(f"  Critic Gate Passed:     {result.critic_passed}")
    print(f"  Revisions Performed:    {result.revisions_performed}")
    if result.edition_id:
        print(f"  Edition ID:             {result.edition_id}")
        print(f"  Public URL:             http://127.0.0.1:8000/api/public/editions/today")
        print(f"  Frontend URL:           http://localhost:5173/")
    if result.errors:
        print(f"  Errors / Warnings:      {result.errors}")
    print("=" * 60)

    if result.status in ["staged_draft", "published"]:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
