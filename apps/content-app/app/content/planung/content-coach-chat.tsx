'use client';

import { useEffect, useRef, useState } from 'react';
import { Wand2, Send, Hash } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

type Msg = { role: 'user' | 'assistant'; content: string };

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? 'http://127.0.0.1:8093';

const CAPABILITIES = [
  'Hook-Coach',
  'Skript-Generator',
  'Caption-Writer',
  'Trigger-Word-Rotation',
  'Cross-Posting IG/LI/YT',
];

const QUICK_PROMPTS = [
  'Gib mir 3 Hook-Optionen für ein Reel zum nächsten BAUEN-Trigger.',
  'Was war an meinen letzten 3 Reels schwach? Konkrete Diagnose.',
  'Schreib mir ein 30-Sekunden-Skript für einen LinkedIn-Karussell zum Thema KI-Team.',
];

export function ContentCoachChat() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  async function send(text: string) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    const next: Msg[] = [...messages, { role: 'user', content: trimmed }];
    setMessages(next);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/coach/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: next }),
      });
      const json = await res.json();
      if (!res.ok || json.error) {
        throw new Error(json.error || `HTTP ${res.status}`);
      }
      setMessages([...next, { role: 'assistant', content: json.content }]);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Fehler');
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setMessages([]);
    setError(null);
  }

  return (
    <div className="rounded-xl border border-primary/30 bg-primary/[0.05] overflow-hidden">
      <div className="flex items-center justify-between gap-3 px-5 py-3 border-b border-primary/20 bg-primary/[0.04]">
        <div className="flex items-center gap-2.5">
          <div className="relative">
            <Wand2 className="size-5 text-primary" />
            <span className="absolute -top-1 -right-1 flex size-2">
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-ok opacity-70" />
              <span className="relative inline-flex size-2 rounded-full bg-ok" />
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="label-mono text-primary">Content-Coach</span>
              <span className="font-mono text-[10px] uppercase tracking-wider text-ok bg-ok/10 px-1.5 py-0.5 rounded border border-ok/30">
                live
              </span>
            </div>
            <div className="text-[11px] text-muted-foreground">
              Sonnet · System-Prompt aus ~/.claude/agents/content-coach.md · Vault-Kontext live
            </div>
          </div>
        </div>
        {messages.length > 0 && (
          <button
            type="button"
            onClick={reset}
            className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground hover:text-foreground transition-colors"
          >
            Neu
          </button>
        )}
      </div>

      {messages.length === 0 && (
        <div className="px-5 py-4 space-y-3">
          <p className="text-sm text-foreground/85 leading-relaxed">
            Liest beim ersten Send automatisch deine letzte AI-Analyse, Brand-Rules,
            Pipeline-State, Performance-Anker und Wettbewerbs-Top-Overview. Antwortet
            im 3-Optionen-Format mit Hook, Voice-Opener, Setting, Caption und
            Performance-Evidenz.
          </p>
          <div className="flex flex-wrap gap-2">
            {CAPABILITIES.map((label) => (
              <span
                key={label}
                className="font-mono text-[10px] uppercase tracking-wider text-primary/80 bg-primary/10 px-2 py-1 rounded border border-primary/20"
              >
                <Hash className="size-2.5 inline mr-1" />
                {label}
              </span>
            ))}
          </div>
          <div className="pt-1">
            <div className="label-mono text-[10px] mb-1.5">Schnellstart</div>
            <div className="flex flex-col gap-1.5">
              {QUICK_PROMPTS.map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => send(p)}
                  className="text-left text-xs px-3 py-2 rounded-lg bg-card/40 border border-border hover:bg-card/60 hover:border-primary/40 transition-colors"
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {messages.length > 0 && (
        <div
          ref={scrollRef}
          className="px-5 py-4 space-y-3 max-h-[520px] overflow-y-auto"
        >
          {messages.map((m, i) => (
            <div
              key={i}
              className={[
                'rounded-lg px-3.5 py-2.5 text-sm',
                m.role === 'user'
                  ? 'bg-foreground/[0.05] border border-border ml-8 whitespace-pre-wrap'
                  : 'bg-card/60 border border-primary/20 mr-8',
              ].join(' ')}
            >
              <div className="label-mono text-[10px] mb-1">
                {m.role === 'user' ? 'Du' : 'Coach'}
              </div>
              {m.role === 'user' ? (
                <div className="text-foreground/90 leading-relaxed">
                  {m.content}
                </div>
              ) : (
                <div className="markdown-body text-sm text-foreground/90 leading-relaxed">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {m.content}
                  </ReactMarkdown>
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="mr-8 bg-card/60 border border-primary/20 rounded-lg px-3.5 py-2.5">
              <div className="label-mono text-[10px] mb-1">Coach</div>
              <div className="flex gap-1.5 items-center text-sm text-muted-foreground">
                <span className="inline-block size-1.5 rounded-full bg-primary animate-pulse" />
                <span className="inline-block size-1.5 rounded-full bg-primary animate-pulse [animation-delay:200ms]" />
                <span className="inline-block size-1.5 rounded-full bg-primary animate-pulse [animation-delay:400ms]" />
                <span className="ml-2">denkt nach</span>
              </div>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="px-5 py-2 text-xs text-destructive bg-destructive/10 border-t border-destructive/30">
          {error}
        </div>
      )}

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="flex items-end gap-2 p-3 border-t border-primary/20 bg-background/40"
      >
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              send(input);
            }
          }}
          placeholder="Frag den Coach... (Enter = senden, Shift+Enter = neue Zeile)"
          rows={2}
          disabled={loading}
          className="flex-1 resize-none bg-card/60 border border-border rounded-lg px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="inline-flex items-center gap-1.5 rounded-lg bg-primary text-primary-foreground px-3.5 py-2 text-xs font-medium hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Send className="size-3.5" />
          Senden
        </button>
      </form>
    </div>
  );
}
