import React, { useEffect, useState, useCallback } from "react";
import {
  fetchHealth,
  fetchJobs,
  fetchLeaderboard,
  fetchFairnessAudit,
  fetchCandidate,
  downloadExport,
  JobProfile,
  HealthStatus,
  LeaderboardItem,
  FairnessAuditReport,
  Candidate,
} from "../api/client";
import { LeaderboardTable } from "../components/LeaderboardTable";
import { UploadPanel } from "../components/UploadPanel";
import { JobRubricPage } from "./JobRubricPage";
import { FairnessPanel } from "../components/FairnessPanel";
import { CandidateDrawer } from "../components/CandidateDrawer";
import { CreateJobModal } from "../components/CreateJobModal";
import {
  Briefcase,
  Users,
  ShieldCheck,
  Cpu,
  Layers,
  PlusCircle,
  FileSpreadsheet,
  FileCode,
  BarChart3,
  Sliders,
  RefreshCw,
  CheckCircle,
  TrendingUp,
  Sparkles,
} from "lucide-react";

interface DashboardPageProps {
  registerOpenCreateJob?: (fn: () => void) => void;
  registerOpenIngest?: (fn: () => void) => void;
}

export function DashboardPage({ registerOpenCreateJob, registerOpenIngest }: DashboardPageProps) {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [jobs, setJobs] = useState<JobProfile[]>([]);
  const [currentJob, setCurrentJob] = useState<JobProfile | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardItem[]>([]);
  const [fairnessReport, setFairnessReport] = useState<FairnessAuditReport | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);

  const [activeTab, setActiveTab] = useState<"leaderboard" | "ingest" | "rubric" | "fairness">("leaderboard");
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState<"csv" | "json" | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [showCreateJobModal, setShowCreateJobModal] = useState(false);

  // Initial load: health & jobs
  useEffect(() => {
    async function init() {
      setLoading(true);
      try {
        const [healthRes, jobsRes] = await Promise.allSettled([fetchHealth(), fetchJobs()]);
        if (healthRes.status === "fulfilled") setHealth(healthRes.value);
        if (jobsRes.status === "fulfilled" && jobsRes.value.length > 0) {
          setJobs(jobsRes.value);
          setCurrentJob(jobsRes.value[0]);
        }
      } catch (err: any) {
        console.error("Dashboard init failed", err);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  // Register external opener functions (from Navbar)
  useEffect(() => {
    if (registerOpenCreateJob) {
      registerOpenCreateJob(() => setShowCreateJobModal(true));
    }
    if (registerOpenIngest) {
      registerOpenIngest(() => setActiveTab("ingest"));
    }
  }, [registerOpenCreateJob, registerOpenIngest]);

  const loadJobData = useCallback(async (jobId: string) => {
    setRefreshing(true);
    try {
      const [lbRes, fairnessRes] = await Promise.allSettled([
        fetchLeaderboard(jobId),
        fetchFairnessAudit(jobId),
      ]);
      if (lbRes.status === "fulfilled") setLeaderboard(lbRes.value.leaderboard || []);
      else setLeaderboard([]);
      if (fairnessRes.status === "fulfilled") setFairnessReport(fairnessRes.value.audit_report);
      else setFairnessReport(null);
    } catch (err) {
      console.warn("Could not load full job data", err);
    } finally {
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    if (currentJob?.job_id) loadJobData(currentJob.job_id);
  }, [currentJob?.job_id, loadJobData]);

  const handleSelectCandidate = async (candidateId: string) => {
    try {
      const cand = await fetchCandidate(candidateId);
      setSelectedCandidate(cand);
    } catch (err) {
      console.error("Failed to load candidate details", err);
    }
  };

  const handleEvaluationComplete = async (evaluatedCandidate: any) => {
    if (currentJob) await loadJobData(currentJob.job_id);
    if (evaluatedCandidate?.candidate_id) {
      try {
        const full = await fetchCandidate(evaluatedCandidate.candidate_id);
        setSelectedCandidate(full);
      } catch {
        setSelectedCandidate(evaluatedCandidate);
      }
    }
  };

  const handleJobUpdated = (updatedJob: JobProfile) => {
    setCurrentJob(updatedJob);
    setJobs((prev) => prev.map((j) => (j.job_id === updatedJob.job_id ? updatedJob : j)));
    loadJobData(updatedJob.job_id);
  };

  const handleJobCreated = (newJob: JobProfile) => {
    setJobs((prev) => [newJob, ...prev]);
    setCurrentJob(newJob);
    loadJobData(newJob.job_id);
  };

  const handleExport = async (format: "csv" | "json") => {
    if (!currentJob) return;
    setExporting(format);
    try {
      await downloadExport(currentJob.job_id, format);
    } catch (err) {
      console.error(`Failed to export ${format}`, err);
    } finally {
      setExporting(null);
    }
  };

  const isFallback =
    health?.mongodb_atlas_connectivity === "fallback" ||
    health?.database_mode?.includes("fallback");

  const tabs = [
    { id: "leaderboard", label: `Leaderboard (${leaderboard.length})`, icon: BarChart3 },
    { id: "ingest", label: "Ingest Candidate", icon: PlusCircle },
    { id: "rubric", label: "Job Rubric & Weights", icon: Sliders },
    { id: "fairness", label: `Fairness Audit (${fairnessReport?.sample_size || 0})`, icon: ShieldCheck },
  ] as const;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">

      {/* ── Top Bar: Active Job Selector & Primary Actions ── */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm card-hover flex flex-col lg:flex-row lg:items-center justify-between gap-5">
        <div className="space-y-2 flex-1 min-w-0">
          <div className="flex items-center space-x-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-widest">
            <Briefcase className="w-3.5 h-3.5 text-[#EF8A62]" />
            <span>Active Screening Rubric &amp; Job Description</span>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Job Select Dropdown */}
            <select
              value={currentJob?.job_id || ""}
              onChange={(e) => {
                const val = e.target.value;
                if (val === "__NEW__") {
                  setShowCreateJobModal(true);
                  return;
                }
                const found = jobs.find((j) => j.job_id === val);
                if (found) setCurrentJob(found);
              }}
              className="bg-[#F7F7F7] border border-slate-200 text-slate-900 font-bold text-base rounded-xl px-4 py-2.5 max-w-sm hover:border-[#EF8A62]/60 cursor-pointer"
            >
              {jobs.map((job) => (
                <option key={job.job_id} value={job.job_id}>
                  {job.title} ({job.department} • {job.location})
                </option>
              ))}
              {jobs.length === 0 && <option value="">No Job Profiles Created</option>}
              <option value="__NEW__" className="text-[#EF8A62] font-bold">
                + Create New Job Profile...
              </option>
            </select>

            {/* Direct "+ Create Job Profile" button */}
            <button
              onClick={() => setShowCreateJobModal(true)}
              className="btn-coral inline-flex items-center space-x-1.5 text-xs text-white font-bold px-4 py-2.5 rounded-xl"
            >
              <PlusCircle className="w-4 h-4" />
              <span>+ Create Job Profile</span>
            </button>

            {/* View / Edit Rubric button */}
            <button
              onClick={() => setActiveTab("rubric")}
              className="inline-flex items-center space-x-1.5 text-xs font-semibold bg-[#F7F7F7] hover:bg-slate-100 text-slate-700 px-3.5 py-2.5 rounded-xl border border-slate-200 hover:border-[#EF8A62]/40 transition"
            >
              <Sliders className="w-3.5 h-3.5 text-[#EF8A62]" />
              <span>Weights &amp; Rubric</span>
            </button>
          </div>

          {currentJob && (
            <p className="text-[11px] text-slate-400 truncate">
              Required: <span className="text-slate-600 font-medium">{currentJob.required_skills?.join(", ") || "None specified"}</span>
              {" · "}Min Exp: <span className="text-slate-600 font-medium">{currentJob.experience_years_min || 0}+ yrs</span>
            </p>
          )}
        </div>

        {/* Export & Refresh actions */}
        <div className="flex items-center space-x-2 shrink-0">
          <button
            onClick={() => handleExport("csv")}
            disabled={exporting !== null || !currentJob}
            className="inline-flex items-center space-x-1.5 text-xs font-semibold px-3.5 py-2 rounded-xl bg-[#F7F7F7] hover:bg-slate-100 text-slate-700 border border-slate-200 hover:border-[#EF8A62]/40 shadow-xs disabled:opacity-50 transition"
          >
            <FileSpreadsheet className="w-4 h-4 text-[#EF8A62]" />
            <span>{exporting === "csv" ? "Exporting…" : "CSV"}</span>
          </button>
          <button
            onClick={() => handleExport("json")}
            disabled={exporting !== null || !currentJob}
            className="inline-flex items-center space-x-1.5 text-xs font-semibold px-3.5 py-2 rounded-xl bg-[#F7F7F7] hover:bg-slate-100 text-slate-700 border border-slate-200 hover:border-[#67A9CF]/40 shadow-xs disabled:opacity-50 transition"
          >
            <FileCode className="w-4 h-4 text-[#67A9CF]" />
            <span>{exporting === "json" ? "Exporting…" : "JSON"}</span>
          </button>
          <button
            onClick={() => currentJob && loadJobData(currentJob.job_id)}
            disabled={refreshing || !currentJob}
            className="p-2.5 rounded-xl bg-[#F7F7F7] hover:bg-slate-100 text-slate-500 hover:text-slate-800 border border-slate-200 shadow-xs transition disabled:opacity-50"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin text-[#EF8A62]" : ""}`} />
          </button>
        </div>
      </div>

      {/* ── Metric Cards ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="relative bg-white border border-slate-200/80 p-5 rounded-2xl shadow-sm card-hover overflow-hidden metric-card metric-card-coral">
          <div className="absolute top-4 right-4 p-2 bg-[#EF8A62]/10 rounded-xl">
            <Users className="w-4 h-4 text-[#EF8A62]" />
          </div>
          <div className="text-[11px] text-slate-400 font-semibold uppercase tracking-widest mb-1">Ranked</div>
          <div className="text-4xl font-black text-slate-900">{leaderboard.length}</div>
          <div className="text-[11px] text-slate-400 mt-1 flex items-center space-x-1">
            <TrendingUp className="w-3 h-3 text-[#EF8A62]" />
            <span>For active position</span>
          </div>
        </div>

        <div className="relative bg-white border border-slate-200/80 p-5 rounded-2xl shadow-sm card-hover overflow-hidden metric-card metric-card-cerulean">
          <div className="absolute top-4 right-4 p-2 bg-[#67A9CF]/10 rounded-xl">
            <Layers className="w-4 h-4 text-[#67A9CF]" />
          </div>
          <div className="text-[11px] text-slate-400 font-semibold uppercase tracking-widest mb-1">Storage</div>
          <div className="flex items-center space-x-2 mt-1">
            <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${isFallback ? "bg-[#EF8A62] animate-pulse" : "bg-[#67A9CF]"}`} />
            <span className={`text-sm font-bold ${isFallback ? "text-[#EF8A62]" : "text-[#67A9CF]"}`}>
              {isFallback ? "Local JSON" : "Atlas"}
            </span>
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            {isFallback ? "Offline fallback mode" : "Production TLS cluster"}
          </div>
        </div>

        <div className="relative bg-white border border-slate-200/80 p-5 rounded-2xl shadow-sm card-hover overflow-hidden metric-card metric-card-cerulean">
          <div className="absolute top-4 right-4 p-2 bg-[#67A9CF]/10 rounded-xl">
            <Cpu className="w-4 h-4 text-[#67A9CF]" />
          </div>
          <div className="text-[11px] text-slate-400 font-semibold uppercase tracking-widest mb-1">Whisper ASR</div>
          <div className="text-sm font-bold text-[#67A9CF] mt-1 truncate">
            {health?.active_models?.whisper_asr || "base / faster-whisper"}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">Multimodal speech engine</div>
        </div>

        <div className="relative bg-white border border-slate-200/80 p-5 rounded-2xl shadow-sm card-hover overflow-hidden metric-card metric-card-coral">
          <div className="absolute top-4 right-4 p-2 bg-[#EF8A62]/10 rounded-xl">
            <ShieldCheck className="w-4 h-4 text-[#EF8A62]" />
          </div>
          <div className="text-[11px] text-slate-400 font-semibold uppercase tracking-widest mb-1">Governance</div>
          <div className="flex items-center space-x-1.5 mt-1">
            <CheckCircle className="w-4 h-4 text-[#EF8A62]" />
            <span className="text-sm font-bold text-[#EF8A62]">Advisory Mode</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-1">Non-adverse action compliant</div>
        </div>
      </div>

      {/* ── Tab Navigation ── */}
      <div className="bg-white border border-slate-200/80 rounded-2xl shadow-sm overflow-hidden">
        <div className="flex border-b border-slate-100 px-2 pt-1 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-3.5 px-4 text-xs font-semibold border-b-2 whitespace-nowrap transition-all rounded-t-lg mr-1 ${
                  active
                    ? "border-[#EF8A62] text-[#EF8A62] bg-[#EF8A62]/5"
                    : "border-transparent text-slate-400 hover:text-slate-700 hover:bg-slate-50"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab content */}
        <div className="p-6 space-y-6 animate-fade-in">
          {activeTab === "leaderboard" && (
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3">
                <div>
                  <h2 className="text-lg font-bold text-slate-900">Ranked Candidate Leaderboard</h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Section-weighted matching across Skills, Experience, Speech/Video &amp; Claim Consistency
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setShowCreateJobModal(true)}
                    className="inline-flex items-center space-x-1.5 text-xs font-semibold bg-[#F7F7F7] hover:bg-slate-100 text-slate-700 px-3.5 py-2 rounded-xl border border-slate-200 hover:border-[#EF8A62]/40 transition"
                  >
                    <PlusCircle className="w-3.5 h-3.5 text-[#EF8A62]" />
                    <span>+ New Job</span>
                  </button>
                  <button
                    onClick={() => setActiveTab("ingest")}
                    className="btn-coral text-xs text-white font-semibold px-4 py-2 rounded-xl"
                  >
                    + Evaluate New Candidate
                  </button>
                </div>
              </div>
              <LeaderboardTable items={leaderboard} onSelectCandidate={handleSelectCandidate} />
            </div>
          )}

          {activeTab === "ingest" && (
            <UploadPanel currentJob={currentJob} onEvaluationComplete={handleEvaluationComplete} />
          )}

          {activeTab === "rubric" && (
            <JobRubricPage
              currentJob={currentJob}
              onJobUpdated={handleJobUpdated}
              onJobCreated={handleJobCreated}
            />
          )}

          {activeTab === "fairness" && (
            <FairnessPanel jobId={currentJob?.job_id || ""} auditReport={fairnessReport} />
          )}
        </div>
      </div>

      {/* Candidate Drawer */}
      <CandidateDrawer candidate={selectedCandidate} onClose={() => setSelectedCandidate(null)} />

      {/* Create Job Profile Modal */}
      <CreateJobModal
        isOpen={showCreateJobModal}
        onClose={() => setShowCreateJobModal(false)}
        onJobCreated={handleJobCreated}
        initialWeights={currentJob?.scoring_weights}
      />
    </div>
  );
}

export default DashboardPage;
