import asyncio
from backend.app.core.database import AsyncSessionLocal
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.app.models.edition import Edition

async def update_intros():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Edition).options(selectinload(Edition.stories)).order_by(Edition.date.desc())
        )
        editions = result.scalars().all()
        for ed in editions:
            lead = next((s for s in ed.stories if s.is_lead), ed.stories[0] if ed.stories else None)
            secondaries = [s for s in ed.stories if s != lead]
            
            if str(ed.date) == "2026-09-09":
                ed.title = "AI Industry Briefing: Hugging Face 4-Bit KV-Cache Sharding, DeepMind Verification & vLLM Speculative Prefill"
                sec_titles = [s.title.strip() for s in secondaries]
                joined_sec = ", ".join(sec_titles[:-1]) + f", and {sec_titles[-1]}"
                ed.introduction = (
                    f"Today's briefing leads with {lead.title}: {lead.summary.rstrip('.')}. "
                    f"Key secondary developments evaluate {joined_sec}."
                )
            elif str(ed.date) == "2026-09-08":
                ed.title = "AI Industry Briefing: Multi-Node Hardware Prefill, Distributed Prefix Caching & Agent Safety Standards"
                ed.introduction = (
                    "September 8 briefing examines accelerator scaling and agentic execution: "
                    "NVIDIA releases architectural benchmarks for disaggregated prefill/decode cluster topologies, "
                    "while SGLang rolls out multi-node RadixAttention prefix caching to slash tool-loop latency. "
                    "Concurrently, NIST issues standardized evaluation suites for autonomous agent containment, "
                    "FlashInfer merges portable fused GQA kernels, and Triton adds automated memory tiling for custom silicon."
                )
            elif str(ed.date) == "2026-09-07":
                ed.title = "AI Industry Briefing: Reasoning Token Scaling, Distributed MoE Scheduling & Verified Agent Baselines"
                ed.introduction = (
                    "September 7 briefing analyzes the shift toward test-time reasoning compute: "
                    "New arXiv research establishes empirical verification gains across multi-turn reasoning traces, "
                    "PyTorch extends async pipeline parallelism for massive MoE architectures, "
                    "Hugging Face alongside the Meta Llama ecosystem standardizes reproducible evaluation baselines for autonomous tool orchestration, "
                    "and vLLM benchmarks 4x speedups on distributed reasoning traces."
                )
        await session.commit()
        print("Successfully synchronized all archive highlights and titles.")

if __name__ == "__main__":
    asyncio.run(update_intros())
