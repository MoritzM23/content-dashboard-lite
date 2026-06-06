import { ExternalLink, Users, Eye, Video, ThumbsUp } from 'lucide-react';
import { SectionCard } from '@/components/section-card';
import type { ContentPiece, YouTubeChannel } from '@/lib/types';

interface YouTubeAccountProps {
  channel?: YouTubeChannel;
  posted: ContentPiece[];
}

function fmtInt(n: number | null | undefined): string {
  if (n === null || n === undefined) return '0';
  return n.toLocaleString('de-DE');
}

function fmtDuration(seconds: number | null | undefined): string {
  if (!seconds || seconds <= 0) return '·';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

function ChannelStat({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Users;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-border bg-card/40 px-4 py-3">
      <Icon className="size-4 text-muted-foreground mt-0.5" />
      <div>
        <div className="label-mono text-[10px] text-muted-foreground">{label}</div>
        <div className="num-mono text-xl font-medium">{value}</div>
      </div>
    </div>
  );
}

export function YouTubeAccount({ channel, posted }: YouTubeAccountProps) {
  const subs = channel?.total_subs ?? 0;
  const totalViews = channel?.total_views ?? 0;
  const totalVideos = channel?.total_videos ?? 0;
  const recent = channel?.recent_videos ?? [];

  const sortedPosted = [...posted].sort((a, b) => {
    const ad = a.posted_at || '';
    const bd = b.posted_at || '';
    return bd.localeCompare(ad);
  });

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <ChannelStat icon={Users} label="Subscribers" value={fmtInt(subs)} />
        <ChannelStat icon={Eye} label="Gesamt-Views" value={fmtInt(totalViews)} />
        <ChannelStat icon={Video} label="Videos" value={fmtInt(totalVideos)} />
        <ChannelStat
          icon={ThumbsUp}
          label="Library-Eintraege"
          value={fmtInt(posted.length)}
        />
      </div>

      <SectionCard
        title="Top-Videos nach Views"
        description="Top 5 aus der lokalen DB (täglich um 06:20 via launchd aktualisiert)"
      >
        {recent.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Noch keine Video-Stats in der DB. Trigger den Tracker via{' '}
            <code className="font-mono text-[11px] bg-card px-1 py-0.5 rounded">
              python scripts/collect_youtube.py
            </code>
            .
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left border-b border-border">
                  <th className="label-mono py-2 pr-4 text-[10px]">Datum</th>
                  <th className="label-mono py-2 pr-4 text-[10px]">Titel</th>
                  <th className="label-mono py-2 pr-4 text-[10px] text-right">Views</th>
                  <th className="label-mono py-2 pr-4 text-[10px] text-right">Likes</th>
                  <th className="label-mono py-2 pr-4 text-[10px] text-right">Comments</th>
                </tr>
              </thead>
              <tbody>
                {recent.map((v, i) => (
                  <tr key={`${v.date}-${i}`} className="border-b border-border/40">
                    <td className="py-2 pr-4 num-mono text-muted-foreground whitespace-nowrap">
                      {v.date || '·'}
                    </td>
                    <td className="py-2 pr-4">{v.title || '·'}</td>
                    <td className="py-2 pr-4 num-mono text-right">{fmtInt(v.views)}</td>
                    <td className="py-2 pr-4 num-mono text-right">{fmtInt(v.likes)}</td>
                    <td className="py-2 pr-4 num-mono text-right">{fmtInt(v.comments)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>

      <SectionCard
        title="Library"
        description={`${posted.length} Video${posted.length === 1 ? '' : 's'} im Vault unter library/youtube/`}
      >
        {sortedPosted.length === 0 ? (
          <p className="text-sm text-muted-foreground leading-relaxed">
            Noch keine Library-Eintraege. Sobald ein Folder unter{' '}
            <code className="font-mono text-[11px] bg-card px-1 py-0.5 rounded">
              04-areas/content/library/youtube/
            </code>{' '}
            mit script.md liegt, erscheint er hier.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left border-b border-border">
                  <th className="label-mono py-2 pr-4 text-[10px]">Posted</th>
                  <th className="label-mono py-2 pr-4 text-[10px]">Titel</th>
                  <th className="label-mono py-2 pr-4 text-[10px] text-right">Views</th>
                  <th className="label-mono py-2 pr-4 text-[10px] text-right">Likes</th>
                  <th className="label-mono py-2 pr-4 text-[10px] text-right">Comments</th>
                  <th className="label-mono py-2 pr-4 text-[10px] text-right">Dauer</th>
                  <th className="label-mono py-2 pr-4 text-[10px]">Link</th>
                </tr>
              </thead>
              <tbody>
                {sortedPosted.map((p) => {
                  const k = p.kpis ?? null;
                  const views = k?.views ?? null;
                  const likes = k?.likes ?? null;
                  const comments = k?.comments ?? null;
                  const link = p.url || p.post_url || '';
                  return (
                    <tr key={p.id} className="border-b border-border/40 hover:bg-card/60 transition-colors">
                      <td className="py-2 pr-4 num-mono text-muted-foreground whitespace-nowrap">
                        {p.posted_at || '·'}
                      </td>
                      <td className="py-2 pr-4">{p.title || '·'}</td>
                      <td className="py-2 pr-4 num-mono text-right">
                        {views === null ? '·' : fmtInt(views)}
                      </td>
                      <td className="py-2 pr-4 num-mono text-right">
                        {likes === null ? '·' : fmtInt(likes)}
                      </td>
                      <td className="py-2 pr-4 num-mono text-right">
                        {comments === null ? '·' : fmtInt(comments)}
                      </td>
                      <td className="py-2 pr-4 num-mono text-right text-muted-foreground">
                        {fmtDuration(p.duration_s)}
                      </td>
                      <td className="py-2 pr-4">
                        {link ? (
                          <a
                            href={link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-[11px] text-primary hover:underline"
                          >
                            YouTube
                            <ExternalLink className="size-3" />
                          </a>
                        ) : (
                          <span className="text-[11px] text-muted-foreground">·</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>
    </div>
  );
}
