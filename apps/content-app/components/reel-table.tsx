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
import type { Reel } from '@/lib/types';
import { fmtDate, fmtNum, fmtPct } from '@/lib/format';
import { SentimentPill } from './sentiment-pill';
import { cn } from '@/lib/utils';

type SortKey =
  | 'posted'
  | 'views'
  | 'likes'
  | 'comments'
  | 'engagement_rate'
  | 'comment_rate'
  | 'video_duration';

// Comment-Rate (comments/views * 100) — pro Reel berechnet falls Feld fehlt.
function commentRate(r: Reel): number {
  if (typeof r.comment_rate === 'number') return r.comment_rate;
  if (!r.views) return 0;
  return ((r.comments ?? 0) / r.views) * 100;
}

interface ReelTableProps {
  reels: Reel[];
  emptyMessage?: string;
  onReelClick?: (reel: Reel) => void;
}

export function ReelTable({ reels, emptyMessage, onReelClick }: ReelTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>('posted');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');

  const sorted = useMemo(() => {
    return reels.slice().sort((a, b) => {
      // Comment-Rate ist berechnet, separat behandeln
      if (sortKey === 'comment_rate') {
        const na = commentRate(a);
        const nb = commentRate(b);
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
  }, [reels, sortKey, sortDir]);

  function toggleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  }

  if (!reels.length) {
    return (
      <div className="text-center text-sm text-muted-foreground py-12">
        {emptyMessage ?? 'Keine Reels im Zeitraum.'}
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow className="border-border hover:bg-transparent">
            <SortHeader
              k="posted"
              label="Posted"
              sortKey={sortKey}
              sortDir={sortDir}
              onSort={toggleSort}
            />
            <TableHead className="label-mono">Caption</TableHead>
            <SortHeader
              k="views"
              label="Views"
              sortKey={sortKey}
              sortDir={sortDir}
              onSort={toggleSort}
              align="right"
            />
            <SortHeader
              k="likes"
              label="Likes"
              sortKey={sortKey}
              sortDir={sortDir}
              onSort={toggleSort}
              align="right"
            />
            <SortHeader
              k="comments"
              label="Komm."
              sortKey={sortKey}
              sortDir={sortDir}
              onSort={toggleSort}
              align="right"
            />
            <SortHeader
              k="engagement_rate"
              label="ER"
              sortKey={sortKey}
              sortDir={sortDir}
              onSort={toggleSort}
              align="right"
            />
            <SortHeader
              k="comment_rate"
              label="C-Rate"
              sortKey={sortKey}
              sortDir={sortDir}
              onSort={toggleSort}
              align="right"
            />
            <SortHeader
              k="video_duration"
              label="Länge"
              sortKey={sortKey}
              sortDir={sortDir}
              onSort={toggleSort}
              align="right"
            />
            <TableHead className="label-mono">Sentiment</TableHead>
            <TableHead className="label-mono">Thema</TableHead>
            <TableHead className="label-mono w-8"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.map((r) => {
            const ai = r.ai_standard ?? {};
            return (
              <TableRow
                key={r.shortcode}
                onClick={() => onReelClick?.(r)}
                className={cn(
                  'border-border hover:bg-accent/40 transition-colors',
                  onReelClick && 'cursor-pointer'
                )}
              >
                <TableCell className="num-mono text-xs whitespace-nowrap">
                  {fmtDate(r.posted)}
                </TableCell>
                <TableCell className="max-w-[300px] truncate">
                  <span title={r.caption_full ?? r.caption_snippet ?? ''}>
                    {r.caption_snippet ?? '—'}
                  </span>
                </TableCell>
                <TableCell className="num-mono text-right whitespace-nowrap">
                  {fmtNum(r.views)}
                </TableCell>
                <TableCell className="num-mono text-right whitespace-nowrap">
                  {fmtNum(r.likes)}
                </TableCell>
                <TableCell className="num-mono text-right whitespace-nowrap">
                  {fmtNum(r.comments)}
                </TableCell>
                <TableCell className="num-mono text-right whitespace-nowrap text-ok font-semibold">
                  {fmtPct(r.engagement_rate)}
                </TableCell>
                <TableCell
                  className="num-mono text-right whitespace-nowrap text-ok"
                  title="Comment-Rate: comments/views * 100, ohne Likes"
                >
                  {fmtPct(commentRate(r))}
                </TableCell>
                <TableCell className="num-mono text-right whitespace-nowrap text-muted-foreground">
                  {r.video_duration ? `${Math.round(r.video_duration)}s` : '—'}
                </TableCell>
                <TableCell>
                  <SentimentPill sentiment={ai.sentiment} />
                </TableCell>
                <TableCell className="text-xs text-muted-foreground">
                  {ai.topic_tag ?? '—'}
                </TableCell>
                <TableCell>
                  <a
                    href={r.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-muted-foreground hover:text-foreground transition-colors"
                    aria-label="Reel auf Instagram öffnen"
                    title="Auf Instagram öffnen"
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
