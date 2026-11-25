import csv
import io
import json
from typing import Any, Dict, List, Optional
from backend.app.services.ranking.fairness_audit import FairnessBatchAuditReport


class ReportingExporterService:
    """
    Generates structured JSON and CSV export payloads for ranked candidate shortlists,
    multi-component evaluation breakdowns, skill-gap reports, and fairness audit records.
    """

    def export_shortlist_csv(self, ranked_candidates: List[Dict[str, Any]]) -> str:
        """
        Exports ranked candidate shortlist to CSV format.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        headers = [
            "Rank",
            "Candidate ID",
            "Candidate Name",
            "Overall Fit Score",
            "Advisory Recommendation",
            "Skill Coverage %",
            "Matched Skills",
            "Missing Required Skills",
            "Speaking Pace",
            "Sentiment Label",
            "Claim Credibility Score",
        ]
        writer.writerow(headers)

        for idx, item in enumerate(ranked_candidates, start=1):
            contact = item.get("contact_info", {})
            eval_score = item.get("hybrid_evaluation", {}) or {}
            multimodal = item.get("multimodal_analysis", {}) or {}
            skill_gap = eval_score.get("skill_gap", {}) or {}

            matched_skills_str = "; ".join(skill_gap.get("matched_skills", []))
            missing_skills_str = "; ".join(skill_gap.get("missing_required_skills", []))

            writer.writerow([
                idx,
                item.get("candidate_id", ""),
                contact.get("name", "Anonymized Candidate"),
                eval_score.get("overall_score", item.get("overall_fit_score", 0.0)),
                eval_score.get("recommendation", "Review"),
                skill_gap.get("coverage_pct", 0.0),
                matched_skills_str,
                missing_skills_str,
                multimodal.get("speaking_pace", "optimal"),
                multimodal.get("sentiment_label", "POSITIVE"),
                eval_score.get("credibility_score", 90.0),
            ])

        return output.getvalue()

    def export_shortlist_json(
        self, ranked_candidates: List[Dict[str, Any]], indent: int = 2
    ) -> str:
        """Exports ranked candidate shortlist to structured JSON."""
        return json.dumps(ranked_candidates, indent=indent, default=str)

    def export_evaluation_breakdown_csv(self, evaluations: List[Dict[str, Any]]) -> str:
        """
        Exports detailed score breakdown per candidate into CSV.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        headers = [
            "Candidate ID",
            "Job ID",
            "Overall Score",
            "Skill Coverage Score",
            "Experience Semantic Score",
            "Presentation Score",
            "Sentiment Polarity Score",
            "Claim Credibility Score",
            "Recommendation",
            "Is Advisory Only",
            "Summary Notes",
        ]
        writer.writerow(headers)

        for ev in evaluations:
            comps = ev.get("components", {})
            def _get_raw(comp_key: str) -> float:
                c = comps.get(comp_key)
                if c is None:
                    return 0.0
                if isinstance(c, dict):
                    return float(c.get("raw_score", 0.0))
                if hasattr(c, "raw_score"):
                    return float(c.raw_score)
                return 0.0

            writer.writerow([
                ev.get("candidate_id", ""),
                ev.get("job_id", ""),
                ev.get("overall_score", 0.0),
                _get_raw("skill_match"),
                _get_raw("experience_match"),
                _get_raw("multimodal_presentation"),
                _get_raw("sentiment_engagement"),
                _get_raw("claim_credibility"),
                ev.get("recommendation", "Review"),
                ev.get("is_advisory_only", True),
                ev.get("recruiter_executive_summary", ""),
            ])

        return output.getvalue()

    def export_evaluation_breakdown_json(
        self, evaluations: List[Dict[str, Any]], indent: int = 2
    ) -> str:
        """Exports detailed evaluations to JSON."""
        return json.dumps(evaluations, indent=indent, default=str)

    def export_fairness_audit_csv(self, audit_report: FairnessBatchAuditReport) -> str:
        """
        Exports statistical calibration and fairness distribution audit metrics into CSV.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["Fairness & Calibration Metric", "Value", "Status / Notes"])
        writer.writerow(["Sample Size (Candidates)", audit_report.sample_size, "Audit Batch"])
        writer.writerow(["Mean Score", f"{audit_report.mean_score:.1f}", "Normal Range 65.0 - 85.0"])
        writer.writerow(["Median Score", f"{audit_report.median_score:.1f}", "P50 Midpoint"])
        writer.writerow(["Standard Deviation", f"{audit_report.std_dev:.1f}", "Dispersion"])
        writer.writerow(["Min Score", f"{audit_report.min_score:.1f}", "Lower Bound"])
        writer.writerow(["Max Score", f"{audit_report.max_score:.1f}", "Upper Bound"])
        writer.writerow(["Score Spread", f"{audit_report.score_spread:.1f}", "Range Span"])
        writer.writerow([
            "Calibration Drift Flag",
            audit_report.calibration_drift_flag,
            "Flagged if mean deviates >15 points from standard baseline",
        ])
        writer.writerow([
            "Advisory Compliance Passed",
            audit_report.advisory_compliance_passed,
            "Guarantees no automated adverse action",
        ])

        writer.writerow([])
        writer.writerow(["Threshold", "Candidate Count Selected", "Selection Rate %"])
        for sens in audit_report.threshold_sensitivities:
            writer.writerow([
                f">= {sens.threshold_score}",
                sens.selected_count,
                f"{sens.selection_rate_pct:.1f}%",
            ])

        if audit_report.audit_warnings:
            writer.writerow([])
            writer.writerow(["Audit Warning Notes", "; ".join(audit_report.audit_warnings), "Action Required"])

        return output.getvalue()

    def export_fairness_audit_json(
        self, audit_report: FairnessBatchAuditReport, indent: int = 2
    ) -> str:
        """Exports fairness batch audit report to JSON."""
        data = audit_report.model_dump()
        return json.dumps(data, indent=indent, default=str)


# Global singleton reporting exporter instance
reporting_exporter = ReportingExporterService()
