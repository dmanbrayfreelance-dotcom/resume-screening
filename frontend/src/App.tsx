import React, { useState, useEffect } from "react";
import { Navbar } from "./components/Navbar";
import { DashboardPage } from "./pages/DashboardPage";
import { fetchHealth, HealthStatus } from "./api/client";

export default function App() {
  const [systemStatus, setSystemStatus] = useState<HealthStatus | null>(null);

  useEffect(() => {
    fetchHealth()
      .then((data) => setSystemStatus(data))
      .catch((err) => console.warn("Backend not reachable yet", err));
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar systemStatus={systemStatus} />
      <main className="flex-1">
        <DashboardPage />
      </main>
      <footer className="border-t border-slate-900 bg-slate-950/80 py-4 px-6 text-center text-xs text-slate-500">
        Multimodal Resume Intelligence & Screening Studio • Advisory Scoring Only • Algorithmic Fairness Compliant
      </footer>
    </div>
  );
}
