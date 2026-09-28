import React from "react";
import { Sliders, RotateCcw, Save, CheckCircle2, AlertTriangle } from "lucide-react";
import type {
  ScoringWeightsConfig,
  ScoringThresholdsConfig,
  ScoringConfigResponse,
} from "../../api";

interface ScoringConfigFormProps {
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

export const ScoringConfigForm: React.FC<ScoringConfigFormProps> = ({
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
  const weightsSum =
    Math.round(
      (weights.significance_weight +
        weights.novelty_weight +
        weights.evidence_weight +
        weights.saturation_weight +
        weights.feedback_weight) *
        100
    ) / 100;

  return (
    <div className="lead-story-card" style={{ padding: "28px" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "12px",
          marginBottom: "16px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <Sliders size={20} style={{ color: "var(--accent-primary)" }} />
          <div>
            <h4 style={{ fontFamily: "var(--font-serif)", fontSize: "1.3rem", margin: 0 }}>
              Live Weight & Threshold Configuration (Database-Backed)
            </h4>
            {scoringConfig?.updated_at && (
              <span
                style={{
                  fontSize: "0.78rem",
                  color: "var(--text-muted)",
                  fontFamily: "var(--font-mono)",
                }}
              >
                Database record updated: {new Date(scoringConfig.updated_at).toLocaleString()}
              </span>
            )}
          </div>
        </div>
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <button
            className="admin-btn"
            onClick={onResetConfig}
            disabled={isSavingConfig}
            style={{
              background: "transparent",
              border: "1px solid var(--border-color)",
              color: "var(--text-muted)",
              padding: "6px 12px",
              fontSize: "0.85rem",
            }}
          >
            <RotateCcw size={13} style={{ marginRight: "6px", verticalAlign: "middle" }} />
            Reset to Defaults
          </button>
          <button
            className="admin-btn primary"
            onClick={onSaveConfig}
            disabled={isSavingConfig}
            style={{ padding: "6px 16px", fontSize: "0.85rem" }}
          >
            <Save size={13} style={{ marginRight: "6px", verticalAlign: "middle" }} />
            {isSavingConfig ? "Saving..." : "Save to Database"}
          </button>
        </div>
      </div>

      <p
        style={{
          color: "var(--text-muted)",
          fontSize: "0.88rem",
          marginTop: "-6px",
          marginBottom: "20px",
        }}
      >
        Modify the weights and thresholds below to immediately update editorial candidate
        evaluations in the database. Changes take effect on the next pipeline run without
        requiring service restarts.
      </p>

      {configSaveSuccess && (
        <div
          style={{
            padding: "10px 14px",
            background: "rgba(16, 185, 129, 0.12)",
            border: "1px solid rgba(16, 185, 129, 0.3)",
            borderRadius: "6px",
            color: "#10b981",
            fontSize: "0.88rem",
            marginBottom: "18px",
          }}
        >
          <CheckCircle2 size={15} style={{ marginRight: "6px", verticalAlign: "middle" }} />
          {configSaveSuccess}
        </div>
      )}

      {configSaveError && (
        <div
          style={{
            padding: "10px 14px",
            background: "rgba(239, 68, 68, 0.12)",
            border: "1px solid rgba(239, 68, 68, 0.3)",
            borderRadius: "6px",
            color: "#ef4444",
            fontSize: "0.88rem",
            marginBottom: "18px",
          }}
        >
          <AlertTriangle size={15} style={{ marginRight: "6px", verticalAlign: "middle" }} />
          {configSaveError}
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: "20px",
          marginBottom: "24px",
        }}
      >
        {/* Weight inputs */}
        <div
          style={{
            padding: "18px",
            background: "var(--bg-surface-sunken)",
            borderRadius: "8px",
            border: "1px solid var(--border-color)",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "12px",
            }}
          >
            <strong style={{ fontSize: "0.95rem" }}>Dimension Weights</strong>
            <span
              style={{
                fontSize: "0.8rem",
                color: weightsSum === 1.0 ? "#10b981" : "#f59e0b",
                fontFamily: "var(--font-mono)",
              }}
            >
              Sum: {weightsSum.toFixed(2)} {weightsSum === 1.0 ? "✓" : "(unnormalized)"}
            </span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "0.85rem" }}>
            <label style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span>Significance (w₁):</span>
              <input
                type="number"
                min="0"
                max="1"
                step="0.05"
                value={weights.significance_weight}
                onChange={(e) =>
                  setWeights({ ...weights, significance_weight: parseFloat(e.target.value) || 0 })
                }
                style={{
                  width: "70px",
                  padding: "4px 6px",
                  borderRadius: "4px",
                  border: "1px solid var(--border-color)",
                  background: "var(--bg-card)",
                  color: "var(--text-main)",
                  textAlign: "right",
                  fontFamily: "var(--font-mono)",
                }}
              />
            </label>

            <label style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span>Novelty (w₂):</span>
              <input
                type="number"
                min="0"
                max="1"
                step="0.05"
                value={weights.novelty_weight}
                onChange={(e) =>
                  setWeights({ ...weights, novelty_weight: parseFloat(e.target.value) || 0 })
                }
                style={{
                  width: "70px",
                  padding: "4px 6px",
                  borderRadius: "4px",
                  border: "1px solid var(--border-color)",
                  background: "var(--bg-card)",
                  color: "var(--text-main)",
                  textAlign: "right",
                  fontFamily: "var(--font-mono)",
                }}
              />
            </label>

            <label style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span>Evidence Rigor (w₃):</span>
              <input
                type="number"
                min="0"
                max="1"
                step="0.05"
                value={weights.evidence_weight}
                onChange={(e) =>
                  setWeights({ ...weights, evidence_weight: parseFloat(e.target.value) || 0 })
                }
                style={{
                  width: "70px",
                  padding: "4px 6px",
                  borderRadius: "4px",
                  border: "1px solid var(--border-color)",
                  background: "var(--bg-card)",
                  color: "var(--text-main)",
                  textAlign: "right",
                  fontFamily: "var(--font-mono)",
                }}
              />
            </label>

            <label style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span>Saturation Penalty (w₄):</span>
              <input
                type="number"
                min="0"
                max="1"
                step="0.05"
                value={weights.saturation_weight}
                onChange={(e) =>
                  setWeights({ ...weights, saturation_weight: parseFloat(e.target.value) || 0 })
                }
                style={{
                  width: "70px",
                  padding: "4px 6px",
                  borderRadius: "4px",
                  border: "1px solid var(--border-color)",
                  background: "var(--bg-card)",
                  color: "var(--text-main)",
                  textAlign: "right",
                  fontFamily: "var(--font-mono)",
                }}
              />
            </label>

            <label style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span>Reader Feedback Bias (w₅):</span>
              <input
                type="number"
                min="0"
                max="1"
                step="0.05"
                value={weights.feedback_weight}
                onChange={(e) =>
                  setWeights({ ...weights, feedback_weight: parseFloat(e.target.value) || 0 })
                }
                style={{
                  width: "70px",
                  padding: "4px 6px",
                  borderRadius: "4px",
                  border: "1px solid var(--border-color)",
                  background: "var(--bg-card)",
                  color: "var(--text-main)",
                  textAlign: "right",
                  fontFamily: "var(--font-mono)",
                }}
              />
            </label>
          </div>
        </div>

        {/* Threshold inputs */}
        <div
          style={{
            padding: "18px",
            background: "var(--bg-surface-sunken)",
            borderRadius: "8px",
            border: "1px solid var(--border-color)",
          }}
        >
          <strong style={{ fontSize: "0.95rem", display: "block", marginBottom: "12px" }}>
            Editorial Quality Thresholds
          </strong>

          <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "0.85rem" }}>
            <label style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span>Min Selection Threshold:</span>
              <input
                type="number"
                min="1"
                max="10"
                step="0.1"
                value={thresholds.min_selection_threshold}
                onChange={(e) =>
                  setThresholds({
                    ...thresholds,
                    min_selection_threshold: parseFloat(e.target.value) || 0,
                  })
                }
                style={{
                  width: "70px",
                  padding: "4px 6px",
                  borderRadius: "4px",
                  border: "1px solid var(--border-color)",
                  background: "var(--bg-card)",
                  color: "var(--text-main)",
                  textAlign: "right",
                  fontFamily: "var(--font-mono)",
                }}
              />
            </label>

            <label style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span>Core Tier Min Score:</span>
              <input
                type="number"
                min="1"
                max="10"
                step="0.1"
                value={thresholds.core_min_score}
                onChange={(e) =>
                  setThresholds({ ...thresholds, core_min_score: parseFloat(e.target.value) || 0 })
                }
                style={{
                  width: "70px",
                  padding: "4px 6px",
                  borderRadius: "4px",
                  border: "1px solid var(--border-color)",
                  background: "var(--bg-card)",
                  color: "var(--text-main)",
                  textAlign: "right",
                  fontFamily: "var(--font-mono)",
                }}
              />
            </label>

            <label style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span>Core Tier Min Evidence:</span>
              <input
                type="number"
                min="1"
                max="10"
                step="0.1"
                value={thresholds.core_min_evidence}
                onChange={(e) =>
                  setThresholds({
                    ...thresholds,
                    core_min_evidence: parseFloat(e.target.value) || 0,
                  })
                }
                style={{
                  width: "70px",
                  padding: "4px 6px",
                  borderRadius: "4px",
                  border: "1px solid var(--border-color)",
                  background: "var(--bg-card)",
                  color: "var(--text-main)",
                  textAlign: "right",
                  fontFamily: "var(--font-mono)",
                }}
              />
            </label>

            <label style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span>Exploratory Min Score:</span>
              <input
                type="number"
                min="1"
                max="10"
                step="0.1"
                value={thresholds.exploratory_min_score}
                onChange={(e) =>
                  setThresholds({
                    ...thresholds,
                    exploratory_min_score: parseFloat(e.target.value) || 0,
                  })
                }
                style={{
                  width: "70px",
                  padding: "4px 6px",
                  borderRadius: "4px",
                  border: "1px solid var(--border-color)",
                  background: "var(--bg-card)",
                  color: "var(--text-main)",
                  textAlign: "right",
                  fontFamily: "var(--font-mono)",
                }}
              />
            </label>

            <label style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span>Stale Backup Min Score:</span>
              <input
                type="number"
                min="1"
                max="10"
                step="0.1"
                value={thresholds.stale_backup_min_score}
                onChange={(e) =>
                  setThresholds({
                    ...thresholds,
                    stale_backup_min_score: parseFloat(e.target.value) || 0,
                  })
                }
                style={{
                  width: "70px",
                  padding: "4px 6px",
                  borderRadius: "4px",
                  border: "1px solid var(--border-color)",
                  background: "var(--bg-card)",
                  color: "var(--text-main)",
                  textAlign: "right",
                  fontFamily: "var(--font-mono)",
                }}
              />
            </label>
          </div>
        </div>
      </div>
    </div>
  );
};
