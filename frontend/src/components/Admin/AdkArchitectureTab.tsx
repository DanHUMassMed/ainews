import React from "react";

export const AdkArchitectureTab: React.FC = () => {
  return (
    <div>
      {/* Top Benchmark Summary */}
      <div className="lead-story-card" style={{ padding: "24px", marginBottom: "24px" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "16px",
            flexWrap: "wrap",
            gap: "12px",
          }}
        >
          <div>
            <h3 style={{ fontFamily: "var(--font-serif)", fontSize: "1.4rem", margin: "0 0 4px 0" }}>
              Google ADK 2.x & LiteLLM Multi-Agent Architecture
            </h3>
            <p style={{ color: "var(--text-muted)", fontSize: "0.88rem", margin: 0 }}>
              Decoupled micro-agents powered by OpenRouter (<code>deepseek/deepseek-v4-flash-0731</code>) and Editorial MCP tools.
            </p>
          </div>
          <div style={{ display: "flex", gap: "8px" }}>
            <span
              className="cat-tag"
              style={{
                background: "rgba(16, 185, 129, 0.15)",
                color: "#10b981",
                border: "1px solid rgba(16, 185, 129, 0.3)",
              }}
            >
              ✓ All Eval Benchmarks Passing
            </span>
            <span className="cat-tag">16 Golden Test Cases</span>
          </div>
        </div>

        {/* Benchmark Metric Cards */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: "14px",
            marginBottom: "20px",
          }}
        >
          <div className="metric-card" style={{ textAlign: "center" }}>
            <div style={{ fontSize: "1.8rem", fontWeight: 700, color: "#10b981", fontFamily: "var(--font-mono)" }}>
              100.0%
            </div>
            <div className="metric-label" style={{ marginTop: "4px" }}>
              Precision (Target &ge; 85%)
            </div>
          </div>
          <div className="metric-card" style={{ textAlign: "center" }}>
            <div style={{ fontSize: "1.8rem", fontWeight: 700, color: "#10b981", fontFamily: "var(--font-mono)" }}>
              100.0%
            </div>
            <div className="metric-label" style={{ marginTop: "4px" }}>
              Recall (Target &ge; 85%)
            </div>
          </div>
          <div className="metric-card" style={{ textAlign: "center" }}>
            <div style={{ fontSize: "1.8rem", fontWeight: 700, color: "#10b981", fontFamily: "var(--font-mono)" }}>
              100.0%
            </div>
            <div className="metric-label" style={{ marginTop: "4px" }}>
              Fluff Rejection (Target &ge; 95%)
            </div>
          </div>
          <div className="metric-card" style={{ textAlign: "center" }}>
            <div style={{ fontSize: "1.8rem", fontWeight: 700, color: "var(--accent-blue)", fontFamily: "var(--font-mono)" }}>
              47 / 47
            </div>
            <div className="metric-label" style={{ marginTop: "4px" }}>
              Test Suite (100% Passing)
            </div>
          </div>
        </div>
      </div>

      {/* Six Specialized Agents Grid */}
      <h4 style={{ fontFamily: "var(--font-serif)", fontSize: "1.2rem", marginBottom: "14px" }}>
        Six Specialized Editorial Agents
      </h4>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: "16px",
          marginBottom: "24px",
        }}
      >
        <div className="lead-story-card" style={{ padding: "18px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <strong style={{ fontSize: "1.05rem" }}>1. Discovery Agent</strong>
            <span className="score-chip mid">Search</span>
          </div>
          <p style={{ fontSize: "0.86rem", color: "var(--text-muted)", marginBottom: "10px" }}>
            Metasearch ecosystem queries across AI focus areas; URL normalization and memory deduplication.
          </p>
          <div style={{ fontSize: "0.78rem", fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>
            Tools: <code>search_web</code>, <code>run_discovery_matrix</code>
          </div>
        </div>

        <div className="lead-story-card" style={{ padding: "18px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <strong style={{ fontSize: "1.05rem" }}>2. Research Agent</strong>
            <span className="score-chip mid">Extraction</span>
          </div>
          <p style={{ fontSize: "0.86rem", color: "var(--text-muted)", marginBottom: "10px" }}>
            Deep Firecrawl scraping, primary canonical source resolution (arXiv, GitHub, engineering blogs).
          </p>
          <div style={{ fontSize: "0.78rem", fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>
            Tools: <code>scrape_webpage</code>
          </div>
        </div>

        <div className="lead-story-card" style={{ padding: "18px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <strong style={{ fontSize: "1.05rem" }}>3. Evaluation Agent</strong>
            <span className="score-chip mid">Scoring</span>
          </div>
          <p style={{ fontSize: "0.86rem", color: "var(--text-muted)", marginBottom: "10px" }}>
            4-dimension scoring (Significance, Novelty, Evidence, Saturation) + feedback bias calibration.
          </p>
          <div style={{ fontSize: "0.78rem", fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>
            Tools: <code>get_editorial_context</code>, <code>get_feedback_analytics</code>
          </div>
        </div>

        <div className="lead-story-card" style={{ padding: "18px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <strong style={{ fontSize: "1.05rem" }}>4. Selection Agent</strong>
            <span className="score-chip high">Portfolio</span>
          </div>
          <p style={{ fontSize: "0.86rem", color: "var(--text-muted)", marginBottom: "10px" }}>
            70/20/10 portfolio partition, exactly 1 Lead Story, diversity rules, low-signal day notices.
          </p>
          <div style={{ fontSize: "0.78rem", fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>
            Tools: <code>fetch_editorial_memory</code>, <code>submit_candidate_stories</code>
          </div>
        </div>

        <div className="lead-story-card" style={{ padding: "18px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <strong style={{ fontSize: "1.05rem" }}>5. Writing Agent</strong>
            <span className="score-chip high">Synthesis</span>
          </div>
          <p style={{ fontSize: "0.86rem", color: "var(--text-muted)", marginBottom: "10px" }}>
            Concise briefing synthesis, prohibited buzzwords enforcement, and mandatory "Why It Matters" callouts.
          </p>
          <div style={{ fontSize: "0.78rem", fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>
            Tools: <code>get_editorial_context</code>
          </div>
        </div>

        <div className="lead-story-card" style={{ padding: "18px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <strong style={{ fontSize: "1.05rem" }}>6. Critic Agent</strong>
            <span className="score-chip low">Adversarial</span>
          </div>
          <p style={{ fontSize: "0.86rem", color: "var(--text-muted)", marginBottom: "10px" }}>
            Adversarial audit for ungrounded claims, buzzwords, and Publication Gate compliance.
          </p>
          <div style={{ fontSize: "0.78rem", fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>
            Tools: <code>stage_edition_draft</code>, <code>get_edition_status</code>
          </div>
        </div>
      </div>

      {/* Quick Command Reference */}
      <div className="metric-card" style={{ padding: "20px" }}>
        <h5 style={{ margin: "0 0 10px 0", fontSize: "0.98rem" }}>CLI & Automation Commands</h5>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
            gap: "10px",
            fontFamily: "var(--font-mono)",
            fontSize: "0.85rem",
          }}
        >
          <div><code>make run-agents</code> - Run multi-agent workflow (demo)</div>
          <div><code>make run-agents-live</code> - Run live SearXNG discovery</div>
          <div><code>make adk-eval</code> - Run Golden Benchmark suite</div>
          <div><code>make test</code> - Run full 47-test suite</div>
        </div>
      </div>
    </div>
  );
};
