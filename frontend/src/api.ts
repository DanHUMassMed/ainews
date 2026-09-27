export interface Source {
  url: string;
  title: string;
  publisher?: string;
  published_at?: string;
  source_type?: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string;
  story_count?: number;
}

export interface Story {
  id: string;
  slug: string;
  title: string;
  summary: string;
  body?: string;
  why_it_matters: string;
  image_url?: string | null;
  is_lead: boolean;
  position: number;
  categories: Category[];
  sources: Source[];
  upvotes?: number;
  downvotes?: number;
  userVote?: number; // 1, -1, or 0
  published_at?: string;
}

export interface EditionDetail {
  id: string;
  date: string;
  title: string;
  introduction?: string;
  status: string;
  low_signal_notice?: string;
  published_at?: string;
  lead_story?: Story;
  stories: Story[];
}

export interface EditionSummary {
  id: string;
  date: string;
  title: string;
  introduction?: string;
  status: string;
  story_count: number;
  published_at?: string;
}

export interface CandidateItem {
  id: string;
  title: string;
  url: string;
  significance_score?: number;
  novelty_score?: number;
  evidence_score?: number;
  saturation_score?: number;
  feedback_bias?: number;
  composite_score?: number;
  selected: boolean;
  rejected_reason?: string;
  discovered_at: string;
  created_at?: string;
  metadata_json?: {
    edition_date?: string;
    published_at?: string;
    occurrence_date?: string;
    recovered_from_backup?: boolean;
    [key: string]: any;
  };
}

export interface FeedbackAnalytics {
  window_days: number;
  total_votes: number;
  total_upvotes: number;
  total_downvotes: number;
  overall_approval_rate: number;
  cold_start_active: boolean;
  categories: Array<{
    category_name: string;
    slug: string;
    upvotes: number;
    downvotes: number;
    approval_rate: number;
  }>;
  top_positive_topics: string[];
  top_negative_topics: string[];
}

const DEFAULT_HERMES_TOKEN = "hermes_editorial_secret_token_change_in_production";

export function getEditorialToken(): string {
  return sessionStorage.getItem("ainews_editorial_token") || DEFAULT_HERMES_TOKEN;
}

export function isEditorialAdminAuthenticated(): boolean {
  return sessionStorage.getItem("ainews_admin_auth") === "true";
}

export function logoutEditorialAdmin(): void {
  sessionStorage.removeItem("ainews_admin_auth");
  sessionStorage.removeItem("ainews_editorial_token");
}

export async function loginEditorialAdmin(password: string): Promise<{ success: boolean; error?: string }> {
  try {
    const res = await fetch("/api/editorial/auth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });
    if (res.ok) {
      const data = await res.json();
      sessionStorage.setItem("ainews_admin_auth", "true");
      if (data.token) {
        sessionStorage.setItem("ainews_editorial_token", data.token);
      }
      return { success: true };
    }
    const errData = await res.json().catch(() => ({}));
    return { success: false, error: errData.detail || "Invalid password. Access denied." };
  } catch (err: any) {
    return { success: false, error: err.message || "Failed to authenticate" };
  }
}

function getSessionId(): string {
  let sid = localStorage.getItem("ainews_reader_session");
  if (!sid) {
    sid = "sess_" + Math.random().toString(36).substring(2, 12);
    localStorage.setItem("ainews_reader_session", sid);
  }
  return sid;
}

export async function fetchTodayEdition(): Promise<EditionDetail> {
  const res = await fetch("/api/public/editions/today");
  if (!res.ok) {
    throw new Error(`Failed to load today's briefing: ${res.status}`);
  }
  return res.json();
}

export async function fetchEditionByDate(dateStr: string): Promise<EditionDetail> {
  const res = await fetch(`/api/public/editions/${dateStr}`);
  if (!res.ok) {
    throw new Error(`Failed to load edition for ${dateStr}: ${res.status}`);
  }
  return res.json();
}

export async function fetchEditionsList(): Promise<EditionSummary[]> {
  const res = await fetch("/api/public/editions?limit=30");
  if (!res.ok) {
    throw new Error("Failed to load archive editions");
  }
  return res.json();
}

export async function searchStories(query: string): Promise<Story[]> {
  const res = await fetch(`/api/public/search?q=${encodeURIComponent(query)}`);
  if (!res.ok) {
    throw new Error("Search request failed");
  }
  return res.json();
}

export async function fetchCategories(): Promise<Category[]> {
  const res = await fetch("/api/public/categories");
  if (!res.ok) {
    throw new Error("Failed to load categories");
  }
  return res.json();
}

export async function sendFeedback(storyId: string, vote: number): Promise<{ upvotes: number; downvotes: number }> {
  const res = await fetch("/api/public/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      story_id: storyId,
      vote: vote,
      session_id: getSessionId(),
    }),
  });
  if (!res.ok) {
    throw new Error("Failed to register feedback");
  }
  return res.json();
}

