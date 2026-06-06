'use client';

import { useState } from 'react';
import { ExternalLink } from 'lucide-react';
import type { ContentPiece } from '@/lib/types';
import { LinkedInPostDetailDialog } from '@/components/linkedin-post-detail-dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface Props {
  posted: ContentPiece[];
}

/**
 * Einfache LinkedIn-Post-Tabelle, sortiert nach Datum (neueste oben).
 * Keine KPIs — LinkedIn liefert dafuer keine zuverlaessige Datenquelle.
 * Klick auf eine Zeile zeigt den vollen Post-Text.
 */
export function LinkedInPostList({ posted }: Props) {
  const [active, setActive] = useState<ContentPiece | null>(null);

  if (posted.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        Noch keine geposteten LinkedIn-Posts in der Library.
      </p>
    );
  }

  const sorted = [...posted].sort((a, b) => {
    const ad = a.posted_at || a.slug || '';
    const bd = b.posted_at || b.slug || '';
    return bd.localeCompare(ad);
  });

  return (
    <>
      <p className="text-[11px] text-muted-foreground leading-relaxed mb-3">
        Klick auf eine Zeile zeigt den vollen Post-Text.
      </p>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="border-border hover:bg-transparent">
              <TableHead className="label-mono w-28">Posted</TableHead>
              <TableHead className="label-mono">Hook / Titel</TableHead>
              <TableHead className="label-mono w-40">Serie</TableHead>
              <TableHead className="label-mono w-8"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sorted.map((p) => {
              const dateStr = (p.posted_at || p.slug || '').slice(0, 10);
              const display = p.hook || p.title || p.body_preview?.slice(0, 100) || '—';
              return (
                <TableRow
                  key={p.id}
                  onClick={() => setActive(p)}
                  className="border-border hover:bg-accent/40 transition-colors cursor-pointer"
                >
                  <TableCell className="num-mono text-xs text-muted-foreground whitespace-nowrap">
                    {dateStr || '—'}
                  </TableCell>
                  <TableCell className="max-w-[500px] truncate">
                    {display}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground truncate">
                    {p.serie || '—'}
                  </TableCell>
                  <TableCell>
                    {p.post_url && (
                      <a
                        href={p.post_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-muted-foreground hover:text-foreground transition-colors"
                        aria-label="Auf LinkedIn öffnen"
                        title="Auf LinkedIn öffnen"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <ExternalLink className="size-3.5" />
                      </a>
                    )}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
      <LinkedInPostDetailDialog
        piece={active}
        onClose={() => setActive(null)}
      />
    </>
  );
}
