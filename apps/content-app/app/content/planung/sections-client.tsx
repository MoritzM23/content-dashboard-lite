'use client';

import { useState } from 'react';
import type { ContentPiece } from '@/lib/types';
import { SectionCard } from '@/components/section-card';
import { Sparkles, Clapperboard, Lightbulb } from 'lucide-react';
import { PlanungList, EditDialog } from './planung-client';
import { TiktokList } from '@/components/tiktok-postbar';
import {
  InstagramIcon,
  TikTokIcon,
  YouTubeIcon,
  LinkedInIcon,
} from '@/components/platform-icons';

type Platform = 'instagram' | 'tiktok' | 'youtube' | 'linkedin';

const PLATFORM_META: Record<
  Platform,
  { label: string; icon: React.FC<React.SVGProps<SVGSVGElement>> }
> = {
  instagram: { label: 'Instagram', icon: InstagramIcon },
  tiktok: { label: 'TikTok', icon: TikTokIcon },
  youtube: { label: 'YouTube', icon: YouTubeIcon },
  linkedin: { label: 'LinkedIn', icon: LinkedInIcon },
};

function statusToneClass(status: string): string {
  const s = status.toLowerCase();
  if (s === 'ready' || s === 'posting-now')
    return 'text-warn bg-warn/10 border-warn/30';
  if (s === 'ready-to-film')
    return 'text-warn bg-warn/10 border-warn/30';
  return 'text-foreground/70 bg-card border-border';
}

function BereitList({
  pieces,
  platform,
  onClick,
}: {
  pieces: ContentPiece[];
  platform: Platform;
  onClick: (p: ContentPiece) => void;
}) {
  const Icon = PLATFORM_META[platform].icon;

  if (pieces.length === 0) {
    return (
      <div className="text-xs text-muted-foreground/70 py-6 text-center">
        Nichts bereit zum Posten. Sobald ein{' '}
        <code className="font-mono text-[10px] bg-card px-1 py-0.5 rounded">
          final.mp4
        </code>{' '}
        in einem Pipeline-Folder liegt, wandert er automatisch hierhin.
      </div>
    );
  }

  return (
    <ul className="divide-y divide-border rounded-lg border border-primary/20 overflow-hidden bg-primary/[0.04]">
      {pieces.map((p) => (
        <li key={p.id}>
          <button
            type="button"
            onClick={() => onClick(p)}
            className="w-full flex items-center gap-3 px-4 py-2.5 text-left hover:bg-primary/[0.08] transition-colors group"
          >
            <Icon className="size-3.5 text-primary shrink-0" />
            <span className="flex-1 text-sm text-foreground/90 group-hover:text-foreground truncate font-medium">
              {p.hook || p.title}
            </span>
            {p.trigger_word && (
              <span className="hidden sm:inline font-mono text-[10px] uppercase tracking-wider text-primary/80 bg-primary/10 px-1.5 py-0.5 rounded border border-primary/20">
                {p.trigger_word}
              </span>
            )}
            {p.serie && (
              <span className="hidden md:inline font-mono text-[10px] text-muted-foreground/70 truncate max-w-[140px]">
                {p.serie}
              </span>
            )}
            {p.final_mp4 && (
              <span className="font-mono text-[10px] uppercase tracking-wider text-ok bg-ok/10 px-1.5 py-0.5 rounded border border-ok/30">
                ▶ Video
              </span>
            )}
            <span
              className={`shrink-0 font-mono text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded border ${statusToneClass(p.status)}`}
            >
              {p.status || 'ready'}
            </span>
          </button>
        </li>
      ))}
    </ul>
  );
}

export function PlanungSections({
  platform,
  bereit,
  konzept,
  ideas,
}: {
  platform: Platform;
  bereit: ContentPiece[];
  konzept: ContentPiece[];
  ideas: ContentPiece[];
}) {
  const [openPath, setOpenPath] = useState<string | null>(null);
  const [openMp4, setOpenMp4] = useState<string | null>(null);

  function openPiece(p: ContentPiece) {
    setOpenPath(p.vault_path);
    setOpenMp4(p.final_mp4 || null);
  }

  // Bei Klick aus PlanungList (konzept/ideas) findet sich Piece via vault_path
  function findFinalMp4(path: string | null): string | null {
    if (!path) return null;
    const all = [...bereit, ...konzept, ...ideas];
    return all.find((p) => p.vault_path === path)?.final_mp4 || null;
  }

  function handleOpenPath(path: string | null) {
    setOpenPath(path);
    setOpenMp4(findFinalMp4(path));
  }

  // TikTok ist Cross-Post-View: keine Konzept-Phase, nur 'postbar'-Cards mit
  // Video-Preview und Status-Toggle. Keine EditDialog noetig, weil die
  // Quell-Datei das Instagram-Skript ist.
  if (platform === 'tiktok') {
    return (
      <SectionCard
        title={`Noch postbar (${bereit.length})`}
        description="Instagram-Reels mit final.mp4, die du noch auf TikTok hochladen kannst. Pfad kopieren, hochladen, abhaken."
        actions={<Sparkles className="size-4 text-primary" />}
      >
        <TiktokList pieces={bereit} mode="postbar" />
      </SectionCard>
    );
  }

  return (
    <>
      <SectionCard
        title={`Bereit zum Posten (${bereit.length})`}
        description="Final.mp4 fertig, wartet auf Upload. Click oeffnet Editor mit Video-Vorschau."
        actions={<Sparkles className="size-4 text-primary" />}
      >
        <BereitList pieces={bereit} platform={platform} onClick={openPiece} />
      </SectionCard>

      <SectionCard
        title={`In Konzeption (${konzept.length})`}
        description="Skripte ohne fertiges Video. Sobald final.mp4 im Folder liegt, wandert er nach 'Bereit'."
        actions={<Clapperboard className="size-4 text-muted-foreground" />}
      >
        <PlanungList
          platform={platform}
          pieces={konzept}
          openPath={openPath}
          onOpenPath={handleOpenPath}
        />
      </SectionCard>

      {ideas.length > 0 && (
        <SectionCard
          title={`Ideen-Pool (${ideas.length})`}
          description="Brainstorms aus 04-areas/content/ideas/"
          actions={<Lightbulb className="size-4 text-warn" />}
        >
          <PlanungList
            platform="instagram"
            pieces={ideas}
            openPath={openPath}
            onOpenPath={handleOpenPath}
          />
        </SectionCard>
      )}

      <EditDialog
        path={openPath}
        platform={platform}
        finalMp4={openMp4}
        onOpenChange={(open) => {
          if (!open) {
            setOpenPath(null);
            setOpenMp4(null);
          }
        }}
      />
    </>
  );
}