export async function fetchEditorialCandidates(limit: number = 100): Promise<CandidateItem[]> {
  const res = await fetch(`/api/editorial/candidates?limit=${limit}`, {
    headers: { Authorization: `Bearer ${getEditorialToken()}` },
  });
  if (!res.ok) {
    throw new Error("Failed to fetch candidate audit trail");
  }
  return res.json();
}

export async function clearEditorialCandidates(): Promise<{ status: string; message: string }> {
  const res = await fetch(`/api/editorial/candidates`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${getEditorialToken()}` },
  });
  if (!res.ok) {
    throw new Error("Failed to clear candidate audit trail");
  }
  return res.json();
}

export async function fetchFeedbackAnalytics(): Promise<FeedbackAnalytics> {
  const res = await fetch("/api/editorial/feedback-analytics", {
    headers: { Authorization: `Bearer ${getEditorialToken()}` },
  });
  if (!res.ok) {
    throw new Error("Failed to fetch feedback analytics");
  }
  return res.json();
}

export async function getEditionGateStatus(editionId: string): Promise<any> {
  const res = await fetch(`/api/editorial/edition/${editionId}/status`, {
    headers: { Authorization: `Bearer ${getEditorialToken()}` },
  });
  if (!res.ok) {
    throw new Error("Failed to fetch edition gate status");
  }
  return res.json();
}

export async function publishEdition(editionId: string): Promise<any> {
  const res = await fetch(`/api/editorial/edition/${editionId}/publish`, {
    method: "POST",
    headers: { Authorization: `Bearer ${getEditorialToken()}` },
  });
  if (!res.ok) {
    throw new Error("Failed to publish edition");
  }
  return res.json();
}

export interface ScoringWeightsConfig {
  significance_weight: number;
  novelty_weight: number;
  evidence_weight: number;
  saturation_weight: number;
  feedback_weight: number;
}

export interface ScoringThresholdsConfig {
  min_selection_threshold: number;
  core_min_score: number;
  core_min_evidence: number;
  exploratory_min_score: number;
  exploratory_min_novelty: number;
  contrarian_min_novelty: number;
  contrarian_max_saturation: number;
  stale_backup_min_score: number;
}

export interface ScoringConfigResponse {
  weights: ScoringWeightsConfig;
  thresholds: ScoringThresholdsConfig;
  description?: string;
  updated_at?: string;
}

export async function fetchScoringConfig(): Promise<ScoringConfigResponse> {
  const token = getEditorialToken();
  const res = await fetch("/api/editorial/config/scoring", {
    headers: { Authorization: "Bearer " + token },
  });
  if (!res.ok) {
    throw new Error("Failed to fetch scoring configuration");
  }
  return res.json();
}

export async function updateScoringConfig(config: {
  weights?: Partial<ScoringWeightsConfig>;
  thresholds?: Partial<ScoringThresholdsConfig>;
}): Promise<ScoringConfigResponse> {
  const token = getEditorialToken();
  const res = await fetch("/api/editorial/config/scoring", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + token,
    },
    body: JSON.stringify(config),
  });
  if (!res.ok) {
    throw new Error("Failed to update scoring configuration");
  }
  return res.json();
}

export async function resetScoringConfig(): Promise<ScoringConfigResponse> {
  const token = getEditorialToken();
  const res = await fetch("/api/editorial/config/scoring/reset", {
    method: "POST",
    headers: { Authorization: "Bearer " + token },
  });
  if (!res.ok) {
    throw new Error("Failed to reset scoring configuration");
  }
  return res.json();
}

export async function fetchCategoryStories(slug: string): Promise<Story[]> {
  const res = await fetch(`/api/public/categories/${slug}`);
  if (!res.ok) {
    throw new Error(`Failed to load stories for category ${slug}`);
  }
  return res.json();
}
