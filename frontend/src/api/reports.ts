// src/api/reports.ts

const BASE = "/api";

export async function generateAllReports(runId: string) {
  const res = await fetch(`${BASE}/reports/${runId}/generate-all`, {
    method: "POST",
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(
      `Failed to generate reports (status ${res.status}): ${body}`,
    );
  }

  return res.json() as Promise<{
    status: string;
    run_id: string;
    summary_pdf: string;
    summary_docx: string;
    technical_pdf: string;
    technical_docx: string;
    architecture_pdf: string;
    architecture_docx: string;
    package_zip: string;
  }>;
}

export function getReportsPackageUrl(runId: string) {
  return `${BASE}/reports/${runId}/download/CloudReadyAI-Assessment-Package.zip`;
}
