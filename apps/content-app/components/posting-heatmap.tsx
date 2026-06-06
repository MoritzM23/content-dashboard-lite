'use client';

import { useMemo, useState } from 'react';
import { Sparkles, Users } from 'lucide-react';
import type { Reel } from '@/lib/types';

interface PostingHeatmapProps {
  reels: Reel[];
  /** Optional: Markt-Reels (alle Konkurrenz-Reels) fuer Vergleich. */
  marketReels?: Reel[];
  bestHour?: number | null;
  bestDayofweek?: string | null;
}

const DAYS_EN = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday',
];
const DAYS_DE = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];

/** 6 Zeit-Buckets statt 24 einzelner Stunden — passt auf 13" ohne Scrollen. */
const BUCKETS = [
  { key: 'frueh', label: 'Frueh', hours: [6, 7, 8, 9], range: '06-10' },
  { key: 'vormittag', label: 'Vormittag', hours: [10, 11], range: '10-12' },
  { key: 'mittag', label: 'Mittag', hours: [12, 13], range: '12-14' },
  { key: 'nachm', label: 'Nachmittag', hours: [14, 15, 16, 17], range: '14-18' },
  { key: 'abend', label: 'Abend', hours: [18, 19, 20, 21], range: '18-22' },
  { key: 'nacht', label: 'Nacht', hours: [22, 23, 0, 1, 2, 3, 4, 5], range: '22-06' },
] as const;

type BucketKey = (typeof BUCKETS)[number]['key'];

function hourToBucket(hour: number): BucketKey | null {
  for (const b of BUCKETS) {
    if ((b.hours as readonly number[]).includes(hour)) return b.key;
  }
  return null;
}

type Cell = { ers: number[]; count: number };
type Grid = Map<string, Cell>;

function buildGrid(reels: Reel[]): Grid {
  const grid: Grid = new Map();
  for (const r of reels) {
    const dow = r.posted_dayofweek;
    const hour = r.posted_hour;
    if (!dow || hour == null) continue;
    const bucket = hourToBucket(hour);
    if (!bucket) continue;
    const key = `${dow}_${bucket}`;
    const cell = grid.get(key) ?? { ers: [], count: 0 };
    cell.ers.push(r.engagement_rate ?? 0);
    cell.count++;
    grid.set(key, cell);
  }
  return grid;
}

function cellAvg(cell: Cell | undefined): number {
  if (!cell || cell.count === 0) return 0;
  return cell.ers.reduce((a, b) => a + b, 0) / cell.count;
}

/** Top 3 Slots als Liste mit Begruendung. */
function topSlots(grid: Grid, minSamples: number = 1): Array<{
  day: string;
  bucket: string;
  range: string;
  avgEr: number;
  count: number;
}> {
  const items: Array<{ day: string; bucket: string; range: string; avgEr: number; count: number }> = [];
  for (let di = 0; di < DAYS_EN.length; di++) {
    for (const b of BUCKETS) {
      const cell = grid.get(`${DAYS_EN[di]}_${b.key}`);
      if (!cell || cell.count < minSamples) continue;
      items.push({
        day: DAYS_DE[di],
        bucket: b.label,
        range: b.range,
        avgEr: cellAvg(cell),
        count: cell.count,
      });
    }
  }
  items.sort((a, b) => b.avgEr - a.avgEr);
  return items.slice(0, 3);
}

