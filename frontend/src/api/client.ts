import axios from "axios";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "https://resume-screening-tvrt.onrender.com/api"
).replace(/\/$/, "");

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Types & Interfaces
export interface HealthStatus {
  status: string;
  project_name: string;
  mongodb_atlas_connectivity: "connected" | "fallback";
  database_mode: string;
  active_models: {
    whisper_asr: string;
    embedding_engine: string;
    sentiment_analyzer: string;
  };
  fallback_modes: {
    local_fallback_store_enabled: boolean;
    is_fallback_active: boolean;
  };
}

export interface ScoringWeights {
  skill_match: number;
  experience_match: number;
  multimodal_presentation: number;
  sentiment_engagement: number;
  claim_credibility: number;
}

export interface JobProfile {
  job_id: string;
  title: string;
  department: string;
  location: string;
  employment_type: string;
  experience_years_min: number;
  experience_years_max?: number;
  education_level: string;
  description: string;
  responsibilities: string[];
  required_skills: string[];
  preferred_skills: string[];
  scoring_weights: ScoringWeights;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ScoreComponent {
  name: string;
  raw_score: number;
  weight: number;
  weighted_score: number;
  status: string;
  details: string;
}

export interface SkillGapReport {
  matched_skills: string[];
  missing_required_skills: string[];
  missing_preferred_skills: string[];
  coverage_pct: number;
  recommendations: string[];
}

export interface DiscrepancyItem {
  category: string;
  claim_in_video: string;
  claim_in_resume: string;
  severity: "low" | "medium" | "high";
  explanation: string;
}

export interface ClaimVerificationResult {
  credibility_score: number;
  aligned: string[];
  mentioned_only_in_video: string[];
  mentioned_only_in_resume: string[];
  potential_discrepancy: DiscrepancyItem[];
  recruiter_notes: string[];
}

export interface MultimodalAnalysis {
  transcript?: string;
  duration_seconds?: number;
  words_per_minute?: number;
  speaking_pace?: string;
  filler_word_ratio?: number;
  sentiment_label?: string;
  sentiment_score?: number;
  presentation_score?: number;
  vocal_energy_score?: number;
  visual_engagement_score?: number;
  analysis_mode?: string;
}

export interface CandidateEvaluation {
  evaluation_id: string;
  job_id: string;
  overall_fit_score: number;
  recommendation: string;
  is_advisory_only: boolean;
  component_breakdown: Record<string, ScoreComponent>;
  skill_gap: SkillGapReport;
  claim_verification: ClaimVerificationResult;
  strengths: string[];
  areas_for_probing: string[];
  recruiter_executive_summary: string;
  evaluated_at: string;
}

export interface Candidate {
  candidate_id: string;
  contact_info: {
    name: string;
    email?: string;
    phone?: string;
    location?: string;
    linkedin_url?: string;
    github_url?: string;
  };
  summary?: string;
  skills: string[];
  sections?: Record<string, string>;
  multimodal_analysis?: MultimodalAnalysis;
  evaluations: CandidateEvaluation[];
  anonymized_view?: {
    anonymous_id: string;
    original_candidate_id: string;
    sanitized_summary: string;
    skills: string[];
    advisory_notice: string;
  };
  status: string;
  created_at: string;
}

export interface LeaderboardItem {
  rank: number;
  candidate_id: string;
  candidate_name: string;
  email?: string;
  overall_fit_score: number;
  recommendation: string;
  is_advisory_only: boolean;
  skill_coverage_pct: number;
  matched_skills: string[];
  missing_required_skills: string[];
  speaking_pace: string;
  sentiment_label: string;
  credibility_score: number;
  discrepancies_count: number;
  recruiter_executive_summary: string;
}

export interface ThresholdSensitivity {
  threshold_score: number;
  selected_count: number;
  selection_rate_pct: number;
}

export interface FairnessAuditReport {
  sample_size: number;
  mean_score: number;
  median_score: number;
  std_dev: number;
  min_score: number;
  max_score: number;
  percentiles: Record<string, number>;
  score_spread: number;
  calibration_drift_flag: boolean;
  threshold_sensitivities: ThresholdSensitivity[];
  advisory_compliance_passed: boolean;
  audit_warnings: string[];
  audited_at: string;
}

// API Methods
export const fetchHealth = async (): Promise<HealthStatus> => {
  const res = await apiClient.get<HealthStatus>("/health");
  return res.data;
};

export const fetchJobs = async (): Promise<JobProfile[]> => {
  const res = await apiClient.get<JobProfile[]>("/jobs");
  return res.data;
};

export const fetchJob = async (jobId: string): Promise<JobProfile> => {
  const res = await apiClient.get<JobProfile>(`/jobs/${jobId}`);
  return res.data;
};

export const createJob = async (jobData: Partial<JobProfile>): Promise<JobProfile> => {
  const res = await apiClient.post<JobProfile>("/jobs", jobData);
  return res.data;
};

export const updateJobWeights = async (
  jobId: string,
  weights: ScoringWeights
): Promise<JobProfile> => {
  const res = await apiClient.patch<JobProfile>(`/jobs/${jobId}/weights`, weights);
  return res.data;
};

export const evaluateCandidate = async (formData: FormData): Promise<any> => {
  const res = await apiClient.post("/candidates/evaluate", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};

export const rerankCandidates = async (jobId: string): Promise<any[]> => {
  const res = await apiClient.post<any[]>(`/candidates/re-rank/${jobId}`);
  return res.data;
};

export const fetchCandidates = async (jobId?: string): Promise<Candidate[]> => {
  const params = jobId ? { job_id: jobId } : {};
  const res = await apiClient.get<Candidate[]>("/candidates", { params });
  return res.data;
};

export const fetchCandidate = async (candidateId: string): Promise<Candidate> => {
  const res = await apiClient.get<Candidate>(`/candidates/${candidateId}`);
  return res.data;
};

export const deleteCandidate = async (candidateId: string): Promise<void> => {
  await apiClient.delete(`/candidates/${candidateId}`);
};

export const fetchLeaderboard = async (
  jobId: string
): Promise<{
  job_id: string;
  job_title: string;
  total_candidates: number;
  leaderboard: LeaderboardItem[];
}> => {
  const res = await apiClient.get(`/analytics/leaderboard/${jobId}`);
  return res.data;
};

export const fetchFairnessAudit = async (
  jobId: string
): Promise<{
  job_id: string;
  job_title: string;
  audit_report: FairnessAuditReport;
}> => {
  const res = await apiClient.get(`/analytics/fairness/${jobId}`);
  return res.data;
};

export const downloadExport = async (jobId: string, format: "json" | "csv"): Promise<void> => {
  const res = await apiClient.get(`/analytics/export/${jobId}`, {
    params: { format },
    responseType: "blob",
  });
  const url = window.URL.createObjectURL(new Blob([res.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", `screening_export_${jobId}.${format}`);
  document.body.appendChild(link);
  link.click();
  link.parentNode?.removeChild(link);
};
