import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import type { AiStandard } from '@/lib/types';

const SENTIMENT_LABEL: Record<string, string> = {
  positive: 'positiv',
  negative: 'negativ',
  neutral: 'neutral',
  mixed: 'gemischt',
};

const SENTIMENT_CLASS: Record<string, string> = {
  positive:
    'border-ok/30 bg-ok/10 text-ok',
  negative:
    'border-destructive/30 bg-destructive/10 text-destructive',
  neutral:
    'border-border bg-muted/40 text-muted-foreground',
  mixed:
    'border-warn/30 bg-warn/10 text-warn',
};

interface SentimentPillProps {
  sentiment?: AiStandard['sentiment'];
}

export function SentimentPill({ sentiment }: SentimentPillProps) {
  if (!sentiment) return <span className="text-muted-foreground text-xs">—</span>;
  return (
    <Badge
      variant="outline"
      className={cn('font-mono text-[10px]', SENTIMENT_CLASS[sentiment])}
      title="Stimmung der Kommentare unter dem Reel"
    >
      {SENTIMENT_LABEL[sentiment] ?? sentiment}
    </Badge>
  );
}
