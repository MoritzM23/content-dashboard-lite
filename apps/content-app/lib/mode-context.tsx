'use client';

/**
 * Persistenter Mode-Context (Live vs. Demo).
 *
 * Hintergrund: Vorher lebte der State nur im useState der Übersichts-Page.
 * Beim Routenwechsel fiel er auf 'live' zurück. Jetzt liegt er im Root-Layout
 * und wird in localStorage gespiegelt (Key: aios-dashboard-mode).
 *
 * SSR-Strategie:
 *   - Initialwert auf Server und beim ersten Client-Render: 'live'.
 *   - Nach Mount lesen wir localStorage und hydraten, falls dort 'demo' steht.
 *   - Dadurch kein Hydration-Mismatch, weil der erste Render auf beiden Seiten
 *     identisch ist.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react';
import type { Mode } from './types';

const STORAGE_KEY = 'aios-dashboard-mode';

type ModeContextValue = {
  mode: Mode;
  setMode: (mode: Mode) => void;
};

const ModeContext = createContext<ModeContextValue | null>(null);

export function ModeProvider({ children }: { children: ReactNode }) {
  // Start immer auf 'live' (SSR-stable). Nach Mount evtl. hydraten.
  const [mode, setModeState] = useState<Mode>('live');

  useEffect(() => {
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      if (stored === 'demo' || stored === 'live') {
        setModeState(stored);
      }
    } catch {
      // localStorage kann in privaten Modi blockiert sein. Dann bleibt 'live'.
    }
  }, []);

  const setMode = useCallback((next: Mode) => {
    setModeState(next);
    try {
      window.localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // siehe oben
    }
  }, []);

  return (
    <ModeContext.Provider value={{ mode, setMode }}>
      {children}
    </ModeContext.Provider>
  );
}

export function useMode(): ModeContextValue {
  const ctx = useContext(ModeContext);
  if (!ctx) {
    throw new Error('useMode muss innerhalb von <ModeProvider> aufgerufen werden.');
  }
  return ctx;
}
