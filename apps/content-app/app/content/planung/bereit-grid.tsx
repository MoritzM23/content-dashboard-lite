'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Play, ExternalLink } from 'lucide-react';
import type { ContentPiece } from '@/lib/types';

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? 'http://127.0.0.1:8093';

function streamUrl(piece: ContentPiece): string | null {
  if (!piece.final_mp4) return null;
  return `${API_BASE}/content/file?path=${encodeURIComponent(piece.final_mp4)}`;
}

export function BereitGrid({
  pieces,
  platform,
  onEdit,
}: {
  pieces: ContentPiece[];
  platform: 'instagram' | 'linkedin' | 'youtube';
  onEdit?: (vaultPath: string) => void;
}) {
  if (pieces.length === 0) {
    return (
      <div className="text-xs text-muted-foreground/70 py-8 text-center">
        Nichts bereit zum Posten. Sobald ein <code className="font-mono text-[10px] bg-card px-1 py-0.5 rounded">final.mp4</code> in
        einem Pipeline-Folder liegt, wandert er automatisch hierhin.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {pieces.map((p) => (
        <BereitCard key={p.id} piece={p} platform={platform} onEdit={onEdit} />
      ))}
    </div>
  );
}

function BereitCard({
  piece,
  platform,
  onEdit,
}: {
  piece: ContentPiece;
  platform: 'instagram' | 'linkedin' | 'youtube';
  onEdit?: (vaultPath: string) => void;
}) {
  const [showVideo, setShowVideo] = useState(false);
  const src = streamUrl(piece);

  return (
    <div className="rounded-xl border border-primary/30 bg-card/40 overflow-hidden flex flex-col hover:border-primary/50 transition-colors">
      <div className="relative aspect-[9/16] bg-background/60 border-b border-border">
        {src ? (
          showVideo ? (
            <video
              src={src}
              controls
              autoPlay
              className="absolute inset-0 w-full h-full object-contain"
            />
          ) : (
            <button
              type="button"
              onClick={() => setShowVideo(true)}
              className="absolute inset-0 flex items-center justify-center group cursor-pointer"
              aria-label="Video abspielen"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-primary/5" />
              <div className="relative size-14 rounded-full bg-primary/90 text-primary-foreground flex items-center justify-center shadow-lg group-hover:scale-110 group-hover:bg-primary transition-all">
                <Play className="size-6 ml-0.5" fill="currentColor" />
              </div>
              <span className="absolute bottom-3 left-3 right-3 text-[10px] font-mono text-muted-foreground/80 uppercase tracking-wider">
                Click zum Abspielen
              </span>
            </button>
          )
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-xs text-muted-foreground/60">
            kein final.mp4
          </div>
        )}
      </div>

      <div className="p-4 space-y-2 flex-1 flex flex-col">
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-sm font-semibold text-foreground/90 leading-tight line-clamp-2">
            {piece.title}
          </h3>
          <span className="shrink-0 font-mono text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded border border-warn/40 bg-warn/10 text-warn">
            ready
          </span>
        </div>

        {piece.hook && (
          <p className="text-xs text-foreground/70 italic line-clamp-2 leading-snug">
            "{piece.hook}"
          </p>
        )}

        <div className="flex flex-wrap items-center gap-1.5 text-[10px] font-mono">
          {piece.trigger_word && (
            <span className="px-1.5 py-0.5 rounded border border-primary/30 bg-primary/10 text-primary uppercase">
              {piece.trigger_word}
            </span>
          )}
          {piece.serie && (
            <span className="px-1.5 py-0.5 rounded border border-border bg-card/60 text-muted-foreground truncate max-w-[160px]">
              {piece.serie}
            </span>
          )}
        </div>

        <div className="flex-1" />

        <div className="flex items-center gap-2 pt-2 border-t border-border">
          {onEdit ? (
            <button
              type="button"
              onClick={() => onEdit(piece.vault_path)}
              className="flex-1 text-xs px-3 py-1.5 rounded-md bg-foreground/[0.06] hover:bg-foreground/[0.10] border border-border transition-colors"
            >
              Bearbeiten
            </button>
          ) : (
            <Link
              href={`/content/planung/${encodeURIComponent(piece.slug)}`}
              className="flex-1 text-xs px-3 py-1.5 rounded-md bg-foreground/[0.06] hover:bg-foreground/[0.10] border border-border transition-colors text-center"
            >
              Bearbeiten
            </Link>
          )}
          <a
            href={`obsidian://open?file=${encodeURIComponent(piece.vault_path)}`}
            target="_blank"
            rel="noreferrer"
            className="text-xs px-2.5 py-1.5 rounded-md border border-border bg-card/40 hover:bg-card/60 transition-colors"
            title="Im Obsidian öffnen"
          >
            <ExternalLink className="size-3" />
          </a>
        </div>
      </div>
    </div>
  );
}
