import Link from 'next/link';
import { ExternalLink } from 'lucide-react';
import {
  InstagramIcon,
  TikTokIcon,
  YouTubeIcon,
  LinkedInIcon,
} from '@/components/platform-icons';
import { loadContentIntel, loadDashboardData } from '@/lib/data';
import { MeinAccountClient } from './mein-account-client';
import { SectionCard } from '@/components/section-card';
import { PageHeader } from '@/components/page-header';
import { LinkedInPostList } from '@/components/linkedin-post-list';
import { YouTubeAccount } from '@/components/youtube-account';
import { TikTokAccount } from '@/components/tiktok-account';
import type { ContentPiece } from '@/lib/types';

export const revalidate = 30;

type Platform = 'instagram' | 'tiktok' | 'youtube' | 'linkedin';

// Reihenfolge: Instagram zuerst (Haupt-Kanal), dann TikTok, YouTube, LinkedIn.
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
}: {
  platform: Platform;
  active: boolean;
}) {
  const meta = PLATFORM_META[platform];
  const Icon = meta.icon;
  return (
    <Link
      href={`/content/mein-account?platform=${platform}`}
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

export default async function MeinAccountPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const platform = parsePlatform(params.platform);

  const intel = platform === 'instagram' ? await loadContentIntel() : null;
  const handle = intel?.self_handle ?? 'self';

  // Scorecard immer laden (auch für IG-Sub-View), damit der Funnel-Overview
  // im Mein-Account-Header sichtbar ist.
  const dashboard = await loadDashboardData();
  const scorecard = dashboard?.marketing_scorecard;
  const tiktokIntel = dashboard?.tiktok_intel;
  const linkedinPlanning = dashboard?.content_planning?.linkedin ?? null;
  const linkedinPosted: ContentPiece[] = linkedinPlanning?.posted ?? [];
  const linkedinEmpty = linkedinPosted.length === 0;

  const youtubeChannel = dashboard?.content?.youtube;
  const youtubePosted: ContentPiece[] =
    dashboard?.content_planning?.youtube?.posted ?? [];
  const youtubeChannelUrl = '';

  return (
    <div className="p-6 space-y-5">
      <PageHeader
        eyebrow="Mein Account"
        title={platform === 'instagram' ? `@${handle}` : PLATFORM_META[platform].label}
        description={
          platform === 'instagram'
            ? 'Alle Metriken nach Zeitraum filterbar. Klick auf Spaltenkopf zum Sortieren.'
            : platform === 'linkedin'
              ? 'Überblick aller geposteten Posts aus dem Vault. Klick zeigt den vollen Text.'
              : platform === 'youtube'
                ? 'Channel-Stats aus der YouTube Data API (täglich um 06:20) plus Library-Eintraege aus dem Vault.'
                : platform === 'tiktok'
                  ? 'TikTok-Videos vom Apify-Scraper (täglich 06:15). Save- und Share-Rate direkt aus der Quelle.'
                  : 'Tracker für diese Plattform ist noch nicht angebunden.'
        }
        actions={
          platform === 'instagram' ? (
            <a
              href={`https://instagram.com/${handle}`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs font-mono text-muted-foreground hover:text-primary transition-colors"
            >
              instagram.com/{handle}
              <ExternalLink className="size-3" />
            </a>
          ) : platform === 'youtube' ? (
            <a
              href={youtubeChannelUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs font-mono text-muted-foreground hover:text-primary transition-colors"
            >
              
              <ExternalLink className="size-3" />
            </a>
          ) : null
        }
      />

      <div className="flex flex-wrap items-center gap-2">
        {PLATFORMS.map((p) => (
          <PlatformPill key={p} platform={p} active={p === platform} />
        ))}
      </div>

      {platform === 'instagram' ? (
        !intel?.available ? (
          <SectionCard>
            <p className="text-sm text-muted-foreground">
              {intel?.note ?? 'Tracker hat noch keinen Snapshot geschrieben.'}{' '}
              Trigger den Tracker manuell über das Einstellungen-Zahnrad (oben
              rechts), oder warte bis 06:00 Uhr morgen früh.
            </p>
          </SectionCard>
        ) : (
          <MeinAccountClient intel={intel} scorecard={scorecard} />
        )
      ) : platform === 'linkedin' ? (
        linkedinEmpty ? (
          <SectionCard
            title="Noch keine geposteten LinkedIn-Posts"
            description="Library ist leer"
          >
            <p className="text-sm text-muted-foreground leading-relaxed">
              Sobald ein Post unter{' '}
              <code className="font-mono text-[11px] bg-card px-1 py-0.5 rounded">
                04-areas/content/library/linkedin/
              </code>{' '}
              landet, erscheint er hier. Geplante Posts liegen in der{' '}
              <Link href="/content/planung?platform=linkedin" className="text-primary hover:underline">
                Planung
              </Link>
              .
            </p>
          </SectionCard>
        ) : (
          <SectionCard
            title="Gepostete Posts"
            description={`${linkedinPosted.length} Post${linkedinPosted.length === 1 ? '' : 's'} · sortiert nach Datum, neueste zuerst`}
          >
            <LinkedInPostList posted={linkedinPosted} />
          </SectionCard>
        )
      ) : platform === 'youtube' ? (
        <YouTubeAccount channel={youtubeChannel} posted={youtubePosted} />
      ) : platform === 'tiktok' ? (
        <TikTokAccount tiktok={tiktokIntel} scorecard={scorecard} />
      ) : null}
    </div>
  );
}
