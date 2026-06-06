/**
 * Client-side API-Client für den Python-Mini-API-Server (dashboard_api.py).
 * Endpoints siehe scripts/dashboard_api.py.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://127.0.0.1:8093';

export type CreatorList = {
  creators: string[];
  self_handle: string;
};

export type ApiOk<T = unknown> = { ok: true } & T;
export type ApiErr = { error: string };
export type ApiResult<T = unknown> = ApiOk<T> | ApiErr;

async function request<T = unknown>(
  path: string,
  init?: RequestInit
): Promise<ApiResult<T>> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    });
    const json = (await res.json()) as ApiResult<T>;
    if (!res.ok && !('ok' in json)) {
      return { error: (json as ApiErr).error ?? `HTTP ${res.status}` };
    }
    return json;
  } catch (e) {
    return { error: e instanceof Error ? e.message : 'API offline' };
  }
}

export const api = {
  health: () => request<{ service: string }>('/health'),
  listCreators: () => request<CreatorList>('/creators'),
  addCreator: (handle: string) =>
    request<{ handle: string; creators: string[] }>('/creators', {
      method: 'POST',
      body: JSON.stringify({ handle }),
    }),
  removeCreator: (handle: string) =>
    request<{ creators: string[] }>(`/creators/${encodeURIComponent(handle)}`, {
      method: 'DELETE',
    }),
  triggerTracker: () =>
    request<{ msg: string }>('/tracker/run', { method: 'POST' }),
  triggerDiscovery: () =>
    request<{ msg: string }>('/discovery/refresh', { method: 'POST' }),
  getPlanningFile: (vaultPath: string) =>
    request<PlanningFile>(
      `/content/planning/file?path=${encodeURIComponent(vaultPath)}`
    ),
  savePlanningFile: (vaultPath: string, payload: PlanningFileUpdate) =>
    request<{ path: string }>(
      `/content/planning/file?path=${encodeURIComponent(vaultPath)}`,
      {
        method: 'PUT',
        body: JSON.stringify(payload),
      }
    ),
};

export type PlanningFile = {
  path: string;
  title: string;
  frontmatter: Record<string, unknown>;
  body: string;
};

export type PlanningFileUpdate = {
  title: string;
  frontmatter: Record<string, unknown>;
  body: string;
};
