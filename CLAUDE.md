# Content Dashboard — Setup-Anweisungen fuer Claude

Wenn dein User fragt das Dashboard einzurichten:

1. Lies `INSTALL.md`.
2. Fuer interaktives Setup nutze den Command `/install-content-dashboard` in
   `.claude/commands/install-content-dashboard.md` — der fuehrt Schritt fuer
   Schritt durch.
3. Die zentrale User-Config liegt in `niche.yaml` (Handle, Niche, Hashtags).
4. API-Keys in `.env` (Pflicht: APIFY_API_TOKEN, ANTHROPIC_API_KEY).

## Architektur kurz

- `scripts/` — Python-Tracker + Daten-Aggregation
- `apps/content-app/` — Next.js Frontend
- `04-areas/content/` — User-Vorlagen (Reel-Skripte, Scorecard, Playbooks)
- `05-reference/` — Tracker-Output (Snapshots, Discovery, Markt-Analyse)
- `data/` — Aggregierte JSON-Files + SQLite-DBs (alles gitignored)

## Wichtige Files

- `niche.yaml` — Single Source of Truth fuer Niche/Handle/Hashtags
- `04-areas/content/scorecard.md` — Posting-Ziele
- `scripts/instagram_tracker_config.yaml` — Tracker-Tuning (Limits, Caches)
- `scripts/tiktok_tracker_config.yaml` — analog fuer TikTok
