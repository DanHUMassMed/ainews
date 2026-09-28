import React from "react";
import { ShieldCheck, Target, SlidersHorizontal } from "lucide-react";
import { ScoringSimulator } from "./ScoringSimulator";
import { ScoringConfigForm } from "./ScoringConfigForm";
import type {
  ScoringWeightsConfig,
  ScoringThresholdsConfig,
  ScoringConfigResponse,
} from "../../api";

interface ScoringFormulaTabProps {
  scoringConfig: ScoringConfigResponse | null;
  weights: ScoringWeightsConfig;
  setWeights: React.Dispatch<React.SetStateAction<ScoringWeightsConfig>>;
  thresholds: ScoringThresholdsConfig;
  setThresholds: React.Dispatch<React.SetStateAction<ScoringThresholdsConfig>>;
  isSavingConfig: boolean;
  configSaveSuccess: string | null;
  configSaveError: string | null;
  onSaveConfig: () => Promise<void>;
  onResetConfig: () => Promise<void>;
}

export const ScoringFormulaTab: React.FC<ScoringFormulaTabProps> = ({
  scoringConfig,
  weights,
  setWeights,
  thresholds,
  setThresholds,
  isSavingConfig,
  configSaveSuccess,
  configSaveError,
  onSaveConfig,
  onResetConfig,
}) => {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "28px" }}>
      {/* 1. Header & Mathematical Formula Overview */}
      <div className="lead-story-card" style={{ padding: "28px" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            flexWrap: "wrap",
            gap: "16px",
            marginBottom: "16px",
          }}
        >
          <div>
            <h3 style={{ fontFamily: "var(--font-serif)", fontSize: "1.6rem", margin: "0 0 6px 0" }}>
              Editorial Selection Framework & Multi-Factor Scoring
            </h3>
            <p
              style={{
                color: "var(--text-muted)",
                fontSize: "0.92rem",
                margin: 0,
                maxWidth: "750px",
              }}
            >
              How the autonomous editorial pipeline discovers, audits, scores, balances, and selects
              candidate stories for daily publication. Every article undergoes continuous
              multi-factor evaluation before tier placement and portfolio balancing.
            </p>
          </div>
          <span
            className="cat-tag"
            style={{
              background: "rgba(99, 102, 241, 0.15)",
              color: "#818cf8",
              border: "1px solid rgba(99, 102, 241, 0.3)",
              padding: "6px 12px",
            }}
          >
            <ShieldCheck size={14} style={{ marginRight: "6px", verticalAlign: "middle" }} />
            Deterministic Quality Gate
          </span>
        </div>

        {/* Formula Display Box */}
        <div
          style={{
            padding: "18px 24px",
            background: "var(--bg-surface-sunken)",
            borderRadius: "8px",
            fontFamily: "var(--font-mono)",
            fontSize: "1.05rem",
            border: "1px solid var(--border-color)",
            marginBottom: "16px",
            overflowX: "auto",
          }}
        >
          <div style={{ color: "var(--accent-primary)", fontWeight: 600, marginBottom: "8px" }}>
            Score = (w₁ &times; Significance) + (w₂ &times; Novelty) + (w₃ &times; Evidence) - (w₄ &times; Saturation) + (w₅ &times; FeedbackBias)
          </div>
          <div style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
            Active Weights: w₁ = {weights.significance_weight} | w₂ = {weights.novelty_weight} | w₃ ={" "}
            {weights.evidence_weight} | w₄ = {weights.saturation_weight} (penalty) | w₅ ={" "}
            {weights.feedback_weight}
          </div>
        </div>
      </div>

      {/* 2. Article Selection Lifecycle Funnel */}
      <div className="lead-story-card" style={{ padding: "28px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "18px" }}>
          <Target size={20} style={{ color: "var(--accent-primary)" }} />
          <h4 style={{ fontFamily: "var(--font-serif)", fontSize: "1.3rem", margin: 0 }}>
            How an Article Is Selected: 5-Stage Editorial Funnel
          </h4>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: "16px",
          }}
        >
          <div className="metric-card" style={{ borderTop: "3px solid #6366f1" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
              <span
                style={{
                  background: "#6366f1",
                  color: "#fff",
                  borderRadius: "50%",
                  width: "22px",
                  height: "22px",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "0.75rem",
                  fontWeight: 700,
                }}
              >
                1
              </span>
              <strong style={{ fontSize: "0.95rem" }}>Ingestion & Recency</strong>
            </div>
            <p style={{ fontSize: "0.83rem", color: "var(--text-muted)", margin: 0, lineHeight: "1.45" }}>
              Whitelisted feeds, arXiv, and SearXNG matrices ingest candidates. URLs undergo HTTP 200 reachability checks. Candidates &gt;48h old that pass are preserved in the <strong>Stale Backup Pool</strong>.
            </p>
          </div>

          <div className="metric-card" style={{ borderTop: "3px solid #06b6d4" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
              <span
                style={{
                  background: "#06b6d4",
                  color: "#fff",
                  borderRadius: "50%",
                  width: "22px",
                  height: "22px",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "0.75rem",
                  fontWeight: 700,
                }}
              >
                2
              </span>
              <strong style={{ fontSize: "0.95rem" }}>Multi-Factor Scoring</strong>
            </div>
            <p style={{ fontSize: "0.83rem", color: "var(--text-muted)", margin: 0, lineHeight: "1.45" }}>
              Evaluator agent computes continuous 1.0–10.0 scores for Significance, Novelty, Evidence, and Saturation, plus Reader Feedback Bias (-3 to +3). Calculates the composite score.
            </p>
          </div>

          <div className="metric-card" style={{ borderTop: "3px solid #10b981" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
              <span
                style={{
                  background: "#10b981",
                  color: "#fff",
                  borderRadius: "50%",
                  width: "22px",
                  height: "22px",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "0.75rem",
                  fontWeight: 700,
                }}
              >
                3
              </span>
              <strong style={{ fontSize: "0.95rem" }}>Tier Classification</strong>
            </div>
            <p style={{ fontSize: "0.83rem", color: "var(--text-muted)", margin: 0, lineHeight: "1.45" }}>
              Candidates below {thresholds.min_selection_threshold} are rejected. Qualified stories are placed into <strong>Core</strong> (≥{thresholds.core_min_score}), <strong>Exploratory</strong> (Novelty ≥{thresholds.exploratory_min_novelty}), or <strong>Contrarian</strong> tiers.
            </p>
          </div>

          <div className="metric-card" style={{ borderTop: "3px solid #f59e0b" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
              <span
                style={{
                  background: "#f59e0b",
                  color: "#fff",
                  borderRadius: "50%",
                  width: "22px",
                  height: "22px",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "0.75rem",
                  fontWeight: 700,
                }}
              >
                4
              </span>
              <strong style={{ fontSize: "0.95rem" }}>Portfolio Balancing</strong>
            </div>
            <p style={{ fontSize: "0.83rem", color: "var(--text-muted)", margin: 0, lineHeight: "1.45" }}>
              Selects 5–7 stories matching the target balance: <strong>~70% Core, ~20% Exploratory, ~10% Contrarian</strong>. Strict domain capping (max 1 per domain) prevents single-source dominance.
            </p>
          </div>

          <div className="metric-card" style={{ borderTop: "3px solid #ec4899" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
              <span
                style={{
                  background: "#ec4899",
                  color: "#fff",
                  borderRadius: "50%",
                  width: "22px",
                  height: "22px",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "0.75rem",
                  fontWeight: 700,
                }}
              >
                5
              </span>
              <strong style={{ fontSize: "0.95rem" }}>Stale Backup Recovery</strong>
            </div>
            <p style={{ fontSize: "0.83rem", color: "var(--text-muted)", margin: 0, lineHeight: "1.45" }}>
              If a low-signal day yields &lt;5 fresh stories, top-scoring candidates from the &gt;48h Stale Backup pool (≥{thresholds.stale_backup_min_score}) are promoted to <strong>Recovered Archive</strong> to fill out the edition.
            </p>
          </div>
        </div>
      </div>

      {/* 3. Variables & Continuous Ranges Reference Table */}
      <div className="lead-story-card" style={{ padding: "28px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
          <SlidersHorizontal size={20} style={{ color: "var(--accent-primary)" }} />
          <h4 style={{ fontFamily: "var(--font-serif)", fontSize: "1.3rem", margin: 0 }}>
            Scoring Variables, Value Ranges & Practical Interpretations
          </h4>
        </div>

        <div style={{ overflowX: "auto" }}>
          <table className="admin-table" style={{ width: "100%", fontSize: "0.88rem" }}>
            <thead>
              <tr>
                <th style={{ textAlign: "left" }}>Variable</th>
                <th style={{ textAlign: "center" }}>Weight</th>
                <th style={{ textAlign: "center" }}>Range</th>
                <th style={{ textAlign: "center" }}>Scale Impact</th>
                <th style={{ textAlign: "left" }}>Low Score (1.0 – 3.0)</th>
                <th style={{ textAlign: "left" }}>High Score (8.0 – 10.0)</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong style={{ color: "#818cf8" }}>Significance</strong></td>
                <td style={{ textAlign: "center", fontFamily: "var(--font-mono)" }}>w₁ = {weights.significance_weight}</td>
                <td style={{ textAlign: "center", fontFamily: "var(--font-mono)" }}>[1.0 – 10.0]</td>
                <td style={{ textAlign: "center" }}><span style={{ color: "#10b981", fontWeight: 600 }}>Positive (+)</span></td>
                <td style={{ color: "var(--text-muted)" }}>Minor product tweak, local meetup, wrapper UI update.</td>
                <td style={{ color: "var(--text-main)" }}>Compute architecture shift, frontier model release, trillion-parameter scale.</td>
              </tr>
              <tr>
                <td><strong style={{ color: "#06b6d4" }}>Novelty</strong></td>
                <td style={{ textAlign: "center", fontFamily: "var(--font-mono)" }}>w₂ = {weights.novelty_weight}</td>
                <td style={{ textAlign: "center", fontFamily: "var(--font-mono)" }}>[1.0 – 10.0]</td>
                <td style={{ textAlign: "center" }}><span style={{ color: "#10b981", fontWeight: 600 }}>Positive (+)</span></td>
                <td style={{ color: "var(--text-muted)" }}>Routine maintenance, familiar prompt template, re-packaged existing model.</td>
                <td style={{ color: "var(--text-main)" }}>Radical new attention mechanism, new reasoning paradigm, unprecedented benchmark.</td>
              </tr>
              <tr>
                <td><strong style={{ color: "#10b981" }}>Evidence</strong></td>
                <td style={{ textAlign: "center", fontFamily: "var(--font-mono)" }}>w₃ = {weights.evidence_weight}</td>
                <td style={{ textAlign: "center", fontFamily: "var(--font-mono)" }}>[1.0 – 10.0]</td>
                <td style={{ textAlign: "center" }}><span style={{ color: "#10b981", fontWeight: 600 }}>Positive (+)</span></td>
                <td style={{ color: "var(--text-muted)" }}>Unverified social media rumor, marketing PR claim without benchmarks.</td>
                <td style={{ color: "var(--text-main)" }}>Reproducible code repo, official lab whitepaper, peer-reviewed arXiv preprint.</td>
              </tr>
              <tr>
                <td><strong style={{ color: "#f43f5e" }}>Saturation</strong></td>
                <td style={{ textAlign: "center", fontFamily: "var(--font-mono)" }}>w₄ = {weights.saturation_weight}</td>
                <td style={{ textAlign: "center", fontFamily: "var(--font-mono)" }}>[1.0 – 10.0]</td>
                <td style={{ textAlign: "center" }}><span style={{ color: "#f43f5e", fontWeight: 600 }}>Negative (–)</span></td>
                <td style={{ color: "var(--text-main)" }}>Unreported or nascent topic; zero coverage in last 28 days (no penalty).</td>
                <td style={{ color: "var(--text-muted)" }}>Heavily recycled news, echo-chamber PR covered 20+ times this week (heavy penalty).</td>
              </tr>
              <tr>
                <td><strong style={{ color: "#eab308" }}>Feedback Bias</strong></td>
                <td style={{ textAlign: "center", fontFamily: "var(--font-mono)" }}>w₅ = {weights.feedback_weight}</td>
                <td style={{ textAlign: "center", fontFamily: "var(--font-mono)" }}>[-3.0 – +3.0]</td>
                <td style={{ textAlign: "center" }}><span style={{ color: "#eab308", fontWeight: 600 }}>Modulator (&plusmn;)</span></td>
                <td style={{ color: "var(--text-muted)" }}>Consistent reader downvotes on this entity or topic tag (-3.0).</td>
                <td style={{ color: "var(--text-main)" }}>Overwhelming reader upvotes and sustained engagement (+3.0).</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. Interactive Live Score Simulator & Tier Predictor */}
      <ScoringSimulator weights={weights} thresholds={thresholds} />

      {/* 5. Live Weight & Threshold Configuration (DB-Backed) */}
      <ScoringConfigForm
        scoringConfig={scoringConfig}
        weights={weights}
        setWeights={setWeights}
        thresholds={thresholds}
        setThresholds={setThresholds}
        isSavingConfig={isSavingConfig}
        configSaveSuccess={configSaveSuccess}
        configSaveError={configSaveError}
        onSaveConfig={onSaveConfig}
        onResetConfig={onResetConfig}
      />
    </div>
  );
};
