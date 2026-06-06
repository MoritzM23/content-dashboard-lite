'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Flame } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Lite-Sidebar: nur Content-Tab. Das ist ein fokussiertes Modul, kein
 * Multi-Bereich-Workspace.
 */
const NAV = [
  { href: '/content/mein-account', label: 'Content', icon: Flame },
] as const;

export function Sidebar() {
  const pathname = usePathname();

  function isActive(href: string): boolean {
    return pathname === href || pathname.startsWith('/content');
  }

  return (
    <aside className="w-56 border-r border-border h-full flex flex-col p-3 gap-1">
      <div className="px-2 py-3 mb-2 border-b border-border">
        <div className="text-sm font-semibold tracking-tight">Content Dashboard</div>
        <div className="text-[10px] text-muted-foreground/70 mt-0.5">Lite</div>
      </div>
      {NAV.map((item) => {
        const Icon = item.icon;
        const active = isActive(item.href);
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors',
              active
                ? 'bg-primary/10 text-primary font-medium'
                : 'text-muted-foreground hover:text-foreground hover:bg-card/60'
            )}
          >
            <Icon className="size-4" />
            {item.label}
          </Link>
        );
      })}
    </aside>
  );
}
