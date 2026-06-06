import { Sparkles } from 'lucide-react';
import type { TopicCluster } from '@/lib/types';
import { cn } from '@/lib/utils';

interface TopicClustersProps {
  clusters: TopicCluster | null | undefined;
  selfHandle: string;
}

export function TopicClusters({ clusters, selfHandle }: TopicClustersProps) {
  if (!clusters?.themes?.length) {
    return (
      <p className="text-sm text-muted-foreground">
        Themen-Cluster werden beim nächsten Tracker-Run erzeugt (KI-Analyse mit
        Sonnet über alle Reels). Cache:
        <code className="font-mono text-xs ml-1">
          05-reference/competitor-content/_ai_analysis/{selfHandle}_topics.json
        </code>
      </p>
    );
  }

  const winner = (clusters.theme_winner ?? '').toLowerCase();

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-2.5">
        {clusters.themes.map((t) => {
          const isWinner = (t.name ?? '').toLowerCase() === winner;
          return (
            <div
              key={t.name}
              className={cn(
                'rounded-xl border p-4',
                isWinner
                  ? 'border-ok/40 bg-ok/5'
                  : 'border-border bg-card/40'
              )}
            >
              <div className="flex items-center gap-2 mb-1.5">
                {isWinner && <Sparkles className="size-3.5 text-ok" />}
                <div className="font-semibold text-sm">{t.name}</div>
              </div>
              <div className="font-mono text-[10px] text-muted-foreground tracking-wider uppercase">
                {(t.reel_shortcodes ?? []).length} Reels
                {t.avg_engagement_rate != null && (
                  <span className="ml-1.5 text-ok font-semibold">
                    {' '}
                    · {t.avg_engagement_rate.toFixed(2)}% ER
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {clusters.recommendation && (
        <div className="rounded-xl border border-primary/30 bg-primary/[0.06] p-5">
          <div className="label-mono text-primary mb-2.5">
            <Sparkles className="size-3 inline -mt-0.5 mr-1.5" />
            Empfehlung KI
          </div>
          <p className="text-sm leading-relaxed">{clusters.recommendation}</p>
          {clusters.gaps && clusters.gaps.length > 0 && (
            <div className="mt-3 pt-3 border-t border-primary/20">
              <div className="label-mono text-[10px] mb-2 text-muted-foreground">
                Ungenutzte Chancen
              </div>
              <ul className="text-sm text-muted-foreground space-y-1 list-disc pl-5">
                {clusters.gaps.map((g, i) => (
                  <li key={i}>{g}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
