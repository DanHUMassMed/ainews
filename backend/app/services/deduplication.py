import re
from urllib.parse import urlparse, urlunparse
from typing import List, Dict, Any, Set

class DeduplicationService:
    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Strips marketing tracking parameters (utm_*, ref, etc.) and fragments.
        """
        if not url:
            return ""
        parsed = urlparse(url.strip())
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        
        # Remove common tracking params
        query_parts = []
        if parsed.query:
            for param in parsed.query.split("&"):
                k = param.split("=")[0].lower()
                if not (k.startswith("utm_") or k in ("ref", "source", "fbclid", "gclid", "t", "spm")):
                    query_parts.append(param)
        
        new_query = "&".join(query_parts)
        path = parsed.path.rstrip("/")
        return urlunparse((parsed.scheme.lower(), netloc, path, "", new_query, ""))

    @staticmethod
    def tokenize_title(title: str) -> Set[str]:
        words = re.findall(r'[a-zA-Z0-9]+', title.lower())
        stopwords = {
            "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "with",
            "is", "are", "was", "were", "of", "by", "as", "new", "ai", "how", "what"
        }
        return {w for w in words if w not in stopwords and len(w) > 2}

    @classmethod
    def jaccard_similarity(cls, title1: str, title2: str) -> float:
        s1 = cls.tokenize_title(title1)
        s2 = cls.tokenize_title(title2)
        if not s1 or not s2:
            return 0.0
        intersection = s1.intersection(s2)
        union = s1.union(s2)
        return len(intersection) / len(union)

    @classmethod
    def cluster_candidates(cls, candidates: List[Dict[str, Any]], threshold: float = 0.50) -> List[Dict[str, Any]]:
        """
        Groups candidates reporting the exact same underlying story into clusters.
        """
        clusters = []
        for cand in candidates:
            cand["normalized_url"] = cls.normalize_url(cand.get("url", ""))
            matched = False
            for cluster in clusters:
                # Compare title similarity
                sim = cls.jaccard_similarity(cand.get("title", ""), cluster["representative"]["title"])
                if sim >= threshold or cand["normalized_url"] == cluster["representative"]["normalized_url"]:
                    cluster["candidates"].append(cand)
                    # Use candidate with higher evidence or significance as representative
                    if cand.get("evidence_score", 0) > cluster["representative"].get("evidence_score", 0):
                        cluster["representative"] = cand
                    matched = True
                    break
            if not matched:
                clusters.append({"representative": cand, "candidates": [cand]})

        # Return representatives with cluster metadata attached
        result = []
        for idx, cl in enumerate(clusters):
            rep = cl["representative"]
            rep["cluster_id"] = f"cluster_{idx+1}"
            rep["related_sources"] = [c.get("url") for c in cl["candidates"] if c.get("url") != rep.get("url")]
            result.append(rep)
        return result
