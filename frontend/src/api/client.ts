// frontend/src/api/client.ts
import axios from "axios";

const API_BASE = "http://localhost:8081";  // Changed from 8000 to 8081

export interface GeneratePayload {
  prompt: string;
  duration_seconds: number;
  refine_with_ai: boolean;
}

export interface GenerateResponse {
  job_id: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: "queued" | "running" | "done" | "failed";
  message?: string;
  video_url?: string | null;
}

export async function generateVideo(payload: GeneratePayload) {
  const res = await axios.post<GenerateResponse>(
    `${API_BASE}/api/video/generate`,
    payload
  );
  return res.data;
}

export async function getJobStatus(jobId: string) {
  const res = await axios.get<JobStatusResponse>(
    `${API_BASE}/api/video/status/${jobId}`
  );
  return res.data;
}

export function getVideoDownloadUrl(jobId: string) {
  return `${API_BASE}/api/video/file/${jobId}`;
}
