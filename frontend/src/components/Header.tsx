import React from 'react';
import { Sun, Moon, Sparkles, Archive, Search, Sliders, ShieldCheck, Tag } from 'lucide-react';

interface HeaderProps {
  currentView: string;
  onViewChange: (view: string) => void;
  isDark: boolean;
  onToggleTheme: () => void;
  editionDate?: string;
  editionStatus?: string;
}

export const Header: React.FC<HeaderProps> = ({
  currentView,
  onViewChange,
  isDark,
  onToggleTheme,
  editionDate,
  editionStatus,
}) => {
  const formattedDate = editionDate
    ? new Date(editionDate + 'T00:00:00').toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : new Date().toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });

  return (
    <header className="masthead">
      <div className="masthead-inner">
        <div className="masthead-top">
          <div className="edition-meta">
            <span>VOL. I &bull; NO. 248</span>
            <span>&bull;</span>
            <span>{formattedDate.toUpperCase()}</span>
            {editionStatus && (
              <span className={`badge-pill status-${editionStatus}`}>
                <ShieldCheck size={13} />
                {editionStatus}
              </span>
            )}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span>AUTONOMOUS BRIEFING PLATFORM</span>
            <button
              className="theme-toggle-btn"
              onClick={onToggleTheme}
              aria-label="Toggle theme"
              id="theme-toggle-btn"
            >
              {isDark ? <Sun size={15} /> : <Moon size={15} />}
              <span>{isDark ? 'Light' : 'Dark'}</span>
            </button>
          </div>
        </div>

        <div className="masthead-brand">
          <div>
            <h1 className="brand-title">AI INDUSTRY NEWS DAILY</h1>
            <p className="brand-tagline">Signal over volume. Importance over popularity.</p>
          </div>
          <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--text-faint)' }}>
              LOCAL INTRANET EDITION
            </span>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--primary)' }}>
              FRONTIER SIGNAL STANDARDS
            </span>
          </div>
        </div>

        <nav className="masthead-nav">
          <ul className="nav-links">
            <li>
              <button
                className={`nav-btn ${currentView === 'today' ? 'active' : ''}`}
                onClick={() => onViewChange('today')}
                id="nav-today-btn"
              >
                <Sparkles size={16} />
                Today's Briefing
              </button>
            </li>
            <li>
              <button
                className={`nav-btn ${currentView === 'archive' ? 'active' : ''}`}
                onClick={() => onViewChange('archive')}
                id="nav-archive-btn"
              >
                <Archive size={16} />
                Archive
              </button>
            </li>
            <li>
              <button
                className={`nav-btn ${currentView === 'categories' ? 'active' : ''}`}
                onClick={() => onViewChange('categories')}
                id="nav-categories-btn"
              >
                <Tag size={16} />
                Taxonomy
              </button>
            </li>
            <li>
              <button
                className={`nav-btn ${currentView === 'search' ? 'active' : ''}`}
                onClick={() => onViewChange('search')}
                id="nav-search-btn"
              >
                <Search size={16} />
                Search
              </button>
            </li>
            <li>
              <button
                className={`nav-btn ${currentView === 'admin' ? 'active' : ''}`}
                onClick={() => onViewChange('admin')}
                id="nav-admin-btn"
              >
                <Sliders size={16} />
                Editorial Admin & Pipeline
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
};
