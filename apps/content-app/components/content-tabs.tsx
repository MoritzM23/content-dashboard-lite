'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Settings } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { SettingsPanel } from '@/components/settings-panel';

const TABS = [
  { href: '/content/mein-account', label: 'Mein Account' },
  { href: '/content/planung', label: 'Planung' },
  { href: '/content/discovery', label: 'Discovery' },
] as const;

export function ContentTabs() {
  const pathname = usePathname();
  const [settingsOpen, setSettingsOpen] = useState(false);

  return (
    <div className="border-b border-border px-6 pt-5">
      <nav className="flex items-center justify-between gap-2 flex-wrap" aria-label="Content-Tabs">
        <div className="flex gap-1 flex-wrap">
          {TABS.map((tab) => {
            const active = pathname === tab.href || pathname.startsWith(tab.href + '/');
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={cn(
                  'px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors',
                  active
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground'
                )}
                aria-current={active ? 'page' : undefined}
              >
                {tab.label}
              </Link>
            );
          })}
        </div>

        <button
          type="button"
          onClick={() => setSettingsOpen(true)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-muted-foreground hover:text-foreground border border-border rounded-md hover:bg-card/60 transition-colors mb-1"
          aria-label="Content-Einstellungen"
        >
          <Settings className="size-3.5" />
          Einstellungen
        </button>
        <Sheet open={settingsOpen} onOpenChange={setSettingsOpen}>
          <SheetContent side="right" className="w-[440px] sm:w-[520px] overflow-y-auto">
            <SheetHeader>
              <SheetTitle>Content-Einstellungen</SheetTitle>
            </SheetHeader>
            <div className="px-4 pb-6">
              <SettingsPanel onClose={() => setSettingsOpen(false)} />
            </div>
          </SheetContent>
        </Sheet>
      </nav>
    </div>
  );
}
