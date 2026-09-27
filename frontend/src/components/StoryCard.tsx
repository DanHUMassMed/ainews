import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import { ThumbsUp, ThumbsDown, ExternalLink, ChevronDown, ChevronUp, Sparkles, Clock, CheckCircle2 } from "lucide-react";
import { type Story, sendFeedback } from "../api";
import { cleanProseMarkdown, formatBodyMarkdown } from "../utils/markdown";

interface StoryCardProps {
  story: Story;
  index: number;
}

export const StoryCard: React.FC<StoryCardProps> = ({ story, index }) => {
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
    <article className="story-card" id={`story-${story.id}`}>
      <div className="story-card-top">
        <div className="category-tags">
          {story.categories.map((c) => (
            <span key={c.id || c.slug} className="cat-tag">
              {c.name}
            </span>
          ))}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          {story.published_at && (
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.72rem", color: "var(--text-muted)", display: "inline-flex", alignItems: "center", gap: "4px" }}>
              <Clock size={11} />
              {new Date(story.published_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
            </span>
          )}
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.75rem", color: "var(--text-faint)" }}>
            #{index + 2}
          </span>
        </div>
      </div>

      <h3 className="story-card-title">{story.title}</h3>

      {story.image_url && (
        <div className="story-hero-image-wrap card-hero-wrap">
          <img
            src={story.image_url}
            alt={story.title}
            className="story-hero-image card-hero-image"
            loading="lazy"
            onError={(e) => {
              const parent = e.currentTarget.parentElement;
              if (parent) parent.style.display = "none";
            }}
          />
        </div>
      )}

      <div className="story-card-summary">
        <ReactMarkdown>{cleanProseMarkdown(story.summary)}</ReactMarkdown>
      </div>

      <div className="why-matters-box" style={{ padding: "12px 16px", marginBottom: "16px" }}>
        <div className="why-matters-label" style={{ fontSize: "0.72rem" }}>
          <Sparkles size={13} />
          Why It Matters
        </div>
        <div className="why-matters-text" style={{ fontSize: "0.92rem" }}>
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
                <ChevronUp size={15} /> Hide Details
              </>
            ) : (
              <>
                <ChevronDown size={15} /> Expand Analysis
              </>
            )}
          </button>

          {expanded && (
            <div className="story-body-block" style={{ fontSize: "0.9rem", padding: "14px" }}>
              <ReactMarkdown>{formatBodyMarkdown(story.body)}</ReactMarkdown>
            </div>
          )}
        </>
      )}

      <div className="story-footer">
        <div className="sources-list">
          {story.sources.map((src, i) => (
            <a
              key={i}
              href={src.url}
              target="_blank"
              rel="noopener noreferrer"
              className="source-link"
              title={src.title}
            >
              <CheckCircle2 size={11} color="var(--accent-green)" />
              <span>{src.publisher || "Source"}</span>
              <ExternalLink size={12} />
            </a>
          ))}
        </div>

        <div className="feedback-actions">
          <button
            className={`vote-btn ${userVote === 1 ? "voted-up" : ""}`}
            onClick={() => handleVote(1)}
            disabled={isSubmitting}
            title="High signal"
            id={`upvote-${story.id}`}
          >
            <ThumbsUp size={14} />
            <span className="vote-count">{upCount}</span>
          </button>
          <button
            className={`vote-btn ${userVote === -1 ? "voted-down" : ""}`}
            onClick={() => handleVote(-1)}
            disabled={isSubmitting}
            title="Low signal"
            id={`downvote-${story.id}`}
          >
            <ThumbsDown size={14} />
            <span className="vote-count">{downCount}</span>
          </button>
        </div>
      </div>
    </article>
  );
};
