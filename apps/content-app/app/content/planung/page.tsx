import Link from 'next/link';
import { Wand2 } from 'lucide-react';
import {
  InstagramIcon,
  TikTokIcon,
  YouTubeIcon,
  LinkedInIcon,
} from '@/components/platform-icons';
import { PageHeader } from '@/components/page-header';
import { SectionCard } from '@/components/section-card';
import { loadDashboardData } from '@/lib/data';
import type { ContentPlanning } from '@/lib/types';
import { PlanungSections } from './sections-client';
import { CoachChat } from '@/components/coach-chat';

// Live-Garantie: kurzer Cache, damit Vault-Schreibvorgaenge schnell sichtbar werden.
// Save aus dem Edit-Sheet triggert generate_dashboard_data.py automatisch.
export const revalidate = 10;

type Platform = 'instagram' | 'tiktok' | 'youtube' | 'linkedin';

const PLATFORMS: Platform[] = ['instagram', 'tiktok', 'youtube', 'linkedin'];

const PLATFORM_META: Record<
  Platform,
  { label: string; icon: React.FC<React.SVGProps<SVGSVGElement>> }
> = {
  instagram: { label: 'Instagram', icon: InstagramIcon },
  tiktok: { label: 'TikTok', icon: TikTokIcon },
  youtube: { label: 'YouTube', icon: YouTubeIcon },
  linkedin: { label: 'LinkedIn', icon: LinkedInIcon },
};

function PlatformPill({
  platform,
  active,
  count,
}: {
  platform: Platform;
  active: boolean;
  count: number;
}) {
  const meta = PLATFORM_META[platform];
  const Icon = meta.icon;
  return (
    <Link
      href={`/content/planung?platform=${platform}`}
      prefetch
      scroll={false}
      className={[
        'inline-flex items-center gap-2 rounded-lg px-3.5 py-2 text-sm font-medium transition-colors border',
        active
          ? 'bg-foreground text-background border-foreground'
          : 'bg-card/40 text-foreground/80 border-border hover:bg-card/60 hover:text-foreground',
      ].join(' ')}
    >
      <Icon className="size-4" />
      <span>{meta.label}</span>
      <span
        className={[
          'font-mono text-[10px] num-mono rounded px-1.5 py-0.5',
          active
            ? 'bg-background/20'
            : 'bg-background/40 text-muted-foreground',
        ].join(' ')}
      >
        {count}
      </span>
    </Link>
  );
}

function parsePlatform(value: string | string[] | undefined): Platform {
  const v = Array.isArray(value) ? value[0] : value;
  if (v === 'linkedin' || v === 'youtube' || v === 'instagram' || v === 'tiktok') return v;
  return 'instagram';
}

type PageProps = {
  searchParams: Promise<{ platform?: string }>;
};

export default async function PlanungPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const platform = parsePlatform(params.platform);

  const data = await loadDashboardData();
  const planning: ContentPlanning | null = data?.content_planning ?? null;

  if (!planning?.available) {
    return (
      <div className="p-6 space-y-4">
        <PageHeader
          eyebrow="Content"
          title="Content-Planung"
          description="Pipeline aus dem Vault, gefiltert nach Plattform"
        />
        <SectionCard>
          <p className="text-sm text-muted-foreground">
            {planning?.note ?? 'Vault-Ordner 04-areas/content/ nicht gefunden.'}
          </p>
        </SectionCard>
      </div>
    );
  }

  const bereit = planning[platform].bereit ?? [];
  const konzept = planning[platform].konzept ?? planning[platform].planned ?? [];
  const ideas = planning.ideas ?? [];

  const counts: Record<Platform, number> = {
    instagram: (planning.instagram.bereit?.length ?? 0) + (planning.instagram.konzept?.length ?? planning.instagram.planned.length),
    // TikTok: nur 'bereit' (Cross-Post-Status), kein Konzept
    tiktok: planning.tiktok?.bereit?.length ?? 0,
    youtube: (planning.youtube.bereit?.length ?? 0) + (planning.youtube.konzept?.length ?? planning.youtube.planned.length),
    linkedin: (planning.linkedin.bereit?.length ?? 0) + (planning.linkedin.konzept?.length ?? planning.linkedin.planned.length),
  };

  return (
    <div className="p-6 space-y-5">
      <PageHeader
        eyebrow="Content"
        title="Content-Planung"
        description="Was als nächstes raus soll. Klick auf einen Eintrag öffnet den Editor."
        actions={
          <div
            className="inline-flex items-center gap-1.5 rounded-lg bg-primary/15 text-primary border border-primary/30 px-3 py-1.5 text-xs font-medium"
            title="Content-Coach läuft als Shared-Subagent unter ~/.claude/agents/content-coach.md"
          >
            <span className="relative flex size-2">
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-primary opacity-60" />
              <span className="relative inline-flex size-2 rounded-full bg-primary" />
            </span>
            <Wand2 className="size-3.5" />
            Content-Coach Live
          </div>
        }
      />

      <div className="flex flex-wrap items-center gap-2">
        {PLATFORMS.map((p) => (
          <PlatformPill
            key={p}
            platform={p}
            active={p === platform}
            count={counts[p]}
          />
        ))}
      </div>

      <PlanungSections
        platform={platform}
        bereit={bereit}
        konzept={konzept}
        ideas={platform === 'instagram' ? ideas : []}
      />

      <CoachChat
        scene="planung"
        title="Content-Coach"
        subtitle="Sonnet · Brand-Rules + Pipeline + Wettbewerbs-Top-Overview als Kontext"
        capabilities={[
          'Hook-Coach',
          'Skript-Generator',
          'Caption-Writer',
          'Trigger-Word-Rotation',
          'Cross-Posting IG/LI/YT',
        ]}
        quickPrompts={[
          'Gib mir 3 Hook-Optionen für ein Reel zum nächsten BAUEN-Trigger.',
          'Was war an meinen letzten 3 Reels schwach? Konkrete Diagnose.',
          'Schreib mir ein 30-Sekunden-Skript für einen LinkedIn-Karussell zum Thema KI-Team.',
        ]}
      />
    </div>
  );
}
