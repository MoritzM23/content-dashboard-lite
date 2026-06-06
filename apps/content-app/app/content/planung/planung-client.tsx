'use client';

import { useCallback, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import {
  Save,
  Loader2,
  Hash,
  Mic,
  type LucideIcon,
} from 'lucide-react';
import {
  InstagramIcon,
  TikTokIcon,
  YouTubeIcon,
  LinkedInIcon,
} from '@/components/platform-icons';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { api, type PlanningFile } from '@/lib/api';
import type { ContentPiece } from '@/lib/types';

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

const STATUS_STAGES = [
  { value: 'brainstorm', label: 'Idee' },
  { value: 'draft', label: 'Skript' },
  { value: 'ready-to-film', label: 'Filmreif' },
  { value: 'in-edit', label: 'Schnitt' },
  { value: 'ready', label: 'Geplant' },
  { value: 'posted', label: 'Live' },
] as const;

function statusToneClass(status: string): string {
  const s = status.toLowerCase();
  if (s === 'live' || s === 'posted' || s === 'published')
    return 'text-ok bg-ok/10 border-ok/30';
  if (s === 'ready-to-film' || s === 'ready')
    return 'text-warn bg-warn/10 border-warn/30';
  if (s === 'brainstorm' || s === 'idea' || s === 'idee')
    return 'text-muted-foreground bg-muted/20 border-border';
  return 'text-foreground/70 bg-card border-border';
}

export function PlanungList({
  platform,
  pieces,
  openPath: openPathProp,
  onOpenPath,
}: {
  platform: Platform;
  pieces: ContentPiece[];
  /** Controlled-mode: wenn gesetzt, wird der Edit-State vom Parent verwaltet. */
  openPath?: string | null;
  onOpenPath?: (p: string | null) => void;
}) {
  const [internalOpen, setInternalOpen] = useState<string | null>(null);
  const isControlled = onOpenPath !== undefined;
  const openPath = isControlled ? (openPathProp ?? null) : internalOpen;
  const setOpenPath = isControlled ? onOpenPath! : setInternalOpen;
  const meta = PLATFORM_META[platform];
  const Icon = meta.icon;

  if (pieces.length === 0) {
    return (
      <div className="text-xs text-muted-foreground/70 py-8 text-center">
        Nichts in der {meta.label}-Pipeline. Frontmatter{' '}
        <code className="font-mono text-[10px] bg-card px-1 py-0.5 rounded">
          platform: {platform}
        </code>{' '}
        im script.md setzen.
      </div>
    );
  }

  return (
    <>
      <ul className="divide-y divide-border rounded-lg border border-border overflow-hidden bg-card/30">
        {pieces.map((p) => (
          <li key={p.id}>
            <button
              type="button"
              onClick={() => setOpenPath(p.vault_path)}
              className="w-full flex items-center gap-3 px-4 py-2.5 text-left hover:bg-card/60 transition-colors group"
            >
              <Icon className="size-3.5 text-muted-foreground shrink-0" />
              <span className="flex-1 text-sm text-foreground/90 group-hover:text-foreground truncate">
                {p.title}
              </span>
              {p.serie && (
                <span className="hidden md:inline font-mono text-[10px] text-muted-foreground/70 truncate max-w-[140px]">
                  {p.serie}
                </span>
              )}
              {p.status && (
                <span
                  className={`shrink-0 font-mono text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded border ${statusToneClass(p.status)}`}
                >
                  {p.status}
                </span>
              )}
            </button>
          </li>
        ))}
      </ul>

      {!isControlled && (
        <EditDialog
          path={openPath}
          platform={platform}
          onOpenChange={(open) => {
            if (!open) setOpenPath(null);
          }}
        />
      )}
    </>
  );
}

export { EditDialog };

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? 'http://127.0.0.1:8093';

type EditDialogProps = {
  path: string | null;
  platform: Platform;
  /** Wenn gesetzt: Inline-Video-Preview oben in der linken Spalte (autoplay muted). */
  finalMp4?: string | null;
  onOpenChange: (open: boolean) => void;
};

function EditDialog({ path, platform: listPlatform, finalMp4, onOpenChange }: EditDialogProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [data, setData] = useState<PlanningFile | null>(null);
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [status, setStatus] = useState('');
  const [hook, setHook] = useState('');
  const [caption, setCaption] = useState('');
  const [hashtags, setHashtags] = useState('');
  const [platform, setPlatform] = useState<string>('');
  const [triggerWord, setTriggerWord] = useState('');
  const [reelNummer, setReelNummer] = useState('');

  const isOpen = path !== null;

  const loadFile = useCallback(async (p: string) => {
    setLoading(true);
    const res = await api.getPlanningFile(p);
    setLoading(false);
    if ('error' in res) {
      toast.error(`Konnte nicht laden: ${res.error}`);
      onOpenChange(false);
      return;
    }
    const file = res as PlanningFile;
    setData(file);
    setTitle(file.title);
    setBody(file.body);
    const fm = file.frontmatter || {};
    setStatus(String(fm.status ?? ''));
    setHook(String(fm.hook ?? ''));
    setCaption(String(fm.caption ?? ''));
    const hs = fm.hashtags;
    setHashtags(
      Array.isArray(hs) ? hs.map((t) => `#${t}`).join(' ') : String(hs ?? '')
    );
    setPlatform(String(fm.platform ?? ''));
    setTriggerWord(String(fm['trigger-word'] ?? ''));
    setReelNummer(String(fm['reel-nummer'] ?? ''));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (path) loadFile(path);
    else setData(null);
  }, [path, loadFile]);

  async function handleSave() {
    if (!path || !data) return;
    setSaving(true);
    const res = await api.savePlanningFile(path, {
      title,
      body,
      frontmatter: {
        ...data.frontmatter,
        status: status || null,
        hook: hook || null,
        caption: caption || null,
        hashtags: hashtags || null,
        'trigger-word': triggerWord || null,
        'reel-nummer': reelNummer || null,
      },
    });
    setSaving(false);
    if ('error' in res) {
      toast.error(`Speichern fehlgeschlagen: ${res.error}`);
      return;
    }
    toast.success('Gespeichert. Liste aktualisiert.');
    router.refresh();
    onOpenChange(false);
  }

  const effectivePlatform = (platform as Platform) || listPlatform;
  const headerMeta = PLATFORM_META[effectivePlatform];
  const HeaderIcon = headerMeta.icon;

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent
        className="!max-w-5xl w-[calc(100vw-3rem)] p-0 gap-0 max-h-[90vh] flex flex-col overflow-hidden"
      >
        {/* Header */}
        <DialogHeader className="px-6 pt-6 pb-4 border-b border-border bg-card/30">
          <div className="flex items-center gap-2 text-[11px] font-mono text-muted-foreground">
            <HeaderIcon className="size-3.5" />
            <span>{headerMeta.label}</span>
            {status && (
              <>
                <span className="opacity-40">·</span>
                <span className="uppercase tracking-wider">{status}</span>
              </>
            )}
            <span className="opacity-40 mx-1">·</span>
            <span className="truncate flex-1 opacity-70">{path ?? ''}</span>
          </div>
          <DialogTitle className="text-xl font-semibold leading-tight pr-10">
            {loading ? 'Lädt…' : title || 'Reel bearbeiten'}
          </DialogTitle>
        </DialogHeader>

        {/* Body */}
        {loading || !data ? (
          <div className="flex-1 flex items-center justify-center py-16 text-muted-foreground">
            <Loader2 className="size-6 animate-spin" />
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto">
            <div className="grid grid-cols-12 gap-6 p-6">
              {/* Linke Spalte: Meta + Video-Preview */}
              <aside className="col-span-12 lg:col-span-4 space-y-4">
                {finalMp4 && (
                  <div className="rounded-lg border border-border bg-black overflow-hidden">
                    <video
                      key={finalMp4}
                      src={`${API_BASE}/content/file?path=${encodeURIComponent(finalMp4)}`}
                      controls
                      autoPlay
                      muted
                      playsInline
                      className="w-full aspect-[9/16] object-contain bg-black"
                    />
                  </div>
                )}

                <Field label="Titel">
                  <Input
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="H1 des Skripts"
                    className="text-base font-medium"
                  />
                </Field>

                <Field label="Status">
                  <StatusPills value={status} onChange={setStatus} />
                </Field>

                <Field label="Reel-Nr">
                  <Input
                    value={reelNummer}
                    onChange={(e) => setReelNummer(e.target.value)}
                    placeholder="6"
                  />
                </Field>

                <Field label="Trigger-Word" icon={Mic}>
                  <Input
                    value={triggerWord}
                    onChange={(e) => setTriggerWord(e.target.value)}
                    placeholder="z.B. dein Trigger-Wort"
                  />
                </Field>

                <Field label="Hashtags" icon={Hash}>
                  <Input
                    value={hashtags}
                    onChange={(e) => setHashtags(e.target.value)}
                    placeholder="#ai #automation"
                    className="font-mono text-xs"
                  />
                  <p className="text-[10px] text-muted-foreground/70 mt-1">
                    Space- oder Komma-getrennt, # optional
                  </p>
                </Field>
              </aside>

              {/* Rechte Spalte: Content */}
              <section className="col-span-12 lg:col-span-8 space-y-4 lg:border-l lg:border-border lg:pl-6">
                <Field label="Hook">
                  <textarea
                    value={hook}
                    onChange={(e) => setHook(e.target.value)}
                    rows={2}
                    placeholder="Der erste Satz, der scrollt stoppt…"
                    className="flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm italic shadow-xs focus-visible:ring-1 focus-visible:ring-ring focus-visible:outline-none resize-y leading-relaxed"
                  />
                </Field>

                <Field label="Caption">
                  <textarea
                    value={caption}
                    onChange={(e) => setCaption(e.target.value)}
                    rows={5}
                    placeholder="Caption für den Post…"
                    className="flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs focus-visible:ring-1 focus-visible:ring-ring focus-visible:outline-none resize-y leading-relaxed whitespace-pre-line"
                  />
                </Field>

                <Field label="Skript / Body (Markdown)">
                  <textarea
                    value={body}
                    onChange={(e) => setBody(e.target.value)}
                    rows={16}
                    spellCheck={false}
                    className="flex w-full rounded-md border border-input bg-transparent px-3 py-3 text-xs font-mono shadow-xs focus-visible:ring-1 focus-visible:ring-ring focus-visible:outline-none resize-y leading-relaxed"
                  />
                </Field>
              </section>
            </div>
          </div>
        )}

        {/* Footer */}
        <DialogFooter className="border-t border-border bg-card/30 px-6 py-3 m-0 rounded-b-xl flex-row items-center justify-end">
          <Button
            type="button"
            onClick={handleSave}
            disabled={loading || saving || !data}
            className="gap-1.5"
          >
            {saving ? (
              <Loader2 className="size-3.5 animate-spin" />
            ) : (
              <Save className="size-3.5" />
            )}
            Speichern
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function Field({
  label,
  icon: Icon,
  children,
}: {
  label: string;
  icon?: LucideIcon;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <label className="label-mono text-[10px] flex items-center gap-1.5">
        {Icon && <Icon className="size-3" />}
        {label}
      </label>
      {children}
    </div>
  );
}

function StatusPills({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  const known = STATUS_STAGES.map((s) => s.value);
  const isCustom = value && !known.includes(value as (typeof known)[number]);

  return (
    <div className="flex flex-wrap gap-1.5">
      {STATUS_STAGES.map((s) => {
        const active = value === s.value;
        return (
          <button
            key={s.value}
            type="button"
            onClick={() => onChange(active ? '' : s.value)}
            className={[
              'inline-flex items-center gap-1 rounded-md border px-2 py-1 text-[11px] transition-colors',
              active
                ? 'bg-foreground text-background border-foreground'
                : 'bg-card/40 text-foreground/70 border-border hover:bg-card/60 hover:text-foreground',
            ].join(' ')}
          >
            {s.label}
          </button>
        );
      })}
      {isCustom && (
        <span
          className="inline-flex items-center gap-1 rounded-md border border-warn/40 bg-warn/10 px-2 py-1 text-[11px] text-warn"
          title="Aus Frontmatter, nicht in der Standard-Pipeline"
        >
          {value}
        </span>
      )}
    </div>
  );
}
