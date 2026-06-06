'use client';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { ExternalLink } from 'lucide-react';
import { BucketPill } from './bucket-pill';
import type { ContentPiece } from '@/lib/types';

interface LinkedInPostDetailDialogProps {
  piece: ContentPiece | null;
  onClose: () => void;
}

export function LinkedInPostDetailDialog({
  piece,
  onClose,
}: LinkedInPostDetailDialogProps) {
  const open = piece !== null;
  if (!piece) {
    return <Dialog open={false} onOpenChange={(o) => !o && onClose()} />;
  }
  const text = piece.post_text || '';

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="!max-w-[min(900px,95vw)] w-[95vw] max-h-[92vh] p-0 gap-0 overflow-hidden bg-card border-border flex flex-col">
        <DialogHeader className="px-6 pt-5 pb-3 pr-14 border-b border-border shrink-0">
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <span className="label-mono text-primary">
              {piece.posted_at || '—'}
            </span>
            <BucketPill bucket={piece.bucket} />
            {piece.serie && (
              <span className="label-mono text-muted-foreground">
                {piece.serie}
              </span>
            )}
          </div>
          <DialogTitle className="text-lg font-semibold leading-tight">
            {piece.hook || piece.title}
          </DialogTitle>
        </DialogHeader>

        <div className="px-6 py-5 overflow-y-auto space-y-5">
          <div>
            <div className="label-mono text-[10px] mb-2">Post-Text</div>
            {text ? (
              <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-foreground bg-card/40 border border-border rounded-lg p-4">
                {text}
              </pre>
            ) : (
              <p className="text-sm text-muted-foreground italic">
                Kein Post-Text extrahierbar. Lege im Skript einen Code-Block
                ({'```'}…{'```'}) mit dem finalen Text an, oder ergänze
                <code className="font-mono text-[11px] bg-card px-1 py-0.5 mx-1 rounded">
                  post_text: |
                </code>
                im Frontmatter.
              </p>
            )}
          </div>

          {piece.caption && (
            <div>
              <div className="label-mono text-[10px] mb-2">Notiz / Caption</div>
              <p className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">
                {piece.caption}
              </p>
            </div>
          )}

          <div className="flex flex-wrap gap-4 items-center pt-2 text-[12px]">
            <span className="font-mono text-muted-foreground">
              {piece.vault_path}
            </span>
            {piece.post_url && (
              <a
                href={piece.post_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-primary hover:underline"
              >
                Auf LinkedIn öffnen
                <ExternalLink className="size-3" />
              </a>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
