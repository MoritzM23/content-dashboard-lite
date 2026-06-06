// Mock-Daten fuer /ki-team Mockup-Dashboard (Reel-Aufnahme).
// Keine Backend-Anbindung, alle Werte statisch.

import { Calendar, Crown, Sparkles, TrendingUp, Wallet, type LucideIcon } from 'lucide-react';

export type AgentId = 'ceo' | 'content' | 'sales' | 'finance' | 'operations';

export interface AgentMeta {
  id: AgentId;
  icon: LucideIcon;
  name: string;
  description: string;
  lastAction: string;
}

export const AGENTS: AgentMeta[] = [
  {
    id: 'ceo',
    icon: Crown,
    name: 'CEO',
    description: 'Strategische Entscheidungen',
    lastAction: 'Preis für Tier 3 auf 4.500 € angehoben',
  },
  {
    id: 'content',
    icon: Sparkles,
    name: 'Content Creator',
    description: 'Reels, Captions, Konkurrenz',
    lastAction: '3 Reel-Skripte für diese Woche fertig',
  },
  {
    id: 'sales',
    icon: TrendingUp,
    name: 'Sales Agent',
    description: 'Leads, DMs, Pipeline',
    lastAction: '12 Leads qualifiziert, 4 hochgestuft',
  },
  {
    id: 'finance',
    icon: Wallet,
    name: 'Finance Agent',
    description: 'Rechnungen, Cashflow',
    lastAction: 'Rechnung Schmidt 2.400 € raus',
  },
  {
    id: 'operations',
    icon: Calendar,
    name: 'Operations Agent',
    description: 'Daily Brief, Kalender',
    lastAction: 'Daily Brief 06:30 zugestellt',
  },
];

// ──────────────────────────────────────────────────────────────────────────
// Shared Types

export interface KpiNumber {
  label: string;
  value: string;
  hint?: string;
  trend?: 'up' | 'down' | 'flat';
}

export interface TimePoint {
  label: string;
  value: number;
}

export interface SeriesPoint {
  label: string;
  a: number;
  b: number;
}

// ──────────────────────────────────────────────────────────────────────────
// CEO

export interface CeoDecisionPoint {
  role: 'CFO' | 'Operator' | 'Vertriebler' | 'Mentor' | 'Skeptiker';
  verdict: string;
}

export interface CeoRecentDecision {
  time: string;
  decision: string;
  impact: string;
}

export interface CeoDetail {
  kind: 'ceo';
  overline: string;
  headline: string;
  kpis: KpiNumber[];
  revenueImpact: TimePoint[];
  points: CeoDecisionPoint[];
  recentDecisions: CeoRecentDecision[];
  footer: string;
}

// ──────────────────────────────────────────────────────────────────────────
// Content

export interface ContentReel {
  hook: string;
  views: string;
  status: 'planned' | 'filmed' | 'posted';
}

export interface ContentDetail {
  kind: 'content';
  overline: string;
  kpis: KpiNumber[];
  viewsPerDay: TimePoint[];
  reels: ContentReel[];
  competitors: { handle: string; followers: string; weeklyViews: string }[];
  insight: string;
}

// ──────────────────────────────────────────────────────────────────────────
// Sales

export interface SalesLead {
  name: string;
  stage: 'qualifiziert' | 'follow-up' | 'hot';
  value: string;
}

export interface SalesStage {
  stage: string;
  count: number;
  value: number;
}

export interface SalesDetail {
  kind: 'sales';
  overline: string;
  kpis: KpiNumber[];
  pipeline: SalesStage[];
  forecast: SeriesPoint[];
  leads: SalesLead[];
}

// ──────────────────────────────────────────────────────────────────────────
// Finance

export interface FinanceInvoice {
  client: string;
  amount: string;
  status: 'offen' | 'bezahlt' | 'überfällig';
}

export interface FinanceDetail {
  kind: 'finance';
  overline: string;
  kpis: KpiNumber[];
  cashflow: SeriesPoint[];
  expensesBreakdown: { label: string; value: number }[];
  invoices: FinanceInvoice[];
}

// ──────────────────────────────────────────────────────────────────────────
// Operations

export interface OperationsCall {
  time: string;
  with: string;
  type: 'sales' | 'sync' | 'onboarding';
}

export interface OperationsDetail {
  kind: 'operations';
  overline: string;
  kpis: KpiNumber[];
  weekLoad: TimePoint[];
  calls: OperationsCall[];
  mail: { important: number; archived: number; replyRate: string };
  tasks: { label: string; done: number; total: number }[];
  topPrio: string;
}

