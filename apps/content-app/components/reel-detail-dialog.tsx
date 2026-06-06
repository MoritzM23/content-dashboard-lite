'use client';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  ExternalLink,
  Sparkles,
  MessageCircle,
  Hash,
  Flame,
  Target,
} from 'lucide-react';
import type { Reel } from '@/lib/types';
import { fmtDate, fmtNum, fmtPct } from '@/lib/format';
import { SentimentPill } from './sentiment-pill';
import { HookPill } from './hook-pill';

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? 'http://127.0.0.1:8093';

interface ReelDetailDialogProps {
  reel: Reel | null;
  onClose: () => void;
}

function commentRate(r: Reel): number {
  if (typeof r.comment_rate === 'number') return r.comment_rate;
  if (!r.views) return 0;
  return ((r.comments ?? 0) / r.views) * 100;
}

export function ReelDetailDialog({ reel, onClose }: ReelDetailDialogProps) {
  const open = reel !== null;
  const r = reel;
  const ai = r?.ai_standard ?? {};
  const deep = r?.ai_deep ?? {};
  const stats = r?.comments_stats;

  const videoSrc = r?.final_mp4
    ? `${API_BASE}/content/file?path=${encodeURIComponent(r.final_mp4)}`
    : null;

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="!max-w-[min(1400px,95vw)] w-[95vw] max-h-[92vh] p-0 gap-0 overflow-hidden bg-card border-border">
        {!r ? null : (
          <>
            <DialogHeader className="px-6 pt-5 pb-3 pr-14 border-b border-border shrink-0">
              <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                <span className="label-mono text-primary">
                  {fmtDate(r.posted)}
                </span>
                {r.posted_dayofweek && (
                  <span className="label-mono text-muted-foreground">
                    · {r.posted_dayofweek}
                    {r.posted_hour != null && ` · ${r.posted_hour}:00`}
                  </span>
                )}
                <a
                  href={r.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-[10px] font-mono uppercase tracking-wider text-muted-foreground hover:text-primary transition-colors ml-1"
                >
                  Instagram
                  <ExternalLink className="size-3" />
                </a>
              </div>
              <DialogTitle className="text-lg font-semibold tracking-tight leading-snug">
                {r.caption_snippet ?? 'Reel'}
              </DialogTitle>
            </DialogHeader>

            <div className="grid grid-cols-1 lg:grid-cols-[360px_1fr] xl:grid-cols-[400px_1fr] flex-1 min-h-0 overflow-hidden">
              {/* Linke Spalte: Video sticky */}
              <aside className="border-b lg:border-b-0 lg:border-r border-border bg-background/30 p-4 lg:overflow-y-auto">
                {videoSrc ? (
                  <video
                    key={videoSrc}
                    src={videoSrc}
                    controls
                    autoPlay
                    muted
                    playsInline
                    className="w-full max-h-[80vh] rounded-lg border border-border bg-black aspect-[9/16] object-contain"
                  />
                ) : (
                  <div className="aspect-[9/16] rounded-lg border border-dashed border-border bg-background/40 flex items-center justify-center text-xs text-muted-foreground/60 text-center px-4">
                    Kein final.mp4 im Vault.<br />
                    Drop das gepostete Video als{' '}
                    <code className="font-mono text-[10px] bg-card px-1 rounded">final.mp4</code>{' '}
                    in den Library-Folder.
                  </div>
                )}
              </aside>

              {/* Rechte Spalte: Scrollbare Insights */}
              <ScrollArea className="h-[calc(92vh-90px)]">
                <div className="px-6 py-5 space-y-5">
                {/* KPI-Pills */}
                <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
                  <KpiMini label="Views" value={fmtNum(r.views)} />
                  <KpiMini label="Likes" value={fmtNum(r.likes)} />
                  <KpiMini label="Comments" value={fmtNum(r.comments)} />
                  <KpiMini
                    label="ER"
                    value={fmtPct(r.engagement_rate)}
                    accent="ok"
                  />
                  <KpiMini
                    label="C-Rate"
                    value={fmtPct(commentRate(r))}
                    accent="ok"
                  />
                  <KpiMini
                    label="Länge"
                    value={r.video_duration ? `${Math.round(r.video_duration)}s` : '—'}
                  />
                </div>

                {/* AI-Pills (Hook, Sentiment, Topic) */}
                {(ai.hook_score || ai.sentiment || ai.topic_tag) && (
                  <div className="flex flex-wrap gap-2 items-center">
                    {ai.hook_score && (
                      <HookPill score={ai.hook_score} type={ai.hook_type} />
                    )}
                    {ai.sentiment && <SentimentPill sentiment={ai.sentiment} />}
                    {ai.topic_tag && (
                      <Badge
                        variant="outline"
                        className="font-mono text-[10px] border-primary/30 bg-primary/10 text-primary"
                      >
                        <Hash className="size-2.5 mr-1" />
                        {ai.topic_tag}
                      </Badge>
                    )}
                    {(ai.topic_subtags ?? []).map((s, i) => (
                      <Badge
                        key={i}
                        variant="outline"
                        className="font-mono text-[10px] text-muted-foreground"
                      >
                        {s}
                      </Badge>
                    ))}
                  </div>
                )}

                {/* Bewertung · Funnel-Sicht (prominent, gleich nach KPIs) */}
                {deep.why_it_worked && (
                  <Section
                    icon={Flame}
                    label="Bewertung · Funnel-Sicht"
                    accent="primary"
                  >
                    <div className="rounded-lg bg-primary/[0.06] border border-primary/20 p-4 space-y-3">
                      <div>
                        <div className="label-mono text-primary mb-1.5">
                          Funnel-Performance dieses Reels
                        </div>
                        <p className="text-sm leading-relaxed">
                          {deep.why_it_worked}
                        </p>
                      </div>

                      {deep.recommendation && (
                        <div>
                          <div className="label-mono text-primary mb-1.5">
                            Empfehlung fürs nächste Reel
                          </div>
                          <p className="text-sm leading-relaxed">
                            {deep.recommendation}
                          </p>
                        </div>
                      )}

                      {(deep.replicable_patterns?.length ?? 0) > 0 && (
                        <div>
                          <div className="label-mono text-primary mb-1.5">
                            Replizierbare Patterns
                          </div>
                          <ul className="text-sm space-y-1 list-disc pl-5">
                            {(deep.replicable_patterns ?? []).map((p, i) => (
                              <li key={i}>{p}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {deep.hook_breakdown && (
                        <div>
                          <div className="label-mono text-primary mb-1.5">
                            Hook-Breakdown
                          </div>
                          <p className="text-sm leading-relaxed text-foreground/85">
                            {deep.hook_breakdown}
                          </p>
                        </div>
                      )}

                      {deep.audience_insight && (
                        <div>
                          <div className="label-mono text-primary mb-1.5">
                            Audience-Insight
                          </div>
                          <p className="text-sm leading-relaxed text-foreground/85">
                            {deep.audience_insight}
                          </p>
                        </div>
                      )}

                      {deep.viral_factors && (
                        <div>
                          <div className="label-mono text-primary mb-2">
                            Viral-Faktoren (1-10)
                          </div>
                          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                            {Object.entries(deep.viral_factors).map(([k, v]) => (
                              <div
                                key={k}
                                className="flex items-center justify-between bg-background/40 border border-border rounded-md px-3 py-1.5"
                              >
                                <span className="text-xs text-muted-foreground capitalize">
                                  {k.replace('_', ' ')}
                                </span>
                                <span className="num-mono text-sm font-semibold">
                                  {v}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </Section>
                )}

                {/* Caption full */}
                {r.caption_full && (
                  <Section label="Caption">
                    <div className="text-sm text-foreground/90 leading-relaxed whitespace-pre-wrap rounded-lg bg-background/40 border border-border p-4">
                      {r.caption_full}
                    </div>
                  </Section>
                )}

                {/* Summary */}
                {r.summary && (
                  <Section icon={Sparkles} label="Worum geht's" accent="primary">
                    <div className="text-sm leading-relaxed text-foreground rounded-lg bg-primary/[0.06] border-l-2 border-primary p-4">
                      {r.summary}
                    </div>
                  </Section>
                )}

                {/* Transkript */}
                {r.transcript && (
                  <Section label="Transkript">
                    <div className="text-sm text-foreground/80 leading-relaxed rounded-lg bg-background/40 border-l-2 border-muted-foreground/40 p-4 max-h-72 overflow-y-auto whitespace-pre-wrap">
                      {r.transcript}
                    </div>
                  </Section>
                )}

                {/* AI-Standard: Audience-Questions + Observations */}
                {(ai.audience_questions?.length ?? 0) > 0 && (
                  <Section
                    icon={MessageCircle}
                    label="Was fragt die Audience"
                    accent="primary"
                  >
                    <ul className="text-sm text-foreground/90 space-y-1.5 pl-1">
                      {(ai.audience_questions ?? []).map((q, i) => (
                        <li
                          key={i}
                          className="rounded-md bg-background/40 border border-border px-3 py-2"
                        >
                          {q}
                        </li>
                      ))}
                    </ul>
                  </Section>
                )}

                {(ai.key_observations?.length ?? 0) > 0 && (
                  <Section icon={Target} label="Key Observations">
                    <ul className="text-sm text-foreground/90 space-y-1 list-disc pl-5">
                      {(ai.key_observations ?? []).map((o, i) => (
                        <li key={i}>{o}</li>
                      ))}
                    </ul>
                  </Section>
                )}

                {/* Comment-Stats */}
                {stats && (stats.total_count ?? 0) > 0 && (
                  <Section icon={MessageCircle} label="Kommentar-Analyse">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      <KpiMini
                        label="Top-Likes"
                        value={fmtNum(stats.top_likes ?? 0)}
                      />
                      <KpiMini
                        label="Unique"
                        value={fmtNum(stats.unique_commenters ?? 0)}
                      />
                      <KpiMini
                        label="Reply-Ratio"
                        value={fmtPct((stats.reply_ratio ?? 0) * 100, 0)}
                      />
                      <KpiMini
                        label="Span (h)"
                        value={(stats.time_span_hours ?? 0).toFixed(1)}
                      />
                    </div>
                    {(stats.top_words?.length ?? 0) > 0 && (
                      <div className="mt-3">
                        <div className="label-mono mb-2">Top-Words</div>
                        <div className="flex flex-wrap gap-1.5">
                          {(stats.top_words ?? []).slice(0, 12).map((w, i) => (
                            <span
                              key={i}
                              className="font-mono text-xs bg-background/40 border border-border rounded px-2 py-0.5"
                            >
                              {w.word}
                              <span className="text-muted-foreground ml-1">
                                {w.count}
                              </span>
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </Section>
                )}
                </div>
              </ScrollArea>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}

function Section({
  icon: Icon,
  label,
  accent,
  children,
}: {
  icon?: React.ComponentType<{ className?: string }>;
  label: string;
  accent?: 'primary';
  children: React.ReactNode;
}) {
  return (
    <section>
      <div
        className={`label-mono mb-2 inline-flex items-center gap-1.5 ${accent === 'primary' ? 'text-primary' : ''}`}
      >
        {Icon && <Icon className="size-3" />}
        {label}
      </div>
      {children}
    </section>
  );
}

function KpiMini({
  label,
  value,
  accent,
}: {
  label: string;
  value: string | number;
  accent?: 'ok';
}) {
  return (
    <div className="rounded-lg border border-border bg-background/40 px-3 py-2">
      <div className="label-mono text-[9px] mb-1">{label}</div>
      <div
        className={`num-mono text-sm font-semibold ${accent === 'ok' ? 'text-ok' : ''}`}
      >
        {value}
      </div>
    </div>
  );
}
