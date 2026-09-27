import React, { useEffect, useState } from "react";
import { type Category, type Story, fetchCategories, fetchCategoryStories } from "../api";
import { Tag, Sparkles, FolderArchive, ArrowRight, RefreshCw, AlertCircle } from "lucide-react";
import { StoryCard } from "./StoryCard";

interface CategoryViewProps {
  onSelectCategory: (slug: string) => void;
  selectedCategory: string | null;
}

export const CategoryView: React.FC<CategoryViewProps> = ({
  onSelectCategory,
  selectedCategory,
}) => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeSlug, setActiveSlug] = useState<string | null>(selectedCategory || null);
  const [stories, setStories] = useState<Story[]>([]);
  const [loadingStories, setLoadingStories] = useState(false);

  useEffect(() => {
    fetchCategories()
      .then((data) => {
        setCategories(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load categories:", err);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (activeSlug) {
      setLoadingStories(true);
      fetchCategoryStories(activeSlug)
        .then((items) => {
          setStories(items);
          setLoadingStories(false);
        })
        .catch((err) => {
          console.error(`Failed to load stories for ${activeSlug}:`, err);
          setStories([]);
          setLoadingStories(false);
        });
    } else {
      setStories([]);
    }
  }, [activeSlug]);

  const handleCardClick = (slug: string) => {
    if (slug === "") {
      onSelectCategory("");
      return;
    }
    setActiveSlug(slug);
  };

  const activeCategoryObj = categories.find((c) => c.slug === activeSlug);

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "60px 0", color: "var(--text-muted)" }}>
        <RefreshCw size={24} className="spin" style={{ margin: "0 auto 12px", color: "var(--primary)" }} />
        <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.9rem" }}>Loading taxonomy classifications...</p>
      </div>
    );
  }

  return (
    <div style={{ marginBottom: "48px" }}>
      <div style={{ marginBottom: "24px" }}>
        <h2 style={{ fontFamily: "var(--font-serif)", fontSize: "2rem", marginBottom: "8px" }}>
          Taxonomy & Topic Classification
        </h2>
        <p style={{ color: "var(--text-muted)", fontSize: "0.95rem" }}>
          Curated editorial domains. Select a domain below to browse full coverage across all editions.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))", gap: "16px" }}>
        <div
          onClick={() => handleCardClick("")}
          className="metric-card"
          style={{
            cursor: "pointer",
            borderColor: activeSlug === null || activeSlug === "" ? "var(--primary)" : "var(--border-color)",
            background: activeSlug === null || activeSlug === "" ? "var(--primary-subtle)" : "var(--bg-surface)",
            transition: "all 0.15s ease",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", fontWeight: 700, color: "var(--text-main)" }}>
              <Tag size={16} color="var(--primary)" />
              All Categories
            </div>
            <span style={{ fontSize: "0.75rem", fontFamily: "var(--font-mono)", color: "var(--text-faint)", background: "var(--bg-surface-raised)", padding: "2px 8px", borderRadius: "12px", border: "1px solid var(--border-color)" }}>
              Live Edition
            </span>
          </div>
          <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginTop: "8px", marginBottom: "8px" }}>
            Switch to the comprehensive cross-domain daily edition briefing.
          </p>
          <div style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "0.8rem", color: "var(--primary)", fontWeight: 600 }}>
            <span>Go to Today's Briefing</span>
            <ArrowRight size={13} />
          </div>
        </div>

        {categories.map((cat) => {
          const isSelected = activeSlug === cat.slug;
          const count = cat.story_count ?? 0;
          return (
            <div
              key={cat.id}
              onClick={() => handleCardClick(cat.slug)}
              className="metric-card"
              style={{
                cursor: "pointer",
                borderColor: isSelected ? "var(--primary)" : "var(--border-color)",
                background: isSelected ? "var(--primary-subtle)" : "var(--bg-surface)",
                transition: "all 0.15s ease",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", fontWeight: 700, color: "var(--text-main)" }}>
                  <Tag size={16} color="var(--primary)" />
                  {cat.name}
                </div>
                <span
                  style={{
                    fontSize: "0.75rem",
                    fontFamily: "var(--font-mono)",
                    fontWeight: 600,
                    color: count > 0 ? "var(--primary)" : "var(--text-faint)",
                    background: count > 0 ? "rgba(59, 130, 246, 0.1)" : "var(--bg-surface-raised)",
                    padding: "2px 8px",
                    borderRadius: "12px",
                    border: "1px solid var(--border-color)",
                  }}
                >
                  {count} {count === 1 ? "story" : "stories"}
                </span>
              </div>
              <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginTop: "8px", marginBottom: 0 }}>
                {cat.description || `Verified developments and technical briefings in ${cat.name}.`}
              </p>
            </div>
          );
        })}
      </div>

      {/* Selected Category Stories Section */}
      {activeSlug && (
        <section style={{ marginTop: "40px", borderTop: "1px solid var(--border-color)", paddingTop: "32px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "16px", marginBottom: "24px" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <FolderArchive size={22} color="var(--primary)" />
                <h3 style={{ margin: 0, fontFamily: "var(--font-serif)", fontSize: "1.5rem" }}>
                  {activeCategoryObj?.name || activeSlug} Archive
                </h3>
                <span style={{ fontSize: "0.82rem", fontFamily: "var(--font-mono)", color: "var(--text-faint)", background: "var(--bg-surface-raised)", padding: "2px 10px", borderRadius: "12px" }}>
                  {stories.length} {stories.length === 1 ? "Story" : "Stories"}
                </span>
              </div>
              <p style={{ margin: "4px 0 0", color: "var(--text-muted)", fontSize: "0.88rem" }}>
                Historical cross-edition reporting indexed under this domain.
              </p>
            </div>

            <button
              onClick={() => onSelectCategory(activeSlug)}
              className="action-btn-primary"
              style={{ display: "flex", alignItems: "center", gap: "8px", padding: "8px 16px", fontSize: "0.86rem" }}
            >
              <Sparkles size={15} />
              Filter Today's Briefing by {activeCategoryObj?.name || activeSlug}
            </button>
          </div>

          {loadingStories ? (
            <div style={{ textAlign: "center", padding: "48px 0", color: "var(--text-muted)" }}>
              <RefreshCw size={24} className="spin" style={{ margin: "0 auto 12px", color: "var(--primary)" }} />
              <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.88rem" }}>Loading {activeCategoryObj?.name} coverage...</p>
            </div>
          ) : stories.length > 0 ? (
            <div className="secondary-stories-grid">
              {stories.map((story, index) => (
                <StoryCard key={story.id} story={story} index={index} />
              ))}
            </div>
          ) : (
            <div
              style={{
                background: "var(--bg-surface-raised)",
                border: "1px dashed var(--border-color)",
                padding: "36px 24px",
                borderRadius: "10px",
                textAlign: "center",
                color: "var(--text-muted)",
              }}
            >
              <AlertCircle size={28} color="var(--text-faint)" style={{ margin: "0 auto 12px" }} />
              <h4 style={{ margin: "0 0 6px", color: "var(--text-main)" }}>No historical stories currently indexed</h4>
              <p style={{ margin: 0, fontSize: "0.86rem" }}>
                Our autonomous editorial workflow actively monitors whitelisted RSS and arXiv feeds for consequential developments in {activeCategoryObj?.name || activeSlug}.
              </p>
            </div>
          )}
        </section>
      )}
    </div>
  );
};
