import React, { useState } from "react";
import { Lock, AlertTriangle, KeyRound, RefreshCw } from "lucide-react";
import { loginEditorialAdmin } from "../../api";

interface AdminLoginProps {
  onAuthenticated: () => void;
}

export const AdminLogin: React.FC<AdminLoginProps> = ({ onAuthenticated }) => {
  const [passwordInput, setPasswordInput] = useState<string>("");
  const [authError, setAuthError] = useState<string | null>(null);
  const [isLoggingIn, setIsLoggingIn] = useState<boolean>(false);

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!passwordInput.trim()) return;
    setIsLoggingIn(true);
    setAuthError(null);
    const res = await loginEditorialAdmin(passwordInput);
    setIsLoggingIn(false);
    if (res.success) {
      setPasswordInput("");
      onAuthenticated();
    } else {
      setAuthError(res.error || "Invalid password. Access denied.");
    }
  };

  return (
    <div
      style={{
        maxWidth: "460px",
        margin: "60px auto",
        padding: "36px 32px",
        background: "var(--bg-surface-raised)",
        border: "1px solid var(--border-color)",
        borderRadius: "14px",
        boxShadow: "0 12px 40px rgba(0, 0, 0, 0.28)",
        textAlign: "center",
      }}
    >
      <div
        style={{
          width: "56px",
          height: "56px",
          borderRadius: "50%",
          background: "rgba(59, 130, 246, 0.12)",
          border: "1px solid var(--primary)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          margin: "0 auto 18px",
        }}
      >
        <Lock size={26} color="var(--primary)" />
      </div>

      <h2 style={{ fontFamily: "var(--font-serif)", fontSize: "1.65rem", margin: "0 0 8px" }}>
        Editorial Admin & Pipeline
      </h2>
      <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", lineHeight: 1.5, margin: "0 0 24px" }}>
        This administrative surface is password-protected. Please enter the password to access pipeline telemetry, candidate audit logs, and publication controls.
      </p>

      {authError && (
        <div
          style={{
            background: "rgba(239, 68, 68, 0.12)",
            border: "1px solid rgba(239, 68, 68, 0.35)",
            color: "#ef4444",
            padding: "10px 14px",
            borderRadius: "8px",
            fontSize: "0.88rem",
            marginBottom: "18px",
            textAlign: "left",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          <AlertTriangle size={16} color="#ef4444" style={{ flexShrink: 0 }} />
          <span>{authError}</span>
        </div>
      )}

      <form onSubmit={handleLoginSubmit}>
        <div style={{ marginBottom: "18px", textAlign: "left" }}>
          <label
            htmlFor="admin-password-input"
            style={{
              display: "block",
              fontSize: "0.8rem",
              fontFamily: "var(--font-mono)",
              color: "var(--text-muted)",
              marginBottom: "6px",
              letterSpacing: "0.04em",
            }}
          >
            ADMIN PASSWORD
          </label>
          <input
            id="admin-password-input"
            type="password"
            value={passwordInput}
            onChange={(e) => setPasswordInput(e.target.value)}
            placeholder="Enter password..."
            autoFocus
            style={{
              width: "100%",
              padding: "12px 14px",
              borderRadius: "8px",
              border: "1px solid var(--border-color)",
              background: "var(--bg-surface)",
              color: "var(--text-main)",
              fontSize: "0.95rem",
              fontFamily: "inherit",
              outline: "none",
              boxSizing: "border-box",
            }}
          />
        </div>

        <button
          type="submit"
          disabled={isLoggingIn || !passwordInput.trim()}
          className="action-btn-primary"
          style={{
            width: "100%",
            justifyContent: "center",
            padding: "12px",
            fontSize: "0.95rem",
          }}
        >
          {isLoggingIn ? (
            <RefreshCw size={16} className="spin" style={{ animation: "spin 1s linear infinite" }} />
          ) : (
            <KeyRound size={16} />
          )}
          {isLoggingIn ? "Verifying..." : "Unlock Admin Dashboard"}
        </button>
      </form>
    </div>
  );
};
