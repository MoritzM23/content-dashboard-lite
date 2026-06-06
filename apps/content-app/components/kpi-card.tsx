interface KpiCardProps {
  label: string;
  value: string | number;
  hint?: string;
  trend?: 'up' | 'down' | 'flat';
}

export function KpiCard({ label, value, hint, trend }: KpiCardProps) {
  const trendColor =
    trend === 'up'
      ? 'text-ok'
      : trend === 'down'
        ? 'text-destructive'
        : 'text-muted-foreground';
  return (
    <div className="rounded-xl border border-border bg-card/40 px-4 py-4">
      <div className="label-mono mb-2 text-[10px]">{label}</div>
      <div className="text-2xl font-semibold tracking-tight num-mono leading-none">
        {value}
      </div>
      {hint && <div className={`mt-1.5 text-[10px] num-mono ${trendColor}`}>{hint}</div>}
    </div>
  );
}
