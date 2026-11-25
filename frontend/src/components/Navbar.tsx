import React from "react";
import { HealthStatus } from "../api/client";
import { Sparkles, Zap, Briefcase } from "lucide-react";

interface NavbarProps {
  systemStatus: HealthStatus | null;
  onOpenIngest?: () => void;
  onOpenCreateJob?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  systemStatus,
  onOpenIngest,
  onOpenCreateJob,
}) => {
  const isFallback =
    systemStatus?.mongodb_atlas_connectivity === "fallback" ||
    systemStatus?.database_mode?.includes("fallback");

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="relative h-9 w-9 rounded-xl bg-gradient-to-tr from-[#EF8A62] via-[#f0a07a] to-[#67A9CF] flex items-center justify-center shadow-lg shadow-[#EF8A62]/30 shrink-0">
            <Sparkles className="w-5 h-5 text-white drop-shadow" />
            <div className="absolute inset-0 rounded-xl bg-white/10" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="font-extrabold text-slate-900 text-base sm:text-lg leading-tight tracking-tight">
                Multimodal Resume{" "}
                <span className="bg-gradient-to-r from-[#EF8A62] to-[#67A9CF] bg-clip-text text-transparent">
                  Intelligence
                </span>
              </h1>
              <span className="hidden sm:inline-flex text-[9px] font-bold uppercase px-2 py-0.5 rounded-full bg-gradient-to-r from-[#EF8A62]/10 to-[#67A9CF]/10 text-[#EF8A62] border border-[#EF8A62]/30 tracking-wider">
                Studio
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium mt-0.5 hidden sm:block">
              Automated Video &amp; Resume Screening · Cross-Modal Claim Verification
            </p>
          </div>
        </div>

        {/* Right cluster */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Status pill */}
          <div
            className={`hidden md:flex items-center space-x-2 text-[11px] px-3 py-1.5 rounded-xl border font-medium transition-all ${
              isFallback
                ? "bg-[#EF8A62]/5 border-[#EF8A62]/30 text-[#EF8A62]"
                : "bg-[#67A9CF]/5 border-[#67A9CF]/30 text-[#67A9CF]"
            }`}
          >
            <span
              className={`h-2 w-2 rounded-full ${
                isFallback ? "bg-[#EF8A62] animate-pulse" : "bg-[#67A9CF]"
              }`}
            />
            <span>{isFallback ? "Offline Fallback" : "MongoDB Atlas"}</span>
          </div>

          {/* Create Job CTA */}
          {onOpenCreateJob && (
            <button
              onClick={onOpenCreateJob}
              className="inline-flex items-center space-x-1.5 text-xs font-semibold px-3.5 py-2 rounded-xl bg-[#F7F7F7] hover:bg-slate-100 text-slate-700 border border-slate-200 hover:border-[#EF8A62]/40 transition"
              title="Create new job profile"
            >
              <Briefcase className="w-3.5 h-3.5 text-[#EF8A62]" />
              <span className="hidden sm:inline">+ Create Job</span>
              <span className="sm:hidden">+ Job</span>
            </button>
          )}

          {/* Ingest Candidate CTA */}
          {onOpenIngest && (
            <button
              onClick={onOpenIngest}
              className="btn-coral flex items-center space-x-1.5 text-xs text-white font-semibold px-4 py-2 rounded-xl"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>Ingest Candidate</span>
            </button>
          )}
        </div>
      </div>

      {/* Gradient bottom line */}
      <div className="h-px bg-gradient-to-r from-transparent via-[#EF8A62]/30 to-transparent" />
    </header>
  );
};

export default Navbar;
