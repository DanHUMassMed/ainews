import React from "react";
import { Lock, RefreshCw, Layers, BarChart3, Sliders, Bot } from "lucide-react";
import type { AdminTab } from "./types";

interface AdminHeaderProps {
  activeTab: AdminTab;
  onTabChange: (tab: AdminTab) => void;
  loading: boolean;
  onRefresh: () => void;
  onLock: () => void;
}

export const AdminHeader: React.FC<AdminHeaderProps> = ({
  activeTab,
  onTabChange,
  loading,
  onRefresh,
  onLock,
}) => {
  return (
    <>
      <div className="admin-header">
        <div>
          <h2 style={{ fontFamily: "var(--font-serif)", fontSize: "1.9rem", marginBottom: "4px" }}>
            Editorial Oversight & Pipeline Inspector
          </h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.92rem" }}>
            Audit candidate scoring, verify publication gate integrity, inspect reader feedback analytics.
          </p>
        </div>
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <button
            onClick={onLock}
            className="action-btn-secondary"
            style={{ borderColor: "rgba(239, 68, 68, 0.4)", color: "#ef4444" }}
            id="admin-lock-btn"
            title="Lock administrative dashboard"
          >
            <Lock size={14} /> Lock Dashboard
          </button>
          <button
            onClick={onRefresh}
            className="action-btn-secondary"
            disabled={loading}
            id="admin-refresh-btn"
          >
            <RefreshCw size={14} className={loading ? "spin" : ""} />
            Refresh
          </button>
        </div>
      </div>

      <div className="admin-tabs">
        <button
          className={`admin-tab-btn ${activeTab === "pipeline" ? "active" : ""}`}
          onClick={() => onTabChange("pipeline")}
          id="tab-pipeline-btn"
        >
          <Layers size={14} style={{ marginRight: "6px", verticalAlign: "middle" }} />
          Pipeline Inspector & Audit Trail
        </button>

        <button
          className={`admin-tab-btn ${activeTab === "feedback" ? "active" : ""}`}
          onClick={() => onTabChange("feedback")}
          id="tab-feedback-btn"
        >
          <BarChart3 size={14} style={{ marginRight: "6px", verticalAlign: "middle" }} />
          Feedback Analytics
        </button>
        <button
          className={`admin-tab-btn ${activeTab === "formula" ? "active" : ""}`}
          onClick={() => onTabChange("formula")}
          id="tab-formula-btn"
        >
          <Sliders size={14} style={{ marginRight: "6px", verticalAlign: "middle" }} />
          Scoring Formula
        </button>
        <button
          className={`admin-tab-btn ${activeTab === "adk" ? "active" : ""}`}
          onClick={() => onTabChange("adk")}
          id="tab-adk-btn"
        >
          <Bot size={14} style={{ marginRight: "6px", verticalAlign: "middle" }} />
          ADK 2.x Agents & Eval
        </button>
      </div>
    </>
  );
};
