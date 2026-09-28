import React from "react";
import {
  RefreshCw,
  Info,
  Settings2,
  Edit2,
  RotateCcw,
  ThumbsUp,
  ThumbsDown,
  ArrowUpDown,
  Trash2,
} from "lucide-react";
import type {
  FeedbackAnalytics,
  FeedbackHistoryItem,
  CategoryFeedbackItem,
} from "../../api";

interface FeedbackAnalyticsTabProps {
  analytics: FeedbackAnalytics | null;
  loading: boolean;
  onRefreshAnalytics: () => void;
  feedbackHistory: FeedbackHistoryItem[];
  historyLoading: boolean;
  historyDays: number;
  onHistoryDaysChange: (days: number) => void;
  onRefreshHistory: () => void;
  voteActionLoading: string | null;
  feedbackActionMsg: string | null;
  onDismissActionMsg: () => void;
  onFlipVote: (item: FeedbackHistoryItem) => Promise<void>;
  onDeleteVote: (item: FeedbackHistoryItem) => Promise<void>;
  onOpenOverrideModal: (cat: CategoryFeedbackItem) => void;
  onResetCategoryOverride: (slug: string, name: string) => Promise<void>;
}

export const FeedbackAnalyticsTab: React.FC<FeedbackAnalyticsTabProps> = ({
  analytics,
  loading,
  onRefreshAnalytics,
  feedbackHistory,
  historyLoading,
  historyDays,
  onHistoryDaysChange,
  onRefreshHistory,
  voteActionLoading,
  feedbackActionMsg,
  onDismissActionMsg,
  onFlipVote,
  onDeleteVote,
  onOpenOverrideModal,
  onResetCategoryOverride,
}) => {
  if (!analytics) {
    return (
      <div style={{ textAlign: "center", padding: "40px", color: "var(--text-muted)" }}>
        Loading feedback analytics...
      </div>
    );
  }

  const activeOverridesCount = analytics.categories.filter((c) => c.override_active).length;

  return (
    <div>
      {/* Top Feedback Metrics */}
      <div className="analytics-grid">
        <div className="metric-card">
          <div className="metric-label">Total Reader Votes</div>
          <div className="metric-value">{analytics.total_votes}</div>
          <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "6px" }}>
            30-day sliding window
          </p>
        </div>
        <div className="metric-card">
          <div className="metric-label">Approval Rate</div>
          <div className="metric-value" style={{ color: "var(--accent-green)" }}>
            {(analytics.overall_approval_rate * 100).toFixed(0)}%
          </div>
          <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "6px" }}>
            {analytics.total_upvotes} Upvotes / {analytics.total_downvotes} Downvotes
          </p>
        </div>
        <div className="metric-card">
          <div className="metric-label">Cold Start Status</div>
          <div className="metric-value" style={{ fontSize: "1.3rem" }}>
            {analytics.cold_start_active ? "Cold-Start Active" : "Trained Active"}
          </div>
          <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "6px" }}>
            {analytics.cold_start_active ? "w₅ = 0.0 until 100 votes reached" : "Feedback weight w₅ = 0.15 active"}
          </p>
        </div>
        <div className="metric-card">
          <div className="metric-label">Editorial Overrides</div>
          <div className="metric-value" style={{ color: activeOverridesCount > 0 ? "#c084fc" : "var(--text-muted)" }}>
            {activeOverridesCount} Active
          </div>
          <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "6px" }}>
            {activeOverridesCount > 0 ? "Manual bias priority enforced" : "Pure reader voting mode"}
          </p>
        </div>
      </div>

      {feedbackActionMsg && (
        <div
          style={{
            background: "rgba(13, 148, 136, 0.15)",
            border: "1px solid var(--accent-green)",
            color: "var(--accent-green)",
            padding: "10px 16px",
            borderRadius: "6px",
            marginBottom: "20px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span>✓ {feedbackActionMsg}</span>
          <button
            onClick={onDismissActionMsg}
            style={{
              background: "none",
              border: "none",
              color: "inherit",
              cursor: "pointer",
              fontWeight: 700,
            }}
          >
            ✕
          </button>
        </div>
      )}

      {/* Educational Guide on Feedback Mechanics */}
      <div className="feedback-guide-card">
        <div className="feedback-guide-header">
          <Info size={18} color="var(--primary)" />
          <span>How Reader Feedback Calibrates Daily Briefing Selection</span>
        </div>
        <div className="feedback-guide-grid">
          <div className="feedback-guide-item">
            <strong>1. Domain Category Attribution</strong>
            When a reader votes on a published story, all assigned domain categories (e.g. <em>AI Models</em>, <em>Open Source</em>) receive that upvote or downvote.
          </div>
          <div className="feedback-guide-item">
            <strong>2. Dynamic Bias Scaling [-3.0 to +3.0]</strong>
            Approval rate is scaled linearly: <code>Bias = 6.0 × (ApprovalRate - 0.50)</code>. Categories require ≥ 3 votes to graduate from neutral 0.0.
          </div>
          <div className="feedback-guide-item">
            <strong>3. Composite Scoring Impact</strong>
            Formula: <code>Score = w₁Sig + w₂Nov + w₃Evi - w₄Sat + w₅FeedbackBias</code>. With w₅ = 0.15, a +3.0 bias adds <strong>+0.45</strong> points, altering rank and tier.
          </div>
          <div className="feedback-guide-item">
            <strong>4. Editorial Override Protection</strong>
            Editors can override category bias directly to prevent echo chambers and stop mainstream hype from penalizing rigorous technical papers.
          </div>
        </div>
      </div>

      {/* Category Feedback Performance Table */}
      <div style={{ marginBottom: "32px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
          <div>
            <h3 style={{ fontFamily: "var(--font-serif)", fontSize: "1.3rem", margin: 0 }}>
              Category Feedback Performance
            </h3>
            <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginTop: "4px" }}>
              All 12 domain categories tracked. Effected by reader votes and adjustable via editorial override.
            </p>
          </div>
          <button
            className="action-btn-secondary"
            onClick={onRefreshAnalytics}
            disabled={loading}
            title="Refresh analytics"
            style={{ padding: "6px 12px", fontSize: "0.8rem" }}
          >
            <RefreshCw size={13} className={loading ? "spin" : ""} />
            <span>Refresh Analytics</span>
          </button>
        </div>

        <div className="inspector-table-wrapper">
          <table className="inspector-table">
            <thead>
              <tr>
                <th>Domain Category</th>
                <th style={{ textAlign: "center" }}>Upvotes</th>
                <th style={{ textAlign: "center" }}>Downvotes</th>
                <th style={{ textAlign: "center" }}>Total Votes</th>
                <th style={{ minWidth: "150px" }}>Approval Rate</th>
                <th style={{ textAlign: "center" }}>Reader Bias</th>
                <th style={{ textAlign: "center" }}>Editorial Status</th>
                <th style={{ textAlign: "center" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {analytics.categories.map((c) => {
                const isOverridden = c.override_active;
                const quorumMet = c.total_votes >= 3;
                const approvalPct = Math.round(c.approval_rate * 100);

                return (
                  <tr key={c.slug}>
                    <td>
                      <div style={{ fontWeight: 600, color: "var(--text-main)" }}>{c.category_name}</div>
                      <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                        {c.slug}
                      </div>
                    </td>
                    <td style={{ textAlign: "center", color: "var(--accent-green)", fontWeight: 700, fontFamily: "var(--font-mono)" }}>
                      +{c.upvotes}
                    </td>
                    <td style={{ textAlign: "center", color: "var(--primary)", fontWeight: 700, fontFamily: "var(--font-mono)" }}>
                      -{c.downvotes}
                    </td>
                    <td style={{ textAlign: "center", fontFamily: "var(--font-mono)" }}>
                      <span style={{ fontSize: "0.82rem", color: quorumMet ? "var(--text-main)" : "var(--text-faint)" }}>
                        {c.total_votes}
                      </span>
                      {!quorumMet && c.total_votes > 0 && (
                        <span style={{ display: "block", fontSize: "0.68rem", color: "var(--accent-amber)" }}>
                          &lt;3 quorum
                        </span>
                      )}
                    </td>
                    <td>
                      <div className="category-approval-bar-wrapper">
                        <div className="category-approval-bar">
                          <div
                            className="category-approval-fill"
                            style={{
                              width: `${approvalPct}%`,
                              background:
                                c.total_votes === 0
                                  ? "var(--text-faint)"
                                  : approvalPct >= 65
                                  ? "var(--accent-green)"
                                  : approvalPct <= 40
                                  ? "var(--primary)"
                                  : "var(--accent-amber)",
                            }}
                          />
                        </div>
                        <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.8rem", minWidth: "36px" }}>
                          {c.total_votes === 0 ? "50%" : `${approvalPct}%`}
                        </span>
                      </div>
                    </td>
                    <td style={{ textAlign: "center", fontFamily: "var(--font-mono)" }}>
                      <span
                        className={`score-chip ${
                          c.raw_bias > 0 ? "high" : c.raw_bias < 0 ? "low" : "mid"
                        }`}
                      >
                        {c.raw_bias > 0 ? `+${c.raw_bias.toFixed(2)}` : c.raw_bias.toFixed(2)}
                      </span>
                    </td>
                    <td style={{ textAlign: "center" }}>
                      {isOverridden ? (
                        <span
                          className="override-status-chip overridden"
                          title={c.override_reason ? `Reason: ${c.override_reason}` : "Editorial override active"}
                        >
                          <Settings2 size={12} />
                          <span>{c.override_bias! > 0 ? `+${c.override_bias!.toFixed(2)}` : c.override_bias!.toFixed(2)} Override</span>
                        </span>
                      ) : (
                        <span className="override-status-chip auto">
                          Auto Reader
                        </span>
                      )}
                    </td>
                    <td style={{ textAlign: "center" }}>
                      <div style={{ display: "inline-flex", gap: "6px" }}>
                        <button
                          className="action-btn-secondary"
                          onClick={() => onOpenOverrideModal(c)}
                          title="Edit category bias override"
                          style={{ padding: "4px 8px", fontSize: "0.76rem" }}
                        >
                          <Edit2 size={12} />
                          <span>Override</span>
                        </button>
                        {isOverridden && (
                          <button
                            className="action-btn-secondary"
                            onClick={() => onResetCategoryOverride(c.slug, c.category_name)}
                            title="Reset override to auto reader bias"
                            style={{ padding: "4px 8px", fontSize: "0.76rem", color: "var(--text-muted)" }}
                          >
                            <RotateCcw size={12} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Granular Reader Votes Stream & Effected Categories Log */}
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
          <div>
            <h3 style={{ fontFamily: "var(--font-serif)", fontSize: "1.3rem", margin: 0 }}>
              Recent Reader Votes & Effected Categories Log
            </h3>
            <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginTop: "4px" }}>
              Detailed audit stream showing individual reader submissions, voted stories, and the domain categories effected.
            </p>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>Time Window:</span>
            <select
              value={historyDays}
              onChange={(e) => {
                const days = Number(e.target.value);
                onHistoryDaysChange(days);
              }}
              style={{
                background: "var(--bg-surface-raised)",
                border: "1px solid var(--border-color)",
                color: "var(--text-main)",
                borderRadius: "4px",
                padding: "4px 8px",
                fontSize: "0.8rem",
              }}
            >
              <option value={7}>Last 7 Days</option>
              <option value={14}>Last 14 Days</option>
              <option value={30}>Last 30 Days</option>
              <option value={90}>Last 90 Days</option>
            </select>
            <button
              className="action-btn-secondary"
              onClick={onRefreshHistory}
              disabled={historyLoading}
              style={{ padding: "5px 10px", fontSize: "0.78rem" }}
            >
              <RefreshCw size={12} className={historyLoading ? "spin" : ""} />
              <span>Refresh Log</span>
            </button>
          </div>
        </div>

        <div className="inspector-table-wrapper">
          <table className="inspector-table vote-stream-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Voted Story</th>
                <th style={{ textAlign: "center" }}>Reader Vote</th>
                <th>Domain Categories Effected</th>
                <th>Session ID</th>
                <th style={{ textAlign: "center" }}>Editorial Actions</th>
              </tr>
            </thead>
            <tbody>
              {feedbackHistory.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: "center", padding: "28px", color: "var(--text-muted)" }}>
                    No reader votes recorded in the selected {historyDays}-day window.
                  </td>
                </tr>
              ) : (
                feedbackHistory.map((item) => (
                  <tr key={item.id}>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: "0.76rem", whiteSpace: "nowrap", color: "var(--text-muted)" }}>
                      {item.created_at ? new Date(item.created_at).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : "—"}
                    </td>
                    <td style={{ maxWidth: "300px" }}>
                      <div style={{ fontWeight: 600, color: "var(--text-main)", fontSize: "0.86rem", lineHeight: "1.3" }}>
                        {item.story_title}
                      </div>
                    </td>
                    <td style={{ textAlign: "center" }}>
                      <span className={`vote-badge-pill ${item.vote === 1 ? "up" : "down"}`}>
                        {item.vote === 1 ? (
                          <>
                            <ThumbsUp size={12} />
                            <span>+1 Upvote</span>
                          </>
                        ) : (
                          <>
                            <ThumbsDown size={12} />
                            <span>-1 Downvote</span>
                          </>
                        )}
                      </span>
                    </td>
                    <td>
                      {item.categories.length === 0 ? (
                        <span style={{ fontSize: "0.75rem", color: "var(--text-faint)" }}>No category tags</span>
                      ) : (
                        item.categories.map((cat) => (
                          <span key={cat.slug} className="category-pill-tag">
                            {cat.name}
                          </span>
                        ))
                      )}
                    </td>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: "0.72rem", color: "var(--text-faint)" }}>
                      {item.session_id.substring(0, 12)}...
                    </td>
                    <td style={{ textAlign: "center" }}>
                      <div style={{ display: "inline-flex", gap: "6px" }}>
                        <button
                          className="action-btn-secondary"
                          onClick={() => onFlipVote(item)}
                          disabled={voteActionLoading === item.id}
                          title={`Flip vote to ${item.vote === 1 ? "Downvote" : "Upvote"}`}
                          style={{ padding: "4px 8px", fontSize: "0.74rem" }}
                        >
                          <ArrowUpDown size={11} />
                          <span>Flip</span>
                        </button>
                        <button
                          className="action-btn-secondary"
                          onClick={() => onDeleteVote(item)}
                          disabled={voteActionLoading === item.id}
                          title="Delete reader vote record"
                          style={{ padding: "4px 8px", fontSize: "0.74rem", color: "var(--primary)" }}
                        >
                          <Trash2 size={11} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
