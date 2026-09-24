import React, { useEffect, useState, useMemo } from 'react';
import {
  fetchTodayEdition,
  fetchEditionByDate,
  fetchEditionsList,
  type EditionDetail,
} from './api';
import { Header } from './components/Header';
import { LeadStoryCard } from './components/LeadStoryCard';
import { StoryCard } from './components/StoryCard';
import { ArchiveView } from './components/ArchiveView';
import { CategoryView } from './components/CategoryView';
import { SearchView } from './components/SearchView';
import { AdminInspector } from './components/AdminInspector';
import {
  AlertTriangle,
  RefreshCw,
  X,
  Radio,
  Cpu,
  Info,
} from 'lucide-react';

export const App: React.FC = () => {
  // Theme state
  const [isDark, setIsDark] = useState<boolean>(() => {
    const saved = localStorage.getItem('ainews_theme');
    if (saved) return saved === 'dark';
    return true; // default dark mode for sleek terminal aesthetic
  });

  // Navigation & View state
  const [currentView, setCurrentView] = useState<string>('today');
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  // Edition state
  const [edition, setEdition] = useState<EditionDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [fallbackNotice, setFallbackNotice] = useState<string | null>(null);

  // Apply theme to html root
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    localStorage.setItem('ainews_theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  // Fetch edition data when viewing 'today' (or specific date) with graceful fallback
  const loadEdition = async (dateStr?: string | null) => {
    setLoading(true);
    setError(null);
    setFallbackNotice(null);
    try {
      let data: EditionDetail;
      if (dateStr) {
        data = await fetchEditionByDate(dateStr);
      } else {
        try {
          data = await fetchTodayEdition();
        } catch (todayErr: any) {
          console.warn("Today's briefing not available or server error, falling back to archive:", todayErr);
          // Graceful fallback to latest published edition from archive
          try {
            const archive = await fetchEditionsList();
            if (archive && archive.length > 0) {
              data = await fetchEditionByDate(archive[0].date);
              setFallbackNotice(
                `Today's edition is currently being finalized. Showing latest published briefing from ${archive[0].date}.`
              );
            } else {
              throw todayErr;
            }
          } catch (archiveErr) {
            // Check localStorage cache as secondary fallback
            const cached = localStorage.getItem("ainews_cached_edition");
            if (cached) {
              data = JSON.parse(cached);
              setFallbackNotice(
                `Server temporarily unreachable. Showing cached briefing from ${data.date}.`
              );
            } else {
              throw todayErr;
            }
          }
        }
      }
      setEdition(data);
      if (!dateStr && !fallbackNotice) {
        try {
          localStorage.setItem("ainews_cached_edition", JSON.stringify(data));
        } catch (_) {}
      }
    } catch (err: any) {
      console.error('Error fetching edition:', err);
      // As a last resort, check offline cache
      const cached = localStorage.getItem("ainews_cached_edition");
      if (cached) {
        try {
          const parsed = JSON.parse(cached);
          setEdition(parsed);
          setFallbackNotice(`Offline mode: Showing cached briefing from ${parsed.date}.`);
          setError(null);
          return;
        } catch (_) {}
      }
      setError(err?.message || 'Failed to load edition');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (currentView === 'today') {
      loadEdition(selectedDate);
    }
  }, [currentView, selectedDate]);

  const handleToggleTheme = () => {
    setIsDark((prev) => !prev);
  };

  const handleViewChange = (view: string) => {
    setCurrentView(view);
    if (view === 'today' && selectedDate) {
      // If user clicks "Today's Briefing" tab, reset to latest today edition
      setSelectedDate(null);
    }
  };

  const handleSelectEdition = (dateStr: string) => {
    setSelectedDate(dateStr);
    setCurrentView('today');
  };

  const handleSelectCategory = (slug: string) => {
    setSelectedCategory(slug);
    setCurrentView('today');
  };

  // Determine Lead Story and Secondary Stories
  const { leadStory, secondaryStories } = useMemo(() => {
    if (!edition || !edition.stories) {
      return { leadStory: null, secondaryStories: [] };
    }

    let allStories = [...edition.stories];

    // Category filter if active
    if (selectedCategory) {
      allStories = allStories.filter((s) =>
        s.categories?.some((c) => c.slug === selectedCategory || c.name.toLowerCase() === selectedCategory.toLowerCase())
      );
    }

    // Lead story is either edition.lead_story or first story flagged is_lead or first story in list
    const lead =
      edition.lead_story ||
      allStories.find((s) => s.is_lead) ||
      (allStories.length > 0 ? allStories[0] : null);

    const secondaries = allStories.filter((s) => s.id !== lead?.id);

    return { leadStory: lead, secondaryStories: secondaries };
  }, [edition, selectedCategory]);

  return (
    <div className="app-container">
      <Header
        currentView={currentView}
        onViewChange={handleViewChange}
        isDark={isDark}
        onToggleTheme={handleToggleTheme}
        editionDate={edition?.date}
        editionStatus={edition?.status}
      />

      <main className="main-content">
        {currentView === 'today' && (
          <>
            {selectedDate && (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  background: 'var(--bg-surface-raised)',
                  border: '1px solid var(--border-color)',
                  padding: '10px 16px',
                  borderRadius: '8px',
                  marginBottom: '20px',
                  fontSize: '0.88rem',
                }}
              >
                <span>
                  Viewing archived edition for <strong>{selectedDate}</strong>
                </span>
                <button
                  onClick={() => setSelectedDate(null)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--primary)',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}
                >
                  <X size={15} /> Return to Latest Today
                </button>
              </div>
            )}

            {selectedCategory && (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  background: 'var(--primary-subtle)',
                  border: '1px solid var(--primary)',
                  padding: '10px 16px',
                  borderRadius: '8px',
                  marginBottom: '20px',
                  fontSize: '0.88rem',
                }}
              >
                <span>
                  Filter active: Stories in <strong>{selectedCategory}</strong>
                </span>
                <button
                  onClick={() => setSelectedCategory(null)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--primary)',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}
                >
                  <X size={15} /> Clear Filter
                </button>
              </div>
            )}

            {loading ? (
              <div
                style={{
                  padding: '80px 20px',
                  textAlign: 'center',
                  color: 'var(--text-muted)',
                }}
              >
                <RefreshCw
                  size={32}
                  className="spin"
                  style={{
                    animation: 'spin 1s linear infinite',
                    margin: '0 auto 16px',
                    color: 'var(--primary)',
                  }}
                />
                <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.92rem' }}>
                  Loading autonomous editorial briefing...
                </p>
              </div>
            ) : error ? (
              <div
                style={{
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  padding: '28px',
                  borderRadius: '10px',
                  textAlign: 'center',
                  margin: '40px 0',
                }}
              >
                <AlertTriangle size={36} color="#ef4444" style={{ margin: '0 auto 12px' }} />
                <h3 style={{ margin: '0 0 8px', color: '#ef4444' }}>Unable to load edition</h3>
                <p style={{ color: 'var(--text-muted)', margin: '0 0 16px' }}>{error}</p>
                <button
                  onClick={() => loadEdition(selectedDate)}
                  className="action-btn-primary"
                >
                  <RefreshCw size={14} /> Retry Loading
                </button>
              </div>
            ) : edition ? (
              <>
                {/* Fallback Edition Notice (PRD Resiliency Rule) */}
                {fallbackNotice && (
                  <div
                    style={{
                      background: 'rgba(59, 130, 246, 0.08)',
                      border: '1px solid rgba(59, 130, 246, 0.3)',
                      padding: '12px 18px',
                      borderRadius: '8px',
                      marginBottom: '20px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      color: 'var(--text-main)',
                      fontSize: '0.88rem',
                    }}
                  >
                    <Info size={18} color="#3b82f6" style={{ flexShrink: 0 }} />
                    <span style={{ flex: 1 }}>{fallbackNotice}</span>
                    <button
                      onClick={() => loadEdition(null)}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--primary)',
                        cursor: 'pointer',
                        fontWeight: 600,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        fontSize: '0.82rem',
                      }}
                    >
                      <RefreshCw size={13} /> Check Today
                    </button>
                  </div>
                )}

                {/* Low Signal Day Banner (PRD2 Rule) */}
                {edition.low_signal_notice && (
                  <div
                    style={{
                      background: 'rgba(245, 158, 11, 0.12)',
                      border: '1px solid var(--accent-amber)',
                      padding: '16px 20px',
                      borderRadius: '8px',
                      marginBottom: '24px',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '12px',
                    }}
                  >
                    <Radio size={20} color="var(--accent-amber)" style={{ marginTop: '2px', flexShrink: 0 }} />
                    <div>
                      <strong style={{ color: 'var(--accent-amber)', display: 'block', marginBottom: '4px' }}>
                        Low Signal Notice
                      </strong>
                      <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
                        {edition.low_signal_notice}
                      </p>
                    </div>
                  </div>
                )}

                {/* Briefing Intro Banner */}
                <section className="briefing-banner">
                  <h2>{edition.title}</h2>
                  {edition.introduction && <p>{edition.introduction}</p>}
                </section>

                {/* Lead Story */}
                {leadStory ? (
                  <section style={{ marginBottom: '40px' }}>
                    <h2 className="story-section-title">
                      <span>TODAY'S LEAD STORY</span>
                    </h2>
                    <LeadStoryCard story={leadStory} />
                  </section>
                ) : null}

                {/* Secondary Stories Grid */}
                {secondaryStories.length > 0 ? (
                  <section style={{ marginBottom: '40px' }}>
                    <h2 className="story-section-title">
                      <span>
                        {selectedCategory
                          ? `FILTERED STORIES (${secondaryStories.length})`
                          : 'SIGNIFICANT TECHNICAL DEVELOPMENTS'}
                      </span>
                    </h2>
                    <div className="secondary-stories-grid">
                      {secondaryStories.map((story, index) => (
                        <StoryCard key={story.id} story={story} index={index} />
                      ))}
                    </div>
                  </section>
                ) : !leadStory ? (
                  <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
                    No stories available for this edition or category.
                  </div>
                ) : null}
              </>
            ) : null}
          </>
        )}

        {currentView === 'archive' && (
          <ArchiveView onSelectEdition={handleSelectEdition} />
        )}

        {currentView === 'categories' && (
          <CategoryView
            selectedCategory={selectedCategory}
            onSelectCategory={handleSelectCategory}
          />
        )}

        {currentView === 'search' && <SearchView />}

        {currentView === 'admin' && <AdminInspector />}
      </main>

      <footer className="site-footer">
        <div className="footer-inner">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <span style={{ fontWeight: 700, letterSpacing: '0.04em', color: 'var(--text-main)' }}>
              AI INDUSTRY NEWS DAILY
            </span>
            <span>Signal over volume. Importance over popularity.</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '0.8rem' }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', fontFamily: 'var(--font-mono)' }}>
              <Cpu size={14} color="var(--primary)" /> Google ADK 2.x + OpenRouter
            </span>
            <span>&bull;</span>
            <span>MCP Editorial Server</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
