'use client';

import { useMemo, useState } from 'react';
import type { ContentIntel, MarketingScorecard, Reel } from '@/lib/types';
import { fmtNum, fmtPct } from '@/lib/format';
import { SectionCard } from '@/components/section-card';
import { KpiCard } from '@/components/kpi-card';
import { RangeFilter, type RangeKey } from '@/components/range-filter';
import { ReelTable } from '@/components/reel-table';
import { AudienceActivity } from '@/components/audience-activity';
import { HashtagGrid } from '@/components/hashtag-grid';
import { TopicClusters } from '@/components/topic-clusters';
import { ReelDetailDialog } from '@/components/reel-detail-dialog';
import { MarketingScorecardCard } from '@/components/marketing-scorecard';

interface Props {
  intel: ContentIntel;
  scorecard?: MarketingScorecard;
}

export function MeinAccountClient({ intel, scorecard }: Props) {
  const handle = intel.self_handle ?? 'self';
  const allReels = intel.all_self_reels ?? [];
  const rangeKpis = intel.range_kpis;

  const [range, setRange] = useState<RangeKey>('all');
  const [selectedReel, setSelectedReel] = useState<Reel | null>(null);

  const counts = useMemo(
    () => ({
      '7d': rangeKpis?.['7d'].count ?? 0,
      '30d': rangeKpis?.['30d'].count ?? 0,
      all: rangeKpis?.all.count ?? 0,
    }),
    [rangeKpis]
  );

  const filteredReels = useMemo(() => {
    if (!allReels.length) return [];
    if (range === 'all') return allReels;
    const today = new Date();
    const cutoff = (days: number) => {
      const d = new Date(today);
      d.setDate(d.getDate() - days);
      return d.toISOString().slice(0, 10);
    };
    const c = cutoff(range === '7d' ? 7 : 30);
    return allReels.filter((r) => (r.posted ?? '') >= c);
  }, [allReels, range]);

  const k = rangeKpis?.[range] ?? {
    count: 0,
    total_views: 0,
    total_likes: 0,
    avg_views: 0,
    avg_engagement_rate: 0,
    avg_comment_rate: 0,
    best_reel_er: 0,
  };

  // Wir nutzen jetzt überall die total_views-Logik aus den Reels die im Zeitraum
  // gepostet wurden. Die alte Delta-Variante (View-Deltas aus reel_history.db)
  // war verwirrend, weil History nur 25 Tage zurückreicht und 30d damit fast
  // identisch zu "all" war.

  const meinAccount = intel.mein_account;

  return (
    <div className="space-y-5">
      <SectionCard>
        <div className="flex items-center justify-between flex-wrap gap-3 mb-4">
          <RangeFilter value={range} onChange={setRange} counts={counts} />
          {intel.snapshot_date && (
            <div className="font-mono text-xs text-muted-foreground">
              Stand: {intel.snapshot_date}
            </div>
          )}
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2.5">
          <KpiCard label="Reels" value={k.count} />
          <KpiCard label="Total Views" value={fmtNum(k.total_views)} />
          <KpiCard label="Total Likes" value={fmtNum(k.total_likes)} />
          <KpiCard label="Ø Views/Reel" value={fmtNum(k.avg_views)} />
          <KpiCard
            label="Ø ER (Likes+Komm.)"
            value={fmtPct(k.avg_engagement_rate)}
            hint="(likes+comments)/views"
          />
          <KpiCard
            label="Ø Comment-Rate"
            value={fmtPct(k.avg_comment_rate ?? 0)}
            hint="comments/views"
          />
          <KpiCard label="Beste ER" value={fmtPct(k.best_reel_er)} />
        </div>
      </SectionCard>

      <MarketingScorecardCard scorecard={scorecard} platform="instagram" />

      <SectionCard
        title="Themen-Cluster"
        description="KI-Analyse mit Opus 4.7, fasst alle deine Reels zu Themengruppen zusammen (täglich 06:00 update)"
      >
        <TopicClusters clusters={intel.topic_clusters} selfHandle={handle} />
      </SectionCard>


      <SectionCard
        title="Audience-Aktivität"
        description="Wann reagiert deine Audience am stärksten? Top-Slots, Wochentage, Tageszeit-Blöcke. Basis: deine Reels der letzten 60 Tage, damit alte Reels mit hohen akkumulierten Views die ER-Statistik nicht verzerren."
      >
        <AudienceActivity
          ownStats={meinAccount}
          ownReels={allReels}
        />
      </SectionCard>

      <SectionCard
        title="Hashtag-Performance"
        description="Sortiert nach Ø Engagement, Tags mit min. 2 Verwendungen"
      >
        <HashtagGrid hashtags={meinAccount?.hashtag_performance ?? []} />
      </SectionCard>

      <SectionCard
        title="Alle deine Reels"
        description={`${filteredReels.length} Reels · ${
          range === '7d'
            ? 'letzte 7 Tage'
            : range === '30d'
              ? 'letzte 30 Tage'
              : 'gesamt'
        }`}
      >
        <ReelTable reels={filteredReels} onReelClick={setSelectedReel} />
      </SectionCard>

      <ReelDetailDialog
        reel={selectedReel}
        onClose={() => setSelectedReel(null)}
      />
    </div>
  );
}
