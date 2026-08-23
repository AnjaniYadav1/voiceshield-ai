import axios from "axios";

// Relative path: works both in dev (Vite proxies /api -> FastAPI on 8000)
// and in production (FastAPI serves the frontend AND the API from the
// same origin, so a relative path just works, no separate server needed).
const API_BASE = import.meta.env.VITE_API_BASE || "/api";

const client = axios.create({ baseURL: API_BASE, timeout: 30000 });

export async function getHealth() {
  const { data } = await client.get("/health");
  return data;
}

export async function analyzeFile(file, speakerId) {
  const form = new FormData();
  form.append("file", file);
  if (speakerId) form.append("speaker_id", speakerId);
  const { data } = await client.post("/analyze", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function analyzeLive(blob, speakerId) {
  const form = new FormData();
  // Change .webm to .wav here:
  form.append("file", blob, "live_recording.wav");
  if (speakerId) form.append("speaker_id", speakerId);
  const { data } = await client.post("/analyze/live", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function registerSpeaker(name, speakerId, file) {
  const form = new FormData();
  form.append("name", name);
  form.append("speaker_id", speakerId);
  form.append("file", file);
  const { data } = await client.post("/speakers/register", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function listSpeakers() {
  const { data } = await client.get("/speakers");
  return data;
}

export async function listAnalyses(limit = 50, offset = 0) {
  const { data } = await client.get("/analyses", { params: { limit, offset } });
  return data;
}

export async function getAnalysis(id) {
  const { data } = await client.get(`/analyses/${id}`);
  return data;
}

export async function deleteAnalysis(id) {
  const { data } = await client.delete(`/analyses/${id}`);
  return data;
}

export async function getStatistics() {
  const { data } = await client.get("/statistics");
  return data;
}

export default client;
