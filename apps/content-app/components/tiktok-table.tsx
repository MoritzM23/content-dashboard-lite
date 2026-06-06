'use client';

import { useMemo, useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { ArrowDown, ArrowUp, ChevronsUpDown, ExternalLink } from 'lucide-react';
import type { TikTokVideo } from '@/lib/types';
import { fmtDate, fmtNum, fmtPct } from '@/lib/format';
import { cn } from '@/lib/utils';

type SortKey =
  | 'posted'
  | 'views'
  | 'likes'
  | 'comments'
  | 'shares'
  | 'saves'
  | 'save_rate'
  | 'engagement_rate'
  | 'video_duration';

function saveRate(v: TikTokVideo): number {
  if (!v.views) return 0;
  return ((v.saves ?? 0) / v.views) * 100;
}

interface TikTokTableProps {
  videos: TikTokVideo[];
  emptyMessage?: string;
}

export function TikTokTable({ videos, emptyMessage }: TikTokTableProps) {
  // Default: neueste oben, analog zur Instagram-ReelTable.
  const [sortKey, setSortKey] = useState<SortKey>('posted');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');

  const sorted = useMemo(() => {
    return videos.slice().sort((a, b) => {
      if (sortKey === 'save_rate') {
        const na = saveRate(a);
        const nb = saveRate(b);
        return sortDir === 'asc' ? na - nb : nb - na;
      }
      const ka = (a as unknown as Record<string, unknown>)[sortKey];
      const kb = (b as unknown as Record<string, unknown>)[sortKey];
      if (typeof ka === 'string' || typeof kb === 'string') {
        const sa = String(ka ?? '');
        const sb = String(kb ?? '');
        return sortDir === 'asc' ? sa.localeCompare(sb) : sb.localeCompare(sa);
      }
      const na = (ka as number) || 0;
      const nb = (kb as number) || 0;
      return sortDir === 'asc' ? na - nb : nb - na;
    });
  }, [videos, sortKey, sortDir]);

  function toggleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  }

  if (!videos.length) {
    return (
      <div className="text-center text-sm text-muted-foreground py-12">
        {emptyMessage ?? 'Keine Videos im Zeitraum.'}
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow className="border-border hover:bg-transparent">
            <SortHeader k="posted" label="Posted" sortKey={sortKey} sortDir={sortDir} onSort={toggleSort} />
            <TableHead className="label-mono">Caption</TableHead>
            <SortHeader k="views" label="Views" sortKey={sortKey} sortDir={sortDir} onSort={toggleSort} align="right" />
            <SortHeader k="likes" label="Likes" sortKey={sortKey} sortDir={sortDir} onSort={toggleSort} align="right" />
            <SortHeader k="comments" label="Komm." sortKey={sortKey} sortDir={sortDir} onSort={toggleSort} align="right" />
            <SortHeader k="saves" label="Saves" sortKey={sortKey} sortDir={sortDir} onSort={toggleSort} align="right" />
            <SortHeader k="shares" label="Shares" sortKey={sortKey} sortDir={sortDir} onSort={toggleSort} align="right" />
            <SortHeader k="save_rate" label="Save-%" sortKey={sortKey} sortDir={sortDir} onSort={toggleSort} align="right" />
            <SortHeader k="engagement_rate" label="ER" sortKey={sortKey} sortDir={sortDir} onSort={toggleSort} align="right" />
            <SortHeader k="video_duration" label="Länge" sortKey={sortKey} sortDir={sortDir} onSort={toggleSort} align="right" />
            <TableHead className="label-mono w-8"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.map((v) => {
            const sr = saveRate(v);
            // Save-Rate-Color: >2% top (PDF-Ziel), 1-2% ok, <1% schwach
            const srTone =
              sr >= 2 ? 'text-ok font-semibold' : sr >= 1 ? 'text-warn' : 'text-foreground/70';
            return (
              <TableRow
                key={v.shortcode}
                className="border-border hover:bg-accent/40 transition-colors"
              >
                <TableCell className="num-mono text-xs whitespace-nowrap">
                  {fmtDate(v.posted)}
                </TableCell>
                <TableCell className="max-w-[300px] truncate">
                  <span title={v.caption_full ?? v.caption_snippet ?? ''}>
                    {v.caption_snippet ?? '—'}
                  </span>
                </TableCell>
                <TableCell className="num-mono text-right whitespace-nowrap">
                  {fmtNum(v.views)}
                </TableCell>
                <TableCell className="num-mono text-right whitespace-nowrap">
                  {fmtNum(v.likes)}
                </TableCell>
                <TableCell className="num-mono text-right whitespace-nowrap">
                  {fmtNum(v.comments)}
                </TableCell>
                <TableCell className="num-mono text-right whitespace-nowrap">
                  {fmtNum(v.saves)}
                </TableCell>
                <TableCell className="num-mono text-right whitespace-nowrap">
                  {fmtNum(v.shares)}
                </TableCell>
                <TableCell
                  className={cn('num-mono text-right whitespace-nowrap', srTone)}
                  title="Save-Rate: Kaufabsichts-Proxy. Ziel laut PDF >2%."
                >
                  {fmtPct(sr)}
                </TableCell>
                <TableCell className="num-mono text-right whitespace-nowrap text-ok">
                  {fmtPct(v.engagement_rate)}
                </TableCell>
                <TableCell className="num-mono text-right whitespace-nowrap text-muted-foreground">
                  {v.video_duration ? `${Math.round(v.video_duration)}s` : '—'}
                </TableCell>
                <TableCell>
                  <a
                    href={v.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-muted-foreground hover:text-foreground transition-colors"
                    aria-label="Video auf TikTok öffnen"
                    title="Auf TikTok öffnen"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <ExternalLink className="size-3.5" />
                  </a>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}

function SortHeader({
  k,
  label,
  sortKey,
  sortDir,
  onSort,
  align,
}: {
  k: SortKey;
  label: string;
  sortKey: SortKey;
  sortDir: 'asc' | 'desc';
  onSort: (k: SortKey) => void;
  align?: 'right';
}) {
  const active = sortKey === k;
  const Icon = active ? (sortDir === 'asc' ? ArrowUp : ArrowDown) : ChevronsUpDown;
  return (
    <TableHead className={cn('label-mono', align === 'right' && 'text-right')}>
      <button
        onClick={() => onSort(k)}
        className={cn(
          'inline-flex items-center gap-1 hover:text-primary transition-colors',
          active && 'text-primary'
        )}
      >
        {label}
        <Icon className="size-3 opacity-60" />
      </button>
    </TableHead>
  );
}
