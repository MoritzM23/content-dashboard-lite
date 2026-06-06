import type { HashtagPerformance } from '@/lib/types';
import { fmtNum, fmtPct } from '@/lib/format';

interface HashtagGridProps {
  hashtags: HashtagPerformance[];
}

export function HashtagGrid({ hashtags }: HashtagGridProps) {
  if (!hashtags.length) {
    return (
      <p className="text-sm text-muted-foreground">
        Hashtag-Performance braucht Tags die mindestens 2× verwendet wurden.
      </p>
    );
  }

  return (
    <div className="grid grid-cols-[repeat(auto-fill,minmax(220px,1fr))] gap-2">
      {hashtags.map((t) => (
        <div
          key={t.tag}
          className="rounded-lg border border-border bg-card/40 px-3 py-3 flex flex-col gap-1.5"
        >
          <div className="font-mono text-sm text-primary font-semibold">#{t.tag}</div>
          <div className="flex gap-3 text-xs text-muted-foreground font-mono">
            <span className="text-ok font-semibold">{fmtPct(t.avg_er)} Ø ER</span>
            <span>{fmtNum(t.avg_views)} Ø views</span>
            <span>{t.count}×</span>
          </div>
        </div>
      ))}
    </div>
  );
}
