# Content Dashboard

> Dein eigenes Live-Tracking fuer Instagram + TikTok. KPIs, Audience-Analyse,
> Wettbewerber-Discovery, Posting-Ziele. Laeuft lokal auf deinem Mac.

| Feld | Wert |
|---|---|
| Modul | `content-dashboard` |
| Version | v1 |
| Stack | Next.js 16 · Python 3.11 · SQLite · Apify · Claude |
| Setup-Zeit | 30 bis 60 Minuten |
| Laufende Kosten | ~$10-15/Monat (Apify + Anthropic) |

## Was du bekommst

- **Live-Dashboard** unter `http://localhost:3000` mit drei Tabs:
  *Mein Account*, *Planung*, *Discovery*
- **4 Plattform-Sichten** (Instagram, TikTok, YouTube, LinkedIn) — Range-Filter
  (7 Tage, 30 Tage, Gesamt), Top-Reel-Tabelle, Audience-Aktivitaet
- **Goal-Tracker pro Plattform** ("X Reels pro Woche", Mo–So gerechnet)
- **Apify-Tracker** fuer Instagram + TikTok mit Views, Likes, Comments, Saves, Shares
- **Time-Series-DB** fuer echte View-Deltas ueber Zeit
- **Discovery-Trend-Hooks** quer durch alle relevanten Creator deines Marktes
- **Themen-Cluster** (KI-Analyse deiner Reels via Claude)
- **Markt-Analyse** (Sonnet-Uebersicht von Wettbewerber-Themen + Luecken)

## Wie es funktioniert

1. Du traegst deinen Handle und deine Niche-Beschreibung in `niche.yaml` ein.
2. Apify-Tracker zieht taeglich deine Reels + die deiner Wettbewerber.
3. Daten landen lokal in `05-reference/competitor-content/_data/`.
4. `generate_dashboard_data.py` aggregiert das in `data/dashboard-data.json`.
5. Das Frontend liest das JSON und zeigt dir das Dashboard.

Alles lokal. Keine Cloud, kein externer Server, deine Daten bleiben bei dir.

## Installation

Detaillierte Anleitung: [INSTALL.md](INSTALL.md)

Kurz-Variante mit Claude Code:

```
git clone https://github.com/MoritzM23/content-dashboard-lite
cd content-dashboard-lite
claude
> "Lies INSTALL.md und richte das fuer mich ein"
```

Claude fuehrt dich durch alle Schritte und schreibt die Configs automatisch.

## Anpassung an deine Niche

Alles was deinen Markt definiert (Handle, Hashtags, Niche-Beschreibung, getrackte
Wettbewerber) steht in **einer einzigen Datei**: `niche.yaml`. Aenderungen dort
greifen automatisch im Tracker, in der Markt-Analyse und in der Discovery.

## Ziele anpassen

`04-areas/content/scorecard.md`:

```yaml
instagram:
  reels_per_week_target: 7
tiktok:
  videos_per_week_target: 14
```

## Architektur

```
content-dashboard-lite/
├── niche.yaml             # ← Deine Markt-Konfiguration (Pflicht)
├── .env                   # ← Deine API-Keys (Pflicht)
├── apps/content-app/      # Next.js Frontend
├── scripts/               # Python-Tracker + Backend
├── config/                # launchd-Plist-Templates fuer Cron
├── 04-areas/content/      # Pipeline-Vorlagen, Goals, Playbooks
└── 05-reference/          # Tracker-Output (wird automatisch befuellt)
```

## Optional: Tracker taeglich automatisch

`config/com.aios.instagram-tracker.plist` ist ein launchd-Template. Platzhalter
ersetzen (`__WORKSPACE_PATH__`, `__PYTHON_PATH__`, `__LOG_PATH__`, `__HOME__`),
nach `~/Library/LaunchAgents/` kopieren, dann `launchctl load`. Tracker laeuft
jeden Morgen automatisch.

## Lizenz

Free fuer eigene Nutzung.
