'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { RefreshCw, Sparkles, TrendingUp, Target, Lightbulb, Trophy, Flame, ExternalLink } from 'lucide-react';
import { toast } from 'sonner';

import { Button } from '@/components/ui/button';
import { PageHeader } from '@/components/page-header';
import { SectionCard } from '@/components/section-card';
import { DiscoveryCard } from '@/components/discovery-card';
import { api } from '@/lib/api';
import { fmtDate, fmtNum, fmtPct } from '@/lib/format';
import type { Discovery, MarketCreator, MarketTopReel, MarketAnalysis } from '@/lib/types';

interface DiscoveryViewProps {
  discovery: Discovery | null;
  marketCreators: MarketCreator[];
  marketTopReels?: MarketTopReel[];
  marketAnalysis?: MarketAnalysis | null;
}

type TrendWindow = '7d' | '30d' | 'all';
type TrendSort = 'er' | 'views';

function MarketTopReelsFeed({ reels }: { reels: MarketTopReel[] }) {
  const [windowKey, setWindow] = useState<TrendWindow>('7d');
  const [sortKey, setSort] = useState<TrendSort>('er');
  const [hookType, setHookType] = useState<string>('');

  // Verfügbare Hook-Types für den Filter-Chip-Bar.
  const hookTypes = Array.from(
    new Set(reels.map((r) => r.hook_type).filter((h): h is string => Boolean(h))),
  ).sort();

  const filtered = reels.filter((r) => {
    if (windowKey !== 'all') {
      const cutoff = new Date();
      cutoff.setDate(cutoff.getDate() - (windowKey === '7d' ? 7 : 30));
      const cutoffStr = cutoff.toISOString().slice(0, 10);
      const posted = (r.posted ?? '').slice(0, 10);
      if (!posted || posted < cutoffStr) return false;
    }
    if (hookType && r.hook_type !== hookType) return false;
    return true;
  });

  const sorted = [...filtered].sort((a, b) =>
    sortKey === 'er'
      ? (b.engagement_rate ?? 0) - (a.engagement_rate ?? 0)
      : (b.views ?? 0) - (a.views ?? 0),
  );

  if (reels.length === 0) return null;

  return (
    <SectionCard
      title={`Trend-Hooks im Markt (${sorted.length}/${reels.length})`}
      description="Reels quer durch alle relevanten Creator als Inspiration. Filtere nach Zeitraum und Hook-Typ, sortiere nach ER oder Views. Klick öffnet auf Instagram."
      actions={<Flame className="size-4 text-primary" />}
    >
      <div className="flex flex-wrap items-center gap-4 mb-3 text-xs">
        <div className="inline-flex items-center gap-1 rounded-md border border-border bg-card/40 p-0.5">
          {(['7d', '30d', 'all'] as const).map((w) => (
            <button
              key={w}
              type="button"
              onClick={() => setWindow(w)}
              className={[
                'px-2.5 py-1 rounded transition-colors',
                windowKey === w
                  ? 'bg-foreground text-background'
                  : 'text-muted-foreground hover:text-foreground',
              ].join(' ')}
            >
              {w === 'all' ? 'all-time' : w}
            </button>
          ))}
        </div>
        <div className="inline-flex items-center gap-1 rounded-md border border-border bg-card/40 p-0.5">
          {(['er', 'views'] as const).map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setSort(s)}
              className={[
                'px-2.5 py-1 rounded transition-colors',
                sortKey === s
                  ? 'bg-foreground text-background'
                  : 'text-muted-foreground hover:text-foreground',
              ].join(' ')}
            >
              {s === 'er' ? 'nach ER' : 'nach Views'}
            </button>
          ))}
        </div>
        {hookTypes.length > 0 && (
          <div className="flex flex-wrap items-center gap-1">
            <button
              type="button"
              onClick={() => setHookType('')}
              className={[
                'px-2 py-1 rounded border text-[10px] transition-colors',
                hookType === ''
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-border text-muted-foreground hover:text-foreground',
              ].join(' ')}
            >
              alle Hooks
            </button>
            {hookTypes.map((h) => (
              <button
                key={h}
                type="button"
                onClick={() => setHookType(h)}
                className={[
                  'px-2 py-1 rounded border text-[10px] transition-colors uppercase tracking-wider',
                  hookType === h
                    ? 'border-primary bg-primary/10 text-primary'
                    : 'border-border text-muted-foreground hover:text-foreground',
                ].join(' ')}
              >
                {h}
              </button>
            ))}
          </div>
        )}
      </div>

      {sorted.length === 0 ? (
        <p className="text-xs text-muted-foreground/70 py-6 text-center">
          Keine Reels im Filter. {windowKey === '7d' && 'Versuch 30d oder all-time.'}
        </p>
      ) : (
        <ul className="rounded-lg border border-border bg-card/30 overflow-hidden divide-y divide-border">
          {sorted.map((r, i) => (
            <li key={`${r.handle}-${r.shortcode || i}`}>
              <a
                href={r.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-3 px-4 py-2.5 hover:bg-card/60 transition-colors"
                title={r.summary || r.why_it_worked || r.caption_snippet}
              >
                <span className="num-mono text-xs text-ok shrink-0 w-14 text-right font-semibold">
                  {fmtPct(r.engagement_rate)}
                </span>
                <span className="num-mono text-[11px] text-muted-foreground shrink-0 w-16 text-right">
                  {fmtNum(r.views)}v
                </span>
                {r.posted && (
                  <span className="hidden lg:inline num-mono text-[10px] text-muted-foreground/60 shrink-0 w-20">
                    {r.posted.slice(0, 10)}
                  </span>
                )}
                <span className="shrink-0 inline-flex items-center gap-1 font-mono text-[10px] text-foreground/80 truncate max-w-[140px]">
                  @{r.handle}
                  {r.source === 'discovered' && (
                    <span className="text-primary/70" title="Neu entdeckt">·</span>
                  )}
                </span>
                {r.hook_type && (
                  <span className="hidden md:inline shrink-0 font-mono text-[9px] uppercase tracking-wider text-primary/80 bg-primary/10 px-1.5 py-0.5 rounded border border-primary/20">
                    {r.hook_type}
                  </span>
                )}
                <span className="flex-1 text-xs text-foreground/85 truncate">
                  {r.caption_snippet || '—'}
                </span>
                <ExternalLink className="size-3 opacity-50 shrink-0" />
              </a>
            </li>
          ))}
        </ul>
      )}
    </SectionCard>
  );
}

