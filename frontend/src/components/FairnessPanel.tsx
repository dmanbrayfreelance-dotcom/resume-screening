import React, { useState } from "react";
import { FairnessAuditReport, downloadExport } from "../api/client";
import { ShieldCheck, AlertTriangle, Download } from "lucide-react";

interface FairnessPanelProps {
  jobId: string;
  auditReport: FairnessAuditReport | null;
}

export const FairnessPanel: React.FC<FairnessPanelProps> = ({ jobId, auditReport }) => {
  const [simulatedThreshold, setSimulatedThreshold] = useState<number>(75);

  if (!auditReport) {
    return (
      <div className="p-8 text-center text-slate-500 text-xs bg-slate-900 border border-slate-800 rounded-2xl">
        Loading algorithmic fairness audit diagnostics...
      </div>
    );
  }

  const selectedSensitivity =
    auditReport.threshold_sensitivities?.find((s) => s.threshold_score === simulatedThreshold) || {
      threshold_score: simulatedThreshold,
      selected_count: 0,
      selection_rate_pct: 0,
    };

  return (
    <div className="space-y-6">
      {/* Governance & Advisory Notice Banner */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-3">
        <div className="flex items-center space-x-2 text-cerulean-400 font-semibold text-sm">
          <ShieldCheck className="w-5 h-5 text-cerulean-400" />
          <span>Algorithmic Fairness & Non-Adverse Action Guardrails</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          In strict compliance with modern AI hiring regulations, all scores are{" "}
          <strong className="text-offwhite">advisory only</strong>. Automated rejection transitions are strictly
          prohibited. All evaluation views redact personally identifiable attributes (name, email, phone, location)
          and neutralize gender and age proxies.
        </p>

        <div className="flex flex-wrap gap-2 pt-2">
          <span className="text-[11px] px-2.5 py-1 rounded-full bg-cerulean-950/60 text-cerulean-300 border border-cerulean-800/60">
            ✓ Auto-Rejection Prohibited
          </span>
          <span className="text-[11px] px-2.5 py-1 rounded-full bg-coral-950/60 text-coral-300 border border-coral-800/60">
            ✓ PII Scrubbed Evaluation Views
          </span>
          <span className="text-[11px] px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
            ✓ Four-Fifths Drift Monitored
          </span>
        </div>
      </div>

      {/* Warnings & Alerts */}
      {auditReport.audit_warnings && auditReport.audit_warnings.length > 0 && (
        <div className="bg-coral-950/40 border border-coral-800/80 p-4 rounded-2xl space-y-2">
          <div className="flex items-center space-x-2 text-coral-400 font-semibold text-xs">
            <AlertTriangle className="w-4 h-4" />
            <span>Calibration & Drift Advisory Notices</span>
          </div>
          <ul className="space-y-1 text-xs text-slate-300 pl-5 list-disc">
            {auditReport.audit_warnings.map((w, idx) => (
              <li key={idx}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Statistical Spread Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-center">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider">Candidate Sample</div>
          <div className="text-xl font-bold text-offwhite mt-1">{auditReport.sample_size}</div>
          <div className="text-[10px] text-slate-500 mt-0.5">Evaluated Pool</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-center">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider">Mean Score</div>
          <div className="text-xl font-bold text-coral-400 mt-1">{auditReport.mean_score}%</div>
          <div className="text-[10px] text-slate-500 mt-0.5">Baseline: 65 - 85%</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-center">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider">Median Score</div>
          <div className="text-xl font-bold text-cerulean-400 mt-1">{auditReport.median_score}%</div>
          <div className="text-[10px] text-slate-500 mt-0.5">P50 Centroid</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-center">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider">Std Deviation</div>
          <div className="text-xl font-bold text-coral-300 mt-1">{auditReport.std_dev}</div>
          <div className="text-[10px] text-slate-500 mt-0.5">Variance Spread</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-center">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider">Calibration Drift</div>
          <div
            className={`text-xl font-bold mt-1 ${
              auditReport.calibration_drift_flag ? "text-coral-400" : "text-cerulean-400"
            }`}
          >
            {auditReport.calibration_drift_flag ? "DRIFT" : "CALIBRATED"}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Model Stability</div>
        </div>
      </div>

      {/* Threshold Sensitivity Simulator */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h4 className="font-semibold text-offwhite text-sm">Threshold Sensitivity Simulator</h4>
            <p className="text-xs text-slate-400 mt-0.5">
              Simulate candidate selection volume across cutoff thresholds without enforcing hard rejections.
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => downloadExport(jobId, "csv")}
              className="flex items-center space-x-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-2 rounded-xl border border-slate-700 transition"
            >
              <Download className="w-3.5 h-3.5 text-coral-400" />
              <span>Export CSV</span>
            </button>
            <button
              onClick={() => downloadExport(jobId, "json")}
              className="flex items-center space-x-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-2 rounded-xl border border-slate-700 transition"
            >
              <Download className="w-3.5 h-3.5 text-cerulean-400" />
              <span>Export JSON</span>
            </button>
          </div>
        </div>

        {/* Buttons for simulated threshold */}
        <div className="grid grid-cols-5 gap-2">
          {[60, 70, 75, 80, 85].map((thresh) => {
            const sens = auditReport.threshold_sensitivities?.find((s) => s.threshold_score === thresh);
            const active = simulatedThreshold === thresh;
            return (
              <button
                key={thresh}
                onClick={() => setSimulatedThreshold(thresh)}
                className={`p-3 rounded-xl border text-center transition ${
                  active
                    ? "bg-coral-950/80 border-coral-500 text-coral-200 shadow-lg shadow-coral-500/10"
                    : "bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700"
                }`}
              >
                <div className="text-[10px] uppercase font-bold text-slate-400">Cutoff {thresh}%</div>
                <div className="text-base font-bold text-offwhite mt-0.5">{sens?.selection_rate_pct || 0}%</div>
                <div className="text-[10px] text-slate-500">{sens?.selected_count || 0} candidates</div>
              </button>
            );
          })}
        </div>

        <div className="p-4 bg-slate-950/70 border border-slate-800/80 rounded-xl flex items-center justify-between text-xs">
          <span className="text-slate-300">
            Selected at &gt;= {selectedSensitivity.threshold_score}%:{" "}
            <strong className="text-coral-400">{selectedSensitivity.selected_count} candidates</strong> (
            {selectedSensitivity.selection_rate_pct}% of total pool)
          </span>
          <span className="text-[11px] text-slate-400">Advisory cutoff simulation</span>
        </div>
      </div>
    </div>
  );
};
