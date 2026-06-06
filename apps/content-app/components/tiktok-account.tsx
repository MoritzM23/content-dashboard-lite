'use client';

import { useMemo, useState } from 'react';
import { ExternalLink } from 'lucide-react';
import type { TikTokIntel, TikTokRangeKpi, MarketingScorecard } from '@/lib/types';
import { fmtNum, fmtPct } from '@/lib/format';
import { SectionCard } from '@/components/section-card';
import { KpiCard } from '@/components/kpi-card';
import { RangeFilter, type RangeKey } from '@/components/range-filter';
import { TikTokTable } from '@/components/tiktok-table';
import { MarketingScorecardCard } from '@/components/marketing-scorecard';

interface Props {
  tiktok?: TikTokIntel;
  scorecard?: MarketingScorecard;
}

export function TikTokAccount({ tiktok, scorecard }: Props) {
  const [range, setRange] = useState<RangeKey>('all');

  if (!tiktok?.available) {
    return (
      <SectionCard>
        <p className="text-sm text-muted-foreground leading-relaxed">
          {tiktok?.note ??
            'TikTok-Tracker hat noch keinen Snapshot geschrieben.'}{' '}
          Der Tracker läuft täglich um 06:15 Uhr (Cron{' '}
          <code className="font-mono text-[11px]">com.aios.tiktok-tracker</code>
          ). Manuell starten:{' '}
          <code className="font-mono text-[11px]">
            ~/aios-venv/bin/python scripts/tiktok_tracker.py
          </code>
        </p>
      </SectionCard>
    );
  }

  const videos = tiktok.all_self_videos ?? [];
  const rangeKpis = tiktok.range_kpis;
  const handle = tiktok.self_handle ?? 'self';

  const counts = {
    '7d': rangeKpis?.['7d'].count ?? 0,
    '30d': rangeKpis?.['30d'].count ?? 0,
    all: rangeKpis?.all.count ?? 0,
  };

  const k: TikTokRangeKpi = rangeKpis?.[range] ?? {
    count: 0,
    total_views: 0,
    total_likes: 0,
    total_comments: 0,
    total_shares: 0,
    total_saves: 0,
    avg_views: 0,
    avg_engagement_rate: 0,
    avg_save_rate: 0,
    avg_share_rate: 0,
  };

  const isWindowed = range === '7d' || range === '30d';
  const windowedViews =
    isWindowed && typeof k.views_delta_total === 'number'
      ? k.views_delta_total
      : k.total_views;

  // Range-Filter auf die Tabelle anwenden, damit der Range-Picker auch die
  // Liste filtert (analog zur Instagram-Sicht in mein-account-client).
  const filteredVideos = useMemo(() => {
    if (range === 'all') return videos;
    const today = new Date();
    const cutoff = new Date(today);
    cutoff.setDate(cutoff.getDate() - (range === '7d' ? 7 : 30));
    const cutoffStr = cutoff.toISOString().slice(0, 10);
    return videos.filter((v) => (v.posted ?? '') >= cutoffStr);
  }, [videos, range]);

  return (
    <div className="space-y-5">
      <SectionCard>
        <div className="flex items-center justify-between flex-wrap gap-3 mb-4">
          <RangeFilter value={range} onChange={setRange} counts={counts} />
          {tiktok.snapshot_date && (
            <div className="font-mono text-xs text-muted-foreground">
              Stand: {tiktok.snapshot_date}
            </div>
          )}
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2.5">
          <KpiCard label="Videos" value={k.count} />
          <KpiCard
            label={isWindowed ? `Views ${range}` : 'Total Views'}
            value={fmtNum(windowedViews)}
            hint={isWindowed ? 'Neue Views im Fenster' : undefined}
          />
          <KpiCard label="Saves total" value={fmtNum(k.total_saves)} />
          <KpiCard label="Shares total" value={fmtNum(k.total_shares)} />
          <KpiCard
            label="Ø Save-Rate"
            value={fmtPct(k.avg_save_rate)}
            hint="Saves/Views. Ziel >2% (PDF)"
          />
          <KpiCard
            label="Ø Share-Rate"
            value={fmtPct(k.avg_share_rate)}
            hint="Shares/Views"
          />
          <KpiCard
            label="Ø ER"
            value={fmtPct(k.avg_engagement_rate)}
            hint="(likes+comments)/views"
          />
        </div>
        <p className="mt-4 text-[11px] text-muted-foreground leading-snug">
          Save-Rate und Share-Rate sind aus TikTok direkt verfügbar (Instagram
          liefert sie nicht). Sie sind laut PDF die zwei stärksten
          Kaufabsichts-Proxies, deutlich aussagekräftiger als ER oder Likes.
        </p>
      </SectionCard>

      <MarketingScorecardCard scorecard={scorecard} platform="tiktok" />

      <SectionCard
        title="Videos"
        description={`${filteredVideos.length} Video${filteredVideos.length === 1 ? '' : 's'} im Zeitraum. Klick auf Spaltenkopf zum Sortieren, Default neueste oben.`}
      >
        <TikTokTable
          videos={filteredVideos}
          emptyMessage="Keine Videos im Zeitraum. Range oben weiten."
        />
        <a
          href={`https://www.tiktok.com/@${handle}`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 mt-4 text-xs font-mono text-muted-foreground hover:text-primary transition-colors"
        >
          tiktok.com/@{handle}
          <ExternalLink className="size-3" />
        </a>
      </SectionCard>
    </div>
  );
}
