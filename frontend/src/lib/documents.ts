import { apiFetch, API_BASE_URL, API_SECRET_KEY } from "@/lib/api";

export interface DocumentSummary {
  id: string;
  filename: string;
  status: string;
  file_type?: string;
  file_size_bytes?: number;
  chunk_count?: number;
  created_at?: string;
  last_activity_at?: string;
}

export interface DocumentStatus {
  id: string;
  status: string;
  [key: string]: unknown;
}

export class UploadError extends Error {}

export async function fetchDocuments(uuid: string): Promise<DocumentSummary[]> {
  return apiFetch<DocumentSummary[]>("/api/documents", {
    headers: { "X-Browser-UUID": uuid },
  });
}

export async function fetchDocumentStatus(id: string, uuid: string): Promise<DocumentStatus> {
  return apiFetch<DocumentStatus>(`/api/documents/${id}/status`, {
    headers: { "X-Browser-UUID": uuid },
  });
}

export async function uploadDocument(file: File, uuid: string): Promise<DocumentSummary> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/documents`, {
    method: "POST",
    headers: {
      "X-Browser-UUID": uuid,
      ...(API_SECRET_KEY ? { Authorization: `Bearer ${API_SECRET_KEY}` } : {}),
    },
    body: formData,
  });

  if (!response.ok) {
    let message = `Upload failed with status ${response.status}.`;
    try {
      const data = await response.json();
      if (data && typeof data.detail === "string") {
        message = data.detail;
      }
    } catch {
      // response body was not JSON; keep the generic message
    }
    throw new UploadError(message);
  }

  return (await response.json()) as DocumentSummary;
}
