'use client';

import { cn } from '@/lib/utils';
import type { AgentMeta } from '@/lib/ki-team-data';

interface AgentCardProps {
  agent: AgentMeta;
  active: boolean;
  onSelect: () => void;
}

export function AgentCard({ agent, active, onSelect }: AgentCardProps) {
  const Icon = agent.icon;

  return (
    <button
      type="button"
      onClick={onSelect}
      className={cn(
        'group relative flex w-full flex-col items-center justify-between rounded-2xl border bg-card/40 px-6 pt-10 pb-7 text-center transition-all duration-300',
        'min-h-[280px]',
        'hover:border-primary/60 hover:bg-card/70 hover:-translate-y-0.5',
        'hover:shadow-[0_30px_60px_-30px] hover:shadow-primary/50',
        'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/60',
        active
          ? 'border-primary/80 bg-card/80 -translate-y-0.5 shadow-[0_30px_70px_-25px] shadow-primary/60 ring-1 ring-primary/40'
          : 'border-border',
      )}
    >
      {/* aktiv-Indikator oben rechts */}
      <span className="absolute right-5 top-5 flex items-center gap-1.5 text-[10px] uppercase tracking-[0.18em] text-primary">
        <span className="relative flex h-1.5 w-1.5">
          <span
            className={cn(
              'absolute inline-flex h-full w-full rounded-full bg-primary',
              active ? 'opacity-70 animate-ping' : 'opacity-60',
            )}
          />
          <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-primary" />
        </span>
        aktiv
      </span>

      {/* Riesen-Icon */}
      <div
        className={cn(
          'flex h-24 w-24 items-center justify-center rounded-2xl transition-all duration-300',
          active
            ? 'bg-primary/20 text-primary shadow-[0_0_50px_-10px] shadow-primary/60'
            : 'bg-primary/8 text-primary/80 group-hover:bg-primary/15 group-hover:text-primary group-hover:shadow-[0_0_40px_-15px] group-hover:shadow-primary/60',
        )}
      >
        <Icon className="h-12 w-12" strokeWidth={1.5} />
      </div>

      {/* Name + Beschreibung */}
      <div className="mt-6 space-y-2">
        <h3 className="font-heading text-xl font-medium leading-tight tracking-tight text-foreground">
          {agent.name}
        </h3>
        <p className="text-xs leading-relaxed text-muted-foreground">
          {agent.description}
        </p>
      </div>
    </button>
  );
}
