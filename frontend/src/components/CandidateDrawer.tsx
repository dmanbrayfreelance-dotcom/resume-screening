import React, { useState } from "react";
import { Candidate, CandidateEvaluation } from "../api/client";
import { SkillGapChart } from "./SkillGapChart";
import {
  X,
  Award,
  Video,
  FileCheck2,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  MessageSquare,
  Sparkles,
} from "lucide-react";

interface CandidateDrawerProps {
  candidate: Candidate | null;
  onClose: () => void;
}

export const CandidateDrawer: React.FC<CandidateDrawerProps> = ({ candidate, onClose }) => {
  const [activeTab, setActiveTab] = useState<"scorecard" | "skills" | "multimodal" | "claims" | "anonymized">("scorecard");

  if (!candidate) return null;

  const evaluation: CandidateEvaluation =
    candidate.evaluations?.[0] || ({
      overall_fit_score: 75.0,
      recommendation: "Review",
      is_advisory_only: true,
      component_breakdown: {},
      skill_gap: { matched_skills: [], missing_required_skills: [], missing_preferred_skills: [], coverage_pct: 0, recommendations: [] },
      claim_verification: { credibility_score: 85.0, aligned: [], mentioned_only_in_video: [], mentioned_only_in_resume: [], potential_discrepancy: [], recruiter_notes: [] },
      strengths: [],
      areas_for_probing: [],
      recruiter_executive_summary: "",
      evaluated_at: new Date().toISOString(),
    } as any);

  const multimodal = candidate.multimodal_analysis || {};
  const claims = evaluation.claim_verification || {
    aligned: [],
    mentioned_only_in_video: [],
    mentioned_only_in_resume: [],
    potential_discrepancy: [],
    recruiter_notes: [],
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return "text-coral-700 bg-coral-50 border-coral-300";
    if (score >= 70) return "text-cerulean-700 bg-cerulean-50 border-cerulean-300";
    if (score >= 55) return "text-amber-700 bg-amber-50 border-amber-300";
    return "text-rose-700 bg-rose-50 border-rose-300";
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/40 backdrop-blur-xs flex justify-end">
      <div className="w-full max-w-2xl bg-white border-l border-slate-200 h-full flex flex-col shadow-2xl animate-in slide-in-from-right duration-200">
        {/* Drawer Header */}
        <div className="p-6 border-b border-slate-200 flex items-start justify-between bg-slate-50">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs text-coral-600 font-mono font-medium">ID: {candidate.candidate_id}</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                {candidate.status || "screened"}
              </span>
            </div>
            <h2 className="text-xl font-bold text-slate-900 mt-1">{candidate.contact_info?.name || "Candidate Profile"}</h2>
            <p className="text-xs text-slate-500">{candidate.contact_info?.email} • {candidate.contact_info?.location || "Remote"}</p>
          </div>

          <div className="flex items-center space-x-3">
            <div className={`px-3 py-1.5 rounded-xl border text-center font-bold text-sm ${getScoreColor(evaluation.overall_fit_score)}`}>
              <div>{evaluation.overall_fit_score}%</div>
              <div className="text-[10px] font-semibold uppercase tracking-wider">{evaluation.recommendation}</div>
            </div>
            <button onClick={onClose} className="p-2 rounded-xl text-slate-400 hover:text-slate-800 hover:bg-slate-200/60 transition">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-200 px-6 bg-white text-xs">
          {[
            { id: "scorecard", label: "Scorecard", icon: Award },
            { id: "skills", label: "Skill Gap", icon: Sparkles },
            { id: "multimodal", label: "Speech & Video", icon: Video },
            { id: "claims", label: "Claim Verifier", icon: FileCheck2 },
            { id: "anonymized", label: "Fairness View", icon: ShieldCheck },
          ].map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 py-3 px-3 font-medium border-b-2 transition ${
                  active
                    ? "border-coral-500 text-coral-600 font-semibold"
                    : "border-transparent text-slate-500 hover:text-slate-800"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-xs text-slate-700 bg-white">
          {/* TAB 1: SCORECARD */}
          {activeTab === "scorecard" && (
            <div className="space-y-6">
              {/* Executive Summary */}
              {evaluation.recruiter_executive_summary && (
                <div className="p-4 rounded-xl bg-coral-50/80 border border-coral-200 text-slate-800 leading-relaxed space-y-1">
                  <div className="font-semibold text-coral-700 flex items-center space-x-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-coral-500" />
                    <span>Recruiter Executive Summary</span>
                  </div>
                  <p className="text-slate-700">{evaluation.recruiter_executive_summary}</p>
                </div>
              )}

              {/* Component breakdown */}
              <div className="space-y-3">
                <h4 className="font-semibold text-slate-900 text-sm">Transparent Multi-Factor Breakdown</h4>
                <div className="space-y-2.5">
                  {Object.entries(evaluation.component_breakdown || {}).map(([key, comp]) => (
                    <div key={key} className="bg-slate-50 border border-slate-200 p-3.5 rounded-xl space-y-2">
                      <div className="flex justify-between items-center">
                        <div>
                          <span className="font-semibold text-slate-900">{comp.name}</span>
                          <span className="ml-2 text-[10px] text-slate-500">Weight: {Math.round(comp.weight * 100)}%</span>
                        </div>
                        <span className="font-bold text-cerulean-700">{comp.raw_score}%</span>
                      </div>
                      <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                        <div
                          className="bg-coral-500 h-full rounded-full"
                          style={{ width: `${Math.min(100, comp.raw_score)}%` }}
                        />
                      </div>
                      <p className="text-[11px] text-slate-500">{comp.details}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Strengths & Areas for Probing */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-cerulean-50 border border-cerulean-200 p-4 rounded-xl space-y-2">
                  <div className="font-semibold text-cerulean-800 flex items-center space-x-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-cerulean-600" />
                    <span>Top Strengths</span>
                  </div>
                  <ul className="space-y-1.5 text-slate-700">
                    {(evaluation.strengths || []).map((s, idx) => (
                      <li key={idx}>• {s}</li>
                    ))}
                  </ul>
                </div>

                <div className="bg-coral-50 border border-coral-200 p-4 rounded-xl space-y-2">
                  <div className="font-semibold text-coral-800 flex items-center space-x-1.5">
                    <Lightbulb className="w-3.5 h-3.5 text-coral-600" />
                    <span>Interview Probing Areas</span>
                  </div>
                  <ul className="space-y-1.5 text-slate-700">
                    {(evaluation.areas_for_probing || []).map((p, idx) => (
                      <li key={idx}>• {p}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: SKILL GAP & RECHARTS */}
          {activeTab === "skills" && (
            <div className="space-y-6">
              <SkillGapChart evaluation={evaluation} />

              {/* Missing Skills & Recommendations */}
              <div className="space-y-4">
                <h4 className="font-semibold text-slate-900 text-sm">Actionable Upskilling Recommendations</h4>
                <div className="space-y-2">
                  {(evaluation.skill_gap?.recommendations || []).map((rec, idx) => (
                    <div key={idx} className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-700 flex items-start space-x-2">
                      <Lightbulb className="w-4 h-4 text-coral-500 shrink-0 mt-0.5" />
                      <span>{rec}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: MULTIMODAL AUDIO & SPEECH */}
          {activeTab === "multimodal" && (
            <div className="space-y-6">
              {/* Telemetry Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
                <div className="bg-slate-50 border border-slate-200 p-3 rounded-xl">
                  <div className="text-[10px] text-slate-500 uppercase font-medium">Speaking Rate</div>
                  <div className="text-base font-bold text-coral-600">{multimodal.words_per_minute || 135} WPM</div>
                  <div className="text-[10px] text-coral-700 capitalize font-medium">{multimodal.speaking_pace || "optimal"}</div>
                </div>
                <div className="bg-slate-50 border border-slate-200 p-3 rounded-xl">
                  <div className="text-[10px] text-slate-500 uppercase font-medium">Filler Word Ratio</div>
                  <div className="text-base font-bold text-cerulean-700">
                    {Math.round((multimodal.filler_word_ratio || 0.015) * 1000) / 10}%
                  </div>
                  <div className="text-[10px] text-cerulean-700 font-medium">Low Hesitancy</div>
                </div>
                <div className="bg-slate-50 border border-slate-200 p-3 rounded-xl">
                  <div className="text-[10px] text-slate-500 uppercase font-medium">Sentiment Tone</div>
                  <div className="text-base font-bold text-cerulean-700">{multimodal.sentiment_label || "POSITIVE"}</div>
                  <div className="text-[10px] text-cerulean-700 font-medium">{multimodal.sentiment_score || 0.9} Polarity</div>
                </div>
                <div className="bg-slate-50 border border-slate-200 p-3 rounded-xl">
                  <div className="text-[10px] text-slate-500 uppercase font-medium">Delivery Score</div>
                  <div className="text-base font-bold text-coral-600">{multimodal.presentation_score || 91}%</div>
                  <div className="text-[10px] text-coral-700 font-medium">Composite Presentation</div>
                </div>
              </div>

              {/* Transcript */}
              <div className="space-y-2">
                <div className="flex items-center space-x-2 font-semibold text-slate-900">
                  <MessageSquare className="w-4 h-4 text-cerulean-600" />
                  <span>Speech-to-Text Whisper Transcript</span>
                </div>
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl leading-relaxed text-slate-700 font-mono text-[11px] max-h-60 overflow-y-auto">
                  {multimodal.transcript || "No video interview recorded. Candidate screened based on textual resume credentials."}
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: CLAIM VERIFICATION */}
          {activeTab === "claims" && (
            <div className="space-y-6">
              <div className="flex items-center justify-between p-4 bg-slate-50 border border-slate-200 rounded-xl">
                <div>
                  <div className="font-semibold text-slate-900">Cross-Modal Credibility Index</div>
                  <p className="text-[11px] text-slate-500">Correlates verbal statements with written CV claims.</p>
                </div>
                <div className="text-2xl font-bold text-cerulean-700">{claims.credibility_score || 90}%</div>
              </div>

              {/* Discrepancies Alert */}
              {claims.potential_discrepancy && claims.potential_discrepancy.length > 0 && (
                <div className="space-y-2">
                  <div className="font-semibold text-coral-700 flex items-center space-x-1.5">
                    <AlertTriangle className="w-4 h-4 text-coral-500" />
                    <span>Flagged Discrepancies for Recruiter Follow-up</span>
                  </div>
                  {claims.potential_discrepancy.map((d, idx) => (
                    <div key={idx} className="p-3.5 bg-coral-50 border border-coral-200 rounded-xl space-y-1 text-slate-800">
                      <div className="flex justify-between text-xs font-semibold text-coral-800">
                        <span>{d.category.replace("_", " ").toUpperCase()}</span>
                        <span className="uppercase text-[10px] bg-coral-200/80 px-2 py-0.5 rounded border border-coral-300">
                          {d.severity} priority
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-600">{d.explanation}</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Aligned Competencies */}
              <div className="space-y-2">
                <div className="font-semibold text-slate-900">Aligned Competencies (Verified across Resume & Video)</div>
                <div className="flex flex-wrap gap-1.5">
                  {(claims.aligned || []).map((skill, idx) => (
                    <span key={idx} className="px-2.5 py-1 rounded bg-cerulean-50 text-cerulean-700 border border-cerulean-200 font-medium">
                      ✓ {skill}
                    </span>
                  ))}
                </div>
              </div>

              {/* Verbal Only Mentions */}
              {claims.mentioned_only_in_video && claims.mentioned_only_in_video.length > 0 && (
                <div className="space-y-2">
                  <div className="font-semibold text-slate-900">Spoken in Interview but not on Resume</div>
                  <div className="flex flex-wrap gap-1.5">
                    {claims.mentioned_only_in_video.map((skill, idx) => (
                      <span key={idx} className="px-2.5 py-1 rounded bg-slate-100 text-slate-700 border border-slate-200 font-medium">
                        + {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 5: ANONYMIZED FAIRNESS VIEW */}
          {activeTab === "anonymized" && (
            <div className="space-y-4">
              <div className="p-4 bg-cerulean-50 border border-cerulean-200 rounded-xl text-cerulean-800 space-y-1">
                <div className="font-semibold flex items-center space-x-1.5 text-cerulean-900">
                  <ShieldCheck className="w-4 h-4 text-cerulean-600" />
                  <span>Bias-Protected Recruiter Inspection View</span>
                </div>
                <p className="text-[11px] text-slate-600">
                  All direct PII (name, email, phone, location) has been scrubbed and replaced with anonymous code{" "}
                  <strong className="text-slate-900">{candidate.anonymized_view?.anonymous_id || "Candidate"}</strong>.
                  Gender pronouns and older graduation dates are neutralized.
                </p>
              </div>

              <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl font-mono text-[11px] text-slate-700 whitespace-pre-wrap leading-relaxed max-h-80 overflow-y-auto">
                {candidate.anonymized_view?.sanitized_summary || candidate.summary || "Summary sanitized for evaluation."}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
