import React, { useEffect, useState } from "react";
import { type Category, fetchCategories } from "../api";
import { Tag } from "lucide-react";

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

  if (loading) {
    return <div style={{ textAlign: "center", padding: "40px 0", color: "var(--text-muted)" }}>Loading taxonomy...</div>;
  }

  return (
    <div style={{ marginBottom: "32px" }}>
      <div style={{ marginBottom: "20px" }}>
        <h2 style={{ fontFamily: "var(--font-serif)", fontSize: "1.8rem", marginBottom: "8px" }}>
          Taxonomy & Topic Classification
        </h2>
        <p style={{ color: "var(--text-muted)" }}>
          PRD Section 11 curated domains. Select a domain to filter coverage.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: "16px" }}>
        <div
          onClick={() => onSelectCategory("")}
          className="metric-card"
          style={{
            cursor: "pointer",
            borderColor: selectedCategory === "" ? "var(--primary)" : "var(--border-color)",
            background: selectedCategory === "" ? "var(--primary-subtle)" : "var(--bg-surface)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px", fontWeight: 700, color: "var(--text-main)" }}>
            <Tag size={16} color="var(--primary)" />
            All Categories (Briefing View)
          </div>
          <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginTop: "6px" }}>
            Comprehensive cross-domain daily edition
          </p>
        </div>

        {categories.map((cat) => (
          <div
            key={cat.id}
            onClick={() => onSelectCategory(cat.slug)}
            className="metric-card"
            style={{
              cursor: "pointer",
              borderColor: selectedCategory === cat.slug ? "var(--primary)" : "var(--border-color)",
              background: selectedCategory === cat.slug ? "var(--primary-subtle)" : "var(--bg-surface)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px", fontWeight: 700, color: "var(--text-main)" }}>
              <Tag size={16} color="var(--primary)" />
              {cat.name}
            </div>
            <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginTop: "6px" }}>
              {cat.description || `Updates and analysis in ${cat.name}`}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
