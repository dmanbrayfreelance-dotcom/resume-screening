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
} from "lucide-react";

export function DashboardPage() {
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

  // Initial load: health & jobs
  useEffect(() => {
    async function init() {
      setLoading(true);
      try {
        const [healthRes, jobsRes] = await Promise.allSettled([
          fetchHealth(),
          fetchJobs(),
        ]);

        if (healthRes.status === "fulfilled") {
          setHealth(healthRes.value);
        }
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

  // When active job changes, load its leaderboard & fairness audit
  const loadJobData = useCallback(async (jobId: string) => {
    setRefreshing(true);
    try {
      const [lbRes, fairnessRes] = await Promise.allSettled([
        fetchLeaderboard(jobId),
        fetchFairnessAudit(jobId),
      ]);

      if (lbRes.status === "fulfilled") {
        setLeaderboard(lbRes.value.leaderboard || []);
      } else {
        setLeaderboard([]);
      }

      if (fairnessRes.status === "fulfilled") {
        setFairnessReport(fairnessRes.value.audit_report);
      } else {
        setFairnessReport(null);
      }
    } catch (err) {
      console.warn("Could not load full job data", err);
    } finally {
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    if (currentJob?.job_id) {
      loadJobData(currentJob.job_id);
    }
  }, [currentJob?.job_id, loadJobData]);

  // Handler for candidate inspection
  const handleSelectCandidate = async (candidateId: string) => {
    try {
      const cand = await fetchCandidate(candidateId);
      setSelectedCandidate(cand);
    } catch (err) {
      console.error("Failed to load candidate details", err);
    }
  };

  // Handler when a candidate evaluation completes via UploadPanel
  const handleEvaluationComplete = async (evaluatedCandidate: any) => {
    if (currentJob) {
      await loadJobData(currentJob.job_id);
    }
    if (evaluatedCandidate?.candidate_id) {
      try {
        const full = await fetchCandidate(evaluatedCandidate.candidate_id);
        setSelectedCandidate(full);
      } catch {
        setSelectedCandidate(evaluatedCandidate);
      }
    }
  };

  // Handler when job weights updated or re-ranked
  const handleJobUpdated = (updatedJob: JobProfile) => {
    setCurrentJob(updatedJob);
    setJobs((prev) => prev.map((j) => (j.job_id === updatedJob.job_id ? updatedJob : j)));
    loadJobData(updatedJob.job_id);
  };

  // Handler when a new job profile is created
  const handleJobCreated = (newJob: JobProfile) => {
    setJobs((prev) => [newJob, ...prev]);
    setCurrentJob(newJob);
    loadJobData(newJob.job_id);
  };

  // Export handlers
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

  const isFallback = health?.mongodb_atlas_connectivity === "fallback" || health?.database_mode?.includes("fallback");

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Bar: Active Job Selector & Export Actions */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div className="space-y-1 flex-1">
          <div className="flex items-center space-x-2 text-xs font-medium text-slate-400">
            <Briefcase className="w-4 h-4 text-coral-400" />
            <span>Active Screening Rubric & Job Profile</span>
          </div>
          <div className="flex flex-wrap items-center gap-3 pt-1">
            <select
              value={currentJob?.job_id || ""}
              onChange={(e) => {
                const found = jobs.find((j) => j.job_id === e.target.value);
                if (found) setCurrentJob(found);
              }}
              className="bg-slate-950 border border-slate-800 text-offwhite font-semibold text-base sm:text-lg rounded-xl px-4 py-2.5 focus:outline-none focus:border-coral-500 max-w-md"
            >
              {jobs.map((job) => (
                <option key={job.job_id} value={job.job_id}>
                  {job.title} ({job.department} • {job.location})
                </option>
              ))}
              {jobs.length === 0 && <option value="">No Job Profiles Created</option>}
            </select>

            <button
              onClick={() => setActiveTab("rubric")}
              className="text-xs bg-slate-800 hover:bg-slate-700 text-offwhite px-3 py-2 rounded-xl border border-slate-700 flex items-center space-x-1.5 transition"
            >
              <PlusCircle className="w-3.5 h-3.5 text-coral-400" />
              <span>Create / Edit Rubric</span>
            </button>
          </div>
          {currentJob && (
            <p className="text-xs text-slate-400 pt-1 line-clamp-1">
              Req Skills: {currentJob.required_skills?.join(", ") || "None specified"} • Min Exp: {currentJob.experience_years_min || 0}+ yrs
            </p>
          )}
        </div>

        {/* Export Buttons */}
        <div className="flex items-center space-x-3 self-start lg:self-center">
          <button
            onClick={() => handleExport("csv")}
            disabled={exporting !== null || !currentJob}
            className="text-xs font-medium px-3.5 py-2 rounded-xl bg-slate-950 hover:bg-slate-800 text-slate-300 hover:text-offwhite border border-slate-800 flex items-center space-x-2 transition disabled:opacity-50"
            title="Download ranked shortlist as CSV"
          >
            <FileSpreadsheet className="w-4 h-4 text-coral-400" />
            <span>{exporting === "csv" ? "Exporting..." : "Export CSV"}</span>
          </button>
          <button
            onClick={() => handleExport("json")}
            disabled={exporting !== null || !currentJob}
            className="text-xs font-medium px-3.5 py-2 rounded-xl bg-slate-950 hover:bg-slate-800 text-slate-300 hover:text-offwhite border border-slate-800 flex items-center space-x-2 transition disabled:opacity-50"
            title="Download full evaluation & fairness report as JSON"
          >
            <FileCode className="w-4 h-4 text-cerulean-400" />
            <span>{exporting === "json" ? "Exporting..." : "Export JSON"}</span>
          </button>
          <button
            onClick={() => currentJob && loadJobData(currentJob.job_id)}
            disabled={refreshing || !currentJob}
            className="p-2 rounded-xl bg-slate-950 hover:bg-slate-800 text-slate-400 hover:text-offwhite border border-slate-800 transition"
            title="Refresh candidate data"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin text-coral-400" : ""}`} />
          </button>
        </div>
      </div>

      {/* Metrics Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Candidates Evaluated */}
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Candidates Ranked</span>
            <Users className="w-4 h-4 text-cerulean-400" />
          </div>
          <div className="text-3xl font-extrabold text-offwhite">{leaderboard.length}</div>
          <div className="text-[11px] text-slate-500">For active position</div>
        </div>

        {/* Storage Architecture */}
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Database Storage</span>
            <Layers className="w-4 h-4 text-coral-400" />
          </div>
          <div className="text-sm font-semibold flex items-center space-x-2 mt-1">
            <span className={`w-2.5 h-2.5 rounded-full ${isFallback ? "bg-coral-400 animate-pulse" : "bg-cerulean-400"}`} />
            <span className={isFallback ? "text-coral-300" : "text-cerulean-300"}>
              {isFallback ? "Local JSON Fallback" : "MongoDB Atlas"}
            </span>
          </div>
          <div className="text-[11px] text-slate-500">
            {isFallback ? "Zero-dependency offline mode" : "Production TLS cloud cluster"}
          </div>
        </div>

        {/* Whisper ASR Engine */}
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Whisper ASR Speech</span>
            <Cpu className="w-4 h-4 text-cerulean-400" />
          </div>
          <div className="text-base font-bold text-cerulean-300 mt-1">
            {health?.active_models?.whisper_asr || "base / faster-whisper"}
          </div>
          <div className="text-[11px] text-slate-500">Multimodal interview parsing</div>
        </div>

        {/* Governance Guardrail */}
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Fairness Governance</span>
            <ShieldCheck className="w-4 h-4 text-coral-400" />
          </div>
          <div className="text-sm font-bold text-coral-400 flex items-center space-x-1.5 mt-1">
            <CheckCircle className="w-4 h-4 text-coral-400" />
            <span>Advisory-Only Mode</span>
          </div>
          <div className="text-[11px] text-slate-500">Non-adverse action compliant</div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-slate-800 flex items-center space-x-2 sm:space-x-4 text-xs font-medium">
        <button
          onClick={() => setActiveTab("leaderboard")}
          className={`flex items-center space-x-2 pb-3 px-3 border-b-2 transition ${
            activeTab === "leaderboard"
              ? "border-coral-500 text-coral-400 font-semibold"
              : "border-transparent text-slate-400 hover:text-offwhite"
          }`}
        >
          <BarChart3 className="w-4 h-4" />
          <span>Screening Leaderboard ({leaderboard.length})</span>
        </button>

        <button
          onClick={() => setActiveTab("ingest")}
          className={`flex items-center space-x-2 pb-3 px-3 border-b-2 transition ${
            activeTab === "ingest"
              ? "border-coral-500 text-coral-400 font-semibold"
              : "border-transparent text-slate-400 hover:text-offwhite"
          }`}
        >
          <PlusCircle className="w-4 h-4" />
          <span>Ingest & Evaluate Candidate</span>
        </button>

        <button
          onClick={() => setActiveTab("rubric")}
          className={`flex items-center space-x-2 pb-3 px-3 border-b-2 transition ${
            activeTab === "rubric"
              ? "border-coral-500 text-coral-400 font-semibold"
              : "border-transparent text-slate-400 hover:text-offwhite"
          }`}
        >
          <Sliders className="w-4 h-4" />
          <span>Job Rubric & Weights</span>
        </button>

        <button
          onClick={() => setActiveTab("fairness")}
          className={`flex items-center space-x-2 pb-3 px-3 border-b-2 transition ${
            activeTab === "fairness"
              ? "border-coral-500 text-coral-400 font-semibold"
              : "border-transparent text-slate-400 hover:text-offwhite"
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          <span>Fairness & Audit ({fairnessReport?.sample_size || 0})</span>
        </button>
      </div>

      {/* Main Tab Content */}
      <div className="space-y-6">
        {activeTab === "leaderboard" && (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2">
              <div>
                <h2 className="text-lg font-bold text-offwhite">Ranked Candidate Leaderboard</h2>
                <p className="text-xs text-slate-400">
                  Section-weighted matching across Skills, Experience, Speech/Video Sentiment & Claim Consistency
                </p>
              </div>
              <button
                onClick={() => setActiveTab("ingest")}
                className="text-xs bg-coral-500 hover:bg-coral-600 text-white font-medium px-4 py-2 rounded-xl transition shadow shadow-coral-500/20"
              >
                + Evaluate New Candidate
              </button>
            </div>

            <LeaderboardTable
              items={leaderboard}
              onSelectCandidate={handleSelectCandidate}
            />
          </div>
        )}

        {activeTab === "ingest" && (
          <div className="space-y-4">
            <UploadPanel
              currentJob={currentJob}
              onEvaluationComplete={handleEvaluationComplete}
            />
          </div>
        )}

        {activeTab === "rubric" && (
          <div className="space-y-4">
            <JobRubricPage
              currentJob={currentJob}
              onJobUpdated={handleJobUpdated}
              onJobCreated={handleJobCreated}
            />
          </div>
        )}

        {activeTab === "fairness" && (
          <div className="space-y-4">
            <FairnessPanel
              jobId={currentJob?.job_id || ""}
              auditReport={fairnessReport}
            />
          </div>
        )}
      </div>

      {/* Candidate Inspection Slide-over Drawer */}
      <CandidateDrawer
        candidate={selectedCandidate}
        onClose={() => setSelectedCandidate(null)}
      />
    </div>
  );
}

export default DashboardPage;