export function PostingHeatmap({
  reels,
  marketReels,
  bestHour,
  bestDayofweek,
}: PostingHeatmapProps) {
  const [view, setView] = useState<'self' | 'market'>('self');
  const haveMarket = (marketReels?.length ?? 0) > 0;

  const activeReels = view === 'market' && haveMarket ? marketReels! : reels;
  const grid = useMemo(() => buildGrid(activeReels), [activeReels]);
  const allErs = Array.from(grid.values()).map(cellAvg);
  const maxEr = allErs.length ? Math.max(...allErs) : 1;
  const top = useMemo(() => topSlots(grid, view === 'self' ? 1 : 2), [grid, view]);

  if (!grid.size) {
    return (
      <div className="text-sm text-muted-foreground py-3">
        Heatmap braucht Reels mit Uhrzeit-Information. Fuellt sich beim
        naechsten Tracker-Run.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Toggle Self/Markt + Top-3-Slots */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-1.5 rounded-lg border border-border bg-card/40 p-0.5">
          <button
            type="button"
            onClick={() => setView('self')}
            className={[
              'inline-flex items-center gap-1.5 px-2.5 py-1 text-xs rounded-md transition-colors',
              view === 'self'
                ? 'bg-foreground text-background'
                : 'text-muted-foreground hover:text-foreground',
            ].join(' ')}
          >
            <Sparkles className="size-3" /> Dein Account
          </button>
          {haveMarket && (
            <button
              type="button"
              onClick={() => setView('market')}
              className={[
                'inline-flex items-center gap-1.5 px-2.5 py-1 text-xs rounded-md transition-colors',
                view === 'market'
                  ? 'bg-foreground text-background'
                  : 'text-muted-foreground hover:text-foreground',
              ].join(' ')}
            >
              <Users className="size-3" /> Markt (Konkurrenz)
            </button>
          )}
        </div>

        <div className="flex-1 min-w-[260px]">
          <div className="label-mono text-[10px] mb-1.5">Top-3 Slots</div>
          <ul className="text-xs space-y-0.5">
            {top.map((s, i) => (
              <li key={i} className="flex items-center gap-2">
                <span className="num-mono text-ok font-semibold w-12 text-right">
                  {s.avgEr.toFixed(2)}%
                </span>
                <span className="text-foreground/85">
                  {s.day}, {s.bucket} ({s.range} Uhr)
                </span>
                <span className="text-muted-foreground text-[10px]">
                  · {s.count} Reel{s.count > 1 ? 's' : ''}
                </span>
              </li>
            ))}
            {top.length === 0 && (
              <li className="text-muted-foreground">Noch nicht genug Daten.</li>
            )}
          </ul>
        </div>
      </div>

      {/* Grid: 7 Tage x 6 Buckets */}
      <div
        className="grid gap-[3px] text-[10px]"
        style={{ gridTemplateColumns: '52px repeat(6, 1fr)' }}
      >
        <div />
        {BUCKETS.map((b) => (
          <div
            key={b.key}
            className="text-center text-muted-foreground py-1 font-mono uppercase tracking-wider"
            title={`${b.range} Uhr`}
          >
            {b.label}
          </div>
        ))}
        {DAYS_EN.map((dow, di) => (
          <Row
            key={dow}
            label={DAYS_DE[di]}
            dow={dow}
            grid={grid}
            maxEr={maxEr}
          />
        ))}
      </div>

      <div className="text-[10px] text-muted-foreground leading-relaxed">
        Farb-Intensitaet = Ø Engagement-Rate (ER) der Reels in diesem Slot.
        Zahl in der Zelle ist Ø ER in Prozent.
        Punkt rechts oben = Anzahl Reels (Sample-Size).
        {(bestHour != null || bestDayofweek) && view === 'self' && (
          <>
            {' '}Tracker-Bester-Slot:{' '}
            <span className="text-ok font-semibold">
              {bestDayofweek
                ? DAYS_DE[DAYS_EN.indexOf(bestDayofweek)] ?? bestDayofweek
                : '—'}
              {bestHour != null && ` · ${bestHour}:00`}
            </span>
            .
          </>
        )}
      </div>
    </div>
  );
}

function Row({
  label,
  dow,
  grid,
  maxEr,
}: {
  label: string;
  dow: string;
  grid: Grid;
  maxEr: number;
}) {
  return (
    <>
      <div className="text-muted-foreground py-2 px-1 text-right text-[10px] font-mono uppercase tracking-wider">
        {label}
      </div>
      {BUCKETS.map((b) => {
        const cell = grid.get(`${dow}_${b.key}`);
        if (!cell || cell.count === 0) {
          return (
            <div
              key={b.key}
              className="h-9 rounded-md bg-muted/30 grid place-items-center text-muted-foreground/40 text-[9px]"
            >
              —
            </div>
          );
        }
        const er = cellAvg(cell);
        const intensity = maxEr > 0 ? Math.min(1, er / maxEr) : 0;
        const lvl = Math.max(1, Math.ceil(intensity * 5));
        const colors = [
          'bg-ok/10',
          'bg-ok/25',
          'bg-ok/45 text-foreground',
          'bg-ok/65 text-foreground',
          'bg-ok/85 text-background font-semibold',
        ];
        return (
          <div
            key={b.key}
            className={`relative h-9 rounded-md grid place-items-center text-xs num-mono ${colors[lvl - 1]}`}
            title={`${label} ${b.label} (${b.range} Uhr) · Ø ${er.toFixed(2)}% ER · ${cell.count} Reel${cell.count > 1 ? 's' : ''}`}
          >
            {er.toFixed(1)}
            <span className="absolute top-0.5 right-1 text-[8px] text-foreground/60 font-mono">
              {cell.count}
            </span>
          </div>
        );
      })}
    </>
  );
}
