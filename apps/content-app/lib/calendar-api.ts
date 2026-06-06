/**
 * Calendar-API-Client: Wrapper für die /calendar/event-Endpoints des Python-Mini-Servers.
 * Backend: scripts/dashboard_api.py
 */

import type { CalendarEventDetail, LeadPrep } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://127.0.0.1:8093';

type ApiOk = { ok: true; deleted?: string };
type ApiErr = { error: string };
type Result<T> = T | ApiErr;

function isErr<T>(v: Result<T>): v is ApiErr {
  return typeof v === 'object' && v !== null && 'error' in v;
}

async function jsonFetch<T>(path: string, init?: RequestInit): Promise<Result<T>> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    });
    const json = (await res.json()) as Result<T>;
    if (!res.ok && !isErr(json)) {
      return { error: `HTTP ${res.status}` };
    }
    return json;
  } catch (e) {
    return { error: e instanceof Error ? e.message : 'API offline' };
  }
}

export const calendarApi = {
  /** Volle Event-Details live von Google Calendar holen. */
  getEvent: (params: { account: string; calendarId: string; eventId: string }) => {
    const q = new URLSearchParams({
      account: params.account || 'primary',
      calendarId: params.calendarId,
      eventId: params.eventId,
    });
    return jsonFetch<CalendarEventDetail>(`/calendar/event?${q.toString()}`);
  },

  /** Termin ändern. Nur gesetzte Felder werden gepatcht. */
  patchEvent: (body: {
    account: string;
    calendar_id: string;
    event_id: string;
    title?: string;
    description?: string;
    location?: string;
    start_iso?: string;
    end_iso?: string;
  }) =>
    jsonFetch<CalendarEventDetail>('/calendar/event', {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),

  /** Termin löschen. */
  deleteEvent: (params: { account: string; calendarId: string; eventId: string }) => {
    const q = new URLSearchParams({
      account: params.account || 'primary',
      calendarId: params.calendarId,
      eventId: params.eventId,
    });
    return jsonFetch<ApiOk>(`/calendar/event?${q.toString()}`, { method: 'DELETE' });
  },

  /** Lead-Prep aus Cache holen (404 wenn noch keine erzeugt). */
  getPrep: (eventId: string) => {
    const q = new URLSearchParams({ eventId });
    return jsonFetch<LeadPrep>(`/calendar/prep?${q.toString()}`);
  },

  /** Lead-Prep neu erzeugen (synchron, dauert 30-60s wegen Web + Claude). */
  generatePrep: (body: { event_id: string; force?: boolean }) =>
    jsonFetch<LeadPrep>('/calendar/prep/generate', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  /** Neuen Termin anlegen. start_iso/end_iso im Format "YYYY-MM-DDTHH:MM:SS+02:00" oder all-day "YYYY-MM-DD". */
  createEvent: (body: {
    account?: string;
    calendar_id?: string;
    title: string;
    start_iso: string;
    end_iso: string;
    description?: string;
    location?: string;
    attendees?: string[];
  }) =>
    jsonFetch<CalendarEventDetail>('/calendar/event', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
};

export function isCalendarApiError<T>(r: Result<T>): r is ApiErr {
  return isErr(r);
}
