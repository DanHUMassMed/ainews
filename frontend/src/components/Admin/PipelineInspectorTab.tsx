import React from "react";
import {
  Calendar,
  CheckCircle2,
  Archive,
  Clock,
  Trash2,
  XCircle,
} from "lucide-react";
import type { CandidateItem } from "../../api";

interface PipelineInspectorTabProps {
  candidates: CandidateItem[];
  activeEditionDate: string;
  loading: boolean;
  isClearing: boolean;
  onClearAudit: () => Promise<void>;
}

export const PipelineInspectorTab: React.FC<PipelineInspectorTabProps> = ({
  candidates,
  activeEditionDate,
  loading,
  isClearing,
  onClearAudit,
}) => {
  const selectedCount = candidates.filter((c) => c.selected).length;
  const recoveredCount = candidates.filter((c) => c.metadata_json?.recovered_from_backup).length;
  const staleBackupCount = candidates.filter(
    (c) => !c.selected && c.rejected_reason?.toLowerCase().includes("stale")
  ).length;

  return (
    <div>
      {/* Target Pipeline Edition Date Banner */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "14px",
          padding: "16px 20px",
          background: "var(--bg-surface-raised)",
          border: "1px solid var(--border-color)",
          borderRadius: "12px",
          marginBottom: "20px",
          boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div
            style={{
              width: "42px",
              height: "42px",
              borderRadius: "10px",
              background: "rgba(59, 130, 246, 0.12)",
              border: "1px solid var(--primary)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Calendar size={20} color="var(--primary)" />
          </div>
          <div>
            <div
              style={{
                fontSize: "0.75rem",
                fontFamily: "var(--font-mono)",
                color: "var(--text-muted)",
                letterSpacing: "0.06em",
                textTransform: "uppercase",
              }}
            >
              Active Edition Publication Target
            </div>
            <div
              style={{
                fontSize: "1.25rem",
                fontWeight: 700,
                color: "var(--text-main)",
                letterSpacing: "-0.01em",
              }}
            >
              {activeEditionDate ? activeEditionDate : "Active Run"}
            </div>
          </div>
        </div>

        <div style={{ display: "flex", flexWrap: "wrap", gap: "10px", alignItems: "center" }}>
          <span
            className="cat-tag"
            style={{
              background: "rgba(34, 197, 94, 0.12)",
              color: "#22c55e",
              borderColor: "rgba(34, 197, 94, 0.3)",
              fontWeight: 600,
            }}
          >
            <CheckCircle2 size={13} style={{ marginRight: "4px", verticalAlign: "middle" }} />
            {selectedCount} Selected for Newsletter
          </span>

          {recoveredCount > 0 && (
            <span
              className="cat-tag"
              style={{
                background: "rgba(168, 85, 247, 0.15)",
                color: "#c084fc",
                borderColor: "rgba(168, 85, 247, 0.35)",
                fontWeight: 600,
              }}
            >
              <Archive size={13} style={{ marginRight: "4px", verticalAlign: "middle" }} />
              {recoveredCount} Recovered from Stale Backup
            </span>
          )}

          {staleBackupCount > 0 && (
            <span
              className="cat-tag"
              style={{
                background: "rgba(245, 158, 11, 0.12)",
                color: "#f59e0b",
                borderColor: "rgba(245, 158, 11, 0.3)",
              }}
            >
              <Clock size={13} style={{ marginRight: "4px", verticalAlign: "middle" }} />
              {staleBackupCount} Available Backup (&gt;48h)
            </span>
          )}

          <span className="cat-tag">{candidates.length} Scored Candidates</span>
        </div>
      </div>

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
        <span style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>
          Auditing candidate pool for target edition date: <strong>{activeEditionDate || "Today"}</strong>. Multi-factor dimensional scores and publication gates enforced.
        </span>
        <button
          onClick={onClearAudit}
          className="action-btn-secondary"
          disabled={loading || isClearing}
          id="admin-clear-audit-btn"
          style={{
            borderColor: "rgba(239, 68, 68, 0.4)",
            color: "#ef4444",
            fontSize: "0.82rem",
            padding: "6px 12px",
          }}
          title="Clear old candidate records for a clean run presentation"
        >
          <Trash2 size={13} />
          {isClearing ? "Clearing..." : "Clear Audit Records"}
        </button>
      </div>

      <div className="inspector-table-wrapper">
        <table className="inspector-table">
          <thead>
            <tr>
              <th>Story / Headline</th>
              <th style={{ textAlign: "center" }}>Occurrence Date</th>
              <th style={{ textAlign: "center" }}>Sig (w=0.35)</th>
              <th style={{ textAlign: "center" }}>Nov (w=0.25)</th>
              <th style={{ textAlign: "center" }}>Evi (w=0.20)</th>
              <th style={{ textAlign: "center" }}>Sat (w=-0.20)</th>
              <th style={{ textAlign: "center" }}>FB</th>
              <th style={{ textAlign: "center" }}>Score</th>
              <th>Status & Rejection Reason</th>
            </tr>
          </thead>
          <tbody>
            {candidates.length === 0 ? (
              <tr>
                <td
                  colSpan={9}
                  style={{ textAlign: "center", padding: "40px", color: "var(--text-muted)" }}
                >
                  No candidate audit records for this run. Run the editorial generator or click Refresh.
                </td>
              </tr>
            ) : (
              candidates.map((c) => {
                const occDate =
                  c.metadata_json?.occurrence_date ||
                  (c.metadata_json?.published_at ? c.metadata_json.published_at.split("T")[0] : null) ||
                  (c.discovered_at ? c.discovered_at.split("T")[0] : "-");

                const isRecovered = Boolean(c.metadata_json?.recovered_from_backup);
                const isStale = Boolean(c.rejected_reason?.toLowerCase().includes("stale"));

                return (
                  <tr key={c.id}>
                    <td style={{ maxWidth: "300px" }}>
                      <div
                        style={{
                          fontWeight: 600,
                          color: "var(--text-main)",
                          marginBottom: "4px",
                        }}
                      >
                        {c.title}
                      </div>
                      <a
                        href={c.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          fontSize: "0.78rem",
                          color: "var(--accent-blue)",
                          wordBreak: "break-all",
                        }}
                      >
                        {c.url}
                      </a>
                    </td>
                    <td style={{ textAlign: "center", whiteSpace: "nowrap" }}>
                      <div
                        style={{
                          fontFamily: "var(--font-mono)",
                          fontSize: "0.85rem",
                          color: "var(--text-main)",
                        }}
                      >
                        {occDate}
                      </div>
                      {isStale && (
                        <span style={{ fontSize: "0.72rem", color: "#f59e0b", display: "block" }}>
                          &gt; 48h lookback
                        </span>
                      )}
                    </td>
                    <td style={{ textAlign: "center" }}>
                      <span className={`score-chip ${(c.significance_score || 0) >= 7 ? "high" : "mid"}`}>
                        {c.significance_score?.toFixed(1) ?? "-"}
                      </span>
                    </td>
                    <td style={{ textAlign: "center" }}>
                      <span className={`score-chip ${(c.novelty_score || 0) >= 7 ? "high" : "mid"}`}>
                        {c.novelty_score?.toFixed(1) ?? "-"}
                      </span>
                    </td>
                    <td style={{ textAlign: "center" }}>
                      <span className={`score-chip ${(c.evidence_score || 0) >= 7 ? "high" : "low"}`}>
                        {c.evidence_score?.toFixed(1) ?? "-"}
                      </span>
                    </td>
                    <td style={{ textAlign: "center" }}>
                      <span className={`score-chip ${(c.saturation_score || 0) >= 6 ? "low" : "high"}`}>
                        {c.saturation_score?.toFixed(1) ?? "-"}
                      </span>
                    </td>
                    <td style={{ textAlign: "center", fontFamily: "var(--font-mono)", fontSize: "0.82rem" }}>
                      {c.feedback_bias?.toFixed(2) ?? "0.00"}
                    </td>
                    <td style={{ textAlign: "center" }}>
                      <strong style={{ fontFamily: "var(--font-mono)", fontSize: "0.95rem" }}>
                        {c.composite_score?.toFixed(2) ?? "-"}
                      </strong>
                    </td>
                    <td>
                      {c.selected ? (
                        isRecovered ? (
                          <div>
                            <span
                              className="status-badge"
                              style={{
                                background: "rgba(168, 85, 247, 0.15)",
                                color: "#c084fc",
                                border: "1px solid rgba(168, 85, 247, 0.35)",
                                marginBottom: "4px",
                                display: "inline-flex",
                                alignItems: "center",
                                gap: "4px",
                              }}
                            >
                              <Archive size={12} /> Recovered Archive
                            </span>
                            <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", margin: "2px 0 0" }}>
                              Pulled from &gt;48h stale backup pool
                            </p>
                          </div>
                        ) : (
                          <span className="status-badge accepted">
                            <CheckCircle2 size={13} /> Selected
                          </span>
                        )
                      ) : isStale ? (
                        <div>
                          <span
                            className="status-badge"
                            style={{
                              background: "rgba(245, 158, 11, 0.12)",
                              color: "#f59e0b",
                              border: "1px solid rgba(245, 158, 11, 0.3)",
                              marginBottom: "4px",
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "4px",
                            }}
                          >
                            <Clock size={12} /> Stale Backup (&gt;48h)
                          </span>
                          {c.rejected_reason && (
                            <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "2px" }}>
                              {c.rejected_reason}
                            </p>
                          )}
                        </div>
                      ) : (
                        <div>
                          <span className="status-badge rejected" style={{ marginBottom: "6px" }}>
                            <XCircle size={13} /> Rejected
                          </span>
                          {c.rejected_reason && (
                            <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "4px" }}>
                              {c.rejected_reason}
                            </p>
                          )}
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
