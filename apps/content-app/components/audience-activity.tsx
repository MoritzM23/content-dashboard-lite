'use client';

import { useMemo } from 'react';
import { Clock, Calendar, Sparkles } from 'lucide-react';
import type { CreatorStats, Reel } from '@/lib/types';

interface Props {
  ownStats?: CreatorStats;
  ownReels: Reel[];
  /** competitors: aktuell ungenutzt, alter Markt-Vergleich-Block wurde entfernt
   * weil er sich mit dem Hauptstellrad überschnitten hat und vom User abgewählt
   * wurde. Prop bleibt für Type-Compat, wird ignoriert. */
  competitors?: Record<string, CreatorStats>;
}

/** Zeitfenster: nur Reels der letzten N Tage in die Slot-Analyse, damit ältere
 * Reels mit akkumulierten Views die ER-Statistik nicht verzerren. 60 Tage ist
 * ein Kompromiss zwischen Sample-Größe und Aktualität. */
const SLOT_WINDOW_DAYS = 60;

const DAYS_EN = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const DAYS_DE = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'];
const DAYS_SHORT = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];

type TimeBlock = { label: string; from: number; to: number };
const TIME_BLOCKS: TimeBlock[] = [
  { label: 'Morgen', from: 6, to: 9 },
  { label: 'Vormittag', from: 10, to: 12 },
  { label: 'Mittag', from: 13, to: 15 },
  { label: 'Nachmittag', from: 16, to: 18 },
  { label: 'Abend', from: 19, to: 22 },
  { label: 'Nacht', from: 23, to: 5 },
];

function dowDe(en: string): string {
  const i = DAYS_EN.indexOf(en);
  return i >= 0 ? DAYS_DE[i] : en;
}

type SlotAgg = {
  dow: string;
  hour: number;
  count: number;
  avg_er: number;
  avg_views: number;
};

function aggregateSlots(reels: Reel[]): SlotAgg[] {
  const map = new Map<string, { er: number[]; views: number[]; dow: string; hour: number }>();
  for (const r of reels) {
    if (!r.posted_dayofweek || r.posted_hour == null) continue;
    const key = `${r.posted_dayofweek}_${r.posted_hour}`;
    const cur = map.get(key) ?? { er: [], views: [], dow: r.posted_dayofweek, hour: r.posted_hour };
    cur.er.push(r.engagement_rate ?? 0);
    cur.views.push(r.views ?? 0);
    map.set(key, cur);
  }
  return Array.from(map.values()).map((s) => ({
    dow: s.dow,
    hour: s.hour,
    count: s.er.length,
    avg_er: s.er.reduce((a, b) => a + b, 0) / s.er.length,
    avg_views: s.views.reduce((a, b) => a + b, 0) / s.views.length,
  }));
}

/** Top-Slots by metric, mit Mindest-Sample-Filter. Fallback ohne Filter
 * wenn kein Slot die Schwelle erreicht (damit User immer was sieht). */
function topSlotsByMetric(
  slots: SlotAgg[],
  metric: 'er' | 'views' | 'count',
  n = 3,
  minCount = 2,
): SlotAgg[] {
  const sorter: (a: SlotAgg, b: SlotAgg) => number =
    metric === 'er'
      ? (a, b) => b.avg_er - a.avg_er
      : metric === 'views'
        ? (a, b) => b.avg_views - a.avg_views
        : (a, b) => b.count - a.count;

  if (metric === 'count') {
    return [...slots].sort(sorter).slice(0, n);
  }
  // Erst mit Mindest-Sample probieren
  const filtered = slots.filter((s) => s.count >= minCount).sort(sorter).slice(0, n);
  if (filtered.length > 0) return filtered;
  // Fallback ohne Filter (Hinweis: zu wenige Reels pro Slot)
  return [...slots].sort(sorter).slice(0, n);
}

function aggregateByBlock(reels: Reel[]) {
  const blocks = TIME_BLOCKS.map((b) => ({ ...b, er: [] as number[], count: 0 }));
  for (const r of reels) {
    if (r.posted_hour == null) continue;
    const h = r.posted_hour;
    for (const b of blocks) {
      const inRange =
        b.from <= b.to ? h >= b.from && h <= b.to : h >= b.from || h <= b.to;
      if (inRange) {
        b.er.push(r.engagement_rate ?? 0);
        b.count++;
        break;
      }
    }
  }
  return blocks.map((b) => ({
    label: b.label,
    range: b.from <= b.to ? `${b.from}-${b.to}` : `${b.from}-${b.to + 24}`,
    count: b.count,
    avg_er: b.er.length ? b.er.reduce((a, b) => a + b, 0) / b.er.length : 0,
  }));
}

