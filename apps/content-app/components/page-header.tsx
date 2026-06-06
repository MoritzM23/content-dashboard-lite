interface PageHeaderProps {
  eyebrow?: string;
  title: string;
  // ReactNode, damit Pages auch Status-Indikatoren / Inline-Markup mitgeben
  // können (siehe System-Page mit dem Overall-Health-Punkt).
  description?: React.ReactNode;
  meta?: React.ReactNode;
  actions?: React.ReactNode;
}

export function PageHeader({
  eyebrow,
  title,
  description,
  meta,
  actions,
}: PageHeaderProps) {
  return (
    <div className="flex items-end justify-between gap-6 flex-wrap mb-6">
      <div>
        {eyebrow && <div className="label-mono mb-1.5 text-primary">{eyebrow}</div>}
        <h1 className="text-2xl font-semibold tracking-tight leading-none">{title}</h1>
        {description && (
          <p className="text-sm text-muted-foreground mt-1.5">{description}</p>
        )}
      </div>
      <div className="flex items-center gap-3">
        {meta && <div className="label-mono">{meta}</div>}
        {actions}
      </div>
    </div>
  );
}
