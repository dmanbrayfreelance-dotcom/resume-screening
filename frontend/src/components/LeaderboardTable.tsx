import React, { useState } from "react";
import { LeaderboardItem } from "../api/client";
import { Search, AlertTriangle, CheckCircle } from "lucide-react";

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
        return "bg-coral-950/80 text-coral-300 border-coral-800/80";
      case "hire":
        return "bg-cerulean-950/80 text-cerulean-300 border-cerulean-800/80";
      case "further review":
        return "bg-amber-950/70 text-amber-300 border-amber-800/80";
      default:
        return "bg-slate-800 text-slate-400 border-slate-700";
    }
  };

  const getRankBadge = (rank: number) => {
    if (rank === 1) return "bg-coral-500/20 text-coral-300 border-coral-500/40";
    if (rank === 2) return "bg-cerulean-500/20 text-cerulean-300 border-cerulean-500/40";
    if (rank === 3) return "bg-slate-300/20 text-offwhite border-slate-400/40";
    return "bg-slate-800/50 text-slate-400 border-slate-800";
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-sm">
      {/* Controls Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 text-xs">
        {/* Search */}
        <div className="relative flex-1 max-w-sm">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search candidates by name, email, or ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-offwhite placeholder:text-slate-500 focus:outline-none focus:border-coral-500"
          />
        </div>

        {/* Filters and Sorting */}
        <div className="flex items-center space-x-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-300 focus:outline-none focus:border-coral-500"
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
            className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-300 focus:outline-none focus:border-coral-500"
          >
            <option value="score">Sort by Overall Score</option>
            <option value="coverage">Sort by Skill Coverage %</option>
            <option value="credibility">Sort by Credibility Index</option>
          </select>
        </div>
      </div>

      {/* Table */}
      {filteredItems.length === 0 ? (
        <div className="text-center py-12 text-slate-500 text-xs bg-slate-950/40 rounded-xl border border-slate-800/60">
          No candidates matching filter. Use the Ingest panel to screen candidates.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-800/80">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4 w-12 text-center">Rank</th>
                <th className="py-3 px-4">Candidate</th>
                <th className="py-3 px-4">Overall Fit</th>
                <th className="py-3 px-4">Skill Coverage</th>
                <th className="py-3 px-4">Speech & Delivery</th>
                <th className="py-3 px-4">Claim Credibility</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 bg-slate-900/60">
              {filteredItems.map((item) => (
                <tr
                  key={item.candidate_id}
                  onClick={() => onSelectCandidate(item.candidate_id)}
                  className="hover:bg-slate-800/40 transition cursor-pointer group"
                >
                  {/* Rank */}
                  <td className="py-3.5 px-4 text-center">
                    <span
                      className={`inline-flex items-center justify-center w-6 h-6 rounded-full font-bold text-[11px] border ${getRankBadge(
                        item.rank
                      )}`}
                    >
                      {item.rank}
                    </span>
                  </td>

                  {/* Candidate Name & Email */}
                  <td className="py-3.5 px-4">
                    <div className="font-semibold text-offwhite group-hover:text-coral-400 transition">
                      {item.candidate_name}
                    </div>
                    <div className="text-[11px] text-slate-400">{item.email || item.candidate_id}</div>
                  </td>

                  {/* Overall Fit Score */}
                  <td className="py-3.5 px-4">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-offwhite text-sm">{item.overall_fit_score}%</span>
                      <span
                        className={`text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full border ${getBadgeStyle(
                          item.recommendation
                        )}`}
                      >
                        {item.recommendation}
                      </span>
                    </div>
                  </td>

                  {/* Skill Coverage % */}
                  <td className="py-3.5 px-4">
                    <div className="w-28 space-y-1">
                      <div className="flex justify-between text-[11px]">
                        <span className="text-slate-300 font-semibold">{item.skill_coverage_pct}%</span>
                        <span className="text-slate-500">{item.matched_skills.length} matched</span>
                      </div>
                      <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                        <div
                          className="bg-coral-500 h-full rounded-full"
                          style={{ width: `${Math.min(100, item.skill_coverage_pct)}%` }}
                        />
                      </div>
                    </div>
                  </td>

                  {/* Speaking Pace & Sentiment */}
                  <td className="py-3.5 px-4">
                    <div className="flex items-center space-x-2">
                      <span className="text-[11px] capitalize text-slate-300 font-medium">
                        {item.speaking_pace || "optimal"} pace
                      </span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-cerulean-300 border border-slate-700">
                        {item.sentiment_label || "POSITIVE"}
                      </span>
                    </div>
                  </td>

                  {/* Claim Credibility */}
                  <td className="py-3.5 px-4">
                    <div className="flex items-center space-x-1.5">
                      <span
                        className={`font-semibold ${
                          item.credibility_score >= 85
                            ? "text-cerulean-400"
                            : item.credibility_score >= 70
                            ? "text-coral-400"
                            : "text-amber-400"
                        }`}
                      >
                        {item.credibility_score}%
                      </span>
                      {item.discrepancies_count > 0 ? (
                        <span className="flex items-center text-[10px] text-coral-400 font-medium bg-coral-950/60 px-1.5 py-0.5 rounded border border-coral-800/80">
                          <AlertTriangle className="w-3 h-3 mr-1" />
                          {item.discrepancies_count} alert
                        </span>
                      ) : (
                        <CheckCircle className="w-3.5 h-3.5 text-cerulean-400" />
                      )}
                    </div>
                  </td>

                  {/* Actions */}
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectCandidate(item.candidate_id);
                      }}
                      className="text-xs font-semibold text-cerulean-400 hover:text-cerulean-300 bg-cerulean-950/40 hover:bg-cerulean-950/80 px-3 py-1.5 rounded-lg border border-cerulean-800/50 transition"
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
