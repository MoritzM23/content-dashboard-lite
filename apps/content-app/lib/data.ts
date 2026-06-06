/**
 * Server-side Daten-Loader für dashboard-data.json.
 * Wird vom Cron-Job alle 30 Min regeneriert (com.aios.dashboard-refresh).
 * Wir lesen die Datei direkt vom Filesystem in einer Server Component.
 */

import { readFile } from 'node:fs/promises';
import path from 'node:path';
import type { ContentIntel, DashboardData } from './types';

const WORKSPACE = process.env.WORKSPACE_PATH || process.cwd();
const DATA_PATH = path.join(WORKSPACE, 'data', 'dashboard-data.json');

export async function loadDashboardData(): Promise<DashboardData | null> {
  try {
    const raw = await readFile(DATA_PATH, 'utf-8');
    return JSON.parse(raw) as DashboardData;
  } catch (e) {
    console.error('loadDashboardData failed:', e);
    return null;
  }
}

export async function loadContentIntel(): Promise<ContentIntel | null> {
  const data = await loadDashboardData();
  return data?.content_intel ?? null;
}
