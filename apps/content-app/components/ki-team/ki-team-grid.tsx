'use client';

import { useState } from 'react';
import { AgentCard } from './agent-card';
import { AgentDetailPanel } from './agent-detail-panel';
import { AGENTS, DETAILS, type AgentId } from '@/lib/ki-team-data';

export function KiTeamGrid() {
  const [activeId, setActiveId] = useState<AgentId>('ceo');
  const activeAgent = AGENTS.find((a) => a.id === activeId) ?? AGENTS[0];
  const activeDetail = DETAILS[activeAgent.id];

  return (
    <div className="space-y-10">
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        {AGENTS.map((agent) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            active={agent.id === activeId}
            onSelect={() => setActiveId(agent.id)}
          />
        ))}
      </div>

      <AgentDetailPanel
        key={activeAgent.id}
        agent={activeAgent}
        detail={activeDetail}
      />
    </div>
  );
}
