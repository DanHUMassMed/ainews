import React, { useEffect, useState } from 'react';
import { Calendar, ChevronRight, BookOpen } from 'lucide-react';
import { type EditionSummary, fetchEditionsList } from '../api';

interface ArchiveViewProps {
  onSelectEdition: (dateStr: string) => void;
}

export const ArchiveView: React.FC<ArchiveViewProps> = ({ onSelectEdition }) => {
  const [editions, setEditions] = useState<EditionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchEditionsList()
      .then((data) => {
        setEditions(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
        Loading publication archive...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--primary)' }}>
        Error loading archive: {error}
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: '1.8rem', marginBottom: '8px' }}>
          Historical Briefing Archive
        </h2>
        <p style={{ color: 'var(--text-muted)' }}>
          Browse every daily edition published by the autonomous editorial engine.
        </p>
      </div>

      <div className="archive-list">
        {editions.map((ed) => {
          const dateObj = new Date(ed.date + 'T00:00:00');
          const formatted = dateObj.toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric',
            year: 'numeric',
          });

          return (
            <div
              key={ed.id}
              className="archive-item"
              onClick={() => onSelectEdition(ed.date)}
              id={`archive-edition-${ed.date}`}
            >
              <div>
                <div className="archive-date">
                  <Calendar size={14} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
                  {formatted.toUpperCase()} &bull; {ed.date}
                </div>
                <div className="archive-title">{ed.title}</div>
                {ed.introduction && (
                  <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    {ed.introduction.length > 120
                      ? ed.introduction.substring(0, 120) + '...'
                      : ed.introduction}
                  </p>
                )}
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <span className="cat-tag" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <BookOpen size={13} />
                  {ed.story_count} stories
                </span>
                <ChevronRight size={18} color="var(--text-faint)" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
