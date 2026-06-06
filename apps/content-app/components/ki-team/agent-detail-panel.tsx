'use client';

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from 'recharts';

import { cn } from '@/lib/utils';
import type {
  AgentDetail,
  AgentMeta,
  CeoDetail,
  ContentDetail,
  ContentReel,
  FinanceDetail,
  FinanceInvoice,
  KpiNumber,
  OperationsDetail,
  SalesDetail,
  SalesLead,
} from '@/lib/ki-team-data';

interface AgentDetailPanelProps {
  agent: AgentMeta;
  detail: AgentDetail;
}

// Brand-Farben fuer Charts (aus globals.css gespiegelt, weil Recharts CSS-Vars
// nicht in allen Props akzeptiert).
const C_PRIMARY = '#c26b4c';
const C_PRIMARY_SOFT = 'rgba(194, 107, 76, 0.18)';
const C_OK = '#7fb685';
const C_WARN = '#e0a458';
const C_MUTED = 'rgba(242, 232, 220, 0.4)';
const C_GRID = 'rgba(242, 232, 220, 0.06)';
const C_AXIS = 'rgba(242, 232, 220, 0.35)';

export function AgentDetailPanel({ agent, detail }: AgentDetailPanelProps) {
  const Icon = agent.icon;
  return (
    <section className="rounded-2xl border border-primary/40 bg-card/60 p-8 shadow-[0_0_80px_-25px] shadow-primary/40 animate-in fade-in slide-in-from-top-2 duration-200">
      <header className="mb-7 flex items-center gap-4 border-b border-border/60 pb-6">
        <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-primary/15 text-primary">
          <Icon className="h-7 w-7" strokeWidth={1.5} />
        </div>
        <div className="flex-1">
          <div className="label-mono mb-1 text-primary">{detail.overline}</div>
          <h2 className="font-heading text-2xl font-medium tracking-tight text-foreground">
            {agent.name}
          </h2>
        </div>
        <span className="hidden items-center gap-1.5 rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-[10px] uppercase tracking-[0.18em] text-primary md:flex">
          <span className="h-1.5 w-1.5 rounded-full bg-primary" />
          live
        </span>
      </header>

      {detail.kind === 'ceo' && <CeoBody detail={detail} />}
      {detail.kind === 'content' && <ContentBody detail={detail} />}
      {detail.kind === 'sales' && <SalesBody detail={detail} />}
      {detail.kind === 'finance' && <FinanceBody detail={detail} />}
      {detail.kind === 'operations' && <OperationsBody detail={detail} />}
    </section>
  );
}

// ──────────────────────────────────────────────────────────────────────────
// Building blocks

