import React, { useState } from "react";
import { LeaderboardItem } from "../api/client";
import { Search, AlertTriangle, CheckCircle, ChevronRight } from "lucide-react";

interface LeaderboardTableProps {
  items: LeaderboardItem[];
  onSelectCandidate: (candidateId: string) => void;
}

export const LeaderboardTable: React.FC<LeaderboardTableProps> = ({ items, onSelectCandidate }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState<"score" | "coverage" | "credibility">("score");

  const filteredItems = items
    .filter((item) => {
      const matchSearch =
        item.candidate_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.candidate_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (item.email && item.email.toLowerCase().includes(searchTerm.toLowerCase()));
      const matchStatus =
        statusFilter === "all" ||
        item.recommendation.toLowerCase().replace(" ", "_") === statusFilter.toLowerCase();
      return matchSearch && matchStatus;
    })
    .sort((a, b) => {
      if (sortBy === "coverage") return b.skill_coverage_pct - a.skill_coverage_pct;
      if (sortBy === "credibility") return b.credibility_score - a.credibility_score;
      return b.overall_fit_score - a.overall_fit_score;
    });

  const getBadgeStyle = (rec: string) => {
    switch (rec.toLowerCase()) {
      case "strong hire":
        return "bg-gradient-to-r from-[#EF8A62]/15 to-[#EF8A62]/5 text-[#c8603a] border-[#EF8A62]/40";
      case "hire":
        return "bg-gradient-to-r from-[#67A9CF]/15 to-[#67A9CF]/5 text-[#3f7fa0] border-[#67A9CF]/40";
      case "further review":
        return "bg-amber-50 text-amber-700 border-amber-300/60";
      default:
        return "bg-slate-100 text-slate-500 border-slate-200";
    }
  };

  const getRankDisplay = (rank: number) => {
    if (rank === 1) return { style: "bg-gradient-to-br from-[#EF8A62] to-[#e06535] text-white shadow-md shadow-[#EF8A62]/30", label: "🥇" };
    if (rank === 2) return { style: "bg-gradient-to-br from-[#67A9CF] to-[#4a8db5] text-white shadow-md shadow-[#67A9CF]/30", label: "🥈" };
    if (rank === 3) return { style: "bg-gradient-to-br from-slate-400 to-slate-500 text-white shadow-md shadow-slate-400/30", label: "🥉" };
    return { style: "bg-slate-100 text-slate-600 border border-slate-200", label: `${rank}` };
  };

  return (
    <div className="space-y-4">
      {/* Controls Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Search */}
        <div className="relative flex-1 max-w-sm">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search candidates…"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full text-xs bg-white border border-slate-200 rounded-xl pl-9 pr-4 py-2.5 text-slate-800 placeholder:text-slate-400 hover:border-slate-300 transition"
          />
        </div>

        <div className="flex items-center space-x-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs bg-white border border-slate-200 rounded-xl px-3 py-2.5 text-slate-700 font-medium hover:border-slate-300 cursor-pointer"
          >
            <option value="all">All Recommendations</option>
            <option value="strong_hire">Strong Hire</option>
            <option value="hire">Hire</option>
            <option value="further_review">Further Review</option>
            <option value="hold_/_revisit">Hold / Revisit</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="text-xs bg-white border border-slate-200 rounded-xl px-3 py-2.5 text-slate-700 font-medium hover:border-slate-300 cursor-pointer"
          >
            <option value="score">Sort: Overall Score</option>
            <option value="coverage">Sort: Skill Coverage</option>
            <option value="credibility">Sort: Credibility</option>
          </select>
        </div>
      </div>

      {/* Table */}
      {filteredItems.length === 0 ? (
        <div className="text-center py-16 text-slate-400 text-xs bg-[#F7F7F7] rounded-2xl border border-slate-200 border-dashed">
          <div className="text-3xl mb-3">🎯</div>
          <div className="font-semibold text-slate-500 mb-1">No candidates yet</div>
          <div>Use the Ingest panel to screen candidates for this role.</div>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-slate-200/80 shadow-sm">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-gradient-to-r from-[#F7F7F7] to-slate-50 border-b border-slate-200">
                <th className="py-3.5 px-4 w-16 text-center text-[10px] font-bold text-slate-400 uppercase tracking-widest">Rank</th>
                <th className="py-3.5 px-4 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Candidate</th>
                <th className="py-3.5 px-4 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Overall Fit</th>
                <th className="py-3.5 px-4 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Skill Coverage</th>
                <th className="py-3.5 px-4 text-[10px] font-bold text-slate-400 uppercase tracking-widest hidden md:table-cell">Speech &amp; Tone</th>
                <th className="py-3.5 px-4 text-[10px] font-bold text-slate-400 uppercase tracking-widest hidden md:table-cell">Credibility</th>
                <th className="py-3.5 px-4 text-right text-[10px] font-bold text-slate-400 uppercase tracking-widest">Action</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-100">
              {filteredItems.map((item) => {
                const rank = getRankDisplay(item.rank);
                return (
                  <tr
                    key={item.candidate_id}
                    onClick={() => onSelectCandidate(item.candidate_id)}
                    className="group hover:bg-gradient-to-r hover:from-[#EF8A62]/3 hover:to-transparent cursor-pointer transition-all duration-150"
                  >
                    {/* Rank */}
                    <td className="py-4 px-4 text-center">
                      <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-[11px] font-black ${rank.style}`}>
                        {rank.label}
                      </span>
                    </td>

                    {/* Candidate */}
                    <td className="py-4 px-4">
                      <div className="font-bold text-slate-900 group-hover:text-[#EF8A62] transition-colors">
                        {item.candidate_name}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-0.5">{item.email || item.candidate_id}</div>
                    </td>

                    {/* Overall Fit */}
                    <td className="py-4 px-4">
                      <div className="flex items-center space-x-2.5">
                        <span className="font-black text-slate-900 text-sm">{item.overall_fit_score}%</span>
                        <span className={`text-[9px] uppercase font-bold px-2 py-0.5 rounded-full border tracking-wider ${getBadgeStyle(item.recommendation)}`}>
                          {item.recommendation}
                        </span>
                      </div>
                    </td>

                    {/* Skill Coverage */}
                    <td className="py-4 px-4">
                      <div className="w-32 space-y-1.5">
                        <div className="flex justify-between text-[11px]">
                          <span className="font-bold text-slate-800">{item.skill_coverage_pct}%</span>
                          <span className="text-slate-400">{item.matched_skills.length} matched</span>
                        </div>
                        <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                          <div
                            className="progress-coral h-full rounded-full transition-all duration-500"
                            style={{ width: `${Math.min(100, item.skill_coverage_pct)}%` }}
                          />
                        </div>
                      </div>
                    </td>

                    {/* Speech & Tone */}
                    <td className="py-4 px-4 hidden md:table-cell">
                      <div className="flex items-center space-x-2">
                        <span className="text-[11px] capitalize text-slate-700 font-semibold">{item.speaking_pace || "optimal"}</span>
                        <span className="text-[9px] px-2 py-0.5 rounded-full bg-[#67A9CF]/10 text-[#67A9CF] border border-[#67A9CF]/30 font-bold uppercase tracking-wider">
                          {item.sentiment_label || "POSITIVE"}
                        </span>
                      </div>
                    </td>

                    {/* Credibility */}
                    <td className="py-4 px-4 hidden md:table-cell">
                      <div className="flex items-center space-x-1.5">
                        <span className={`font-bold ${
                          item.credibility_score >= 85 ? "text-[#67A9CF]" :
                          item.credibility_score >= 70 ? "text-[#EF8A62]" : "text-amber-500"
                        }`}>
                          {item.credibility_score}%
                        </span>
                        {item.discrepancies_count > 0 ? (
                          <span className="flex items-center text-[9px] text-[#c8603a] font-bold bg-[#EF8A62]/10 px-1.5 py-0.5 rounded-full border border-[#EF8A62]/30">
                            <AlertTriangle className="w-2.5 h-2.5 mr-0.5" />
                            {item.discrepancies_count}
                          </span>
                        ) : (
                          <CheckCircle className="w-3.5 h-3.5 text-[#67A9CF]" />
                        )}
                      </div>
                    </td>

                    {/* Action */}
                    <td className="py-4 px-4 text-right">
                      <button
                        onClick={(e) => { e.stopPropagation(); onSelectCandidate(item.candidate_id); }}
                        className="inline-flex items-center space-x-1 text-[11px] font-bold text-[#67A9CF] hover:text-white bg-[#67A9CF]/10 hover:bg-[#67A9CF] px-3 py-1.5 rounded-lg border border-[#67A9CF]/30 hover:border-[#67A9CF] transition-all duration-150 group/btn"
                      >
                        <span>Inspect</span>
                        <ChevronRight className="w-3 h-3 group-hover/btn:translate-x-0.5 transition-transform" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
