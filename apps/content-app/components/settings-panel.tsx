'use client';

import { useCallback, useEffect, useState } from 'react';
import { Plus, Trash2, Play, RefreshCw, Compass } from 'lucide-react';
import { toast } from 'sonner';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';

/**
 * Settings-Panel für den Content-Bereich, eingebettet im Tabs-Sheet.
 * Enthält: Self-Handle, Wettbewerber-Liste, manuelle Trigger.
 * Ersetzt die alte /content/verwaltung Page.
 */
export function SettingsPanel({ onClose }: { onClose?: () => void }) {
  const [creators, setCreators] = useState<string[]>([]);
  const [selfHandle, setSelfHandle] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [apiOffline, setApiOffline] = useState(false);

  const [newHandle, setNewHandle] = useState('');
  const [adding, setAdding] = useState(false);

  const [tracking, setTracking] = useState(false);
  const [discovering, setDiscovering] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    const res = await api.listCreators();
    if ('ok' in res) {
      setCreators(res.creators ?? []);
      setSelfHandle(res.self_handle ?? '');
      setApiOffline(false);
    } else {
      setApiOffline(true);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  function cleanHandle(raw: string): string {
    let h = raw.trim();
    if (h.startsWith('@')) h = h.slice(1);
    const m = h.match(/instagram\.com\/([A-Za-z0-9._]+)/i);
    if (m) h = m[1];
    return h.replace(/\/+$/, '');
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const handle = cleanHandle(newHandle);
    if (!handle) {
      toast.error('Bitte einen Handle eingeben');
      return;
    }
    setAdding(true);
    const res = await api.addCreator(handle);
    if ('ok' in res) {
      toast.success(`@${handle} hinzugefügt`);
      setNewHandle('');
      await load();
    } else {
      toast.error(res.error || 'Hinzufügen fehlgeschlagen');
    }
    setAdding(false);
  }

  async function handleRemove(handle: string) {
    const ok = window.confirm(`@${handle} aus der Tracking-Liste entfernen?`);
    if (!ok) return;
    const res = await api.removeCreator(handle);
    if ('ok' in res) {
      toast.success(`@${handle} entfernt`);
      await load();
    } else {
      toast.error(res.error || 'Entfernen fehlgeschlagen');
    }
  }

  async function handleTracker() {
    if (tracking) return;
    const ok = window.confirm('Tracker manuell starten? Apify-Cost ~$0.30 pro Run.');
    if (!ok) return;
    setTracking(true);
    const res = await api.triggerTracker();
    if ('ok' in res) {
      toast.success('Tracker gestartet. Ergebnisse in 2-5 Min.');
    } else {
      toast.error(res.error || 'Tracker-Start fehlgeschlagen');
    }
    setTracking(false);
  }

  async function handleDiscovery() {
    if (discovering) return;
    const ok = window.confirm('Discovery-Run starten? Apify-Cost ~$0.55, Dauer ~30 Sekunden.');
    if (!ok) return;
    setDiscovering(true);
    const res = await api.triggerDiscovery();
    if ('ok' in res) {
      toast.success('Discovery-Run gestartet.');
    } else {
      toast.error(res.error || 'Discovery-Start fehlgeschlagen');
    }
    setDiscovering(false);
  }

  return (
    <div className="space-y-6 pt-4">
      {apiOffline && (
        <div className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-xs text-destructive">
          API offline (Port 8093). Prüfe ob{' '}
          <code className="num-mono">dashboard_api.py</code> läuft.
        </div>
      )}

      <section className="space-y-2">
        <h3 className="label-mono text-[10px]">Creator hinzufügen</h3>
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            type="text"
            placeholder="@handle oder instagram.com/handle"
            value={newHandle}
            onChange={(e) => setNewHandle(e.target.value)}
            disabled={adding || apiOffline}
            autoComplete="off"
            className="flex-1 text-sm"
          />
          <Button type="submit" size="sm" disabled={adding || apiOffline}>
            <Plus className="size-3.5" />
            {adding ? '…' : 'Hinzufügen'}
          </Button>
        </form>
      </section>

      <section className="space-y-2">
        <h3 className="label-mono text-[10px]">Manuelle Aktionen</h3>
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleTracker}
            disabled={tracking || apiOffline}
          >
            <Play className="size-3.5" />
            {tracking ? 'Läuft…' : 'Tracker starten'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleDiscovery}
            disabled={discovering || apiOffline}
          >
            <Compass className="size-3.5" />
            {discovering ? 'Läuft…' : 'Discovery starten'}
          </Button>
        </div>
        <p className="text-[10px] text-muted-foreground/70 leading-snug">
          Tracker: ~$0.30 pro Run, ~2-5 Min. Discovery: ~$0.55 pro Run, ~30 Sek.
        </p>
      </section>

      <section className="space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="label-mono text-[10px]">
            Getrackte Creator{' '}
            {!loading && !apiOffline && (
              <span className="text-muted-foreground/60 font-normal">({creators.length})</span>
            )}
          </h3>
          <Button
            variant="ghost"
            size="xs"
            onClick={() => void load()}
            disabled={loading}
            aria-label="Neu laden"
          >
            <RefreshCw className={`size-3 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
        {loading ? (
          <p className="text-xs text-muted-foreground">Lädt…</p>
        ) : apiOffline ? (
          <p className="text-xs text-destructive">API offline</p>
        ) : creators.length === 0 ? (
          <p className="text-xs text-muted-foreground">
            Noch keine Creator. Oben einen Handle hinzufügen.
          </p>
        ) : (
          <ul className="divide-y divide-border rounded-md border border-border overflow-hidden">
            {creators.map((handle) => {
              const isSelf = handle === selfHandle;
              return (
                <li
                  key={handle}
                  className="flex items-center justify-between gap-2 px-3 py-2"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <a
                      href={`https://instagram.com/${handle}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-medium hover:text-primary transition-colors truncate"
                    >
                      @{handle}
                    </a>
                    {isSelf && (
                      <Badge
                        variant="outline"
                        className="font-mono text-[9px] uppercase border-primary/40 text-primary"
                      >
                        self
                      </Badge>
                    )}
                  </div>
                  {!isSelf && (
                    <Button
                      variant="ghost"
                      size="xs"
                      onClick={() => handleRemove(handle)}
                      aria-label={`@${handle} entfernen`}
                    >
                      <Trash2 className="size-3" />
                    </Button>
                  )}
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </div>
  );
}
