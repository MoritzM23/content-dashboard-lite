'use client';

import { Target, Check } from 'lucide-react';
import type { MarketingScorecard, ScorecardGoal } from '@/lib/types';

/**
 * Minimal-Ziel-Tracker. Pro Plattform genau ein Ziel.
 * Wird auf der Plattform-Sicht (Mein-Account) als oberster Block angezeigt.
 */
export function MarketingScorecardCard({
  scorecard,
  platform,
}: {
  scorecard?: MarketingScorecard;
  platform: 'instagram' | 'tiktok';
}) {
  if (!scorecard?.available) return null;
  const goal = scorecard.goals[platform];
  if (!goal) return null;
  return <GoalTracker goal={goal} />;
}

function GoalTracker({ goal }: { goal: ScorecardGoal }) {
  const ratio = goal.target > 0 ? goal.value / goal.target : 0;
  const reached = ratio >= 1;
  const pct = Math.min(100, ratio * 100);

  return (
    <div className="rounded-xl border border-border bg-card/40 p-5">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-3">
          <div
            className={[
              'flex items-center justify-center size-10 rounded-lg border',
              reached
                ? 'bg-ok/15 border-ok/40 text-ok'
                : 'bg-primary/10 border-primary/30 text-primary',
            ].join(' ')}
          >
            {reached ? <Check className="size-5" /> : <Target className="size-5" />}
          </div>
          <div>
            <div className="label-mono text-[10px] text-muted-foreground">Mein Ziel</div>
            <div className="text-base font-semibold text-foreground">
              {goal.target} {goal.label}{' '}
              <span className="text-muted-foreground/70 font-normal">
                · {goal.period}
              </span>
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="num-mono text-2xl font-semibold">
            <span className={reached ? 'text-ok' : 'text-foreground'}>{goal.value}</span>
            <span className="text-muted-foreground/60 text-base"> / {goal.target}</span>
          </div>
          <div className="text-[10px] text-muted-foreground/70">
            {reached ? 'Ziel erreicht' : `${(ratio * 100).toFixed(0)}%`}
          </div>
        </div>
      </div>
      <div className="mt-4 h-2 bg-card/60 rounded-full overflow-hidden">
        <div
          className={[
            'h-full rounded-full transition-all',
            reached ? 'bg-ok' : 'bg-primary/70',
          ].join(' ')}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
