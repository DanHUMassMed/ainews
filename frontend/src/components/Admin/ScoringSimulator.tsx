import React, { useState } from "react";
import { Calculator, Clock } from "lucide-react";
import type { ScoringWeightsConfig, ScoringThresholdsConfig } from "../../api";

interface ScoringSimulatorProps {
  weights: ScoringWeightsConfig;
  thresholds: ScoringThresholdsConfig;
}

export const ScoringSimulator: React.FC<ScoringSimulatorProps> = ({
  weights,
  thresholds,
}) => {
  const [simSig, setSimSig] = useState<number>(7.5);
  const [simNov, setSimNov] = useState<number>(7.0);
  const [simEvi, setSimEvi] = useState<number>(8.0);
  const [simSat, setSimSat] = useState<number>(3.0);
  const [simFb, setSimFb] = useState<number>(0.0);

  // Calculate simulated score
  const simScore =
    Math.round(
      (weights.significance_weight * simSig +
        weights.novelty_weight * simNov +
        weights.evidence_weight * simEvi -
        weights.saturation_weight * simSat +
        weights.feedback_weight * simFb) *
        1000
    ) / 1000;

  let simTier = "Contrarian";
  let simTierColor = "#a855f7";
  let simTierBg = "rgba(168, 85, 247, 0.15)";
  let simTierBorder = "rgba(168, 85, 247, 0.35)";
  let simTierReason =
    "Meets baseline criteria as a niche, contrarian, or under-reported opportunity.";

  if (simScore < thresholds.min_selection_threshold) {
    simTier = "Rejected";
    simTierColor = "#ef4444";
    simTierBg = "rgba(239, 68, 68, 0.15)";
    simTierBorder = "rgba(239, 68, 68, 0.35)";
    simTierReason = `Composite score (${simScore}) is below the minimum selection threshold (${thresholds.min_selection_threshold}). Article is dropped.`;
  } else if (
    simScore >= thresholds.core_min_score &&
    simEvi >= thresholds.core_min_evidence
  ) {
    simTier = "Core";
    simTierColor = "#10b981";
    simTierBg = "rgba(16, 185, 129, 0.15)";
    simTierBorder = "rgba(16, 185, 129, 0.35)";
    simTierReason = `Rigorous evidence (${simEvi} ≥ ${thresholds.core_min_evidence}) and high composite score (${simScore} ≥ ${thresholds.core_min_score}). Prime candidate for Lead Story.`;
  } else if (
    simNov >= thresholds.exploratory_min_novelty &&
    simScore >= thresholds.exploratory_min_score
  ) {
    simTier = "Exploratory";
    simTierColor = "#06b6d4";
    simTierBg = "rgba(6, 182, 212, 0.15)";
    simTierBorder = "rgba(6, 182, 212, 0.35)";
    simTierReason = `High technical novelty (${simNov} ≥ ${thresholds.exploratory_min_novelty}) and solid score (${simScore} ≥ ${thresholds.exploratory_min_score}). Covers emerging tools and nascent paradigms.`;
  } else if (
    simNov >= thresholds.contrarian_min_novelty &&
    simSat <= thresholds.contrarian_max_saturation
  ) {
    simTier = "Contrarian";
    simTierColor = "#a855f7";
    simTierBg = "rgba(168, 85, 247, 0.15)";
    simTierBorder = "rgba(168, 85, 247, 0.35)";
    simTierReason = `Unusual novelty (${simNov} ≥ ${thresholds.contrarian_min_novelty}) with low saturation (${simSat} ≤ ${thresholds.contrarian_max_saturation}). Counter-consensus perspective.`;
  }

  return (
    <div className="lead-story-card" style={{ padding: "28px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
        <Calculator size={20} style={{ color: "var(--accent-primary)" }} />
        <h4 style={{ fontFamily: "var(--font-serif)", fontSize: "1.3rem", margin: 0 }}>
          Interactive Live Score Simulator & Tier Predictor
        </h4>
      </div>
      <p
        style={{
          color: "var(--text-muted)",
          fontSize: "0.88rem",
          marginTop: "-8px",
          marginBottom: "24px",
        }}
      >
        Adjust the continuous dimension sliders below to test how different score profiles are
        classified by the active editorial gate in real time.
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
          gap: "24px",
        }}
      >
        {/* Sliders Column */}
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: "6px",
                fontSize: "0.88rem",
              }}
            >
              <span>
                <strong>Significance (1.0 – 10.0)</strong>
              </span>
              <span style={{ fontFamily: "var(--font-mono)", fontWeight: 700, color: "#818cf8" }}>
                {simSig.toFixed(1)}
              </span>
            </div>
            <input
              type="range"
              min="1.0"
              max="10.0"
              step="0.1"
              value={simSig}
              onChange={(e) => setSimSig(parseFloat(e.target.value))}
              style={{ width: "100%", accentColor: "#818cf8" }}
            />
          </div>

          <div>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: "6px",
                fontSize: "0.88rem",
              }}
            >
              <span>
                <strong>Novelty (1.0 – 10.0)</strong>
              </span>
              <span style={{ fontFamily: "var(--font-mono)", fontWeight: 700, color: "#06b6d4" }}>
                {simNov.toFixed(1)}
              </span>
            </div>
            <input
              type="range"
              min="1.0"
              max="10.0"
              step="0.1"
              value={simNov}
              onChange={(e) => setSimNov(parseFloat(e.target.value))}
              style={{ width: "100%", accentColor: "#06b6d4" }}
            />
          </div>

          <div>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: "6px",
                fontSize: "0.88rem",
              }}
            >
              <span>
                <strong>Evidence Rigor (1.0 – 10.0)</strong>
              </span>
              <span style={{ fontFamily: "var(--font-mono)", fontWeight: 700, color: "#10b981" }}>
                {simEvi.toFixed(1)}
              </span>
            </div>
            <input
              type="range"
              min="1.0"
              max="10.0"
              step="0.1"
              value={simEvi}
              onChange={(e) => setSimEvi(parseFloat(e.target.value))}
              style={{ width: "100%", accentColor: "#10b981" }}
            />
          </div>

          <div>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: "6px",
                fontSize: "0.88rem",
              }}
            >
              <span>
                <strong>Saturation Penalty (1.0 – 10.0, Subtracted)</strong>
              </span>
              <span style={{ fontFamily: "var(--font-mono)", fontWeight: 700, color: "#f43f5e" }}>
                {simSat.toFixed(1)}
              </span>
            </div>
            <input
              type="range"
              min="1.0"
              max="10.0"
              step="0.1"
              value={simSat}
              onChange={(e) => setSimSat(parseFloat(e.target.value))}
              style={{ width: "100%", accentColor: "#f43f5e" }}
            />
          </div>

          <div>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: "6px",
                fontSize: "0.88rem",
              }}
            >
              <span>
                <strong>Reader Feedback Bias (-3.0 to +3.0)</strong>
              </span>
              <span style={{ fontFamily: "var(--font-mono)", fontWeight: 700, color: "#eab308" }}>
                {simFb > 0 ? `+${simFb.toFixed(1)}` : simFb.toFixed(1)}
              </span>
            </div>
            <input
              type="range"
              min="-3.0"
              max="3.0"
              step="0.1"
              value={simFb}
              onChange={(e) => setSimFb(parseFloat(e.target.value))}
              style={{ width: "100%", accentColor: "#eab308" }}
            />
          </div>
        </div>

        {/* Outcome Prediction Box */}
        <div
          style={{
            padding: "24px",
            background: "var(--bg-surface-sunken)",
            borderRadius: "8px",
            border: "1px solid var(--border-color)",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
          }}
        >
          <div>
            <div
              style={{
                fontSize: "0.85rem",
                color: "var(--text-muted)",
                textTransform: "uppercase",
                letterSpacing: "0.5px",
                marginBottom: "4px",
              }}
            >
              Simulated Composite Score
            </div>
            <div
              style={{
                display: "flex",
                alignItems: "baseline",
                gap: "12px",
                marginBottom: "16px",
              }}
            >
              <span
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "2.8rem",
                  fontWeight: 800,
                  color: simScore >= 4.0 ? "#10b981" : "#ef4444",
                }}
              >
                {simScore.toFixed(3)}
              </span>
              <span
                className="cat-tag"
                style={{
                  background: simTierBg,
                  color: simTierColor,
                  border: `1px solid ${simTierBorder}`,
                  padding: "6px 12px",
                  fontWeight: 700,
                  fontSize: "0.88rem",
                }}
              >
                {simTier} Tier
              </span>
            </div>

            <div
              style={{
                fontSize: "0.88rem",
                color: "var(--text-main)",
                lineHeight: "1.5",
                marginBottom: "16px",
              }}
            >
              {simTierReason}
            </div>

            {/* Low signal backup note */}
            {simScore >= thresholds.stale_backup_min_score && (
              <div
                style={{
                  padding: "10px 12px",
                  background: "rgba(245, 158, 11, 0.1)",
                  border: "1px solid rgba(245, 158, 11, 0.25)",
                  borderRadius: "6px",
                  fontSize: "0.82rem",
                  color: "#f59e0b",
                }}
              >
                <Clock size={13} style={{ marginRight: "6px", verticalAlign: "middle" }} />
                <strong>Stale Backup Eligible:</strong> If older than 48h, this opportunity will
                be safely recovered during low-signal runs (≥{thresholds.stale_backup_min_score}).
              </div>
            )}
          </div>

          <div
            style={{
              marginTop: "18px",
              paddingTop: "14px",
              borderTop: "1px solid var(--border-color)",
              fontFamily: "var(--font-mono)",
              fontSize: "0.78rem",
              color: "var(--text-muted)",
              wordBreak: "break-all",
            }}
          >
            ({weights.significance_weight} &times; {simSig.toFixed(1)}) + (
            {weights.novelty_weight} &times; {simNov.toFixed(1)}) + (
            {weights.evidence_weight} &times; {simEvi.toFixed(1)}) - (
            {weights.saturation_weight} &times; {simSat.toFixed(1)}) + (
            {weights.feedback_weight} &times; {simFb.toFixed(1)}) ={" "}
            <strong>{simScore.toFixed(3)}</strong>
          </div>
        </div>
      </div>
    </div>
  );
};
