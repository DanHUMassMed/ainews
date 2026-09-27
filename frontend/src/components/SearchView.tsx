import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import { cleanProseMarkdown } from "../utils/markdown";
import { Search as SearchIcon, ExternalLink, Sparkles } from "lucide-react";
import { type Story, searchStories } from "../api";

export const SearchView: React.FC = () => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Story[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setHasSearched(true);
    try {
      const data = await searchStories(query.trim());
      setResults(data);
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: "24px" }}>
        <h2 style={{ fontFamily: "var(--font-serif)", fontSize: "1.8rem", marginBottom: "8px" }}>
          Full-Text Briefing Search
        </h2>
        <p style={{ color: "var(--text-muted)" }}>
          Search published AI developments using the PostgreSQL full-text index.
        </p>
      </div>

      <form onSubmit={handleSearch} className="search-container">
        <div className="search-input-wrapper">
          <SearchIcon size={18} className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search by topic, architecture, author, or keyword (e.g. MoE, TSMC, FP4)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            id="search-input-field"
          />
        </div>
      </form>

      {loading && (
        <div style={{ textAlign: "center", padding: "40px 0", color: "var(--text-muted)" }}>
          Searching briefing corpus...
        </div>
      )}

      {!loading && hasSearched && results.length === 0 && (
        <div style={{ textAlign: "center", padding: "60px 0", color: "var(--text-muted)" }}>
          No stories matched your search query. Try broadening your keywords.
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
        {results.map((story) => (
          <div key={story.id} className="story-card" style={{ padding: "20px" }}>
            <div className="story-card-top">
              <div className="category-tags">
                {story.categories.map((c) => (
                  <span key={c.id || c.slug} className="cat-tag">
                    {c.name}
                  </span>
                ))}
              </div>
              {story.is_lead && (
                <span className="lead-badge" style={{ fontSize: "0.68rem", padding: "2px 6px" }}>
                  LEAD STORY
                </span>
              )}
            </div>

            <h3 className="story-card-title" style={{ fontSize: "1.25rem" }}>
              {story.title}
            </h3>

            <div className="story-card-summary">
              <ReactMarkdown>{cleanProseMarkdown(story.summary)}</ReactMarkdown>
            </div>

            <div className="why-matters-box" style={{ padding: "10px 14px", margin: "12px 0" }}>
              <div className="why-matters-label" style={{ fontSize: "0.72rem" }}>
                <Sparkles size={13} />
                Why It Matters
              </div>
              <div className="why-matters-text" style={{ fontSize: "0.9rem" }}>
                <ReactMarkdown>{cleanProseMarkdown(story.why_it_matters)}</ReactMarkdown>
              </div>
            </div>

            <div className="story-footer" style={{ marginTop: "12px", paddingTop: "12px" }}>
              <div className="sources-list">
                {story.sources.map((src, i) => (
                  <a
                    key={i}
                    href={src.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="source-link"
                  >
                    <span>{src.publisher || "Source"}</span>
                    <ExternalLink size={12} />
                  </a>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