function KpiRow({ kpis }: { kpis: KpiNumber[] }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {kpis.map((k) => (
        <div
          key={k.label}
          className="rounded-xl border border-border/60 bg-background/40 px-4 py-4"
        >
          <div className="label-mono mb-2 text-[10px]">{k.label}</div>
          <div className="num-mono text-2xl font-semibold tracking-tight leading-none text-foreground">
            {k.value}
          </div>
          {k.hint && (
            <div
              className={cn(
                'num-mono mt-2 text-[10px]',
                k.trend === 'up' && 'text-ok',
                k.trend === 'down' && 'text-destructive',
                (!k.trend || k.trend === 'flat') && 'text-muted-foreground',
              )}
            >
              {k.hint}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function ChartCard({
  title,
  hint,
  children,
  className,
}: {
  title: string;
  hint?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn('rounded-xl border border-border/60 bg-background/40 p-5', className)}>
      <div className="mb-4 flex items-baseline justify-between">
        <div className="label-mono text-primary">{title}</div>
        {hint && <div className="num-mono text-[10px] text-muted-foreground">{hint}</div>}
      </div>
      <div className="h-44 w-full">
        <ResponsiveContainer width="100%" height="100%">
          {children as React.ReactElement}
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────────
// CEO

function CeoBody({ detail }: { detail: CeoDetail }) {
  return (
    <div className="space-y-6">
      <KpiRow kpis={detail.kpis} />

      <div className="grid gap-5 lg:grid-cols-5">
        <ChartCard
          title="Revenue-Impact letzte Tage"
          hint={'+18.400 € MTD'}
          className="lg:col-span-3"
        >
          <AreaChart data={detail.revenueImpact} margin={{ top: 5, right: 12, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="ceoArea" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={C_PRIMARY} stopOpacity={0.5} />
                <stop offset="100%" stopColor={C_PRIMARY} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke={C_GRID} vertical={false} />
            <XAxis dataKey="label" stroke={C_AXIS} fontSize={10} tickLine={false} axisLine={false} />
            <YAxis stroke={C_AXIS} fontSize={10} tickLine={false} axisLine={false} width={32} />
            <Area
              type="monotone"
              dataKey="value"
              stroke={C_PRIMARY}
              strokeWidth={2}
              fill="url(#ceoArea)"
            />
          </AreaChart>
        </ChartCard>

        <div className="rounded-xl border border-border/60 bg-background/40 p-5 lg:col-span-2">
          <div className="label-mono mb-4 text-primary">Letzte Entscheidungen</div>
          <ul className="space-y-2.5">
            {detail.recentDecisions.map((d) => (
              <li key={d.time} className="flex items-start gap-3">
                <span className="num-mono w-12 shrink-0 text-xs font-semibold text-primary">
                  {d.time}
                </span>
                <div className="flex-1">
                  <div className="text-xs text-foreground/95">{d.decision}</div>
                  <div className="num-mono text-[10px] text-ok">{d.impact}</div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div>
        <div className="label-mono mb-3 text-primary">{detail.headline} · Boardroom-Verdict</div>
        <div className="grid gap-2 lg:grid-cols-5">
          {detail.points.map((p) => (
            <div
              key={p.role}
              className="rounded-lg border border-border/60 bg-background/40 px-3 py-3"
            >
              <div className="label-mono mb-1.5 text-[9px] text-primary">{p.role}</div>
              <p className="text-[11px] leading-snug text-foreground/90">{p.verdict}</p>
            </div>
          ))}
        </div>
        <div className="label-mono mt-3 text-[10px] text-muted-foreground">{detail.footer}</div>
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────────
// Content

const REEL_STATUS_STYLES: Record<ContentReel['status'], string> = {
  planned: 'border-muted-foreground/30 bg-muted/20 text-muted-foreground',
  filmed: 'border-warn/40 bg-warn/10 text-warn',
  posted: 'border-ok/40 bg-ok/10 text-ok',
};

const REEL_STATUS_LABEL: Record<ContentReel['status'], string> = {
  planned: 'geplant',
  filmed: 'gefilmt',
  posted: 'live',
};

function ContentBody({ detail }: { detail: ContentDetail }) {
  return (
    <div className="space-y-6">
      <KpiRow kpis={detail.kpis} />

      <div className="grid gap-5 lg:grid-cols-5">
        <ChartCard title="Views letzte 7 Tage" hint="487k Total" className="lg:col-span-3">
          <BarChart data={detail.viewsPerDay} margin={{ top: 5, right: 12, left: 0, bottom: 0 }}>
            <CartesianGrid stroke={C_GRID} vertical={false} />
            <XAxis dataKey="label" stroke={C_AXIS} fontSize={10} tickLine={false} axisLine={false} />
            <YAxis
              stroke={C_AXIS}
              fontSize={10}
              tickLine={false}
              axisLine={false}
              width={36}
              tickFormatter={(v) => `${Math.round(v / 1000)}k`}
            />
            <Bar dataKey="value" radius={[4, 4, 0, 0]}>
              {detail.viewsPerDay.map((d, i) => (
                <Cell key={i} fill={d.value >= 40000 ? C_PRIMARY : C_PRIMARY_SOFT} />
              ))}
            </Bar>
          </BarChart>
        </ChartCard>

        <div className="rounded-xl border border-border/60 bg-background/40 p-5 lg:col-span-2">
          <div className="label-mono mb-4 text-primary">Konkurrenz-Tracking</div>
          <ul className="space-y-3">
            {detail.competitors.map((c) => (
              <li key={c.handle} className="flex items-center justify-between">
                <div>
                  <div className="text-xs font-medium text-foreground/95">{c.handle}</div>
                  <div className="num-mono text-[10px] text-muted-foreground">
                    {c.followers} Follower
                  </div>
                </div>
                <div className="text-right">
                  <div className="num-mono text-sm font-semibold text-primary">{c.weeklyViews}</div>
                  <div className="label-mono text-[9px]">/ Woche</div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        {detail.reels.map((reel, i) => (
          <article
            key={i}
            className="flex h-full flex-col justify-between rounded-lg border border-border/60 bg-background/40 p-4"
          >
            <p className="text-sm leading-snug text-foreground/95">„{reel.hook}"</p>
            <div className="mt-3 flex items-center justify-between">
              <span
                className={cn(
                  'inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] uppercase tracking-[0.14em]',
                  REEL_STATUS_STYLES[reel.status],
                )}
              >
                {REEL_STATUS_LABEL[reel.status]}
              </span>
              <span className="num-mono text-xs font-semibold text-primary">{reel.views}</span>
            </div>
          </article>
        ))}
      </div>

      <div className="rounded-lg border border-primary/30 bg-primary/8 px-4 py-3">
        <div className="label-mono mb-1 text-primary">Konkurrenz-Insight</div>
        <p className="text-sm text-foreground/90">{detail.insight}</p>
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────────
// Sales

const LEAD_STAGE_STYLES: Record<SalesLead['stage'], string> = {
  qualifiziert: 'border-muted-foreground/30 bg-muted/20 text-muted-foreground',
  'follow-up': 'border-warn/40 bg-warn/10 text-warn',
  hot: 'border-primary/50 bg-primary/15 text-primary',
};

function SalesBody({ detail }: { detail: SalesDetail }) {
  return (
    <div className="space-y-6">
      <KpiRow kpis={detail.kpis} />

      <div className="grid gap-5 lg:grid-cols-5">
        <ChartCard
          title="Pipeline nach Stage"
          hint="58 Leads · 84.5k €"
          className="lg:col-span-2"
        >
          <BarChart
            data={detail.pipeline}
            margin={{ top: 5, right: 12, left: 0, bottom: 0 }}
            layout="vertical"
          >
            <CartesianGrid stroke={C_GRID} horizontal={false} />
            <XAxis type="number" stroke={C_AXIS} fontSize={10} tickLine={false} axisLine={false} />
            <YAxis
              type="category"
              dataKey="stage"
              stroke={C_AXIS}
              fontSize={10}
              tickLine={false}
              axisLine={false}
              width={70}
            />
            <Bar dataKey="count" fill={C_PRIMARY} radius={[0, 4, 4, 0]} />
          </BarChart>
        </ChartCard>

        <ChartCard title="Forecast vs. Pipeline" hint="6 KW" className="lg:col-span-3">
          <LineChart data={detail.forecast} margin={{ top: 5, right: 12, left: 0, bottom: 0 }}>
            <CartesianGrid stroke={C_GRID} vertical={false} />
            <XAxis dataKey="label" stroke={C_AXIS} fontSize={10} tickLine={false} axisLine={false} />
            <YAxis
              stroke={C_AXIS}
              fontSize={10}
              tickLine={false}
              axisLine={false}
              width={42}
              tickFormatter={(v) => `${Math.round(v / 1000)}k`}
            />
            <Legend wrapperStyle={{ fontSize: 10, color: C_MUTED }} iconType="circle" />
            <Line
              type="monotone"
              dataKey="a"
              name="Forecast"
              stroke={C_PRIMARY}
              strokeWidth={2}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="b"
              name="Pipeline"
              stroke={C_OK}
              strokeWidth={2}
              dot={false}
              strokeDasharray="4 4"
            />
          </LineChart>
        </ChartCard>
      </div>

      <div className="space-y-2">
        <div className="label-mono mb-2 text-primary">Top-Leads</div>
        {detail.leads.map((lead) => (
          <div
            key={lead.name}
            className="flex items-center justify-between rounded-lg border border-border/60 bg-background/40 px-4 py-3"
          >
            <span className="text-sm text-foreground/95">{lead.name}</span>
            <div className="flex items-center gap-4">
              <span className="num-mono text-sm font-semibold text-primary">{lead.value}</span>
              <span
                className={cn(
                  'inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] uppercase tracking-[0.14em]',
                  LEAD_STAGE_STYLES[lead.stage],
                )}
              >
                {lead.stage}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────────
// Finance

const INVOICE_STATUS_STYLES: Record<FinanceInvoice['status'], string> = {
  offen: 'border-warn/40 bg-warn/10 text-warn',
  bezahlt: 'border-ok/40 bg-ok/10 text-ok',
  'überfällig': 'border-destructive/40 bg-destructive/10 text-destructive',
};

function FinanceBody({ detail }: { detail: FinanceDetail }) {
  const totalExpenses = detail.expensesBreakdown.reduce((s, e) => s + e.value, 0);

  return (
    <div className="space-y-6">
      <KpiRow kpis={detail.kpis} />

      <div className="grid gap-5 lg:grid-cols-5">
        <ChartCard title="Cashflow (Income vs Expenses)" hint="letzte 7 Monate" className="lg:col-span-3">
          <AreaChart data={detail.cashflow} margin={{ top: 5, right: 12, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="finIncome" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={C_OK} stopOpacity={0.45} />
                <stop offset="100%" stopColor={C_OK} stopOpacity={0} />
              </linearGradient>
              <linearGradient id="finExpense" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={C_PRIMARY} stopOpacity={0.45} />
                <stop offset="100%" stopColor={C_PRIMARY} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke={C_GRID} vertical={false} />
            <XAxis dataKey="label" stroke={C_AXIS} fontSize={10} tickLine={false} axisLine={false} />
            <YAxis
              stroke={C_AXIS}
              fontSize={10}
              tickLine={false}
              axisLine={false}
              width={42}
              tickFormatter={(v) => `${Math.round(v / 1000)}k`}
            />
            <Legend wrapperStyle={{ fontSize: 10, color: C_MUTED }} iconType="circle" />
            <Area
              type="monotone"
              dataKey="a"
              name="Income"
              stroke={C_OK}
              strokeWidth={2}
              fill="url(#finIncome)"
            />
            <Area
              type="monotone"
              dataKey="b"
              name="Expenses"
              stroke={C_PRIMARY}
              strokeWidth={2}
              fill="url(#finExpense)"
            />
          </AreaChart>
        </ChartCard>

        <div className="rounded-xl border border-border/60 bg-background/40 p-5 lg:col-span-2">
          <div className="mb-4 flex items-baseline justify-between">
            <div className="label-mono text-primary">Expenses-Breakdown</div>
            <div className="num-mono text-[10px] text-muted-foreground">
              {totalExpenses.toLocaleString('de-DE')} €
            </div>
          </div>
          <ul className="space-y-3">
            {detail.expensesBreakdown.map((e) => {
              const pct = Math.round((e.value / totalExpenses) * 100);
              return (
                <li key={e.label}>
                  <div className="mb-1 flex items-center justify-between text-[11px]">
                    <span className="text-foreground/90">{e.label}</span>
                    <span className="num-mono text-muted-foreground">
                      {e.value.toLocaleString('de-DE')} €
                    </span>
                  </div>
                  <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted/30">
                    <div
                      className="h-full rounded-full bg-primary"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      </div>

      <div className="space-y-2">
        <div className="label-mono mb-2 text-primary">Offene & letzte Rechnungen</div>
        {detail.invoices.map((inv) => (
          <div
            key={inv.client}
            className="flex items-center justify-between rounded-lg border border-border/60 bg-background/40 px-4 py-3"
          >
            <div>
              <div className="text-sm text-foreground/95">{inv.client}</div>
              <div className="num-mono text-xs text-muted-foreground">{inv.amount}</div>
            </div>
            <span
              className={cn(
                'inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] uppercase tracking-[0.14em]',
                INVOICE_STATUS_STYLES[inv.status],
              )}
            >
              {inv.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────────
// Operations

const CALL_TYPE_STYLES: Record<OperationsDetail['calls'][number]['type'], string> = {
  sales: 'border-primary/40 bg-primary/10 text-primary',
  sync: 'border-warn/40 bg-warn/10 text-warn',
  onboarding: 'border-ok/40 bg-ok/10 text-ok',
};

const CALL_TYPE_LABEL: Record<OperationsDetail['calls'][number]['type'], string> = {
  sales: 'Sales',
  sync: 'Sync',
  onboarding: 'Onboarding',
};

function OperationsBody({ detail }: { detail: OperationsDetail }) {
  return (
    <div className="space-y-6">
      <KpiRow kpis={detail.kpis} />

      <div className="grid gap-5 lg:grid-cols-5">
        <ChartCard title="Arbeitslast diese Woche" hint="Std/Tag" className="lg:col-span-3">
          <BarChart data={detail.weekLoad} margin={{ top: 5, right: 12, left: 0, bottom: 0 }}>
            <CartesianGrid stroke={C_GRID} vertical={false} />
            <XAxis dataKey="label" stroke={C_AXIS} fontSize={10} tickLine={false} axisLine={false} />
            <YAxis stroke={C_AXIS} fontSize={10} tickLine={false} axisLine={false} width={28} />
            <Bar dataKey="value" radius={[4, 4, 0, 0]}>
              {detail.weekLoad.map((d, i) => (
                <Cell
                  key={i}
                  fill={d.value >= 8 ? C_WARN : d.value >= 5 ? C_PRIMARY : C_PRIMARY_SOFT}
                />
              ))}
            </Bar>
          </BarChart>
        </ChartCard>

        <div className="space-y-4 lg:col-span-2">
          <div className="rounded-xl border border-border/60 bg-background/40 p-5">
            <div className="label-mono mb-3 text-primary">Task-Progress</div>
            <ul className="space-y-3">
              {detail.tasks.map((t) => {
                const pct = Math.round((t.done / t.total) * 100);
                return (
                  <li key={t.label}>
                    <div className="mb-1 flex items-center justify-between text-[11px]">
                      <span className="text-foreground/90">{t.label}</span>
                      <span className="num-mono text-muted-foreground">
                        {t.done} / {t.total}
                      </span>
                    </div>
                    <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted/30">
                      <div className="h-full rounded-full bg-primary" style={{ width: `${pct}%` }} />
                    </div>
                  </li>
                );
              })}
            </ul>
          </div>

          <div className="rounded-xl border border-border/60 bg-background/40 p-5">
            <div className="label-mono mb-2 text-primary">Mail-Triage</div>
            <div className="flex items-baseline gap-4">
              <div>
                <div className="num-mono text-2xl font-semibold leading-none text-foreground">
                  {detail.mail.important}
                </div>
                <div className="label-mono mt-1 text-[9px]">wichtig</div>
              </div>
              <div>
                <div className="num-mono text-2xl font-semibold leading-none text-muted-foreground">
                  {detail.mail.archived}
                </div>
                <div className="label-mono mt-1 text-[9px]">archiviert</div>
              </div>
              <div className="ml-auto text-right">
                <div className="num-mono text-lg font-semibold leading-none text-ok">
                  {detail.mail.replyRate}
                </div>
                <div className="label-mono mt-1 text-[9px]">reply-rate</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div>
        <div className="label-mono mb-3 text-primary">Calls heute</div>
        <div className="space-y-2">
          {detail.calls.map((c) => (
            <div
              key={c.time}
              className="flex items-center gap-4 rounded-lg border border-border/60 bg-background/40 px-4 py-3"
            >
              <span className="num-mono w-14 text-sm font-semibold text-primary">{c.time}</span>
              <span className="flex-1 text-sm text-foreground/95">{c.with}</span>
              <span
                className={cn(
                  'inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] uppercase tracking-[0.14em]',
                  CALL_TYPE_STYLES[c.type],
                )}
              >
                {CALL_TYPE_LABEL[c.type]}
              </span>
              <span className="rounded-md border border-primary/30 bg-primary/10 px-2 py-0.5 text-[10px] uppercase tracking-[0.14em] text-primary">
                Briefing
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-lg border border-primary/30 bg-primary/8 px-4 py-3">
        <div className="label-mono mb-1 text-primary">Top-Prio</div>
        <p className="text-sm text-foreground/95">{detail.topPrio}</p>
      </div>
    </div>
  );
}
