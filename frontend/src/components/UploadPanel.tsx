import React, { useState, useRef } from "react";
import { evaluateCandidate, JobProfile } from "../api/client";
import { UploadCloud, FileText, Video, CheckCircle2, AlertCircle, Loader2, Sparkles } from "lucide-react";

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
  const [progressPct, setProgressPct] = useState(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successData, setSuccessData] = useState<any | null>(null);

  const resumeInputRef = useRef<HTMLInputElement>(null);
  const videoInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentJob) { setErrorMsg("Please select or create an active Job Description first."); return; }
    if (!resumeFile) { setErrorMsg("Please provide a resume document (PDF, DOCX, or TXT)."); return; }

    setUploading(true);
    setErrorMsg(null);
    setSuccessData(null);
    setProgressPct(15);

    const formData = new FormData();
    formData.append("job_id", currentJob.job_id);
    formData.append("resume_file", resumeFile);
    if (videoFile) formData.append("video_file", videoFile);
    if (name.trim()) formData.append("name", name.trim());
    if (email.trim()) formData.append("email", email.trim());
    if (phone.trim()) formData.append("phone", phone.trim());
    if (location.trim()) formData.append("location", location.trim());

    try {
      setProgressStage("Parsing resume text and extracting entities…");
      setTimeout(() => { setProgressStage("Running Whisper speech-to-text & sentiment analysis…"); setProgressPct(45); }, 1200);
      setTimeout(() => { setProgressStage("Cross-checking claims & computing hybrid fit score…"); setProgressPct(75); }, 2600);

      const result = await evaluateCandidate(formData);
      setProgressPct(100);
      setSuccessData(result);
      onEvaluationComplete(result);

      setResumeFile(null); setVideoFile(null);
      setName(""); setEmail(""); setPhone(""); setLocation("");
      if (resumeInputRef.current) resumeInputRef.current.value = "";
      if (videoInputRef.current) videoInputRef.current.value = "";
    } catch (err: any) {
      console.error("Evaluation failed", err);
      setErrorMsg(err.response?.data?.detail || "Failed to process candidate submission.");
    } finally {
      setUploading(false);
      setProgressStage("");
      setProgressPct(0);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h3 className="font-extrabold text-slate-900 text-lg flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-[#EF8A62]" />
          <span>Multimodal Candidate Ingestion</span>
        </h3>
        <p className="text-xs text-slate-400 mt-1">
          Upload resume CV and optional video interview for end-to-end evaluation against{" "}
          <span className="text-[#EF8A62] font-semibold">{currentJob?.title || "selected role"}</span>.
        </p>
      </div>

      {/* Error */}
      {errorMsg && (
        <div className="flex items-start space-x-3 bg-[#EF8A62]/5 border border-[#EF8A62]/30 text-[#c8603a] text-xs px-4 py-3.5 rounded-xl font-medium animate-fade-in">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-[#EF8A62]" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Success */}
      {successData && (
        <div className="bg-[#67A9CF]/5 border border-[#67A9CF]/30 text-[#3f7fa0] text-xs p-4 rounded-xl space-y-1.5 animate-fade-in">
          <div className="flex items-center space-x-2 font-bold text-[#67A9CF]">
            <CheckCircle2 className="w-4 h-4" />
            <span>Evaluation Complete for {successData.candidate_name}!</span>
          </div>
          <p className="text-slate-600">
            Overall Fit: <strong className="text-slate-900">{successData.overall_fit_score}%</strong> ({successData.recommendation}). Added to leaderboard.
          </p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Dropzones */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Resume */}
          <div
            onClick={() => resumeInputRef.current?.click()}
            className={`group relative border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all duration-200 ${
              resumeFile
                ? "border-[#EF8A62] bg-[#EF8A62]/5 shadow-sm shadow-[#EF8A62]/10"
                : "border-slate-200 hover:border-[#EF8A62]/60 hover:bg-[#EF8A62]/3 hover:shadow-sm"
            }`}
          >
            <input ref={resumeInputRef} type="file" accept=".pdf,.docx,.txt,.md" className="hidden"
              onChange={(e) => { if (e.target.files?.[0]) setResumeFile(e.target.files[0]); }} />
            <div className={`w-12 h-12 mx-auto rounded-xl flex items-center justify-center mb-3 transition-all ${
              resumeFile ? "bg-[#EF8A62]/15" : "bg-slate-100 group-hover:bg-[#EF8A62]/10"
            }`}>
              <FileText className={`w-6 h-6 ${resumeFile ? "text-[#EF8A62]" : "text-slate-400 group-hover:text-[#EF8A62]"}`} />
            </div>
            <div className="text-sm font-bold text-slate-800">
              {resumeFile ? resumeFile.name : "Upload Resume"}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              {resumeFile ? "✓ Ready to evaluate" : "PDF, DOCX, TXT · Required"}
            </div>
            {!resumeFile && (
              <div className="mt-3 inline-block text-[10px] font-semibold text-[#EF8A62] border border-[#EF8A62]/30 rounded-lg px-2.5 py-1 bg-[#EF8A62]/5">
                Choose File
              </div>
            )}
          </div>

          {/* Video */}
          <div
            onClick={() => videoInputRef.current?.click()}
            className={`group relative border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all duration-200 ${
              videoFile
                ? "border-[#67A9CF] bg-[#67A9CF]/5 shadow-sm shadow-[#67A9CF]/10"
                : "border-slate-200 hover:border-[#67A9CF]/60 hover:bg-[#67A9CF]/3 hover:shadow-sm"
            }`}
          >
            <input ref={videoInputRef} type="file" accept=".mp4,.webm,.mov,.mkv" className="hidden"
              onChange={(e) => { if (e.target.files?.[0]) setVideoFile(e.target.files[0]); }} />
            <div className={`w-12 h-12 mx-auto rounded-xl flex items-center justify-center mb-3 transition-all ${
              videoFile ? "bg-[#67A9CF]/15" : "bg-slate-100 group-hover:bg-[#67A9CF]/10"
            }`}>
              <Video className={`w-6 h-6 ${videoFile ? "text-[#67A9CF]" : "text-slate-400 group-hover:text-[#67A9CF]"}`} />
            </div>
            <div className="text-sm font-bold text-slate-800">
              {videoFile ? videoFile.name : "Upload Video Interview"}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              {videoFile ? "✓ Whisper ASR queued" : "MP4, WEBM, MOV · Optional"}
            </div>
            {!videoFile && (
              <div className="mt-3 inline-block text-[10px] font-semibold text-[#67A9CF] border border-[#67A9CF]/30 rounded-lg px-2.5 py-1 bg-[#67A9CF]/5">
                Choose File
              </div>
            )}
          </div>
        </div>

        {/* Metadata fields */}
        <div>
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest mb-3">Candidate Info (Optional)</div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
            {[
              { label: "Full Name", placeholder: "Sarah Chen", value: name, setter: setName, type: "text" },
              { label: "Email", placeholder: "sarah@example.com", value: email, setter: setEmail, type: "email" },
              { label: "Phone", placeholder: "+1-555-0192", value: phone, setter: setPhone, type: "text" },
              { label: "Location", placeholder: "San Francisco, CA", value: location, setter: setLocation, type: "text" },
            ].map(({ label, placeholder, value, setter, type }) => (
              <div key={label}>
                <label className="block text-slate-500 mb-1.5 font-semibold">{label}</label>
                <input
                  type={type}
                  placeholder={placeholder}
                  value={value}
                  onChange={(e) => setter(e.target.value)}
                  className="w-full text-xs bg-[#F7F7F7] border border-slate-200 rounded-xl px-3 py-2.5 text-slate-900 placeholder:text-slate-400 hover:border-slate-300 transition"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Progress */}
        {uploading && (
          <div className="bg-[#F7F7F7] border border-slate-200 p-4 rounded-xl space-y-3 animate-fade-in">
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center space-x-2 font-semibold text-[#EF8A62]">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processing Multimodal Pipeline…</span>
              </span>
              <span className="text-[11px] text-slate-400 font-medium">{progressPct}%</span>
            </div>
            <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700 ease-out"
                style={{
                  width: `${progressPct}%`,
                  background: "linear-gradient(90deg, #EF8A62, #f6b89f, #67A9CF)",
                }}
              />
            </div>
            <p className="text-[11px] text-slate-400">{progressStage}</p>
          </div>
        )}

        <div className="flex justify-end pt-1">
          <button
            type="submit"
            disabled={uploading || !resumeFile}
            className="btn-coral flex items-center space-x-2 text-white font-bold text-sm px-7 py-3 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none"
          >
            <UploadCloud className="w-4 h-4" />
            <span>{uploading ? "Evaluating…" : "Run Screening Evaluation"}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
