import React, { useState, useRef } from "react";
import { evaluateCandidate, JobProfile } from "../api/client";
import { UploadCloud, FileText, Video, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";

interface UploadPanelProps {
  currentJob: JobProfile | null;
  onEvaluationComplete: (evaluatedCandidate: any) => void;
}

export const UploadPanel: React.FC<UploadPanelProps> = ({ currentJob, onEvaluationComplete }) => {
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [location, setLocation] = useState("");

  const [uploading, setUploading] = useState(false);
  const [progressStage, setProgressStage] = useState<string>("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successData, setSuccessData] = useState<any | null>(null);

  const resumeInputRef = useRef<HTMLInputElement>(null);
  const videoInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentJob) {
      setErrorMsg("Please select or create an active Job Description first.");
      return;
    }
    if (!resumeFile) {
      setErrorMsg("Please provide a resume document (PDF, DOCX, or TXT).");
      return;
    }

    setUploading(true);
    setErrorMsg(null);
    setSuccessData(null);

    const formData = new FormData();
    formData.append("job_id", currentJob.job_id);
    formData.append("resume_file", resumeFile);
    if (videoFile) {
      formData.append("video_file", videoFile);
    }
    if (name.trim()) formData.append("name", name.trim());
    if (email.trim()) formData.append("email", email.trim());
    if (phone.trim()) formData.append("phone", phone.trim());
    if (location.trim()) formData.append("location", location.trim());

    try {
      setProgressStage("Parsing resume text and extracting entities...");
      setTimeout(() => setProgressStage("Running Whisper speech-to-text & sentiment telemetry..."), 1200);
      setTimeout(() => setProgressStage("Cross-checking claims and computing hybrid fit score..."), 2600);

      const result = await evaluateCandidate(formData);
      setSuccessData(result);
      onEvaluationComplete(result);

      // Reset form
      setResumeFile(null);
      setVideoFile(null);
      setName("");
      setEmail("");
      setPhone("");
      setLocation("");
      if (resumeInputRef.current) resumeInputRef.current.value = "";
      if (videoInputRef.current) videoInputRef.current.value = "";
    } catch (err: any) {
      console.error("Evaluation failed", err);
      setErrorMsg(err.response?.data?.detail || "Failed to process candidate submission.");
    } finally {
      setUploading(false);
      setProgressStage("");
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-6 shadow-sm">
      <div>
        <h3 className="font-semibold text-offwhite text-base">Multimodal Candidate Ingestion</h3>
        <p className="text-xs text-slate-400 mt-1">
          Upload candidate resume CV and optional video interview recording for automated end-to-end evaluation against{" "}
          <span className="text-coral-400 font-medium">{currentJob?.title || "selected role"}</span>.
        </p>
      </div>

      {errorMsg && (
        <div className="flex items-center space-x-2 bg-coral-950/60 border border-coral-800/80 text-coral-300 text-xs px-4 py-3 rounded-xl">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {successData && (
        <div className="bg-cerulean-950/60 border border-cerulean-800/80 text-cerulean-300 text-xs p-4 rounded-xl space-y-2">
          <div className="flex items-center space-x-2 font-semibold">
            <CheckCircle2 className="w-4 h-4" />
            <span>Evaluation Completed for {successData.candidate_name}!</span>
          </div>
          <p className="text-cerulean-300/90">
            Overall Fit Score: <strong className="text-offwhite">{successData.overall_fit_score}%</strong> (
            {successData.recommendation}). Candidate has been added to the active leaderboard.
          </p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Upload Dropzones */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Resume Upload */}
          <div
            onClick={() => resumeInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-5 text-center cursor-pointer transition ${
              resumeFile
                ? "border-coral-500 bg-coral-950/20"
                : "border-slate-800 hover:border-slate-700 bg-slate-950/50"
            }`}
          >
            <input
              ref={resumeInputRef}
              type="file"
              accept=".pdf,.docx,.txt,.md"
              className="hidden"
              onChange={(e) => {
                if (e.target.files?.[0]) setResumeFile(e.target.files[0]);
              }}
            />
            <FileText className="w-8 h-8 mx-auto text-coral-400 mb-2" />
            <div className="text-xs font-semibold text-slate-200">
              {resumeFile ? resumeFile.name : "Upload Resume (Required)"}
            </div>
            <p className="text-[11px] text-slate-400 mt-1">
              Supports PDF, DOCX, TXT. Automatically extracts skills, experience & scrubbed PII.
            </p>
          </div>

          {/* Video Upload */}
          <div
            onClick={() => videoInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-5 text-center cursor-pointer transition ${
              videoFile
                ? "border-cerulean-500 bg-cerulean-950/20"
                : "border-slate-800 hover:border-slate-700 bg-slate-950/50"
            }`}
          >
            <input
              ref={videoInputRef}
              type="file"
              accept=".mp4,.webm,.mov,.mkv"
              className="hidden"
              onChange={(e) => {
                if (e.target.files?.[0]) setVideoFile(e.target.files[0]);
              }}
            />
            <Video className="w-8 h-8 mx-auto text-cerulean-400 mb-2" />
            <div className="text-xs font-semibold text-slate-200">
              {videoFile ? videoFile.name : "Upload Video Interview (Optional)"}
            </div>
            <p className="text-[11px] text-slate-400 mt-1">
              Supports MP4, WEBM. Analyzes Whisper transcription, speaking pace, tone & claim alignment.
            </p>
          </div>
        </div>

        {/* Optional Metadata */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
          <div>
            <label className="block text-slate-400 mb-1">Candidate Name</label>
            <input
              type="text"
              placeholder="e.g. Sarah Chen"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-offwhite focus:outline-none focus:border-coral-500"
            />
          </div>
          <div>
            <label className="block text-slate-400 mb-1">Email</label>
            <input
              type="email"
              placeholder="sarah@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-offwhite focus:outline-none focus:border-coral-500"
            />
          </div>
          <div>
            <label className="block text-slate-400 mb-1">Phone</label>
            <input
              type="text"
              placeholder="+1-555-0192"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-offwhite focus:outline-none focus:border-coral-500"
            />
          </div>
          <div>
            <label className="block text-slate-400 mb-1">Location</label>
            <input
              type="text"
              placeholder="San Francisco, CA"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-offwhite focus:outline-none focus:border-coral-500"
            />
          </div>
        </div>

        {/* Upload Progress Bar */}
        {uploading && (
          <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-2">
            <div className="flex items-center justify-between text-xs text-coral-300">
              <span className="flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin text-coral-400" />
                <span>Processing Multimodal Pipeline...</span>
              </span>
              <span className="text-[11px] text-slate-400">{progressStage}</span>
            </div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
              <div className="bg-gradient-to-r from-coral-500 via-coral-400 to-cerulean-500 h-full w-3/4 animate-pulse rounded-full" />
            </div>
          </div>
        )}

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={uploading || !resumeFile}
            className="flex items-center space-x-2 bg-coral-500 hover:bg-coral-600 disabled:opacity-50 text-white font-semibold text-xs px-6 py-3 rounded-xl shadow-lg shadow-coral-500/25 transition"
          >
            <UploadCloud className="w-4 h-4" />
            <span>{uploading ? "Evaluating..." : "Run Screening Evaluation"}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