function MarketAnalysisCard({ analysis }: { analysis: MarketAnalysis }) {
  return (
    <SectionCard
      title="Markt-Analyse"
      description={`Sonnet-Übersicht von ${analysis.creators_input.length} relevanten Creators · gecacht 24h`}
      actions={<TrendingUp className="size-4 text-primary" />}
    >
      <div className="space-y-4">
        {analysis.summary && (
          <p className="text-sm text-foreground/90 leading-relaxed">
            {analysis.summary}
          </p>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          {analysis.themes.length > 0 && (
            <div className="rounded-lg border border-border bg-card/30 p-3 space-y-1.5">
              <div className="label-mono text-[10px] flex items-center gap-1.5 text-primary">
                <Target className="size-3" /> Dominante Themen
              </div>
              <ul className="text-xs space-y-1 text-foreground/85">
                {analysis.themes.map((t, i) => (
                  <li key={i} className="leading-snug">· {t}</li>
                ))}
              </ul>
            </div>
          )}

          {analysis.top_performers.length > 0 && (
            <div className="rounded-lg border border-border bg-card/30 p-3 space-y-1.5">
              <div className="label-mono text-[10px] flex items-center gap-1.5 text-ok">
                <Trophy className="size-3" /> Top-Performer
              </div>
              <ul className="text-xs space-y-1 text-foreground/85">
                {analysis.top_performers.map((t, i) => (
                  <li key={i} className="leading-snug">· {t}</li>
                ))}
              </ul>
            </div>
          )}

          {analysis.gaps.length > 0 && (
            <div className="rounded-lg border border-warn/30 bg-warn/[0.05] p-3 space-y-1.5">
              <div className="label-mono text-[10px] flex items-center gap-1.5 text-warn">
                <Lightbulb className="size-3" /> Lücken für dich
              </div>
              <ul className="text-xs space-y-1 text-foreground/85">
                {analysis.gaps.map((g, i) => (
                  <li key={i} className="leading-snug">· {g}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </SectionCard>
  );
}

export function DiscoveryView({ discovery, marketCreators, marketTopReels = [], marketAnalysis }: DiscoveryViewProps) {
  const router = useRouter();
  const [refreshing, setRefreshing] = useState(false);

  const themes = discovery?.themes_used ?? [];
  const dropped = discovery?.candidates_dropped_irrelevant ?? 0;
  const trackedCount = marketCreators.filter((c) => c.source === 'tracked').length;
  const discoveredCount = marketCreators.filter((c) => c.source === 'discovered').length;

  async function handleRefresh() {
    if (refreshing) return;
    const ok = window.confirm(
      'Discovery-Run jetzt starten? Apify-Cost ~$0.80 (8 Hashtags) plus ~$0.05 Sonnet, Dauer ~45 Sekunden.'
    );
    if (!ok) return;

    setRefreshing(true);
    const res = await api.triggerDiscovery();
    if ('ok' in res) {
      toast.success('Discovery-Run gestartet. Ergebnisse erscheinen in ~45s.');
      setTimeout(() => router.refresh(), 45_000);
    } else {
      toast.error(res.error || 'Discovery-Refresh fehlgeschlagen');
    }
    setRefreshing(false);
  }

  return (
    <section className="px-8 py-8 max-w-7xl mx-auto space-y-6">
      <PageHeader
        eyebrow="Content"
        title="Markt-Analyse"
        description="Alle relevanten Creators in deinem Markt. Sortiert nach Ähnlichkeit zu deinem Profil."
        meta={
          discovery?.discovered_at ? (
            <span>
              Letzter Discovery-Run: {fmtDate(discovery.discovered_at)}
              {dropped > 0 && ` · ${dropped} irrelevante gefiltert`}
            </span>
          ) : null
        }
        actions={
          <Button
            variant="default"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw
              className={`size-3.5 ${refreshing ? 'animate-spin' : ''}`}
            />
            {refreshing ? 'Läuft…' : 'Discovery jetzt aktualisieren'}
          </Button>
        }
      />

      {marketAnalysis && marketAnalysis.summary && (
        <MarketAnalysisCard analysis={marketAnalysis} />
      )}

      <MarketTopReelsFeed reels={marketTopReels} />

      <SectionCard
        title={`Alle Creator im Markt (${marketCreators.length})`}
        description={
          `${trackedCount} getrackt · ${discoveredCount} neu entdeckt` +
          (themes.length > 0
            ? ` · Hashtags: ${themes.slice(0, 8).join(', ')}`
            : '')
        }
        actions={<Sparkles className="size-4 text-primary" />}
      >
        {marketCreators.length === 0 ? (
          <p className="text-sm text-muted-foreground leading-relaxed py-4">
            Noch keine Markt-Daten. Tracker läuft täglich 06:00, Discovery 1×/Woche
            (Sonntag) oder per Button oben rechts ({' '}
            <span className="text-foreground">"Discovery jetzt aktualisieren"</span>
            ).
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {marketCreators.map((c) => (
              <DiscoveryCard key={`${c.source}-${c.handle}`} creator={c} />
            ))}
          </div>
        )}
      </SectionCard>
    </section>
  );
}
