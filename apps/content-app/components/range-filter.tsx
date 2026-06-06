'use client';

// 'today' wurde rausgenommen: zeigte typisch 0/0/0 wenn an dem Tag nichts
// gepostet wurde und wirkte deshalb wie ein Bug.
export type RangeKey = '7d' | '30d' | 'all';

const RANGES: Array<{ k: RangeKey; l: string }> = [
  { k: '7d', l: '7 Tage' },
  { k: '30d', l: '30 Tage' },
  { k: 'all', l: 'Gesamt' },
];

interface RangeFilterProps {
  value: RangeKey;
  onChange: (key: RangeKey) => void;
  counts?: Record<RangeKey, number>;
}

export function RangeFilter({ value, onChange, counts }: RangeFilterProps) {
  return (
    <div className="flex gap-1.5 flex-wrap">
      {RANGES.map((r) => {
        const active = value === r.k;
        const cnt = counts?.[r.k];
        return (
          <button
            key={r.k}
            onClick={() => onChange(r.k)}
            className={`px-4 py-2 rounded-lg text-xs font-medium border transition-colors ${
              active
                ? 'bg-primary/10 border-primary/40 text-primary'
                : 'bg-card/40 border-border text-muted-foreground hover:text-foreground hover:border-border/80'
            }`}
          >
            {r.l}
            {cnt != null && (
              <span className="ml-1.5 num-mono text-[11px] opacity-70">{cnt}</span>
            )}
          </button>
        );
      })}
    </div>
  );
}
