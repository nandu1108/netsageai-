import { useState } from "react";
import ProblemForm from "../components/ProblemForm";
import DiagnosisReport from "../components/DiagnosisReport";

/**
 * Top-level page. Wire this into a Vite/CRA project with Tailwind
 * configured (see frontend README notes in the project root README.md).
 */
export default function App() {
  const [diagnosis, setDiagnosis] = useState(null);

  return (
    <main className="p-8 space-y-8">
      <h1 className="text-2xl font-bold">NetSage AI</h1>
      <ProblemForm onDiagnosis={setDiagnosis} />
      <DiagnosisReport diagnosis={diagnosis} />

      {/* TODO: add a DashboardStats component pulling from GET /api/dashboard */}
    </main>
  );
}
