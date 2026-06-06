# Content Dashboard — Installation

Dieses Modul gibt dir ein lokales Dashboard für deine Instagram- und TikTok-
Reels: Live-KPIs, Audience-Analyse, Posting-Ziele, Wettbewerber-Discovery.
Laeuft auf deinem Mac, alles lokal, deine Daten bleiben bei dir.

Sag zu Claude Code: "Lies INSTALL.md und richte das fuer mich ein." Dann geht
es Schritt fuer Schritt. Oder von Hand wie unten.

---

## Was du brauchst

Vier Werte plus eine Niche-Beschreibung. Hier die Mini-Anleitung pro Stueck.

### 1. Eigener Instagram-Handle

Dein Handle ohne `@`, also `dein.handle` statt `@dein.handle`. Wird in
`niche.yaml` unter `self_handle` eingetragen.

### 2. APIFY_API_TOKEN (Pflicht)

Apify ist der Scraper, der deine Reel-KPIs aus Instagram zieht.

1. Auf [apify.com](https://apify.com) Account anlegen.
2. Im Dashboard auf **Settings → Integrations → API**.
3. **Personal API Token** kopieren.
4. In die `.env` als `APIFY_API_TOKEN=apify_api_...`

Kosten: ca. $0,30 pro Tracker-Lauf (1x taeglich = ~$9/Monat).

### 3. ANTHROPIC_API_KEY (Pflicht)

Anthropic bringt Claude — wird fuer die optionale Markt-Analyse und das
Topic-Clustering deiner Reels gebraucht.

1. Auf [console.anthropic.com](https://console.anthropic.com) Account anlegen.
2. **API Keys** anlegen, $5 Guthaben aufladen.
3. Key kopieren, in die `.env` als `ANTHROPIC_API_KEY=sk-ant-...`

Kosten: $1-3/Monat bei normalem Volumen.

### 4. Niche-Beschreibung

Eine 2-3-Saetze-Beschreibung deines Markts. Beispiel:

> Personal-Trainer fuer Frauen ueber 35. Themen: Krafttraining, Hormone,
> nachhaltiges Abnehmen. Zielgruppe: berufstaetige Frauen die abnehmen wollen
> ohne Mainstream-Diaeten.

Die KI nutzt das, um relevante Wettbewerber und Themen-Gaps zu finden.

### 5. Hashtags fuer Discovery (4-8 Stueck)

Hashtags die deinen Markt definieren. Beispiel fuer Personal-Trainerin:
`hyrox`, `krafttraining`, `nachhaltigabnehmen`, `hormone`, `fitnessfuerfrauen`.

---

## Installation Schritt fuer Schritt

### 1. Repo klonen

```bash
git clone https://github.com/MoritzM23/content-dashboard-lite ~/Developer/content-dashboard
cd ~/Developer/content-dashboard
```

### 2. Python-venv anlegen

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install apify-client anthropic pyyaml python-dateutil python-dotenv fastapi uvicorn
```

### 3. Frontend-Dependencies

```bash
cd apps/content-app
npm install
cd ../..
```

### 4. `.env` anlegen

```bash
cp .env.example .env
```

In `.env` die zwei Pflicht-Keys eintragen (`APIFY_API_TOKEN`, `ANTHROPIC_API_KEY`)
plus den Workspace-Pfad:

```
WORKSPACE_PATH=/Users/dein-name/Developer/content-dashboard
```

### 5. `niche.yaml` anlegen

```bash
cp niche.example.yaml niche.yaml
```

Datei oeffnen und ausfuellen — `self_handle`, `niche_name`, `niche_description`,
`discovery_hashtags`, optional `tracked_competitors`.

### 6. Erster Tracker-Lauf

```bash
.venv/bin/python scripts/instagram_tracker.py
```

Dauert 2-5 Minuten. Schreibt deine Reel-Daten nach
`05-reference/competitor-content/_data/<heute>.json` (wird automatisch angelegt).

### 7. Dashboard-Daten generieren

```bash
.venv/bin/python scripts/generate_dashboard_data.py
```

Dauert ~10 Sekunden. Schreibt `data/dashboard-data.json`.

### 8. Frontend starten

```bash
cd apps/content-app
npm run dev
```

Oeffnet auf http://localhost:3000. Du landest direkt auf `/content/mein-account`
und siehst deine ersten KPIs.

---

## Was du danach siehst

- **Marketing-Goal-Tracker**: Wieviele Reels du diese Woche schon hast vs. Ziel
- **KPI-Cards**: Views, Likes, ER, Comment-Rate fuer 7d / 30d / Gesamt
- **Audience-Aktivitaet**: Top-Posting-Slots, beste Wochentage nach ER + Views
- **Hashtag-Performance**: Welche Hashtags am besten laufen
- **Themen-Cluster**: KI-gruppierte Themen aus deinem Content
- **Discovery**: Cross-Creator Top-Reels aus deinem Markt

## Optional: TikTok mit dazu

Wenn du auch TikTok trackst:
1. In `niche.yaml` den `tiktok_handle` setzen.
2. `.venv/bin/python scripts/tiktok_tracker.py` laufen lassen.
3. Im Dashboard auf den TikTok-Pill klicken.

## Optional: Tracker automatisch taeglich

`config/com.content-dashboard.instagram-tracker.plist` ist ein launchd-Template. Platzhalter
ersetzen (`__WORKSPACE_PATH__`, `__PYTHON_PATH__`, `__LOG_PATH__`, `__HOME__`),
nach `~/Library/LaunchAgents/` kopieren, dann:

```bash
launchctl load ~/Library/LaunchAgents/com.content-dashboard.instagram-tracker.plist
```

Laeuft dann jeden Morgen um 06:00 automatisch.

---

## Probleme

**Apify-Run schlaegt fehl** → Pruefe ob `APIFY_API_TOKEN` korrekt in `.env` steht.
Test: `.venv/bin/python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('APIFY_API_TOKEN'))"`

**Frontend zeigt "keine Daten"** → Tracker noch nicht gelaufen, oder
`generate_dashboard_data.py` nicht ausgefuehrt. Schritte 6 + 7 nochmal pruefen.

**Discovery findet nichts** → Hashtags in `niche.yaml` zu spezifisch. 4-8
generische Tags eintragen, die in deinem Markt verbreitet sind.

---

## Kosten-Uebersicht

| Service | Kosten |
|---|---|
| Apify | ~$0,30 pro Run, also ~$9/Monat bei 1x taeglich |
| Anthropic (Sonnet) | $1-3/Monat bei normalem Volumen |
| Hosting | $0 — laeuft lokal |
| **Gesamt** | **~$10-15/Monat** |
