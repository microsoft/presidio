const API_BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    let detail = body;
    try {
      const parsed = JSON.parse(body);
      if (parsed.detail) detail = parsed.detail;
    } catch { /* use raw body */ }
    throw new Error(detail);
  }
  return res.json();
}

async function uploadFile<T>(path: string, formData: FormData): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const body = await res.text();
    let detail = body;
    try {
      const parsed = JSON.parse(body);
      if (parsed.detail) detail = parsed.detail;
    } catch { /* use raw body */ }
    throw new Error(detail);
  }
  return res.json();
}

// --- Datasets ---
export const api = {
  datasets: {
    list: () => request<any[]>("/datasets"),
    saved: () => request<any[]>("/datasets/saved"),
    get: (id: string) => request<any>(`/datasets/${encodeURIComponent(id)}`),
    load: (params: { path: string; format: string; text_column: string; entities_column?: string; name?: string; description?: string }) =>
      request<any>("/datasets/load", {
        method: "POST",
        body: JSON.stringify(params),
      }),
    rename: (id: string, name: string) =>
      request<any>(`/datasets/${encodeURIComponent(id)}/rename`, {
        method: "PATCH",
        body: JSON.stringify({ name }),
      }),
    remove: (id: string) =>
      request<any>(`/datasets/${encodeURIComponent(id)}`, {
        method: "DELETE",
      }),
    upload: (file: File, opts?: { text_column?: string; entities_column?: string; name?: string; description?: string }) => {
      const fd = new FormData();
      fd.append('file', file);
      fd.append('text_column', opts?.text_column || 'text');
      fd.append('entities_column', opts?.entities_column || '');
      fd.append('name', opts?.name || '');
      fd.append('description', opts?.description || '');
      return uploadFile<any>('/datasets/upload', fd);
    },
    preview: (id: string, limit = 5) =>
      request<any>(`/datasets/${encodeURIComponent(id)}/preview?limit=${limit}`),
    records: (id: string) =>
      request<any[]>(`/datasets/${encodeURIComponent(id)}/records`),
  },



  analysis: {
    start: () => request<any>("/analysis/start", { method: "POST" }),
    status: () => request<any>("/analysis/status"),
    records: () => request<any[]>("/analysis/records"),
    record: (id: string) => request<any>(`/analysis/records/${encodeURIComponent(id)}`),
  },

  llm: {
    models: () => request<{ id: string; label: string; provider: string }[]>("/llm/models"),
    settings: () => request<{ env_ready: boolean; has_endpoint: boolean; has_api_key: boolean; auth_method: string; deployment_name: string; configured: boolean }>("/llm/settings"),
    configure: (deploymentName: string) =>
      request<any>("/llm/configure", { method: "POST", body: JSON.stringify({ deployment_name: deploymentName }) }),
    status: () => request<{ configured: boolean; running: boolean; progress: number; total: number; error: string | null; entity_count: number; elapsed_ms: number | null }>("/llm/status"),
    analyze: (datasetId: string) => request<any>("/llm/analyze", { method: "POST", body: JSON.stringify({ dataset_id: datasetId }) }),
    disconnect: () => request<any>("/llm/disconnect", { method: "POST" }),
    results: () => request<Record<string, any[]>>("/llm/results"),
    recordResults: (id: string) => request<any[]>(`/llm/results/${encodeURIComponent(id)}`),
  },

  presidio: {
    configs: () => request<{ name: string; path: string | null }[]>("/presidio/configs"),
    saveConfig: (name: string, path: string) =>
      request<any>("/presidio/configs", { method: "POST", body: JSON.stringify({ name, path }) }),
    deleteConfig: (name: string) =>
      request<any>(`/presidio/configs/${encodeURIComponent(name)}`, { method: "DELETE" }),
    uploadConfig: (file: File, name: string) => {
      const fd = new FormData();
      fd.append('file', file);
      fd.append('name', name);
      return uploadFile<any>('/presidio/configs/upload', fd);
    },
    configure: (configName?: string, configPath?: string) =>
      request<any>("/presidio/configure", { method: "POST", body: JSON.stringify({ config_name: configName || null, config_path: configPath || null }) }),
    status: () => request<{ configured: boolean; loading: boolean; config_name: string | null; config_path: string; running: boolean; progress: number; total: number; error: string | null; entity_count: number; elapsed_ms: number | null }>("/presidio/status"),
    analyze: (datasetId: string) =>
      request<any>("/presidio/analyze", { method: "POST", body: JSON.stringify({ dataset_id: datasetId }) }),
    results: () => request<Record<string, any[]>>("/presidio/results"),
    disconnect: () => request<any>("/presidio/disconnect", { method: "POST" }),
  },

  review: {
    records: () => request<any[]>("/review/records"),
    confirm: (recordId: string, entity: any, source: string) =>
      request<any>(`/review/records/${encodeURIComponent(recordId)}/confirm`, {
        method: "POST",
        body: JSON.stringify({ entity, source }),
      }),
    reject: (recordId: string, entity: any, source: string) =>
      request<any>(`/review/records/${encodeURIComponent(recordId)}/reject`, {
        method: "POST",
        body: JSON.stringify({ entity, source }),
      }),
    addManual: (recordId: string, entity: any) =>
      request<any>(`/review/records/${encodeURIComponent(recordId)}/manual`, {
        method: "POST",
        body: JSON.stringify({ entity, source: "manual" }),
      }),
    progress: () => request<any>("/review/progress"),
    saveFinalEntities: (datasetId: string, goldenSet: Record<string, any[]>) =>
      request<any>("/review/save-final-entities", {
        method: "POST",
        body: JSON.stringify({ dataset_id: datasetId, golden_set: goldenSet }),
      }),
    saveConfigResults: (datasetId: string) =>
      request<any>("/review/save-config-results", {
        method: "POST",
        body: JSON.stringify({ dataset_id: datasetId }),
      }),
  },

  evaluation: {
    run: () => request<any>("/evaluation/run", { method: "POST" }),
    summary: (datasetId: string, configNames?: string[]) => {
      const params = new URLSearchParams();
      params.set('dataset_id', datasetId);
      configNames?.forEach((name) => params.append('config_names', name));
      return request<any>(`/evaluation/summary?${params.toString()}`);
    },
    misses: (filters?: { miss_type?: string; entity_type?: string; risk_level?: string }) => {
      const params = new URLSearchParams();
      if (filters?.miss_type) params.set("miss_type", filters.miss_type);
      if (filters?.entity_type) params.set("entity_type", filters.entity_type);
      if (filters?.risk_level) params.set("risk_level", filters.risk_level);
      const qs = params.toString();
      return request<any[]>(`/evaluation/misses${qs ? `?${qs}` : ""}`);
    },
    metrics: () => request<any>("/evaluation/metrics"),
    patterns: () => request<any>("/evaluation/patterns"),
  },

  decision: {
    save: (decision: string, notes: string, improvements: string[]) =>
      request<any>("/decision", {
        method: "POST",
        body: JSON.stringify({
          decision,
          notes,
          selected_improvements: improvements,
        }),
      }),
    improvements: () => request<any[]>("/decision/improvements"),
    saveArtifacts: () =>
      request<any>("/decision/save-artifacts", { method: "POST" }),
  },
};