export type AgentDetail =
  | CeoDetail
  | ContentDetail
  | SalesDetail
  | FinanceDetail
  | OperationsDetail;

// ──────────────────────────────────────────────────────────────────────────
// DATA

export const DETAILS: Record<AgentId, AgentDetail> = {
  ceo: {
    kind: 'ceo',
    overline: 'Aktuelle Entscheidung',
    headline: 'Pricing Tier 3 angehoben',
    kpis: [
      { label: 'Entscheidungen heute', value: '8', hint: '+3 vs gestern', trend: 'up' },
      { label: 'Ø Entscheidungszeit', value: '47 s', hint: '−12 s', trend: 'up' },
      { label: 'Confidence-Score', value: '94 %', hint: 'Top-Quartil', trend: 'up' },
      { label: 'Revenue-Impact MTD', value: '+18.400 €', hint: 'aus 5 Calls', trend: 'up' },
    ],
    revenueImpact: [
      { label: '01.05', value: 1200 },
      { label: '03.05', value: 1800 },
      { label: '05.05', value: 1500 },
      { label: '07.05', value: 2400 },
      { label: '09.05', value: 2100 },
      { label: '10.05', value: 3200 },
      { label: '11.05', value: 4100 },
      { label: '12.05', value: 4800 },
    ],
    points: [
      { role: 'CFO', verdict: 'Marge auf Tier 3 lag unter 38 %, jetzt 52 %.' },
      { role: 'Operator', verdict: 'Delivery-Aufwand rechtfertigt das neue Pricing.' },
      { role: 'Vertriebler', verdict: 'Letzte 3 Closes haben null Preisreibung gezeigt.' },
      { role: 'Mentor', verdict: 'Positionierung wird durch höheren Preis geschärft.' },
      { role: 'Skeptiker', verdict: 'Bestandskunden bekommen 30 Tage Grandfather-Frist.' },
    ],
    recentDecisions: [
      { time: '09:14', decision: 'Pricing Tier 3 → 4.500 €', impact: '+12 % Marge' },
      { time: '08:42', decision: 'Hiring-Stopp Q2 aufgehoben', impact: '+1 Senior' },
      { time: '08:07', decision: 'Affiliate-Programm gestoppt', impact: '−480 €/mo' },
      { time: '07:51', decision: 'Pitch-Deck Müller approved', impact: '24k Deal' },
    ],
    footer: 'Entscheidung in 47 Sek getroffen',
  },

  content: {
    kind: 'content',
    overline: 'Content-Performance',
    kpis: [
      { label: 'Views 30 Tage', value: '487k', hint: '+62 %', trend: 'up' },
      { label: 'Reels live', value: '24', hint: '8 diese Woche', trend: 'up' },
      { label: 'Ø Views / Reel', value: '20.3k', hint: '+4.1k', trend: 'up' },
      { label: 'Best-Performer', value: '89.4k', hint: 'KI-Team-Reel', trend: 'up' },
    ],
    viewsPerDay: [
      { label: 'Mo', value: 18000 },
      { label: 'Di', value: 24500 },
      { label: 'Mi', value: 31200 },
      { label: 'Do', value: 28100 },
      { label: 'Fr', value: 42800 },
      { label: 'Sa', value: 51400 },
      { label: 'So', value: 38900 },
    ],
    reels: [
      { hook: 'Dieses KI-Team leitet mein Unternehmen', views: '89.4k', status: 'filmed' },
      { hook: 'Warum 90 % aller Solopreneure 2026 ein KI-Team brauchen', views: '—', status: 'planned' },
      { hook: 'So baust du dir einen Sales Agent in 3 Stunden', views: '42.1k', status: 'posted' },
    ],
    competitors: [
      { handle: '@karpathys', followers: '184k', weeklyViews: '1.2M' },
      { handle: '@aiengineer', followers: '96k', weeklyViews: '480k' },
      { handle: '@buildwithai', followers: '52k', weeklyViews: '210k' },
    ],
    insight: 'Top-Hook der Woche: „Karpathys Setup ist überbewertet" (32k Views in 48 h)',
  },

  sales: {
    kind: 'sales',
    overline: 'Pipeline & Forecast',
    kpis: [
      { label: 'Pipeline-Wert', value: '84.500 €', hint: '+24 %', trend: 'up' },
      { label: 'Neue Leads heute', value: '12', hint: '+5 vs gestern', trend: 'up' },
      { label: 'Conversion-Rate', value: '38 %', hint: '+6 pp', trend: 'up' },
      { label: 'Ø Deal-Größe', value: '3.250 €', hint: 'Tier-3-Mix', trend: 'up' },
    ],
    pipeline: [
      { stage: 'Lead', count: 28, value: 14000 },
      { stage: 'Qualified', count: 14, value: 21000 },
      { stage: 'Discovery', count: 8, value: 18500 },
      { stage: 'Pitch', count: 5, value: 17500 },
      { stage: 'Closing', count: 3, value: 13500 },
    ],
    forecast: [
      { label: 'KW 18', a: 8200, b: 6400 },
      { label: 'KW 19', a: 11500, b: 9800 },
      { label: 'KW 20', a: 14800, b: 12200 },
      { label: 'KW 21', a: 18400, b: 15600 },
      { label: 'KW 22', a: 22100, b: 18900 },
      { label: 'KW 23', a: 26800, b: 22400 },
    ],
    leads: [
      { name: 'M. Schmidt — Agentur DACH', stage: 'hot', value: '6.500 €' },
      { name: 'L. Becker — SaaS-Founder', stage: 'qualifiziert', value: '4.500 €' },
      { name: 'A. Reinhardt — Coach', stage: 'follow-up', value: '3.200 €' },
    ],
  },

  finance: {
    kind: 'finance',
    overline: 'Finance Cockpit',
    kpis: [
      { label: 'MRR', value: '12.4k €', hint: '+18 %', trend: 'up' },
      { label: 'Cash on Hand', value: '47.8k €', hint: 'gesund', trend: 'up' },
      { label: 'Burn Rate', value: '3.2k €', hint: '−400 €', trend: 'up' },
      { label: 'Runway', value: '15 Monate', hint: 'kein Stress', trend: 'flat' },
    ],
    cashflow: [
      { label: 'Nov', a: 8200, b: 5100 },
      { label: 'Dez', a: 9400, b: 5400 },
      { label: 'Jan', a: 10100, b: 5800 },
      { label: 'Feb', a: 11200, b: 6100 },
      { label: 'Mär', a: 11800, b: 6400 },
      { label: 'Apr', a: 12100, b: 6800 },
      { label: 'Mai', a: 12400, b: 7100 },
    ],
    expensesBreakdown: [
      { label: 'Tools & Software', value: 1240 },
      { label: 'Freelancer', value: 1800 },
      { label: 'Marketing', value: 920 },
      { label: 'Steuern (Rücklage)', value: 2400 },
    ],
    invoices: [
      { client: 'Schmidt GmbH', amount: '2.400 €', status: 'bezahlt' },
      { client: 'Reinhardt Coaching', amount: '4.500 €', status: 'offen' },
      { client: 'Becker Studio', amount: '1.800 €', status: 'überfällig' },
    ],
  },

  operations: {
    kind: 'operations',
    overline: 'Daily Operations',
    kpis: [
      { label: 'Calls heute', value: '3', hint: '4 h Block', trend: 'flat' },
      { label: 'Focus Time', value: '4 h 30', hint: '+45 min', trend: 'up' },
      { label: 'Mails verarbeitet', value: '17', hint: '4 wichtig', trend: 'up' },
      { label: 'Tasks erledigt', value: '12 / 16', hint: '75 %', trend: 'up' },
    ],
    weekLoad: [
      { label: 'Mo', value: 6.5 },
      { label: 'Di', value: 8.2 },
      { label: 'Mi', value: 7.4 },
      { label: 'Do', value: 9.1 },
      { label: 'Fr', value: 5.8 },
      { label: 'Sa', value: 2.4 },
      { label: 'So', value: 1.2 },
    ],
    calls: [
      { time: '10:00', with: 'Sales-Call Müller', type: 'sales' },
      { time: '13:30', with: 'Strategy Sync Tim', type: 'sync' },
      { time: '16:00', with: 'Onboarding Reinhardt', type: 'onboarding' },
    ],
    mail: { important: 4, archived: 13, replyRate: '94 %' },
    tasks: [
      { label: 'Content', done: 4, total: 5 },
      { label: 'Sales', done: 3, total: 4 },
      { label: 'Admin', done: 5, total: 7 },
    ],
    topPrio: 'Pitch-Deck für Müller fertigstellen',
  },
};