function SlotColumn({
  title,
  hint,
  slots,
  metric,
  tone,
}: {
  title: string;
  hint: string;
  slots: SlotAgg[];
  metric: 'er' | 'views' | 'count';
  tone: 'ok' | 'primary' | 'muted';
}) {
  const toneClass =
    tone === 'ok'
      ? 'text-ok'
      : tone === 'primary'
        ? 'text-primary'
        : 'text-foreground/70';
  function fmtMetric(s: SlotAgg): string {
    if (metric === 'er') return `${s.avg_er.toFixed(2)}%`;
    if (metric === 'views') {
      const v = Math.round(s.avg_views);
      if (v >= 1000) return `${(v / 1000).toFixed(1)}k`;
      return String(v);
    }
    return `${s.count}×`;
  }
  return (
    <div className="rounded-lg border border-border bg-card/30 p-3 space-y-2">
      <div className="flex items-baseline justify-between gap-2">
        <span className={`label-mono text-[10px] ${toneClass}`}>{title}</span>
      </div>
      <p className="text-[10px] text-muted-foreground/70 leading-snug">{hint}</p>
      <ul className="space-y-1 pt-1">
        {slots.length === 0 ? (
          <li className="text-xs text-muted-foreground">Noch keine Daten</li>
        ) : (
          slots.map((s, i) => (
            <li
              key={`${s.dow}-${s.hour}-${metric}`}
              className="flex items-center gap-2 text-xs"
            >
              <span className="num-mono text-[10px] text-muted-foreground w-3 shrink-0">
                {i + 1}.
              </span>
              <span className="flex-1 truncate">
                {dowDe(s.dow)}{' '}
                <span className="num-mono">
                  {String(s.hour).padStart(2, '0')}:00
                </span>
              </span>
              <span className={`num-mono font-semibold shrink-0 ${toneClass}`}>
                {fmtMetric(s)}
              </span>
              <span className="num-mono text-[10px] text-muted-foreground/60 shrink-0 w-6 text-right">
                ·{s.count}
              </span>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}

function Bar({
  label,
  value,
  max,
  count,
  best,
  hint,
}: {
  label: string;
  value: number;
  max: number;
  count: number;
  best: boolean;
  hint?: string;
}) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0;
  return (
    <div className="grid grid-cols-[100px_1fr_80px] gap-2 items-center text-xs">
      <span className={`truncate ${best ? 'font-semibold text-ok' : 'text-foreground/85'}`}>
        {label}
        {hint && <span className="text-muted-foreground/60 ml-1.5 font-mono text-[10px]">{hint}</span>}
      </span>
      <div className="h-2 bg-card/60 rounded-full overflow-hidden">
        <div
          className={`h-full ${best ? 'bg-ok' : 'bg-primary/60'} rounded-full transition-all`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="num-mono text-[11px] text-foreground/80 text-right">
        {value.toFixed(2)}%
        <span className="text-muted-foreground/60 ml-1.5">·{count}</span>
      </span>
    </div>
  );
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export function AudienceActivity({ ownStats, ownReels, competitors: _ignored }: Props) {
  // Fenster: nur Reels der letzten 60 Tage, damit alte Reels mit viel
  // akkumulierten Views die ER-Statistik nicht verzerren. Ein Reel vom 1. April
  // hat heute >5x mehr Views als am Tag des Postings -> künstlich niedrige ER.
  // Frische Reels sind als Slot-Indikator aussagekräftiger.
  const recentReels = useMemo(() => {
    if (ownReels.length === 0) return [];
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - SLOT_WINDOW_DAYS);
    const cutoffStr = cutoff.toISOString().slice(0, 10);
    const filtered = ownReels.filter((r) => (r.posted ?? '').slice(0, 10) >= cutoffStr);
    // Fallback: wenn weniger als 6 Reels im Fenster sind, alle nehmen
    return filtered.length >= 6 ? filtered : ownReels;
  }, [ownReels]);

  const usingWindow = recentReels.length < ownReels.length;

  const allSlots = useMemo(() => aggregateSlots(recentReels), [recentReels]);
  const slotsByEr = useMemo(() => topSlotsByMetric(allSlots, 'er', 3, 2), [allSlots]);
  const slotsByViews = useMemo(() => topSlotsByMetric(allSlots, 'views', 3, 2), [allSlots]);
  const slotsByCount = useMemo(() => topSlotsByMetric(allSlots, 'count', 3, 1), [allSlots]);
  // Hinweis wenn Sample-Size schwach: kein Slot hatte 2+ Reels
  const lowSample = useMemo(
    () => allSlots.length > 0 && allSlots.every((s) => s.count < 2),
    [allSlots],
  );
  const blocks = useMemo(() => aggregateByBlock(recentReels), [recentReels]);

  // Day-of-week aggregation aus den gefensterten Reels.
  // Sammelt sowohl ER (Likes+Comments/Views) als auch Ø Views pro Wochentag.
  // Views sind robuster gegen den Akkumulations-Bias bei alten Reels, weil
  // sie absolut sind statt durch Views geteilt zu werden. Folgt der PDF-Logik
  // "Reichweite ist das Volumen oben im Funnel" (Stufe 2).
  const dowAgg = useMemo(() => {
    const map = new Map<string, { er: number[]; views: number[]; count: number }>();
    for (const r of recentReels) {
      if (!r.posted_dayofweek) continue;
      const cur = map.get(r.posted_dayofweek) ?? { er: [], views: [], count: 0 };
      cur.er.push(r.engagement_rate ?? 0);
      cur.views.push(r.views ?? 0);
      cur.count++;
      map.set(r.posted_dayofweek, cur);
    }
    return DAYS_EN.map((d, i) => {
      const cur = map.get(d);
      return {
        day_en: d,
        day_de: DAYS_DE[i],
        avg_er: cur && cur.er.length ? cur.er.reduce((a, b) => a + b, 0) / cur.er.length : 0,
        avg_views: cur && cur.views.length ? cur.views.reduce((a, b) => a + b, 0) / cur.views.length : 0,
        count: cur?.count ?? 0,
      };
    });
  }, [recentReels]);

  const bestDowEr = dowAgg.reduce((acc, d) => (d.avg_er > acc.avg_er ? d : acc), dowAgg[0]);
  const bestDowViews = dowAgg.reduce((acc, d) => (d.avg_views > acc.avg_views ? d : acc), dowAgg[0]);
  const bestBlock = blocks.reduce((acc, b) => (b.avg_er > acc.avg_er ? b : acc), blocks[0]);
  const maxDowEr = Math.max(...dowAgg.map((d) => d.avg_er), 0.01);
  const maxDowViews = Math.max(...dowAgg.map((d) => d.avg_views), 1);
  const maxBlockEr = Math.max(...blocks.map((b) => b.avg_er), 0.01);

  if (ownReels.length < 3) {
    return (
      <p className="text-sm text-muted-foreground py-6 text-center">
        Brauche mindestens 3 Reels mit Posting-Zeitstempel für Audience-Analyse.
      </p>
    );
  }

  return (
    <div className="space-y-6">
      {usingWindow && (
        <p className="text-[10px] text-muted-foreground bg-card/40 border border-border rounded px-2.5 py-1.5">
          Slot-Analyse basiert nur auf Reels der letzten {SLOT_WINDOW_DAYS} Tage
          ({recentReels.length} von {ownReels.length}). Ältere Reels verzerren die
          ER-Statistik, weil ihre akkumulierten Views künstlich niedrig wirken
          lassen.
        </p>
      )}

      {/* Top-Slots dreifach: ER / Views / Häufigkeit */}
      <div className="space-y-3">
        <div className="label-mono text-[10px] flex items-center gap-1.5 text-primary">
          <Sparkles className="size-3" /> Top-Posting-Slots deiner Reels
        </div>
        {lowSample && (
          <p className="text-[10px] text-warn bg-warn/10 border border-warn/30 rounded px-2.5 py-1.5">
            Wenig Daten: kein Slot hat 2+ Reels. Rankings unten basieren auf Einzel-Reels, also statistisch unzuverlässig. Mehr Reels in gleichen Slot posten erhöht die Aussagekraft.
          </p>
        )}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <SlotColumn
            title="Beste ER"
            hint="Engagement-Rate (Likes+Comments / Views)"
            slots={slotsByEr}
            metric="er"
            tone="ok"
          />
          <SlotColumn
            title="Meiste Views"
            hint="Wo der Algo dich am stärksten ausspielt"
            slots={slotsByViews}
            metric="views"
            tone="primary"
          />
          <SlotColumn
            title="Häufigster Slot"
            hint="Wo du konsistent postest"
            slots={slotsByCount}
            metric="count"
            tone="muted"
          />
        </div>
      </div>

      {/* Wochentage: ER + Views nebeneinander, damit der Akkumulations-Bias
         sichtbar wird. Frische Reels haben höhere ER (Mittwoch im Mai), reichere
         Reels haben höhere Views (oft Samstag). */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div>
          <div className="label-mono text-[10px] mb-2 flex items-center gap-1.5">
            <Calendar className="size-3" /> Wochentag (Ø ER)
          </div>
          <div className="space-y-1">
            {dowAgg
              .filter((d) => d.count > 0)
              .sort((a, b) => b.avg_er - a.avg_er)
              .map((d) => (
                <Bar
                  key={d.day_en}
                  label={d.day_de}
                  value={d.avg_er}
                  max={maxDowEr}
                  count={d.count}
                  best={d.day_en === bestDowEr.day_en}
                />
              ))}
          </div>
          {bestDowEr.count > 0 && (
            <p className="text-[11px] text-muted-foreground mt-2">
              Beste ER:{' '}
              <span className="text-ok font-semibold">{bestDowEr.day_de}</span> mit Ø{' '}
              <span className="num-mono">{bestDowEr.avg_er.toFixed(2)}%</span>.
            </p>
          )}
        </div>

        <div>
          <div className="label-mono text-[10px] mb-2 flex items-center gap-1.5">
            <Calendar className="size-3" /> Wochentag (Ø Views)
          </div>
          <div className="space-y-1">
            {dowAgg
              .filter((d) => d.count > 0)
              .sort((a, b) => b.avg_views - a.avg_views)
              .map((d) => {
                const pct = maxDowViews > 0 ? Math.min(100, (d.avg_views / maxDowViews) * 100) : 0;
                const best = d.day_en === bestDowViews.day_en;
                return (
                  <div key={d.day_en} className="grid grid-cols-[100px_1fr_80px] gap-2 items-center text-xs">
                    <span className={best ? 'font-semibold text-ok' : 'text-foreground/85'}>
                      {d.day_de}
                    </span>
                    <div className="h-2 bg-card/60 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${best ? 'bg-ok' : 'bg-primary/60'} rounded-full transition-all`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="num-mono text-[11px] text-foreground/80 text-right">
                      {d.avg_views >= 1000 ? `${(d.avg_views / 1000).toFixed(1)}k` : Math.round(d.avg_views)}
                      <span className="text-muted-foreground/60 ml-1.5">·{d.count}</span>
                    </span>
                  </div>
                );
              })}
          </div>
          {bestDowViews.count > 0 && (
            <p className="text-[11px] text-muted-foreground mt-2">
              Meiste Views:{' '}
              <span className="text-ok font-semibold">{bestDowViews.day_de}</span> mit Ø{' '}
              <span className="num-mono">
                {bestDowViews.avg_views >= 1000 ? `${(bestDowViews.avg_views / 1000).toFixed(1)}k` : Math.round(bestDowViews.avg_views)}
              </span>{' '}
              Views.
            </p>
          )}
        </div>
      </div>

      {/* Tageszeit-Blöcke */}
      <div>
        <div className="label-mono text-[10px] mb-2 flex items-center gap-1.5">
          <Clock className="size-3" /> Tageszeit (Ø ER pro Block)
        </div>
        <div className="space-y-1">
          {blocks
            .filter((b) => b.count > 0)
            .sort((a, b) => b.avg_er - a.avg_er)
            .map((b) => (
              <Bar
                key={b.label}
                label={b.label}
                hint={`${b.range} Uhr`}
                value={b.avg_er}
                max={maxBlockEr}
                count={b.count}
                best={b.label === bestBlock.label}
              />
            ))}
        </div>
        {bestBlock.count > 0 && (
          <p className="text-[11px] text-muted-foreground mt-2">
            Beste Tageszeit:{' '}
            <span className="text-ok font-semibold">{bestBlock.label}</span> (
            {bestBlock.range} Uhr) mit Ø{' '}
            <span className="num-mono">{bestBlock.avg_er.toFixed(2)}%</span> ER.
          </p>
        )}
      </div>

    </div>
  );
}
