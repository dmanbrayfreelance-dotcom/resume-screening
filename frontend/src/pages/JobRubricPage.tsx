import React, { useState, useEffect } from "react";
import { JobProfile, ScoringWeights, updateJobWeights, rerankCandidates, createJob } from "../api/client";
import { Sliders, RefreshCw, CheckCircle2, Plus } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

interface JobRubricPageProps {
  currentJob: JobProfile | null;
  onJobUpdated: (updatedJob: JobProfile) => void;
  onJobCreated?: (newJob: JobProfile) => void;
}

const COLORS = ["#EF8A62", "#67A9CF", "#f6b89f", "#9ecbe3", "#d96f45"];

export const JobRubricPage: React.FC<JobRubricPageProps> = ({
  currentJob,
  onJobUpdated,
  onJobCreated,
}) => {
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
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [newReqSkills, setNewReqSkills] = useState("");

  useEffect(() => {
    if (currentJob && currentJob.scoring_weights) {
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
    setWeights((prev) => ({
      ...prev,
      [key]: Math.round(val * 100) / 100,
    }));
    setSaveSuccess(false);
  };

  const totalWeight = Object.values(weights).reduce((a, b) => a + b, 0);

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
      console.error("Failed to update weights and re-rank", err);
    } finally {
      setSaving(false);
    }
  };

  const handleCreateNewJob = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    try {
      const skillsArray = newReqSkills
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);

      const created = await createJob({
        title: newTitle.trim(),
        description: newDesc.trim() || "Multimodal role screened via automated intelligence studio.",
        required_skills: skillsArray,
        scoring_weights: weights,
      });

      setShowNewJobModal(false);
      setNewTitle("");
      setNewDesc("");
      setNewReqSkills("");
      if (onJobCreated) onJobCreated(created);
    } catch (err) {
      console.error("Failed to create job profile", err);
    }
  };

  if (!currentJob) {
    return (
      <div className="p-8 text-center text-slate-500 text-xs bg-slate-900 border border-slate-800 rounded-2xl">
        No active job selected. Please select or create a Job Profile to adjust scoring weights.
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

  return (
    <div className="space-y-6">
      {/* Rubric Header */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-medium text-slate-400">
            <span>Job Profile Rubric ID:</span>
            <span className="font-mono text-coral-400">{currentJob.job_id}</span>
          </div>
          <h2 className="text-xl font-bold text-offwhite mt-1">{currentJob.title}</h2>
          <p className="text-xs text-slate-400 mt-1 line-clamp-1">{currentJob.description}</p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowNewJobModal(true)}
            className="flex items-center space-x-2 text-xs bg-slate-800 hover:bg-slate-700 text-offwhite px-4 py-2.5 rounded-xl border border-slate-700 transition"
          >
            <Plus className="w-4 h-4 text-coral-400" />
            <span>New Job Description</span>
          </button>
          <button
            onClick={handleSaveAndRerank}
            disabled={saving}
            className="flex items-center space-x-2 text-xs font-semibold bg-coral-500 hover:bg-coral-600 disabled:opacity-50 text-white px-5 py-2.5 rounded-xl shadow-lg shadow-coral-500/25 transition"
          >
            <RefreshCw className={`w-4 h-4 ${saving ? "animate-spin" : ""}`} />
            <span>{saving ? "Recalibrating..." : "Save & Re-rank"}</span>
          </button>
        </div>
      </div>

      {saveSuccess && (
        <div className="flex items-center space-x-2 bg-cerulean-950/60 border border-cerulean-800/80 text-cerulean-300 text-xs px-4 py-3 rounded-xl animate-fade-in">
          <CheckCircle2 className="w-4 h-4" />
          <span>Weights updated successfully! All candidates re-ranked dynamically.</span>
        </div>
      )}

      {/* Main Grid: Sliders & Recharts Weight Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sliders Panel */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-6">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <Sliders className="w-4 h-4 text-coral-400" />
              <h3 className="font-semibold text-offwhite text-sm">Multi-Factor Weight Rubric</h3>
            </div>
            <div
              className={`text-xs px-2.5 py-1 rounded-full font-semibold border ${
                Math.abs(totalWeight - 1.0) < 0.05
                  ? "bg-cerulean-950/50 text-cerulean-400 border-cerulean-800/60"
                  : "bg-coral-950/50 text-coral-400 border-coral-800/60"
              }`}
            >
              Sum: {Math.round(totalWeight * 100)}%
            </div>
          </div>

          {/* Slider 1: Skills */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="font-medium text-slate-200">1. Skill Coverage & Taxonomy Overlap</span>
              <span className="font-bold text-coral-400">{Math.round(weights.skill_match * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.80"
              step="0.05"
              value={weights.skill_match}
              onChange={(e) => handleSliderChange("skill_match", parseFloat(e.target.value))}
              className="w-full accent-[#EF8A62] bg-slate-800 h-2 rounded-lg cursor-pointer"
            />
            <p className="text-[11px] text-slate-400">
              Rewards candidates possessing exact required skills and adjacent framework taxonomy matches.
            </p>
          </div>

          {/* Slider 2: Experience */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="font-medium text-slate-200">2. Career Experience & Semantic Fit</span>
              <span className="font-bold text-cerulean-400">{Math.round(weights.experience_match * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.80"
              step="0.05"
              value={weights.experience_match}
              onChange={(e) => handleSliderChange("experience_match", parseFloat(e.target.value))}
              className="w-full accent-[#67A9CF] bg-slate-800 h-2 rounded-lg cursor-pointer"
            />
            <p className="text-[11px] text-slate-400">
              Evaluates dense vector embedding similarity between written project achievements and JD responsibilities.
            </p>
          </div>

          {/* Slider 3: Multimodal Presentation */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="font-medium text-slate-200">3. Speech Cadence, Prosody & Delivery</span>
              <span className="font-bold text-coral-400">
                {Math.round(weights.multimodal_presentation * 100)}%
              </span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.60"
              step="0.05"
              value={weights.multimodal_presentation}
              onChange={(e) => handleSliderChange("multimodal_presentation", parseFloat(e.target.value))}
              className="w-full accent-[#EF8A62] bg-slate-800 h-2 rounded-lg cursor-pointer"
            />
            <p className="text-[11px] text-slate-400">
              Rewards optimal speaking rate (115–165 WPM), low filler-word frequency, and acoustic clarity.
            </p>
          </div>

          {/* Slider 4: Sentiment */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="font-medium text-slate-200">4. Interview Sentiment & Constructive Tone</span>
              <span className="font-bold text-cerulean-400">{Math.round(weights.sentiment_engagement * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.40"
              step="0.05"
              value={weights.sentiment_engagement}
              onChange={(e) => handleSliderChange("sentiment_engagement", parseFloat(e.target.value))}
              className="w-full accent-[#67A9CF] bg-slate-800 h-2 rounded-lg cursor-pointer"
            />
            <p className="text-[11px] text-slate-400">
              Gauges verbal engagement, optimism, and proactive problem-solving sentiment during spoken questions.
            </p>
          </div>

          {/* Slider 5: Claim Credibility */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="font-medium text-slate-200">5. Cross-Modal Claim Consistency</span>
              <span className="font-bold text-coral-400">{Math.round(weights.claim_credibility * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.50"
              step="0.05"
              value={weights.claim_credibility}
              onChange={(e) => handleSliderChange("claim_credibility", parseFloat(e.target.value))}
              className="w-full accent-[#EF8A62] bg-slate-800 h-2 rounded-lg cursor-pointer"
            />
            <p className="text-[11px] text-slate-400">
              Penalizes inflated experience years or unbacked seniority claims spoken in video but absent on CV.
            </p>
          </div>
        </div>

        {/* Visualizer Card */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-4 flex flex-col justify-between">
          <div>
            <h3 className="font-semibold text-offwhite text-sm">Weight Allocation Distribution</h3>
            <p className="text-xs text-slate-400 mt-1">
              Visualizes relative ranking importance across modalities.
            </p>
          </div>

          <div className="h-48 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={75}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {pieData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0e1726",
                    borderColor: "#1b2943",
                    fontSize: "12px",
                    borderRadius: "8px",
                    color: "#F7F7F7",
                  }}
                  itemStyle={{ color: "#F7F7F7" }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-1.5 pt-2 border-t border-slate-800">
            {pieData.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <span
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                  />
                  <span className="text-slate-300">{item.name}</span>
                </div>
                <span className="font-semibold text-offwhite">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* New Job Modal */}
      {showNewJobModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-offwhite">Create New Job Description</h3>
            <form onSubmit={handleCreateNewJob} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 mb-1 font-medium">Job Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Lead Multimodal AI Architect"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-offwhite focus:outline-none focus:border-coral-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 mb-1 font-medium">Description</label>
                <textarea
                  rows={3}
                  placeholder="Brief role responsibilities and mission..."
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-offwhite focus:outline-none focus:border-coral-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 mb-1 font-medium">
                  Required Skills (comma separated)
                </label>
                <input
                  type="text"
                  placeholder="Python, FastAPI, Whisper, PyTorch, Docker"
                  value={newReqSkills}
                  onChange={(e) => setNewReqSkills(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-offwhite focus:outline-none focus:border-coral-500"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowNewJobModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-coral-500 hover:bg-coral-600 text-white font-semibold shadow-md shadow-coral-500/25 transition"
                >
                  Create Job Profile
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
