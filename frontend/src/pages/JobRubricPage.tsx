import React, { useState, useEffect } from "react";
import { JobProfile, ScoringWeights, updateJobWeights, rerankCandidates } from "../api/client";
import { Sliders, RefreshCw, CheckCircle2, Plus } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { CreateJobModal } from "../components/CreateJobModal";

interface JobRubricPageProps {
  currentJob: JobProfile | null;
  onJobUpdated: (updatedJob: JobProfile) => void;
  onJobCreated?: (newJob: JobProfile) => void;
}

const COLORS = ["#EF8A62", "#67A9CF", "#f6b89f", "#9ecbe3", "#c8603a"];

export const JobRubricPage: React.FC<JobRubricPageProps> = ({ currentJob, onJobUpdated, onJobCreated }) => {
  const [weights, setWeights] = useState<ScoringWeights>({
    skill_match: 0.35,
    experience_match: 0.25,
    multimodal_presentation: 0.15,
    sentiment_engagement: 0.1,
    claim_credibility: 0.15,
  });

  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [showNewJobModal, setShowNewJobModal] = useState(false);

  useEffect(() => {
    if (currentJob?.scoring_weights) {
      setWeights({
        skill_match: currentJob.scoring_weights.skill_match ?? 0.35,
        experience_match: currentJob.scoring_weights.experience_match ?? 0.25,
        multimodal_presentation: currentJob.scoring_weights.multimodal_presentation ?? 0.15,
        sentiment_engagement: currentJob.scoring_weights.sentiment_engagement ?? 0.1,
        claim_credibility: currentJob.scoring_weights.claim_credibility ?? 0.15,
      });
    }
  }, [currentJob]);

  const handleSliderChange = (key: keyof ScoringWeights, val: number) => {
    setWeights((prev) => ({ ...prev, [key]: Math.round(val * 100) / 100 }));
    setSaveSuccess(false);
  };

  const totalWeight = Object.values(weights).reduce((a, b) => a + b, 0);
  const isBalanced = Math.abs(totalWeight - 1.0) < 0.05;

  const handleSaveAndRerank = async () => {
    if (!currentJob) return;
    setSaving(true);
    setSaveSuccess(false);
    try {
      const updated = await updateJobWeights(currentJob.job_id, weights);
      await rerankCandidates(currentJob.job_id);
      onJobUpdated(updated);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 4000);
    } catch (err) {
      console.error("Failed to update weights", err);
    } finally {
      setSaving(false);
    }
  };

  if (!currentJob) {
    return (
      <div className="p-12 text-center text-slate-400 text-xs bg-[#F7F7F7] border border-dashed border-slate-200 rounded-2xl">
        <Sliders className="w-10 h-10 text-slate-300 mx-auto mb-3" />
        <div className="font-semibold text-slate-500 mb-1">No active job selected</div>
        <div>Select or create a Job Profile to adjust scoring weights.</div>
        <button
          onClick={() => setShowNewJobModal(true)}
          className="btn-coral mt-4 text-xs text-white font-bold px-4 py-2 rounded-xl inline-flex items-center space-x-1.5"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Create New Job Profile</span>
        </button>
        <CreateJobModal
          isOpen={showNewJobModal}
          onClose={() => setShowNewJobModal(false)}
          onJobCreated={(j) => {
            if (onJobCreated) onJobCreated(j);
          }}
        />
      </div>
    );
  }

  const pieData = [
    { name: "Skill Match", value: Math.round(weights.skill_match * 100) },
    { name: "Experience", value: Math.round(weights.experience_match * 100) },
    { name: "Speech/Cadence", value: Math.round(weights.multimodal_presentation * 100) },
    { name: "Sentiment/Tone", value: Math.round(weights.sentiment_engagement * 100) },
    { name: "Claim Consistency", value: Math.round(weights.claim_credibility * 100) },
  ];

  const sliders = [
    { key: "skill_match" as const, label: "1. Skill Coverage & Taxonomy Overlap", desc: "Rewards exact required skills and adjacent framework taxonomy matches.", accent: "#EF8A62", max: 0.80 },
    { key: "experience_match" as const, label: "2. Career Experience & Semantic Fit", desc: "Dense vector embedding similarity between project achievements and JD responsibilities.", accent: "#67A9CF", max: 0.80 },
    { key: "multimodal_presentation" as const, label: "3. Speech Cadence, Prosody & Delivery", desc: "Optimal speaking rate (115–165 WPM), low filler-word frequency, and acoustic clarity.", accent: "#EF8A62", max: 0.60 },
    { key: "sentiment_engagement" as const, label: "4. Interview Sentiment & Constructive Tone", desc: "Verbal engagement, optimism, and proactive problem-solving sentiment during responses.", accent: "#67A9CF", max: 0.40 },
    { key: "claim_credibility" as const, label: "5. Cross-Modal Claim Consistency", desc: "Penalizes inflated experience claims spoken in video but absent from written CV.", accent: "#EF8A62", max: 0.50 },
  ];

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="bg-white border border-slate-200/80 p-5 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-sm">
        <div>
          <div className="flex items-center space-x-2 text-[11px] font-semibold text-slate-400 uppercase tracking-widest">
            <span>Rubric ID:</span>
            <span className="font-mono text-[#EF8A62] normal-case font-bold tracking-normal">{currentJob.job_id}</span>
          </div>
          <h2 className="text-xl font-extrabold text-slate-900 mt-1">{currentJob.title}</h2>
          <p className="text-xs text-slate-400 mt-0.5 line-clamp-1">{currentJob.description}</p>
        </div>

        <div className="flex items-center space-x-3 shrink-0">
          <button
            onClick={() => setShowNewJobModal(true)}
            className="inline-flex items-center space-x-2 text-xs font-semibold bg-[#F7F7F7] hover:bg-slate-100 text-slate-700 px-4 py-2.5 rounded-xl border border-slate-200 hover:border-[#EF8A62]/30 transition"
          >
            <Plus className="w-3.5 h-3.5 text-[#EF8A62]" />
            <span>New Job Description</span>
          </button>
          <button
            onClick={handleSaveAndRerank}
            disabled={saving}
            className="btn-coral inline-flex items-center space-x-2 text-xs font-bold text-white px-5 py-2.5 rounded-xl disabled:opacity-50 disabled:transform-none disabled:shadow-none"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${saving ? "animate-spin" : ""}`} />
            <span>{saving ? "Recalibrating…" : "Save & Re-rank"}</span>
          </button>
        </div>
      </div>

      {saveSuccess && (
        <div className="flex items-center space-x-2 bg-[#67A9CF]/5 border border-[#67A9CF]/30 text-[#3f7fa0] text-xs px-4 py-3 rounded-xl font-semibold animate-fade-in">
          <CheckCircle2 className="w-4 h-4 text-[#67A9CF]" />
          <span>Weights saved! All candidates dynamically re-ranked.</span>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Sliders */}
        <div className="lg:col-span-2 bg-white border border-slate-200/80 p-6 rounded-2xl space-y-6 shadow-sm">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div className="flex items-center space-x-2">
              <div className="p-1.5 bg-[#EF8A62]/10 rounded-lg">
                <Sliders className="w-4 h-4 text-[#EF8A62]" />
              </div>
              <h3 className="font-bold text-slate-900">Multi-Factor Weight Rubric</h3>
            </div>
            <div className={`text-[11px] px-3 py-1 rounded-full font-bold border ${
              isBalanced
                ? "bg-[#67A9CF]/10 text-[#3f7fa0] border-[#67A9CF]/30"
                : "bg-[#EF8A62]/10 text-[#c8603a] border-[#EF8A62]/30"
            }`}>
              Σ {Math.round(totalWeight * 100)}% {isBalanced ? "✓" : "⚠"}
            </div>
          </div>

          <div className="space-y-5">
            {sliders.map(({ key, label, desc, accent, max }) => (
              <div key={key} className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold text-slate-700">{label}</span>
                  <span className="font-black" style={{ color: accent }}>{Math.round(weights[key] * 100)}%</span>
                </div>
                <input
                  type="range"
                  min="0.05"
                  max={max}
                  step="0.05"
                  value={weights[key]}
                  onChange={(e) => handleSliderChange(key, parseFloat(e.target.value))}
                  className="w-full h-2 rounded-lg cursor-pointer appearance-none bg-slate-100"
                  style={{ accentColor: accent }}
                />
                <div className="relative h-1.5 bg-slate-100 rounded-full overflow-hidden -mt-1">
                  <div
                    className="absolute left-0 top-0 h-full rounded-full transition-all duration-300"
                    style={{ width: `${(weights[key] / max) * 100}%`, background: `linear-gradient(90deg, ${accent}, ${accent}99)` }}
                  />
                </div>
                <p className="text-[11px] text-slate-400">{desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Pie chart */}
        <div className="bg-white border border-slate-200/80 p-6 rounded-2xl space-y-4 flex flex-col shadow-sm">
          <div>
            <h3 className="font-bold text-slate-900 text-sm">Weight Distribution</h3>
            <p className="text-xs text-slate-400 mt-0.5">Relative ranking importance across modalities.</p>
          </div>

          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={42} outerRadius={72} paddingAngle={3} dataKey="value">
                  {pieData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="white" strokeWidth={2} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: "#fff", borderColor: "#e2e8f0", fontSize: "12px", borderRadius: "10px", boxShadow: "0 4px 20px rgba(0,0,0,0.08)" }}
                  itemStyle={{ color: "#1e293b" }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-2 pt-2 border-t border-slate-100 flex-1">
            {pieData.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs group">
                <div className="flex items-center space-x-2.5">
                  <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: COLORS[idx % COLORS.length] }} />
                  <span className="text-slate-600 font-medium">{item.name}</span>
                </div>
                <span className="font-black text-slate-800">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* New Job Modal */}
      <CreateJobModal
        isOpen={showNewJobModal}
        onClose={() => setShowNewJobModal(false)}
        onJobCreated={(j) => {
          if (onJobCreated) onJobCreated(j);
        }}
        initialWeights={weights}
      />
    </div>
  );
};
