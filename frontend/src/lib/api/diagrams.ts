export type CloudProvider = 'aws' | 'azure' | 'gcp';
export type DiagramType = 'landing_zone' | 'network' | 'application';
export type OverlayProfile = 'dod' | 'fedramp' | 'zero_trust' | null;

export interface DiagramGenerateRequest {
  cloud: CloudProvider;
  diagram_type: DiagramType;
  org_name?: string | null;
  environment?: string | null;
  workload_name?: string | null;
  overlay_profile?: OverlayProfile;
}

export interface DiagramGenerateResponse {
  xml: string;
}

export interface DiagramPackageRequest {
  org_name: string;
  environment: string;
  workload_name: string;
  overlay_profile?: OverlayProfile;
  opportunity_id?: string;
  version_tag?: string;
}

export interface DiagramPackageResponse {
  zip_filename: string;
  zip_base64: string;
  file_count: number;
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

/**
 * Call backend Phase 7D diagram generator.
 */
export async function generateDiagram(
  payload: DiagramGenerateRequest
): Promise<DiagramGenerateResponse> {
  const res = await fetch(`${API_BASE}/v1/diagram/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(`Failed to generate diagram (HTTP ${res.status})`);
  }

  return res.json();
}

/**
 * Turn XML into a .drawio file on the client.
 */
export function downloadDiagramXml(
  xml: string,
  filename = 'cloudready-diagram.drawio'
) {
  const blob = new Blob([xml], { type: 'application/xml' });
  const url = window.URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();

  window.URL.revokeObjectURL(url);
}

/**
 * Call backend /v1/diagram/package and return the JSON payload.
 */
export async function fetchDiagramPackage(
  payload: DiagramPackageRequest
): Promise<DiagramPackageResponse> {
  const res = await fetch(`${API_BASE}/v1/diagram/package`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(`Failed to build diagram package (HTTP ${res.status})`);
  }

  return res.json();
}

/**
 * Convenience helper: calls fetchDiagramPackage and triggers a ZIP download.
 */
export async function triggerDiagramPackageDownload(
  payload: DiagramPackageRequest
): Promise<void> {
  const data = await fetchDiagramPackage(payload);

  if (!data.zip_base64) {
    throw new Error('Server response missing ZIP data');
  }

  // Decode base64 -> Uint8Array -> Blob -> download
  const binaryString = atob(data.zip_base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);

  for (let i = 0; i < len; i += 1) {
    bytes[i] = binaryString.charCodeAt(i);
  }

  const blob = new Blob([bytes], { type: 'application/zip' });
  const url = window.URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = url;
  a.download = data.zip_filename || 'cloudready-diagrams.zip';
  document.body.appendChild(a);
  a.click();
  a.remove();

  window.URL.revokeObjectURL(url);
}
