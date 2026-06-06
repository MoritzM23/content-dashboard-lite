'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Play, Check, RotateCcw, Copy } from 'lucide-react';
import { toast } from 'sonner';
import type { ContentPiece } from '@/lib/types';

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? 'http://127.0.0.1:8093';

function streamUrl(piece: ContentPiece): string | null {
  if (!piece.final_mp4) return null;
  return `${API_BASE}/content/file?path=${encodeURIComponent(piece.final_mp4)}`;
}

export function TiktokList({
  pieces,
  mode,
}: {
  pieces: ContentPiece[];
  mode: 'postbar' | 'done';
}) {
  if (pieces.length === 0) {
    return (
      <div className="text-xs text-muted-foreground/70 py-8 text-center">
        {mode === 'postbar'
          ? 'Nichts offen — alle Reels mit Video sind auf TikTok.'
          : 'Noch nichts als TikTok-gepostet markiert.'}
      </div>
    );
  }
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {pieces.map((p) => (
        <TiktokCard key={p.id} piece={p} mode={mode} />
      ))}
    </div>
  );
}

function TiktokCard({
  piece,
  mode,
}: {
  piece: ContentPiece;
  mode: 'postbar' | 'done';
}) {
  const router = useRouter();
  const [showVideo, setShowVideo] = useState(false);
  const [busy, setBusy] = useState(false);
  const src = streamUrl(piece);

  async function setStatus(status: 'posted' | 'open') {
    if (busy) return;
    setBusy(true);
    try {
      const res = await fetch(`${API_BASE}/content/crosspost`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vault_path: piece.vault_path,
          platform: 'tiktok',
          status,
        }),
      });
      const json = await res.json();
      if (!res.ok || json.error) throw new Error(json.error || `HTTP ${res.status}`);
      toast.success(
        status === 'posted'
          ? 'Als TikTok-gepostet markiert'
          : 'Zurück auf postbar gesetzt',
      );
      setTimeout(() => router.refresh(), 600);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Fehler');
    } finally {
      setBusy(false);
    }
  }

  function copyPath() {
    if (!piece.final_mp4) return;
    const abs = piece.final_mp4;
    navigator.clipboard.writeText(abs);
    toast.success('MP4-Pfad kopiert');
  }

  return (
    <div className="rounded-xl border border-border bg-card/40 overflow-hidden flex flex-col">
      <div className="relative aspect-[9/16] bg-background/60 border-b border-border">
        {src ? (
          showVideo ? (
            <video
              src={src}
              controls
              autoPlay
              muted
              playsInline
              className="absolute inset-0 w-full h-full object-contain bg-black"
            />
          ) : (
            <button
              type="button"
              onClick={() => setShowVideo(true)}
              className="absolute inset-0 flex items-center justify-center group cursor-pointer"
              aria-label="Video abspielen"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-primary/5" />
              <div className="relative size-14 rounded-full bg-primary/90 text-primary-foreground flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                <Play className="size-6 ml-0.5" fill="currentColor" />
              </div>
            </button>
          )
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-xs text-muted-foreground/60">
            kein final.mp4
          </div>
        )}
      </div>

      <div className="p-4 space-y-2.5 flex-1 flex flex-col">
        <h3 className="text-sm font-semibold text-foreground/90 leading-tight line-clamp-2">
          {piece.hook || piece.title}
        </h3>
        <div className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground">
          <span>{piece.posted_at?.slice(0, 10) || piece.slug.slice(0, 10)}</span>
          {piece.shortcode && <span className="opacity-50">·</span>}
          {piece.shortcode && (
            <a
              href={`https://instagram.com/p/${piece.shortcode}`}
              target="_blank"
              rel="noreferrer"
              className="hover:text-primary"
            >
              Instagram
            </a>
          )}
        </div>

        <button
          type="button"
          onClick={copyPath}
          className="flex items-center gap-1.5 text-[11px] text-muted-foreground hover:text-foreground transition-colors text-left"
          title="Absoluten MP4-Pfad in die Zwischenablage"
        >
          <Copy className="size-3 shrink-0" />
          <span className="truncate font-mono">{piece.final_mp4}</span>
        </button>

        <div className="flex-1" />

        {mode === 'postbar' ? (
          <button
            type="button"
            onClick={() => setStatus('posted')}
            disabled={busy}
            className="inline-flex items-center justify-center gap-1.5 rounded-lg bg-primary text-primary-foreground px-3 py-2 text-xs font-medium hover:opacity-90 transition-opacity disabled:opacity-40"
          >
            <Check className="size-3.5" />
            {busy ? 'Speichern…' : 'Auf TikTok gepostet'}
          </button>
        ) : (
          <button
            type="button"
            onClick={() => setStatus('open')}
            disabled={busy}
            className="inline-flex items-center justify-center gap-1.5 rounded-lg bg-card border border-border px-3 py-2 text-xs font-medium hover:bg-card/60 transition-colors disabled:opacity-40"
          >
            <RotateCcw className="size-3.5" />
            {busy ? 'Speichern…' : 'Zurück auf postbar'}
          </button>
        )}
      </div>
    </div>
  );
}
