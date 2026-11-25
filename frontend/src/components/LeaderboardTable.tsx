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
        return "bg-coral-50 text-coral-700 border-coral-200";
      case "hire":
        return "bg-cerulean-50 text-cerulean-700 border-cerulean-200";
      case "further review":
        return "bg-amber-50 text-amber-700 border-amber-200";
      default:
        return "bg-slate-100 text-slate-600 border-slate-200";
    }
  };

  const getRankBadge = (rank: number) => {
    if (rank === 1) return "bg-coral-100 text-coral-700 border-coral-300";
    if (rank === 2) return "bg-cerulean-100 text-cerulean-700 border-cerulean-300";
    if (rank === 3) return "bg-slate-100 text-slate-700 border-slate-300";
    return "bg-slate-100 text-slate-500 border-slate-200";
  };

  return (
    <div className="bg-white border border-slate-200/90 rounded-2xl p-6 space-y-4 shadow-xs">
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
            className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-9 pr-4 py-2 text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-coral-500 focus:bg-white transition"
          />
        </div>

        {/* Filters and Sorting */}
        <div className="flex items-center space-x-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-700 focus:outline-none focus:border-coral-500 font-medium"
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
            className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-700 focus:outline-none focus:border-coral-500 font-medium"
          >
            <option value="score">Sort by Overall Score</option>
            <option value="coverage">Sort by Skill Coverage %</option>
            <option value="credibility">Sort by Credibility Index</option>
          </select>
        </div>
      </div>

      {/* Table */}
      {filteredItems.length === 0 ? (
        <div className="text-center py-12 text-slate-400 text-xs bg-slate-50/60 rounded-xl border border-slate-200">
          No candidates matching filter. Use the Ingest panel to screen candidates.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-200">
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
            <tbody className="divide-y divide-slate-100 bg-white">
              {filteredItems.map((item) => (
                <tr
                  key={item.candidate_id}
                  onClick={() => onSelectCandidate(item.candidate_id)}
                  className="hover:bg-slate-50/80 transition cursor-pointer group"
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
                    <div className="font-semibold text-slate-900 group-hover:text-coral-600 transition">
                      {item.candidate_name}
                    </div>
                    <div className="text-[11px] text-slate-500">{item.email || item.candidate_id}</div>
                  </td>

                  {/* Overall Fit Score */}
                  <td className="py-3.5 px-4">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-slate-900 text-sm">{item.overall_fit_score}%</span>
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
                        <span className="text-slate-700 font-semibold">{item.skill_coverage_pct}%</span>
                        <span className="text-slate-400">{item.matched_skills.length} matched</span>
                      </div>
                      <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
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
                      <span className="text-[11px] capitalize text-slate-700 font-medium">
                        {item.speaking_pace || "optimal"} pace
                      </span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-cerulean-50 text-cerulean-700 border border-cerulean-200">
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
                            ? "text-cerulean-600"
                            : item.credibility_score >= 70
                            ? "text-coral-500"
                            : "text-amber-500"
                        }`}
                      >
                        {item.credibility_score}%
                      </span>
                      {item.discrepancies_count > 0 ? (
                        <span className="flex items-center text-[10px] text-coral-700 font-medium bg-coral-50 px-1.5 py-0.5 rounded border border-coral-200">
                          <AlertTriangle className="w-3 h-3 mr-1" />
                          {item.discrepancies_count} alert
                        </span>
                      ) : (
                        <CheckCircle className="w-3.5 h-3.5 text-cerulean-500" />
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
                      className="text-xs font-semibold text-cerulean-700 hover:text-cerulean-800 bg-cerulean-50 hover:bg-cerulean-100 px-3 py-1.5 rounded-lg border border-cerulean-200 transition"
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
