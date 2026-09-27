import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import { ThumbsUp, ThumbsDown, ExternalLink, ChevronDown, ChevronUp, Zap, Sparkles, Clock, CheckCircle2 } from "lucide-react";
import { type Story, sendFeedback } from "../api";
import { cleanProseMarkdown, formatBodyMarkdown } from "../utils/markdown";

interface LeadStoryCardProps {
  story: Story;
}

export const LeadStoryCard: React.FC<LeadStoryCardProps> = ({ story }) => {
  const [expanded, setExpanded] = useState(false);
  const [userVote, setUserVote] = useState<number | null>(null);
  const [upCount, setUpCount] = useState<number>(story.upvotes || 0);
  const [downCount, setDownCount] = useState<number>(story.downvotes || 0);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleVote = async (voteVal: number) => {
    if (isSubmitting || userVote === voteVal) return;
    setIsSubmitting(true);
    try {
      const res = await sendFeedback(story.id, voteVal);
      setUserVote(voteVal);
      setUpCount(res.upvotes);
      setDownCount(res.downvotes);
    } catch (e) {
      console.error("Feedback error:", e);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <article className="lead-story-card" id={`story-${story.id}`}>
      <div className="lead-header-row">
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span className="lead-badge">
            <Zap size={13} style={{ marginRight: "4px", verticalAlign: "middle" }} />
            Today's Lead Story
          </span>
          <div className="category-tags">
            {story.categories.map((c) => (
              <span key={c.id || c.slug} className="cat-tag">
                {c.name}
              </span>
            ))}
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          {story.published_at && (
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.78rem", color: "var(--text-muted)", display: "inline-flex", alignItems: "center", gap: "4px" }}>
              <Clock size={12} />
              Published: {new Date(story.published_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
            </span>
          )}
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.78rem", color: "var(--text-faint)" }}>
            #1 OF BRIEFING
          </span>
        </div>
      </div>

      <h2 className="lead-title">{story.title}</h2>

      {story.image_url && (
        <div className="story-hero-image-wrap lead-hero-wrap">
          <img
            src={story.image_url}
            alt={story.title}
            className="story-hero-image lead-hero-image"
            loading="lazy"
            onError={(e) => {
              const parent = e.currentTarget.parentElement;
              if (parent) parent.style.display = "none";
            }}
          />
        </div>
      )}

      <div className="lead-summary">
        <ReactMarkdown>{cleanProseMarkdown(story.summary)}</ReactMarkdown>
      </div>

      <div className="why-matters-box">
        <div className="why-matters-label">
          <Sparkles size={14} />
          Why It Matters
        </div>
        <div className="why-matters-text">
          <ReactMarkdown>{cleanProseMarkdown(story.why_it_matters)}</ReactMarkdown>
        </div>
      </div>

      {story.body && (
        <>
          <button
            className="expand-toggle"
            onClick={() => setExpanded(!expanded)}
            id={`toggle-body-${story.id}`}
          >
            {expanded ? (
              <>
                <ChevronUp size={16} /> Hide Technical Deep-Dive
              </>
            ) : (
              <>
                <ChevronDown size={16} /> Read Technical Deep-Dive & Analysis
              </>
            )}
          </button>

          {expanded && (
            <div className="story-body-block">
              <ReactMarkdown>{formatBodyMarkdown(story.body)}</ReactMarkdown>
            </div>
          )}
        </>
      )}

      <div className="story-footer">
        <div className="sources-list">
          <span className="source-label">Sources:</span>
          {story.sources.map((src, i) => (
            <a
              key={i}
              href={src.url}
              target="_blank"
              rel="noopener noreferrer"
              className="source-link"
              title={src.title}
            >
              <CheckCircle2 size={12} color="var(--accent-green)" />
              <span>{src.publisher || "Direct Source"}</span>
              <ExternalLink size={12} />
            </a>
          ))}
        </div>

        <div className="feedback-actions">
          <button
            className={`vote-btn ${userVote === 1 ? "voted-up" : ""}`}
            onClick={() => handleVote(1)}
            disabled={isSubmitting}
            title="High signal — more of this"
            id={`upvote-lead-${story.id}`}
          >
            <ThumbsUp size={15} />
            <span className="vote-count">{upCount}</span>
          </button>
          <button
            className={`vote-btn ${userVote === -1 ? "voted-down" : ""}`}
            onClick={() => handleVote(-1)}
            disabled={isSubmitting}
            title="Low signal / marketing fluff"
            id={`downvote-lead-${story.id}`}
          >
            <ThumbsDown size={15} />
            <span className="vote-count">{downCount}</span>
          </button>
        </div>
      </div>
    </article>
  );
};
