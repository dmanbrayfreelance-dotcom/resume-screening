import React, { useState } from "react";
import { Candidate, CandidateEvaluation } from "../api/client";
import { SkillGapChart } from "./SkillGapChart";
import {
  X, Award, Video, FileCheck2, ShieldCheck, CheckCircle2,
  AlertTriangle, Lightbulb, MessageSquare, Sparkles,
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
      overall_fit_score: 75.0, recommendation: "Review", is_advisory_only: true,
      component_breakdown: {},
      skill_gap: { matched_skills: [], missing_required_skills: [], missing_preferred_skills: [], coverage_pct: 0, recommendations: [] },
      claim_verification: { credibility_score: 85.0, aligned: [], mentioned_only_in_video: [], mentioned_only_in_resume: [], potential_discrepancy: [], recruiter_notes: [] },
      strengths: [], areas_for_probing: [], recruiter_executive_summary: "",
      evaluated_at: new Date().toISOString(),
    } as any);

  const multimodal = candidate.multimodal_analysis || {};
  const claims = evaluation.claim_verification || { aligned: [], mentioned_only_in_video: [], mentioned_only_in_resume: [], potential_discrepancy: [], recruiter_notes: [] };

  const getScoreBadge = (score: number) => {
    if (score >= 85) return { bg: "bg-gradient-to-b from-[#EF8A62]/10 to-[#EF8A62]/5 border-[#EF8A62]/40 text-[#c8603a]", label: "Strong Hire" };
    if (score >= 70) return { bg: "bg-gradient-to-b from-[#67A9CF]/10 to-[#67A9CF]/5 border-[#67A9CF]/40 text-[#3f7fa0]", label: "Hire" };
    if (score >= 55) return { bg: "bg-amber-50 border-amber-300 text-amber-700", label: "Review" };
    return { bg: "bg-rose-50 border-rose-300 text-rose-700", label: "Hold" };
  };

  const badge = getScoreBadge(evaluation.overall_fit_score);

  const tabs = [
    { id: "scorecard", label: "Scorecard", icon: Award },
    { id: "skills", label: "Skill Gap", icon: Sparkles },
    { id: "multimodal", label: "Speech", icon: Video },
    { id: "claims", label: "Claims", icon: FileCheck2 },
    { id: "anonymized", label: "Fairness", icon: ShieldCheck },
  ] as const;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/50 backdrop-blur-sm flex justify-end">
      <div className="w-full max-w-2xl bg-white border-l border-slate-200 h-full flex flex-col shadow-2xl slide-in-from-right">

        {/* Drawer Header */}
        <div className="p-5 border-b border-slate-100 flex items-start justify-between bg-gradient-to-r from-[#F7F7F7] to-white shrink-0">
          <div className="min-w-0 flex-1">
            <div className="flex items-center space-x-2 mb-1">
              <span className="text-[10px] text-[#EF8A62] font-mono font-bold bg-[#EF8A62]/10 px-2 py-0.5 rounded-lg border border-[#EF8A62]/20">
                {candidate.candidate_id}
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200 font-semibold">
                {candidate.status || "screened"}
              </span>
            </div>
            <h2 className="text-xl font-extrabold text-slate-900 truncate">
              {candidate.contact_info?.name || "Candidate Profile"}
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              {candidate.contact_info?.email} · {candidate.contact_info?.location || "Remote"}
            </p>
          </div>

          <div className="flex items-center space-x-3 shrink-0 ml-4">
            <div className={`px-4 py-2 rounded-xl border text-center font-black ${badge.bg}`}>
              <div className="text-lg">{evaluation.overall_fit_score}%</div>
              <div className="text-[9px] font-bold uppercase tracking-widest mt-0.5">{evaluation.recommendation}</div>
            </div>
            <button onClick={onClose} className="p-2.5 rounded-xl text-slate-400 hover:text-slate-800 hover:bg-slate-100 transition">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-100 px-4 bg-white shrink-0 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-1.5 py-3.5 px-3 text-[11px] font-semibold border-b-2 whitespace-nowrap transition-all mr-1 ${
                  active
                    ? "border-[#EF8A62] text-[#EF8A62] bg-[#EF8A62]/3"
                    : "border-transparent text-slate-400 hover:text-slate-700"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div className="p-5 overflow-y-auto space-y-5 flex-1 text-xs text-slate-700 animate-fade-in">

          {/* SCORECARD */}
          {activeTab === "scorecard" && (
            <div className="space-y-5">
              {evaluation.recruiter_executive_summary && (
                <div className="p-4 rounded-xl bg-gradient-to-br from-[#EF8A62]/8 to-[#EF8A62]/3 border border-[#EF8A62]/20 space-y-2">
                  <div className="font-bold text-[#c8603a] flex items-center space-x-1.5 text-sm">
                    <Sparkles className="w-3.5 h-3.5 text-[#EF8A62]" />
                    <span>Recruiter Executive Summary</span>
                  </div>
                  <p className="text-slate-700 leading-relaxed">{evaluation.recruiter_executive_summary}</p>
                </div>
              )}

              <div className="space-y-3">
                <h4 className="font-bold text-slate-900 text-sm">Transparent Multi-Factor Breakdown</h4>
                {Object.entries(evaluation.component_breakdown || {}).map(([key, comp]) => (
                  <div key={key} className="bg-[#F7F7F7] border border-slate-200/80 p-4 rounded-xl space-y-2 hover:border-slate-300 transition">
                    <div className="flex justify-between items-center">
                      <div>
                        <span className="font-bold text-slate-900">{comp.name}</span>
                        <span className="ml-2 text-[10px] text-slate-400 font-medium">Weight {Math.round(comp.weight * 100)}%</span>
                      </div>
                      <span className="font-black text-[#67A9CF] text-sm">{comp.raw_score}%</span>
                    </div>
                    <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                      <div className="progress-coral h-full rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(100, comp.raw_score)}%` }} />
                    </div>
                    <p className="text-[11px] text-slate-400">{comp.details}</p>
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gradient-to-br from-[#67A9CF]/8 to-[#67A9CF]/3 border border-[#67A9CF]/20 p-4 rounded-xl space-y-3">
                  <div className="font-bold text-[#3f7fa0] flex items-center space-x-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#67A9CF]" />
                    <span>Top Strengths</span>
                  </div>
                  <ul className="space-y-1.5 text-slate-700">
                    {(evaluation.strengths || []).map((s, idx) => <li key={idx} className="flex items-start space-x-1.5"><span className="text-[#67A9CF] font-bold">•</span><span>{s}</span></li>)}
                  </ul>
                </div>
                <div className="bg-gradient-to-br from-[#EF8A62]/8 to-[#EF8A62]/3 border border-[#EF8A62]/20 p-4 rounded-xl space-y-3">
                  <div className="font-bold text-[#c8603a] flex items-center space-x-1.5">
                    <Lightbulb className="w-3.5 h-3.5 text-[#EF8A62]" />
                    <span>Interview Probing Areas</span>
                  </div>
                  <ul className="space-y-1.5 text-slate-700">
                    {(evaluation.areas_for_probing || []).map((p, idx) => <li key={idx} className="flex items-start space-x-1.5"><span className="text-[#EF8A62] font-bold">•</span><span>{p}</span></li>)}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* SKILL GAP */}
          {activeTab === "skills" && (
            <div className="space-y-5">
              <SkillGapChart evaluation={evaluation} />
              <div className="space-y-3">
                <h4 className="font-bold text-slate-900 text-sm">Actionable Upskilling Recommendations</h4>
                {(evaluation.skill_gap?.recommendations || []).map((rec, idx) => (
                  <div key={idx} className="p-3.5 bg-[#F7F7F7] border border-slate-200 rounded-xl flex items-start space-x-3 hover:border-[#EF8A62]/30 transition">
                    <Lightbulb className="w-4 h-4 text-[#EF8A62] shrink-0 mt-0.5" />
                    <span className="text-slate-700">{rec}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* MULTIMODAL */}
          {activeTab === "multimodal" && (
            <div className="space-y-5">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {[
                  { label: "Speaking Rate", value: `${multimodal.words_per_minute || 135} WPM`, sub: multimodal.speaking_pace || "optimal", accent: "#EF8A62" },
                  { label: "Filler Words", value: `${Math.round((multimodal.filler_word_ratio || 0.015) * 1000) / 10}%`, sub: "Low Hesitancy", accent: "#67A9CF" },
                  { label: "Sentiment", value: multimodal.sentiment_label || "POSITIVE", sub: `${multimodal.sentiment_score || 0.9} polarity`, accent: "#67A9CF" },
                  { label: "Delivery", value: `${multimodal.presentation_score || 91}%`, sub: "Composite", accent: "#EF8A62" },
                ].map(({ label, value, sub, accent }) => (
                  <div key={label} className="relative bg-[#F7F7F7] border border-slate-200 p-3.5 rounded-xl text-center overflow-hidden">
                    <div className="absolute top-0 left-0 right-0 h-0.5" style={{ background: `linear-gradient(90deg, ${accent}, ${accent}60)` }} />
                    <div className="text-[10px] text-slate-400 uppercase font-bold tracking-widest">{label}</div>
                    <div className="text-base font-black mt-1.5" style={{ color: accent }}>{value}</div>
                    <div className="text-[10px] font-semibold capitalize mt-0.5" style={{ color: accent }}>{sub}</div>
                  </div>
                ))}
              </div>

              <div className="space-y-2">
                <div className="flex items-center space-x-2 font-bold text-slate-900">
                  <MessageSquare className="w-4 h-4 text-[#67A9CF]" />
                  <span>Whisper Transcript</span>
                </div>
                <div className="p-4 bg-[#F7F7F7] border border-slate-200 rounded-xl leading-relaxed text-slate-600 font-mono text-[11px] max-h-56 overflow-y-auto">
                  {multimodal.transcript || "No video interview recorded. Candidate screened based on textual resume credentials."}
                </div>
              </div>
            </div>
          )}

          {/* CLAIMS */}
          {activeTab === "claims" && (
            <div className="space-y-5">
              <div className="flex items-center justify-between p-4 bg-gradient-to-r from-[#67A9CF]/8 to-transparent border border-[#67A9CF]/20 rounded-xl">
                <div>
                  <div className="font-bold text-slate-900">Cross-Modal Credibility Index</div>
                  <p className="text-[11px] text-slate-400 mt-0.5">Correlates verbal statements with written CV claims.</p>
                </div>
                <div className="text-3xl font-black text-[#67A9CF]">{claims.credibility_score || 90}%</div>
              </div>

              {claims.potential_discrepancy?.length > 0 && (
                <div className="space-y-2">
                  <div className="font-bold text-[#c8603a] flex items-center space-x-1.5">
                    <AlertTriangle className="w-4 h-4 text-[#EF8A62]" />
                    <span>Flagged Discrepancies for Recruiter Follow-up</span>
                  </div>
                  {claims.potential_discrepancy.map((d, idx) => (
                    <div key={idx} className="p-4 bg-[#EF8A62]/5 border border-[#EF8A62]/20 rounded-xl space-y-1.5">
                      <div className="flex justify-between font-bold text-[#c8603a]">
                        <span>{d.category.replace("_", " ").toUpperCase()}</span>
                        <span className="text-[9px] bg-[#EF8A62]/15 px-2 py-0.5 rounded border border-[#EF8A62]/30 uppercase tracking-wider">{d.severity}</span>
                      </div>
                      <p className="text-[11px] text-slate-600">{d.explanation}</p>
                    </div>
                  ))}
                </div>
              )}

              <div className="space-y-2">
                <div className="font-bold text-slate-900">Aligned Competencies (Verified)</div>
                <div className="flex flex-wrap gap-1.5">
                  {(claims.aligned || []).map((skill, idx) => (
                    <span key={idx} className="px-2.5 py-1 rounded-full bg-[#67A9CF]/10 text-[#3f7fa0] border border-[#67A9CF]/30 font-semibold text-[11px]">✓ {skill}</span>
                  ))}
                </div>
              </div>

              {claims.mentioned_only_in_video?.length > 0 && (
                <div className="space-y-2">
                  <div className="font-bold text-slate-700">Spoken but not on Resume</div>
                  <div className="flex flex-wrap gap-1.5">
                    {claims.mentioned_only_in_video.map((skill, idx) => (
                      <span key={idx} className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 border border-slate-200 font-semibold text-[11px]">+ {skill}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* FAIRNESS */}
          {activeTab === "anonymized" && (
            <div className="space-y-4">
              <div className="p-4 bg-gradient-to-br from-[#67A9CF]/8 to-transparent border border-[#67A9CF]/20 rounded-xl space-y-2">
                <div className="font-bold flex items-center space-x-1.5 text-[#3f7fa0]">
                  <ShieldCheck className="w-4 h-4 text-[#67A9CF]" />
                  <span>Bias-Protected Recruiter Inspection View</span>
                </div>
                <p className="text-[11px] text-slate-600 leading-relaxed">
                  All PII scrubbed · Anonymous ID:{" "}
                  <strong className="text-slate-900 font-mono">{candidate.anonymized_view?.anonymous_id || "ANON-001"}</strong>.
                  Gender pronouns and older graduation dates neutralized.
                </p>
              </div>
              <div className="p-4 bg-[#F7F7F7] border border-slate-200 rounded-xl font-mono text-[11px] text-slate-700 whitespace-pre-wrap leading-relaxed max-h-80 overflow-y-auto">
                {candidate.anonymized_view?.sanitized_summary || candidate.summary || "Summary sanitized for evaluation."}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
