import type { Metadata } from 'next';
import { Space_Grotesk, JetBrains_Mono } from 'next/font/google';
import { Toaster } from '@/components/ui/sonner';
import { TooltipProvider } from '@/components/ui/tooltip';
import { Sidebar } from '@/components/sidebar';
import { ModeProvider } from '@/lib/mode-context';
import './globals.css';

const sans = Space_Grotesk({
  variable: '--font-sans',
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
});

const mono = JetBrains_Mono({
  variable: '--font-mono',
  subsets: ['latin'],
  weight: ['400', '500', '600'],
});

export const metadata: Metadata = {
  title: 'Content Dashboard',
  description: 'Persoenliches Operating System für Content, Sales, Wissen',
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="de"
      className={`dark ${sans.variable} ${mono.variable} h-full antialiased`}
    >
      <body className="min-h-full bg-background text-foreground">
        <ModeProvider>
          <TooltipProvider>
            <div className="flex h-screen w-full overflow-hidden">
              <Sidebar />
              <main className="flex-1 overflow-y-auto">{children}</main>
            </div>
          </TooltipProvider>
          <Toaster richColors position="bottom-right" />
        </ModeProvider>
      </body>
    </html>
  );
}
