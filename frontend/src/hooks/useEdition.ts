import { useState, useEffect, useCallback } from 'react';
import {
  fetchTodayEdition,
  fetchEditionByDate,
  fetchEditionsList,
  type EditionDetail,
} from '../api';

export interface UseEditionResult {
  edition: EditionDetail | null;
  loading: boolean;
  error: string | null;
  fallbackNotice: string | null;
  loadEdition: (dateStr?: string | null) => Promise<void>;
  setEdition: React.Dispatch<React.SetStateAction<EditionDetail | null>>;
  dismissFallbackNotice: () => void;
}

export function useEdition(currentView: string, selectedDate: string | null): UseEditionResult {
  const [edition, setEdition] = useState<EditionDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [fallbackNotice, setFallbackNotice] = useState<string | null>(null);

  const loadEdition = useCallback(async (dateStr?: string | null) => {
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
      if (!dateStr) {
        try {
          localStorage.setItem("ainews_cached_edition", JSON.stringify(data));
        } catch (_) {}
      }
    } catch (err: any) {
      console.error('Error fetching edition:', err);
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
  }, []);

  useEffect(() => {
    if (currentView === 'today') {
      loadEdition(selectedDate);
    }
  }, [currentView, selectedDate, loadEdition]);

  const dismissFallbackNotice = useCallback(() => {
    setFallbackNotice(null);
  }, []);

  return {
    edition,
    loading,
    error,
    fallbackNotice,
    loadEdition,
    setEdition,
    dismissFallbackNotice,
  };
}
