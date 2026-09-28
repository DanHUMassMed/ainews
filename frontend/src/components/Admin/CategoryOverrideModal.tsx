import React, { useState } from "react";
import type { CategoryFeedbackItem } from "../../api";

interface CategoryOverrideModalProps {
  category: CategoryFeedbackItem;
  isSaving: boolean;
  onClose: () => void;
  onSave: (slug: string, bias: number, active: boolean, reason: string) => Promise<void>;
}

export const CategoryOverrideModal: React.FC<CategoryOverrideModalProps> = ({
  category,
  isSaving,
  onClose,
  onSave,
}) => {
  const [overrideBiasInput, setOverrideBiasInput] = useState<number>(() =>
    category.override_active && category.override_bias != null
      ? category.override_bias
      : category.raw_bias || 0.0
  );
  const [overrideActiveInput, setOverrideActiveInput] = useState<boolean>(true);
  const [overrideReasonInput, setOverrideReasonInput] = useState<string>(
    () => category.override_reason || ""
  );

  const handleSave = () => {
    onSave(category.slug, overrideBiasInput, overrideActiveInput, overrideReasonInput);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h3>Editorial Bias Override</h3>
            <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", margin: "4px 0 0" }}>
              Category: <strong>{category.category_name}</strong> ({category.slug})
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              color: "var(--text-muted)",
              cursor: "pointer",
              fontSize: "1.2rem",
            }}
          >
            ✕
          </button>
        </div>

        <div className="modal-body">
          <div
            style={{
              background: "var(--bg-surface-raised)",
              border: "1px solid var(--border-color)",
              borderRadius: "6px",
              padding: "12px",
              marginBottom: "18px",
              fontSize: "0.82rem",
              display: "grid",
              gridTemplateColumns: "1fr 1fr 1fr",
              gap: "8px",
              textAlign: "center",
            }}
          >
            <div>
              <div style={{ color: "var(--text-muted)", fontSize: "0.72rem" }}>Upvotes</div>
              <div style={{ fontWeight: 700, color: "var(--accent-green)" }}>+{category.upvotes}</div>
            </div>
            <div>
              <div style={{ color: "var(--text-muted)", fontSize: "0.72rem" }}>Downvotes</div>
              <div style={{ fontWeight: 700, color: "var(--primary)" }}>-{category.downvotes}</div>
            </div>
            <div>
              <div style={{ color: "var(--text-muted)", fontSize: "0.72rem" }}>Reader Approval</div>
              <div style={{ fontWeight: 700 }}>{Math.round(category.approval_rate * 100)}%</div>
            </div>
          </div>

          <div style={{ marginBottom: "18px" }}>
            <label
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                cursor: "pointer",
                fontWeight: 600,
                fontSize: "0.9rem",
              }}
            >
              <input
                type="checkbox"
                checked={overrideActiveInput}
                onChange={(e) => setOverrideActiveInput(e.target.checked)}
              />
              <span>Enable Editorial Bias Override</span>
            </label>
            <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", margin: "4px 0 0 24px" }}>
              When enabled, this manual bias score overrides automatic reader approval ratings during candidate evaluation.
            </p>
          </div>

          <div style={{ marginBottom: "18px" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "6px",
              }}
            >
              <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Manual Bias Score:</span>
              <span
                style={{
                  fontFamily: "var(--font-mono)",
                  fontWeight: 700,
                  fontSize: "1.1rem",
                  color:
                    overrideBiasInput > 0
                      ? "var(--accent-green)"
                      : overrideBiasInput < 0
                      ? "var(--primary)"
                      : "var(--text-muted)",
                }}
              >
                {overrideBiasInput > 0 ? `+${overrideBiasInput.toFixed(2)}` : overrideBiasInput.toFixed(2)}
              </span>
            </div>

            <input
              type="range"
              min={-3.0}
              max={3.0}
              step={0.1}
              value={overrideBiasInput}
              disabled={!overrideActiveInput}
              onChange={(e) => setOverrideBiasInput(parseFloat(e.target.value))}
              style={{ width: "100%", cursor: overrideActiveInput ? "pointer" : "not-allowed" }}
            />

            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                fontSize: "0.72rem",
                color: "var(--text-faint)",
                marginTop: "4px",
              }}
            >
              <span>-3.00 (Heavy Penalty)</span>
              <span>0.00 (Neutral)</span>
              <span>+3.00 (Strong Boost)</span>
            </div>

            {/* Presets */}
            <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginTop: "12px" }}>
              {[
                { label: "+2.0 High Boost", val: 2.0 },
                { label: "+1.0 Boost", val: 1.0 },
                { label: "0.0 Neutral", val: 0.0 },
                { label: "-1.0 Dampen", val: -1.0 },
                { label: "-2.0 Suppress", val: -2.0 },
              ].map((preset) => (
                <button
                  key={preset.label}
                  type="button"
                  className={`preset-chip-btn ${overrideBiasInput === preset.val ? "active" : ""}`}
                  disabled={!overrideActiveInput}
                  onClick={() => setOverrideBiasInput(preset.val)}
                >
                  {preset.label}
                </button>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: "12px" }}>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "6px" }}>
              Editorial Rationale / Note:
            </label>
            <input
              type="text"
              value={overrideReasonInput}
              placeholder="e.g., Prioritizing semiconductor architectures; counteracting consumer PR fatigue"
              onChange={(e) => setOverrideReasonInput(e.target.value)}
              style={{
                width: "100%",
                background: "var(--bg-surface-raised)",
                border: "1px solid var(--border-color)",
                borderRadius: "6px",
                padding: "8px 12px",
                color: "var(--text-main)",
                fontSize: "0.85rem",
              }}
            />
          </div>
        </div>

        <div className="modal-footer">
          <button
            className="action-btn-secondary"
            onClick={onClose}
            disabled={isSaving}
          >
            Cancel
          </button>
          <button
            className="action-btn-primary"
            onClick={handleSave}
            disabled={isSaving}
            style={{ padding: "8px 18px", fontSize: "0.88rem" }}
          >
            {isSaving ? "Saving..." : "Save Override"}
          </button>
        </div>
      </div>
    </div>
  );
};
