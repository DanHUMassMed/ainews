import React, { useEffect, useState } from "react";
import {
  type CandidateItem,
  type FeedbackAnalytics,
  type FeedbackHistoryItem,
  type CategoryFeedbackItem,
  fetchEditorialCandidates,
  clearEditorialCandidates,
  fetchFeedbackAnalytics,
  fetchFeedbackHistory,
  updateFeedbackVote,
  deleteFeedbackVote,
  setCategoryOverride,
  deleteCategoryOverride,
  fetchTodayEdition,
  isEditorialAdminAuthenticated,
  logoutEditorialAdmin,
  fetchScoringConfig,
  updateScoringConfig,
  resetScoringConfig,
  type ScoringWeightsConfig,
  type ScoringThresholdsConfig,
  type ScoringConfigResponse,
} from "../api";
import {
  type AdminTab,
  AdminHeader,
  AdminLogin,
  PipelineInspectorTab,
  FeedbackAnalyticsTab,
  CategoryOverrideModal,
  ScoringFormulaTab,
  AdkArchitectureTab,
} from "./Admin";

export const AdminInspector: React.FC = () => {
  const [activeTab, setActiveTab] = useState<AdminTab>("pipeline");
  const [candidates, setCandidates] = useState<CandidateItem[]>([]);
  const [analytics, setAnalytics] = useState<FeedbackAnalytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() =>
    isEditorialAdminAuthenticated()
  );
  const [activeEditionDate, setActiveEditionDate] = useState<string>("");
  const [isClearing, setIsClearing] = useState<boolean>(false);

  // Feedback Tab & Override State
  const [feedbackHistory, setFeedbackHistory] = useState<FeedbackHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState<boolean>(false);
  const [historyDays, setHistoryDays] = useState<number>(30);
  const [voteActionLoading, setVoteActionLoading] = useState<string | null>(null);
  const [feedbackActionMsg, setFeedbackActionMsg] = useState<string | null>(null);

  // Category Override Modal State
  const [selectedCategoryForOverride, setSelectedCategoryForOverride] =
    useState<CategoryFeedbackItem | null>(null);
  const [isSavingOverride, setIsSavingOverride] = useState<boolean>(false);

  // Scoring Formula & Simulator State
  const [scoringConfig, setScoringConfig] = useState<ScoringConfigResponse | null>(null);
  const [weights, setWeights] = useState<ScoringWeightsConfig>({
    significance_weight: 0.35,
    novelty_weight: 0.25,
    evidence_weight: 0.2,
    saturation_weight: 0.2,
    feedback_weight: 0.15,
  });
  const [thresholds, setThresholds] = useState<ScoringThresholdsConfig>({
    min_selection_threshold: 4.0,
    core_min_score: 6.0,
    core_min_evidence: 7.0,
    exploratory_min_score: 5.0,
    exploratory_min_novelty: 6.5,
    contrarian_min_novelty: 8.0,
    contrarian_max_saturation: 4.0,
    stale_backup_min_score: 4.5,
  });
  const [isSavingConfig, setIsSavingConfig] = useState<boolean>(false);
  const [configSaveSuccess, setConfigSaveSuccess] = useState<string | null>(null);
  const [configSaveError, setConfigSaveError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [candData, analData, todayData, cfgData, histData] = await Promise.all([
        fetchEditorialCandidates(100).catch(() => []),
        fetchFeedbackAnalytics().catch(() => null),
        fetchTodayEdition().catch(() => null),
        fetchScoringConfig().catch(() => null),
        fetchFeedbackHistory(50, 30).catch(() => []),
      ]);
      if (cfgData) {
        setScoringConfig(cfgData);
        if (cfgData.weights) setWeights(cfgData.weights);
        if (cfgData.thresholds) setThresholds(cfgData.thresholds);
      }
      setCandidates(candData);
      setAnalytics(analData);
      setFeedbackHistory(histData);
      if (todayData?.date) {
        setActiveEditionDate(todayData.date);
      } else if (candData[0]?.metadata_json?.edition_date) {
        setActiveEditionDate(candData[0].metadata_json.edition_date);
      } else {
        setActiveEditionDate(new Date().toISOString().split("T")[0]);
      }
    } catch (err) {
      console.error("Failed to load admin data:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadFeedbackHistoryData = async (days: number = historyDays) => {
    setHistoryLoading(true);
    try {
      const hist = await fetchFeedbackHistory(50, days);
      setFeedbackHistory(hist);
    } catch (e) {
      console.error("Failed to load feedback history:", e);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleFlipVote = async (item: FeedbackHistoryItem) => {
    const newVote = item.vote === 1 ? -1 : 1;
    setVoteActionLoading(item.id);
    setFeedbackActionMsg(null);
    try {
      await updateFeedbackVote(item.id, newVote);
      setFeedbackActionMsg(`Vote flipped to ${newVote === 1 ? "+1 Upvote" : "-1 Downvote"}`);
      const [newAnal, newHist] = await Promise.all([
        fetchFeedbackAnalytics().catch(() => null),
        fetchFeedbackHistory(50, historyDays).catch(() => []),
      ]);
      if (newAnal) setAnalytics(newAnal);
      setFeedbackHistory(newHist);
    } catch (err: any) {
      alert("Failed to update vote: " + (err?.message || err));
    } finally {
      setVoteActionLoading(null);
    }
  };

  const handleDeleteVote = async (item: FeedbackHistoryItem) => {
    if (!window.confirm(`Delete reader vote for "${item.story_title}"?`)) return;
    setVoteActionLoading(item.id);
    setFeedbackActionMsg(null);
    try {
      await deleteFeedbackVote(item.id);
      setFeedbackActionMsg("Reader vote deleted");
      const [newAnal, newHist] = await Promise.all([
        fetchFeedbackAnalytics().catch(() => null),
        fetchFeedbackHistory(50, historyDays).catch(() => []),
      ]);
      if (newAnal) setAnalytics(newAnal);
      setFeedbackHistory(newHist);
    } catch (err: any) {
      alert("Failed to delete vote: " + (err?.message || err));
    } finally {
      setVoteActionLoading(null);
    }
  };

  const handleOpenOverrideModal = (cat: CategoryFeedbackItem) => {
    setSelectedCategoryForOverride(cat);
  };

  const handleSaveCategoryOverride = async (
    slug: string,
    bias: number,
    active: boolean,
    reason: string
  ) => {
    setIsSavingOverride(true);
    try {
      await setCategoryOverride(slug, bias, active, reason);
      const catName = selectedCategoryForOverride?.category_name || slug;
      setSelectedCategoryForOverride(null);
      setFeedbackActionMsg(`Override saved for ${catName}`);
      const newAnal = await fetchFeedbackAnalytics();
      setAnalytics(newAnal);
    } catch (err: any) {
      alert("Failed to save override: " + (err?.message || err));
    } finally {
      setIsSavingOverride(false);
    }
  };

  const handleResetCategoryOverride = async (slug: string, name: string) => {
    if (!window.confirm(`Reset editorial override for ${name} back to automatic reader bias?`)) {
      return;
    }
    try {
      await deleteCategoryOverride(slug);
      setFeedbackActionMsg(`Override cleared for ${name}`);
      const newAnal = await fetchFeedbackAnalytics();
      setAnalytics(newAnal);
    } catch (err: any) {
      alert("Failed to reset override: " + (err?.message || err));
    }
  };

  const handleSaveScoringConfig = async () => {
    setIsSavingConfig(true);
    setConfigSaveSuccess(null);
    setConfigSaveError(null);
    try {
      const updated = await updateScoringConfig({ weights, thresholds });
      setScoringConfig(updated);
      setWeights(updated.weights);
      setThresholds(updated.thresholds);
      setConfigSaveSuccess("Scoring weights and thresholds successfully saved to database!");
      setTimeout(() => setConfigSaveSuccess(null), 4000);
    } catch (err: any) {
      console.error("Failed to save scoring config:", err);
      setConfigSaveError(err?.message || "Failed to update configuration");
    } finally {
      setIsSavingConfig(false);
    }
  };

  const handleResetScoringConfig = async () => {
    if (!window.confirm("Reset all scoring weights and thresholds to default canonical values?")) {
      return;
    }
    setIsSavingConfig(true);
    setConfigSaveSuccess(null);
    setConfigSaveError(null);
    try {
      const reset = await resetScoringConfig();
      setScoringConfig(reset);
      setWeights(reset.weights);
      setThresholds(reset.thresholds);
      setConfigSaveSuccess("Reset configuration to default canonical values!");
      setTimeout(() => setConfigSaveSuccess(null), 4000);
    } catch (err: any) {
      console.error("Failed to reset scoring config:", err);
      setConfigSaveError(err?.message || "Failed to reset configuration");
    } finally {
      setIsSavingConfig(false);
    }
  };

  const handleClearAudit = async () => {
    if (
      !window.confirm(
        "Are you sure you want to clear the candidate audit records? Next editorial pipeline run will populate a fresh candidate pool."
      )
    ) {
      return;
    }
    setIsClearing(true);
    try {
      await clearEditorialCandidates();
      await loadData();
    } catch (err) {
      console.error("Failed to clear candidate records:", err);
      alert("Failed to clear candidate records");
    } finally {
      setIsClearing(false);
    }
  };

  const handleLogout = () => {
    logoutEditorialAdmin();
    setIsAuthenticated(false);
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadData();
    }
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return <AdminLogin onAuthenticated={() => setIsAuthenticated(true)} />;
  }

  return (
    <div>
      <AdminHeader
        activeTab={activeTab}
        onTabChange={setActiveTab}
        loading={loading}
        onRefresh={loadData}
        onLock={handleLogout}
      />

      {activeTab === "pipeline" && (
        <PipelineInspectorTab
          candidates={candidates}
          activeEditionDate={activeEditionDate}
          loading={loading}
          isClearing={isClearing}
          onClearAudit={handleClearAudit}
        />
      )}

      {activeTab === "feedback" && (
        <>
          <FeedbackAnalyticsTab
            analytics={analytics}
            loading={loading}
            onRefreshAnalytics={loadData}
            feedbackHistory={feedbackHistory}
            historyLoading={historyLoading}
            historyDays={historyDays}
            onHistoryDaysChange={(days) => {
              setHistoryDays(days);
              loadFeedbackHistoryData(days);
            }}
            onRefreshHistory={() => loadFeedbackHistoryData(historyDays)}
            voteActionLoading={voteActionLoading}
            feedbackActionMsg={feedbackActionMsg}
            onDismissActionMsg={() => setFeedbackActionMsg(null)}
            onFlipVote={handleFlipVote}
            onDeleteVote={handleDeleteVote}
            onOpenOverrideModal={handleOpenOverrideModal}
            onResetCategoryOverride={handleResetCategoryOverride}
          />

          {selectedCategoryForOverride && (
            <CategoryOverrideModal
              key={selectedCategoryForOverride.slug}
              category={selectedCategoryForOverride}
              isSaving={isSavingOverride}
              onClose={() => setSelectedCategoryForOverride(null)}
              onSave={handleSaveCategoryOverride}
            />
          )}
        </>
      )}

      {activeTab === "formula" && (
        <ScoringFormulaTab
          scoringConfig={scoringConfig}
          weights={weights}
          setWeights={setWeights}
          thresholds={thresholds}
          setThresholds={setThresholds}
          isSavingConfig={isSavingConfig}
          configSaveSuccess={configSaveSuccess}
          configSaveError={configSaveError}
          onSaveConfig={handleSaveScoringConfig}
          onResetConfig={handleResetScoringConfig}
        />
      )}

      {activeTab === "adk" && <AdkArchitectureTab />}
    </div>
  );
};
