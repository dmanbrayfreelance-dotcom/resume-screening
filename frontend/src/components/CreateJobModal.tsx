import React, { useState } from "react";
import { JobProfile, ScoringWeights, createJob } from "../api/client";
import { PlusCircle, X, Sparkles, Briefcase, MapPin, Building, GraduationCap, Award } from "lucide-react";

interface CreateJobModalProps {
  isOpen: boolean;
  onClose: () => void;
  onJobCreated: (newJob: JobProfile) => void;
  initialWeights?: ScoringWeights;
}

export const CreateJobModal: React.FC<CreateJobModalProps> = ({
  isOpen,
  onClose,
  onJobCreated,
  initialWeights,
}) => {
  const [title, setTitle] = useState("");
  const [department, setDepartment] = useState("Engineering");
  const [location, setLocation] = useState("Remote / Hybrid");
  const [employmentType, setEmploymentType] = useState("Full-time");
  const [minExp, setMinExp] = useState(2);
  const [educationLevel, setEducationLevel] = useState("Bachelor's Degree or Equivalent");
  const [description, setDescription] = useState("");
  const [requiredSkills, setRequiredSkills] = useState("");
  const [preferredSkills, setPreferredSkills] = useState("");
  const [responsibilities, setResponsibilities] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setErrorMsg("Job Title is required.");
      return;
    }

    setSubmitting(true);
    setErrorMsg(null);

    try {
      const reqSkillsArr = requiredSkills
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);

      const prefSkillsArr = preferredSkills
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);

      const respArr = responsibilities
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean);

      const payload = {
        title: title.trim(),
        department: department.trim() || "Engineering",
        location: location.trim() || "Remote",
        employment_type: employmentType,
        experience_years_min: Number(minExp) || 0,
        education_level: educationLevel,
        description:
          description.trim() ||
          "Multimodal AI role evaluating video interview cadence, resume skills, and claim credibility.",
        responsibilities: respArr.length > 0 ? respArr : [
          "Screen candidate resumes and evaluate multi-modal interview recordings",
          "Ensure compliance with fair hiring and algorithmic governance",
        ],
        required_skills: reqSkillsArr.length > 0 ? reqSkillsArr : ["Python", "FastAPI"],
        preferred_skills: prefSkillsArr,
        scoring_weights: initialWeights || {
          skill_match: 0.35,
          experience_match: 0.25,
          multimodal_presentation: 0.15,
          sentiment_engagement: 0.1,
          claim_credibility: 0.15,
        },
        status: "open",
      };

      const created = await createJob(payload);
      onJobCreated(created);
      onClose();

      // Reset
      setTitle("");
      setDescription("");
      setRequiredSkills("");
      setPreferredSkills("");
      setResponsibilities("");
    } catch (err: any) {
      console.error("Failed to create job", err);
      setErrorMsg(err.response?.data?.detail || "Failed to create job profile.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white border border-slate-200 rounded-2xl max-w-2xl w-full p-6 space-y-5 shadow-2xl animate-fade-in my-8 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-[#EF8A62]/10 rounded-xl">
              <Briefcase className="w-5 h-5 text-[#EF8A62]" />
            </div>
            <div>
              <h3 className="text-lg font-extrabold text-slate-900">Create New Job Profile</h3>
              <p className="text-xs text-slate-400">
                Define the role, required skills, and screening criteria for candidate ranking.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-800 hover:bg-slate-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {errorMsg && (
          <div className="p-3 bg-[#EF8A62]/10 border border-[#EF8A62]/30 text-[#c8603a] rounded-xl text-xs font-semibold">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {/* Row 1: Title & Department */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-700 font-bold mb-1">
                Job Title <span className="text-[#EF8A62]">*</span>
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Senior AI / ML Research Engineer"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full bg-[#F7F7F7] border border-slate-200 rounded-xl px-3 py-2.5 text-slate-900 font-medium hover:border-slate-300 transition"
              />
            </div>
            <div>
              <label className="block text-slate-700 font-bold mb-1">Department</label>
              <input
                type="text"
                placeholder="e.g. AI Engineering"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                className="w-full bg-[#F7F7F7] border border-slate-200 rounded-xl px-3 py-2.5 text-slate-900 font-medium hover:border-slate-300 transition"
              />
            </div>
          </div>

          {/* Row 2: Location, Employment Type, Min Exp */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-slate-700 font-bold mb-1">Location</label>
              <input
                type="text"
                placeholder="e.g. Remote / San Francisco"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full bg-[#F7F7F7] border border-slate-200 rounded-xl px-3 py-2.5 text-slate-900 font-medium hover:border-slate-300 transition"
              />
            </div>
            <div>
              <label className="block text-slate-700 font-bold mb-1">Employment Type</label>
              <select
                value={employmentType}
                onChange={(e) => setEmploymentType(e.target.value)}
                className="w-full bg-[#F7F7F7] border border-slate-200 rounded-xl px-3 py-2.5 text-slate-900 font-medium hover:border-slate-300 transition cursor-pointer"
              >
                <option value="Full-time">Full-time</option>
                <option value="Contract">Contract</option>
                <option value="Part-time">Part-time</option>
                <option value="Internship">Internship</option>
              </select>
            </div>
            <div>
              <label className="block text-slate-700 font-bold mb-1">Min Experience (Years)</label>
              <input
                type="number"
                min="0"
                step="0.5"
                value={minExp}
                onChange={(e) => setMinExp(parseFloat(e.target.value) || 0)}
                className="w-full bg-[#F7F7F7] border border-slate-200 rounded-xl px-3 py-2.5 text-slate-900 font-medium hover:border-slate-300 transition"
              />
            </div>
          </div>

          {/* Row 3: Description */}
          <div>
            <label className="block text-slate-700 font-bold mb-1">Job Description</label>
            <textarea
              rows={3}
              placeholder="Overview of the position, mission, team context..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-[#F7F7F7] border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-medium hover:border-slate-300 transition resize-none"
            />
          </div>

          {/* Row 4: Required Skills */}
          <div>
            <label className="block text-slate-700 font-bold mb-1">
              Required Skills (comma-separated) <span className="text-[#EF8A62]">*</span>
            </label>
            <input
              type="text"
              required
              placeholder="Python, PyTorch, Whisper, FastAPI, MongoDB, NLP"
              value={requiredSkills}
              onChange={(e) => setRequiredSkills(e.target.value)}
              className="w-full bg-[#F7F7F7] border border-slate-200 rounded-xl px-3 py-2.5 text-slate-900 font-medium hover:border-slate-300 transition"
            />
            <p className="text-[10px] text-slate-400 mt-1">
              Used by semantic skill extractor to compute candidate skill alignment ratio.
            </p>
          </div>

          {/* Row 5: Preferred Skills */}
          <div>
            <label className="block text-slate-700 font-bold mb-1">
              Preferred Skills (comma-separated, optional)
            </label>
            <input
              type="text"
              placeholder="Docker, Kubernetes, AWS, TensorRT, LangChain"
              value={preferredSkills}
              onChange={(e) => setPreferredSkills(e.target.value)}
              className="w-full bg-[#F7F7F7] border border-slate-200 rounded-xl px-3 py-2.5 text-slate-900 font-medium hover:border-slate-300 transition"
            />
          </div>

          {/* Row 6: Responsibilities */}
          <div>
            <label className="block text-slate-700 font-bold mb-1">
              Key Responsibilities (one per line, optional)
            </label>
            <textarea
              rows={2}
              placeholder="Design multimodal neural architectures&#10;Deploy speech-to-text inference at scale"
              value={responsibilities}
              onChange={(e) => setResponsibilities(e.target.value)}
              className="w-full bg-[#F7F7F7] border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-medium hover:border-slate-300 transition resize-none"
            />
          </div>

          {/* Action buttons */}
          <div className="flex justify-end space-x-3 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              disabled={submitting}
              className="px-4 py-2.5 rounded-xl bg-[#F7F7F7] text-slate-700 hover:bg-slate-100 transition font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="btn-coral px-6 py-2.5 rounded-xl text-white font-bold inline-flex items-center space-x-2"
            >
              <PlusCircle className="w-4 h-4" />
              <span>{submitting ? "Creating Job..." : "Create & Activate Profile"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateJobModal;
