import React, { useState } from "react";
import { FairnessAuditReport, downloadExport } from "../api/client";
import { ShieldCheck, AlertTriangle, Download, TrendingUp } from "lucide-react";

interface FairnessPanelProps {
  jobId: string;
  auditReport: FairnessAuditReport | null;
}

export const FairnessPanel: React.FC<FairnessPanelProps> = ({ jobId, auditReport }) => {
  const [simulatedThreshold, setSimulatedThreshold] = useState<number>(75);

  if (!auditReport) {
    return (
      <div className="p-12 text-center text-slate-400 text-xs bg-[#F7F7F7] border border-dashed border-slate-200 rounded-2xl">
        <ShieldCheck className="w-10 h-10 text-slate-300 mx-auto mb-3" />
        <div className="font-semibold text-slate-500 mb-1">Loading fairness diagnostics…</div>
        <div>Algorithmic audit data will appear after candidates are screened.</div>
      </div>
    );
  }

  const selectedSensitivity =
    auditReport.threshold_sensitivities?.find((s) => s.threshold_score === simulatedThreshold) || {
      threshold_score: simulatedThreshold, selected_count: 0, selection_rate_pct: 0,
    };

  return (
    <div className="space-y-5">
      {/* Governance Banner */}
      <div className="bg-gradient-to-br from-[#67A9CF]/5 to-white border border-[#67A9CF]/20 p-6 rounded-2xl space-y-4 shadow-sm">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 bg-[#67A9CF]/10 rounded-xl">
            <ShieldCheck className="w-5 h-5 text-[#67A9CF]" />
          </div>
          <div>
            <div className="font-bold text-slate-900 text-sm">Algorithmic Fairness &amp; Non-Adverse Action Guardrails</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Advisory-only compliance framework · EU AI Act + EEOC aligned</div>
          </div>
        </div>
        <p className="text-xs text-slate-600 leading-relaxed">
          All scores are <strong className="text-slate-900">advisory only</strong>. Automated rejection transitions are strictly
          prohibited. Evaluation views redact PII and neutralize gender/age proxies.
        </p>
        <div className="flex flex-wrap gap-2">
          {[
            { label: "✓ Auto-Rejection Prohibited", color: "cerulean" },
            { label: "✓ PII Scrubbed Views", color: "coral" },
            { label: "✓ Four-Fifths Drift Monitored", color: "slate" },
          ].map(({ label, color }) => (
            <span
              key={label}
              className={`text-[11px] px-3 py-1 rounded-full font-semibold border ${
                color === "cerulean"
                  ? "bg-[#67A9CF]/10 text-[#3f7fa0] border-[#67A9CF]/30"
                  : color === "coral"
                  ? "bg-[#EF8A62]/10 text-[#c8603a] border-[#EF8A62]/30"
                  : "bg-slate-100 text-slate-600 border-slate-200"
              }`}
            >
              {label}
            </span>
          ))}
        </div>
      </div>

      {/* Warnings */}
      {auditReport.audit_warnings && auditReport.audit_warnings.length > 0 && (
        <div className="bg-[#EF8A62]/5 border border-[#EF8A62]/20 p-5 rounded-2xl space-y-3 animate-fade-in">
          <div className="flex items-center space-x-2 text-[#c8603a] font-bold text-sm">
            <AlertTriangle className="w-4 h-4 text-[#EF8A62]" />
            <span>Calibration &amp; Drift Advisory Notices</span>
          </div>
          <ul className="space-y-1.5 text-xs text-slate-700 pl-5 list-disc">
            {auditReport.audit_warnings.map((w, idx) => <li key={idx}>{w}</li>)}
          </ul>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {[
          { label: "Sample Size", value: auditReport.sample_size, sub: "Evaluated Pool", accent: "slate" },
          { label: "Mean Score", value: `${auditReport.mean_score}%`, sub: "Baseline 65–85%", accent: "coral" },
          { label: "Median Score", value: `${auditReport.median_score}%`, sub: "P50 Centroid", accent: "cerulean" },
          { label: "Std Deviation", value: auditReport.std_dev, sub: "Variance Spread", accent: "coral" },
          {
            label: "Calibration",
            value: auditReport.calibration_drift_flag ? "DRIFT" : "STABLE",
            sub: "Model Stability",
            accent: auditReport.calibration_drift_flag ? "coral" : "cerulean",
          },
        ].map(({ label, value, sub, accent }) => (
          <div key={label} className="relative bg-white border border-slate-200/80 p-4 rounded-xl text-center shadow-sm card-hover overflow-hidden">
            <div className={`absolute top-0 left-0 right-0 h-0.5 ${
              accent === "coral" ? "bg-gradient-to-r from-[#EF8A62] to-[#f6b89f]"
              : accent === "cerulean" ? "bg-gradient-to-r from-[#67A9CF] to-[#9ecbe3]"
              : "bg-slate-200"
            }`} />
            <div className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold mt-1">{label}</div>
            <div className={`text-xl font-black mt-2 ${
              accent === "coral" ? "text-[#EF8A62]" : accent === "cerulean" ? "text-[#67A9CF]" : "text-slate-900"
            }`}>{value}</div>
            <div className="text-[10px] text-slate-400 mt-1">{sub}</div>
          </div>
        ))}
      </div>

      {/* Threshold Simulator */}
      <div className="bg-white border border-slate-200/80 p-6 rounded-2xl space-y-5 shadow-sm">
        <div className="flex justify-between items-start">
          <div>
            <h4 className="font-bold text-slate-900 text-sm flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-[#EF8A62]" />
              <span>Threshold Sensitivity Simulator</span>
            </h4>
            <p className="text-xs text-slate-400 mt-0.5">
              Simulate candidate selection volume across cutoff thresholds — advisory only.
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => downloadExport(jobId, "csv")}
              className="inline-flex items-center space-x-1.5 text-[11px] font-semibold bg-[#F7F7F7] hover:bg-slate-100 text-slate-700 px-3 py-2 rounded-xl border border-slate-200 hover:border-[#EF8A62]/30 transition"
            >
              <Download className="w-3 h-3 text-[#EF8A62]" />
              <span>CSV</span>
            </button>
            <button
              onClick={() => downloadExport(jobId, "json")}
              className="inline-flex items-center space-x-1.5 text-[11px] font-semibold bg-[#F7F7F7] hover:bg-slate-100 text-slate-700 px-3 py-2 rounded-xl border border-slate-200 hover:border-[#67A9CF]/30 transition"
            >
              <Download className="w-3 h-3 text-[#67A9CF]" />
              <span>JSON</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-5 gap-2">
          {[60, 70, 75, 80, 85].map((thresh) => {
            const sens = auditReport.threshold_sensitivities?.find((s) => s.threshold_score === thresh);
            const active = simulatedThreshold === thresh;
            return (
              <button
                key={thresh}
                onClick={() => setSimulatedThreshold(thresh)}
                className={`p-3.5 rounded-xl border text-center transition-all duration-150 ${
                  active
                    ? "bg-gradient-to-b from-[#EF8A62]/10 to-[#EF8A62]/5 border-[#EF8A62]/50 shadow-sm"
                    : "bg-[#F7F7F7] border-slate-200 hover:border-slate-300 hover:bg-white"
                }`}
              >
                <div className={`text-[9px] uppercase font-bold tracking-widest ${active ? "text-[#EF8A62]" : "text-slate-400"}`}>
                  ≥ {thresh}%
                </div>
                <div className={`text-lg font-black mt-1 ${active ? "text-[#EF8A62]" : "text-slate-900"}`}>
                  {sens?.selection_rate_pct || 0}%
                </div>
                <div className="text-[10px] text-slate-400">{sens?.selected_count || 0} candidates</div>
              </button>
            );
          })}
        </div>

        <div className="p-4 bg-gradient-to-r from-[#EF8A62]/5 to-transparent border border-[#EF8A62]/20 rounded-xl flex items-center justify-between text-xs">
          <span className="text-slate-700">
            At ≥ {selectedSensitivity.threshold_score}%:{" "}
            <strong className="text-[#EF8A62]">{selectedSensitivity.selected_count} candidates</strong>
            {" "}({selectedSensitivity.selection_rate_pct}% of pool)
          </span>
          <span className="text-[11px] text-slate-400 font-medium">Advisory simulation</span>
        </div>
      </div>
    </div>
  );
};
