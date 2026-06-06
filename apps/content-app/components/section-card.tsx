import { cn } from '@/lib/utils';

interface SectionCardProps {
  title?: string;
  description?: string;
  actions?: React.ReactNode;
  className?: string;
  children: React.ReactNode;
}

export function SectionCard({
  title,
  description,
  actions,
  className,
  children,
}: SectionCardProps) {
  return (
    <section
      className={cn(
        'rounded-xl border border-border bg-card/40 p-5',
        className
      )}
    >
      {(title || description || actions) && (
        <div className="flex items-start justify-between gap-4 mb-4">
          <div>
            {title && <div className="label-mono">{title}</div>}
            {description && (
              <p className="text-xs text-muted-foreground mt-1">{description}</p>
            )}
          </div>
          {actions}
        </div>
      )}
      {children}
    </section>
  );
}
