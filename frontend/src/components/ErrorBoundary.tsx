import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error in ErrorBoundary:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div
          style={{
            padding: "2rem",
            maxWidth: "600px",
            margin: "3rem auto",
            textAlign: "center",
            border: "1px solid var(--border, #e2e8f0)",
            borderRadius: "8px",
            background: "var(--bg-secondary, #f8fafc)",
          }}
        >
          <h2 style={{ color: "var(--text-primary, #0f172a)", marginBottom: "1rem" }}>
            Something went wrong
          </h2>
          <p style={{ color: "var(--text-secondary, #64748b)", marginBottom: "1.5rem" }}>
            An unexpected error occurred while rendering this view.
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: "0.5rem 1.25rem",
              background: "var(--primary, #2563eb)",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              fontWeight: 500,
            }}
          >
            Reload Application
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
