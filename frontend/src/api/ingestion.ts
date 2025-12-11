// src/api/ingestion.ts
// CSV upload helpers for ingestion.

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    try {
      const data = JSON.parse(text);
      const msg = data.detail || data.message || text || res.statusText;
      throw new Error(msg);
    } catch {
      throw new Error(text || res.statusText);
    }
  }
  // Some ingestion endpoints might return no JSON body; handle both cases.
  try {
    return (await res.json()) as T;
  } catch {
    return {} as T;
  }
}

/**
 * Upload servers CSV for a specific run.
 *
 * Assumes FastAPI endpoint:
 *   POST /v1/ingest/servers?run_id=...
 * body: multipart form-data with fields:
 *   - file: CSV file
 *   - run_id: run id (redundant but harmless)
 */
export async function uploadServersCsv(
  runId: string,
  file: File
): Promise<void> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("run_id", runId);

  const res = await fetch(
    `/v1/ingest/servers?run_id=${encodeURIComponent(runId)}`,
    {
      method: "POST",
      body: formData,
    }
  );

  await handleResponse<unknown>(res);
}
