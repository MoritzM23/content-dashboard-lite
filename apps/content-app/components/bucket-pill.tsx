import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

/**
 * Visualisiert den Content-Bucket eines LinkedIn-Posts.
 * Bucket-Slug bestimmt Akzent-Farbe; unbekannte Slugs landen im neutralen Stil.
 */
const BUCKET_META: Record<string, { label: string; classes: string }> = {
  'personal-story': {
    label: 'Personal Story',
    classes: 'border-primary/30 bg-primary/10 text-primary',
  },
  education: {
    label: 'Education',
    classes: 'border-ok/30 bg-ok/10 text-ok',
  },
  'build-in-public': {
    label: 'Build in Public',
    classes: 'border-warn/30 bg-warn/10 text-warn',
  },
  contrarian: {
    label: 'Contrarian',
    classes: 'border-destructive/30 bg-destructive/10 text-destructive',
  },
  'soft-pitch': {
    label: 'Soft Pitch',
    classes:
      'border-[color:var(--terra-glow)]/30 bg-[color:var(--terra-glow)]/10 text-[color:var(--terra-glow)]',
  },
};

interface BucketPillProps {
  bucket?: string;
}

export function BucketPill({ bucket }: BucketPillProps) {
  const key = (bucket ?? '').trim().toLowerCase();
  if (!key) {
    return <span className="text-muted-foreground text-xs">—</span>;
  }
  const meta = BUCKET_META[key];
  const label = meta?.label ?? key;
  const classes = meta?.classes ?? 'border-border bg-muted/40 text-muted-foreground';
  return (
    <Badge
      variant="outline"
      className={cn('font-mono text-[10px] uppercase tracking-wide', classes)}
    >
      {label}
    </Badge>
  );
}
