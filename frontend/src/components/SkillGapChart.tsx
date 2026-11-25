import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
} from "recharts";
import { CandidateEvaluation } from "../api/client";

interface SkillGapChartProps {
  evaluation: CandidateEvaluation;
}

export const SkillGapChart: React.FC<SkillGapChartProps> = ({ evaluation }) => {
  const components = evaluation.component_breakdown || {};

  const radarData = [
    {
      subject: "Skills",
      score: components.skill_match?.raw_score || 0,
      fullMark: 100,
    },
    {
      subject: "Experience",
      score: components.experience_match?.raw_score || 0,
      fullMark: 100,
    },
    {
      subject: "Delivery",
      score: components.multimodal_presentation?.raw_score || 0,
      fullMark: 100,
    },
    {
      subject: "Tone",
      score: components.sentiment_engagement?.raw_score || 0,
      fullMark: 100,
    },
    {
      subject: "Credibility",
      score: components.claim_credibility?.raw_score || 0,
      fullMark: 100,
    },
  ];

  const skillGap = evaluation.skill_gap || {
    matched_skills: [],
    missing_required_skills: [],
    missing_preferred_skills: [],
    coverage_pct: 0,
  };

  const barData = [
    { name: "Matched", count: skillGap.matched_skills.length, color: "#67A9CF" },
    { name: "Missing Req", count: skillGap.missing_required_skills.length, color: "#EF8A62" },
    { name: "Missing Pref", count: skillGap.missing_preferred_skills.length, color: "#f6b89f" },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Radar Chart: Multi-Component Competency Profile */}
      <div className="bg-slate-950/70 border border-slate-800 p-4 rounded-xl flex flex-col items-center">
        <div className="text-xs font-semibold text-slate-300 mb-2">Multimodal Competency Profile</div>
        <div className="h-44 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
              <PolarGrid stroke="#1b2943" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: "#F7F7F7", fontSize: 11 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "#67A9CF", fontSize: 9 }} />
              <Radar
                name="Score"
                dataKey="score"
                stroke="#EF8A62"
                fill="#EF8A62"
                fillOpacity={0.45}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0e1726",
                  borderColor: "#1b2943",
                  fontSize: "11px",
                  borderRadius: "8px",
                  color: "#F7F7F7",
                }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bar Chart: Skill Match Breakdown */}
      <div className="bg-slate-950/70 border border-slate-800 p-4 rounded-xl flex flex-col justify-between">
        <div>
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs font-semibold text-slate-300">Skill Alignment Ratio</span>
            <span className="text-xs font-bold text-cerulean-400">{skillGap.coverage_pct}% Coverage</span>
          </div>
          <p className="text-[11px] text-slate-400">
            Categorization of candidate taxonomy matches against target JD requirements.
          </p>
        </div>

        <div className="h-32 w-full mt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
              <XAxis type="number" hide />
              <YAxis
                type="category"
                dataKey="name"
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#F7F7F7", fontSize: 11 }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0e1726",
                  borderColor: "#1b2943",
                  fontSize: "11px",
                  borderRadius: "8px",
                  color: "#F7F7F7",
                }}
              />
              <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                {barData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Matched skills pill row preview */}
        <div className="flex flex-wrap gap-1 pt-2 border-t border-slate-800/80">
          {skillGap.matched_skills.slice(0, 4).map((s, idx) => (
            <span
              key={idx}
              className="text-[10px] px-2 py-0.5 rounded bg-cerulean-950/60 text-cerulean-300 border border-cerulean-800/60"
            >
              ✓ {s}
            </span>
          ))}
          {skillGap.missing_required_skills.slice(0, 2).map((s, idx) => (
            <span
              key={idx}
              className="text-[10px] px-2 py-0.5 rounded bg-coral-950/60 text-coral-300 border border-coral-800/60"
            >
              ✕ {s}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};
