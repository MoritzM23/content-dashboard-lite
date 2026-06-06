'use client';

import { useState } from 'react';
import { ExternalLink, Plus, Play, Sparkles, Users } from 'lucide-react';
import { toast } from 'sonner';
import { useRouter } from 'next/navigation';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { fmtNum, fmtPct } from '@/lib/format';
import type { MarketCreator } from '@/lib/types';

interface DiscoveryCardProps {
  creator: MarketCreator;
}

function similarityTone(s: number | undefined): string {
  if (s == null) return 'text-muted-foreground bg-muted/20 border-border';
  if (s >= 90) return 'text-ok bg-ok/15 border-ok/40';
  if (s >= 70) return 'text-ok bg-ok/10 border-ok/30';
  if (s >= 50) return 'text-primary bg-primary/10 border-primary/30';
  return 'text-warn bg-warn/10 border-warn/30';
}

export function DiscoveryCard({ creator }: DiscoveryCardProps) {
  const router = useRouter();
  const [adding, setAdding] = useState(false);

  const isTracked = creator.source === 'tracked';
  const sim = creator.similarity_score;
  const reason = creator.similarity_reason || '';
  const topReels = creator.top_reels ?? [];

  async function handleAdd() {
    if (adding) return;
    setAdding(true);
    const res = await api.addCreator(creator.handle);
    if ('ok' in res) {
      toast.success(`@${creator.handle} hinzugefügt`);
      router.refresh();
    } else {
      toast.error(res.error || 'Hinzufügen fehlgeschlagen');
    }
    setAdding(false);
  }

  return (
    <article className="rounded-xl border border-border bg-card/40 p-4 flex flex-col gap-3">
      <header className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <a
            href={`https://instagram.com/${creator.handle}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-sm font-semibold hover:text-primary transition-colors"
          >
            <span className="truncate">@{creator.handle}</span>
            <ExternalLink className="size-3.5 opacity-60 shrink-0" />
          </a>
          <div className="flex items-center gap-1.5 mt-1">
            <span
              className={[
                'font-mono text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded border',
                isTracked
                  ? 'text-primary bg-primary/10 border-primary/30'
                  : 'text-foreground/70 bg-card/60 border-border',
              ].join(' ')}
            >
              {isTracked ? (
                <span className="inline-flex items-center gap-1">
                  <Users className="size-2.5" /> Tracked
                </span>
              ) : (
                'Neu'
              )}
            </span>
            <Badge
              variant="outline"
              className="font-mono text-[9px] uppercase"
            >
              {creator.language ?? 'unknown'}
            </Badge>
          </div>
        </div>
        <div
          className={`shrink-0 inline-flex items-center gap-1 px-2 py-1 rounded-md border ${similarityTone(sim)} font-mono text-xs`}
          title="Ähnlichkeit zu deinem Profil (0-100)"
        >
          <Sparkles className="size-3" />
          <span className="num-mono font-semibold">{sim ?? '—'}</span>
        </div>
      </header>

      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-muted-foreground num-mono">
        {creator.avg_views != null && (
          <span>Ø {fmtNum(creator.avg_views)} Views</span>
        )}
        {creator.avg_engagement_rate != null && (
          <span className="text-ok">ER {fmtPct(creator.avg_engagement_rate)}</span>
        )}
        {creator.reels_count != null && (
          <span>{creator.reels_count} Reels</span>
        )}
      </div>

      {reason && (
        <p className="text-xs text-foreground/85 leading-relaxed">{reason}</p>
      )}

      {topReels.length > 0 && (
        <div className="space-y-2 border-t border-border pt-2.5">
          <div className="label-mono text-[9px] flex items-center gap-1">
            <Play className="size-2.5" /> Top-Reels (Empfehlung zum Replizieren)
          </div>
          <ul className="space-y-2">
            {topReels.slice(0, 3).map((r, i) => (
              <li
                key={i}
                className="rounded-md border border-border bg-background/40 p-2 space-y-1.5"
              >
                <div className="flex items-center gap-2 text-[10px] font-mono">
                  <span className="text-ok font-semibold">
                    {fmtPct(r.engagement_rate)} ER
                  </span>
                  <span className="text-muted-foreground">
                    · {fmtNum(r.views)} Views
                  </span>
                  {r.topic_tag && (
                    <span className="text-primary uppercase tracking-wider px-1 py-0.5 rounded bg-primary/10 border border-primary/30">
                      {r.topic_tag}
                    </span>
                  )}
                  {r.hook_score != null && (
                    <span className="text-foreground/80">
                      Hook {r.hook_score}/10
                    </span>
                  )}
                  {r.hook_type && (
                    <span className="text-muted-foreground italic">
                      · {r.hook_type}
                    </span>
                  )}
                  <a
                    href={r.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-auto text-muted-foreground hover:text-primary"
                    title="Auf Instagram öffnen"
                  >
                    <ExternalLink className="size-3" />
                  </a>
                </div>
                {r.caption_snippet && (
                  <p className="text-[11px] text-foreground/85 leading-snug line-clamp-2">
                    {r.caption_snippet}
                  </p>
                )}
                {r.summary && (
                  <p className="text-[11px] text-muted-foreground leading-snug italic line-clamp-2">
                    {r.summary}
                  </p>
                )}
                {r.why_it_worked && (
                  <p className="text-[11px] text-foreground/70 leading-snug line-clamp-3 border-l-2 border-primary/40 pl-2">
                    {r.why_it_worked}
                  </p>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {!isTracked && (
        <div className="flex items-center justify-between gap-2 pt-2 mt-auto border-t border-border">
          <Button
            variant="default"
            size="sm"
            onClick={handleAdd}
            disabled={adding}
          >
            <Plus className="size-3.5" />
            {adding ? 'Hinzufügen…' : 'Tracken'}
          </Button>
          {creator.final_score != null && (
            <span className="font-mono text-[10px] text-muted-foreground/60">
              Rang: {Math.round(creator.final_score)}
            </span>
          )}
        </div>
      )}
    </article>
  );
}
