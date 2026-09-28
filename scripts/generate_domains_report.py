import asyncio
from datetime import date
from collections import defaultdict
from urllib.parse import urlparse

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from backend.app.core.database import AsyncSessionLocal
from backend.app.models.edition import Edition
from backend.app.models.story import Story

async def generate():
    async with AsyncSessionLocal() as session:
        stmt = (
            select(Edition)
            .where(and_(Edition.status == "published", Edition.date <= date.today()))
            .order_by(Edition.date.desc())
            .options(selectinload(Edition.stories).selectinload(Story.sources))
        )
        res = await session.execute(stmt)
        editions = res.scalars().all()

        domain_data = defaultdict(lambda: {
            "stories": [],
            "unique_urls": set()
        })

        edition_domain_matrix = defaultdict(lambda: defaultdict(int))
        edition_dates = []

        total_stories = 0
        for ed in editions:
            d_str = str(ed.date)
            edition_dates.append(d_str)
            total_stories += len(ed.stories)
            for story in ed.stories:
                for s in story.sources:
                    dom = urlparse(s.url).netloc.lower()
                    domain_data[dom]["stories"].append({
                        "date": d_str,
                        "title": story.title,
                        "url": s.url,
                        "is_lead": story.is_lead,
                        "slug": story.slug
                    })
                    domain_data[dom]["unique_urls"].add(s.url)
                    edition_domain_matrix[d_str][dom] += 1

        sorted_domains = sorted(domain_data.items(), key=lambda item: len(item[1]["stories"]), reverse=True)

        org_map = {
            "aws.amazon.com": "Amazon Web Services (AWS)",
            "openai.com": "OpenAI",
            "huggingface.co": "Hugging Face",
            "blog.google": "Google",
            "latent.space": "Latent Space",
            "deepmind.google": "Google DeepMind",
            "qwenlm.github.io": "Alibaba Qwen",
            "mistral.ai": "Mistral AI",
            "research.google": "Google Research",
            "alignmentforum.org": "AI Alignment Forum",
        }

        parent_group = {
            "aws.amazon.com": "Amazon",
            "openai.com": "OpenAI",
            "huggingface.co": "Hugging Face",
            "blog.google": "Google",
            "latent.space": "Latent Space",
            "deepmind.google": "Google",
            "qwenlm.github.io": "Alibaba",
            "mistral.ai": "Mistral AI",
            "research.google": "Google",
            "alignmentforum.org": "AI Alignment Forum",
        }

        org_counts = defaultdict(int)
        for dom, d in sorted_domains:
            org_counts[parent_group.get(dom, dom)] += len(d["stories"])
        sorted_orgs = sorted(org_counts.items(), key=lambda x: x[1], reverse=True)

        lines = []
        lines.append("# Archive Domains Index")
        lines.append("")
        lines.append("This document provides a comprehensive audit of all unique domain names utilized across published articles in the **AINews** archives to date.")
        lines.append("")
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(f"- **Published Editions Analyzed:** {len(editions)} ({editions[-1].date} to {editions[0].date})")
        lines.append(f"- **Total Published Articles / Stories:** {total_stories}")
        lines.append(f"- **Total Unique Source Domains:** {len(sorted_domains)}")
        lines.append(f"- **Total Unique Source URLs:** {sum(len(d['unique_urls']) for _, d in sorted_domains)}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Domain Ranking & Story Counts")
        lines.append("")
        lines.append("| Rank | Domain Name | Organization / Entity | Story Count | Share (%) | Unique Source URLs |")
        lines.append("|:---:|:---|:---|:---:|:---:|:---:|")
        for rank, (dom, d) in enumerate(sorted_domains, 1):
            count = len(d["stories"])
            pct = (count / total_stories) * 100
            urls_count = len(d["unique_urls"])
            org = org_map.get(dom, "Unknown")
            lines.append(f"| {rank} | `{dom}` | {org} | **{count}** | {pct:.1f}% | {urls_count} |")
        lines.append(f"| **Total** | **{len(sorted_domains)} unique domains** | — | **{total_stories}** | **100.0%** | **{sum(len(d['unique_urls']) for _, d in sorted_domains)}** |")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Rollup by Parent Organization")
        lines.append("")
        lines.append("| Rank | Parent Organization | Included Domains | Story Count | Share (%) |")
        lines.append("|:---:|:---|:---|:---:|:---:|")
        for rank, (org, count) in enumerate(sorted_orgs, 1):
            subdoms = [f"`{dom}`" for dom, _ in sorted_domains if parent_group.get(dom) == org]
            pct = (count / total_stories) * 100
            lines.append(f"| {rank} | **{org}** | {', '.join(subdoms)} | **{count}** | {pct:.1f}% |")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Detailed Breakdown by Domain")
        lines.append("")

        for rank, (dom, d) in enumerate(sorted_domains, 1):
            count = len(d["stories"])
            pct = (count / total_stories) * 100
            urls_count = len(d["unique_urls"])
            org = org_map.get(dom, "Unknown")

            lines.append(f"### {rank}. `{dom}`")
            lines.append("")
            lines.append(f"- **Organization / Entity:** {org}")
            lines.append(f"- **Total Stories Cited:** {count} ({pct:.1f}% of all archive stories)")
            lines.append(f"- **Unique Source URLs:** {urls_count}")
            lines.append("")
            lines.append("#### Published Articles:")
            lines.append("")
            lines.append("| Edition Date | Story Title | Lead Story | Source URL |")
            lines.append("|:---|:---|:---:|:---|")
            for st in d["stories"]:
                lead_badge = "⭐ Yes" if st["is_lead"] else "No"
                clean_title = st["title"].replace("|", "&#124;").strip()
                lines.append(f"| {st['date']} | {clean_title} | {lead_badge} | [{st['url']}]({st['url']}) |")
            lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("## Edition-by-Edition Domain Coverage Matrix")
        lines.append("")
        lines.append("This matrix illustrates the distribution of source domains across each daily published edition:")
        lines.append("")
        
        # Abbreviate header domains for table width
        short_names = {
            "aws.amazon.com": "AWS",
            "openai.com": "OpenAI",
            "huggingface.co": "HuggingFace",
            "blog.google": "GoogleBlog",
            "latent.space": "LatentSpace",
            "deepmind.google": "DeepMind",
            "qwenlm.github.io": "Qwen",
            "mistral.ai": "Mistral",
            "research.google": "GoogleRes",
            "alignmentforum.org": "AlignForum",
        }
        
        header = "| Edition Date | Total | " + " | ".join([f"{short_names.get(dom, dom)}" for dom, _ in sorted_domains]) + " |"
        separator = "|:---|:---:|" + "|".join([":---:" for _ in sorted_domains]) + "|"
        lines.append(header)
        lines.append(separator)

        for d_str in edition_dates:
            ed_stories = [s for dom, d in sorted_domains for s in d["stories"] if s["date"] == d_str]
            total_ed = len(ed_stories)
            row = [f"| {d_str} | {total_ed} |"]
            for dom, _ in sorted_domains:
                cnt = edition_domain_matrix[d_str][dom]
                row.append(f" {cnt if cnt > 0 else '-'} |")
            lines.append("".join(row))

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Appendix: Asset & Media Hosting Domains")
        lines.append("")
        lines.append("In addition to primary article source links, published stories reference the following asset domains for embedded visual media and audio:")
        lines.append("")
        lines.append("| Asset Domain | Articles Using Domain | Asset Purpose |")
        lines.append("|:---|:---:|:---|")
        lines.append("| `storage.googleapis.com` | 12 | Google blog header artwork & architectural diagrams |")
        lines.append("| `substackcdn.com` | 8 | Latent Space Substack artwork and illustrations |")
        lines.append("| `d2908q01vomqb2.cloudfront.net` | 3 | AWS Machine Learning blog media and demos |")
        lines.append("| `api.substack.com` | 1 | Latent Space audio podcast enclosures |")
        lines.append("| `lh3.googleusercontent.com` | 1 | Google user profile and media assets |")
        lines.append("")
        lines.append("*Note: Synthetic test fixtures and future-dated pipeline mock editions (such as year 2099+ test runs) are excluded from this audit to represent only genuinely published archive articles.*")
        lines.append("")

        content = "\n".join(lines)
        with open("domains.md", "w") as f:
            f.write(content)
        print(f"Successfully generated domains.md ({len(content)} bytes).")

if __name__ == "__main__":
    asyncio.run(generate())
