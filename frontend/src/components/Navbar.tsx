import React from "react";
import { HealthStatus } from "../api/client";
import { Sparkles } from "lucide-react";

interface NavbarProps {
  systemStatus: HealthStatus | null;
  onOpenIngest?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ systemStatus, onOpenIngest }) => {
  const isFallback =
    systemStatus?.mongodb_atlas_connectivity === "fallback" ||
    systemStatus?.database_mode?.includes("fallback");

  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-40 px-4 sm:px-6 py-3.5 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        {/* Brand Icon: Coral to Cerulean Gradient */}
        <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-coral-500 via-coral-400 to-cerulean-500 flex items-center justify-center font-bold text-white shadow-lg shadow-coral-500/25">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="font-bold text-offwhite text-base sm:text-lg leading-tight tracking-tight">
              Multimodal Resume Intelligence
            </h1>
            <span className="hidden sm:inline-flex text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-coral-950/80 text-coral-300 border border-coral-800/80">
              Studio v1.0
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Automated Video & Resume Screening with Cross-Modal Claim Verification
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-3">
        {/* Storage status pill */}
        <div className="flex items-center space-x-2 text-xs px-3 py-1.5 rounded-xl border border-slate-800 bg-slate-950">
          <span
            className={`h-2 w-2 rounded-full ${
              isFallback ? "bg-coral-400 animate-pulse" : "bg-cerulean-400"
            }`}
          />
          <span className="text-slate-300 text-[11px] sm:text-xs">
            {isFallback ? "Offline Fallback Store" : "MongoDB Atlas Connected"}
          </span>
        </div>

        {/* Ingest Candidate CTA */}
        {onOpenIngest && (
          <button
            onClick={onOpenIngest}
            className="text-xs bg-coral-500 hover:bg-coral-600 text-white font-medium px-3.5 py-1.5 rounded-xl transition-all shadow-md shadow-coral-500/30 flex items-center space-x-1.5"
          >
            <span>+ Ingest Candidate</span>
          </button>
        )}
      </div>
    </header>
  );
};

export default Navbar;
