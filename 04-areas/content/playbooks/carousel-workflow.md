---
type: playbook
tags: [content, carousel, workflow, pipeline]
status: aktiv
gilt-für: Erstellung und Posting von Karussell-Posts
---

# Karussell-Workflow Step-by-Step

> Wie ein Karussell-Post von der Idee bis ins Library wandert. Analog zum Reel-Workflow, aber mit eigener Design-Pipeline.

---

## Workflow-Phasen

```
Idee → Skript → Design → Schedule → Posten → Library + KPI-Track
```

---

## Schritt 1: Idee + Pattern waehlen

1. Pattern-Bibliothek pruefen: [[playbooks/carousel-patterns]]
2. Welcher Pattern-Typ passt zu deinem Ziel?
   - **Awareness / Save-Rate** → `quote`, `framework-list`, `data-reveal`
   - **Mid-Funnel / Education** → `listicle`, `cheat-sheet`, `mistake-better`
   - **Conversion / DM-Funnel** → `photo-overlay` mit CTA, `story-arc` mit Pain → Solution
3. Trigger-Wort waehlen (rotieren, nicht 2x dasselbe in Folge): siehe [[playbooks/brand-rules]]

---

## Schritt 2: Skript anlegen im Vault

```bash
mkdir -p $WORKSPACE_PATH/04-areas/content/pipeline/$(date +%Y-%m-%d)_<slug>
cp $WORKSPACE_PATH/04-areas/content/pipeline/_template-carousel.md \
   $WORKSPACE_PATH/04-areas/content/pipeline/$(date +%Y-%m-%d)_<slug>/script.md
```

Im script.md ausfuellen:
- Frontmatter: `template`, `slide_count`, `hook`, `cta-type`, `cta-keyword`
- Slide 1 Hook
- Slide 2 Pattern-Interrupt
- Slide 3-7 Body
- Slide 8 CTA
- Caption (im Frontmatter und nochmal ausformuliert unten)

---

## Schritt 3: Design

**Aktuell (Manual-Phase):**
- Slides in Canva oder Figma bauen, basierend auf [[playbooks/carousel-brand-rules]]
- PNGs ablegen in: `pipeline/<datum>_<slug>/slides/01.png` ... `08.png`
- Format: 1080 x 1350 (Instagram Portrait)
- Bei LinkedIn-Variante: zusaetzlich `slides-linkedin/` als 1080x1080 PNGs, am Ende als PDF zusammenfuegen

**Später (Renderer-Phase, Sprint 6e geplant):**
- HTML/CSS-Renderer `scripts/carousel_render.py` liest `script.md`
- Pro Slide ein HTML-Template aus `playbooks/carousel-templates/<slug>.html`
- Playwright/Chrome rendert auf 1080x1350 und screenshotted
- Output landet in `slides/01.png` ... automatisch
- Photos werden via CSS-`background-image` ins Template gemixed

---

## Schritt 4: Schedule oder direkt posten

**Instagram:**
- Manuell hochladen (kein Scheduler-Risiko, Algo bevorzugt nativ)
- Erste Slide aus `slides/01.png` als Cover
- Reihenfolge: 01 → 08
- Caption aus `script.md` (Sektion "Caption final")
- Hashtags aus Frontmatter

**LinkedIn:**
- Slides als PDF zusammenfuegen (1080x1080 quadratisch)
- Als Document-Post hochladen (NICHT als Image-Karussell, LinkedIn-Algo bevorzugt Documents)
- Caption laenger als bei IG (LinkedIn liest, IG scrollt)

---

## Schritt 5: Frontmatter updaten

Nach dem Posten:
```yaml
status: posted
post_url: https://www.instagram.com/p/XXXXX/
shortcode: XXXXX
posted_at: 2026-05-12T10:30:00Z
```

Der `content_pipeline_move`-Cron (taeglich 06:35) erkennt den `posted`-Status und verschiebt den Folder nach `library/instagram/<datum>_<slug>/`.

---

## Schritt 6: KPI-Track + Auto-Refresh

`content_meta_refresh.py` zieht taeglich:
- Reach, Impressions, Saves, Shares
- Karussell-spezifische Save-Rate (Save / Reach × 100)
- Slide-Completion-Rate (wenn Instagram Insights-API verfuegbar)

Live-KPIs landen in `library/instagram/<datum>_<slug>/meta.md` zwischen den AUTO-Markern.

---

## Was bei Underperformance tun

1. **Save-Rate <3%:** Hook (Slide 1) war schwach. In 14 Tagen Re-Post mit alternativem Hook aus dem `Alt-Hooks`-Block im script.md
2. **Reach unter 30% deiner Followers:** Karussell hat Engagement nicht gehalten. Slide 2 verbessern (Pattern-Interrupt-Test)
3. **DM-Rate 0:** CTA war unklar. Trigger-Wort prominenter machen, ggf. Slide 8 redesignen mit groesserem Pill-Button

---

## Cross-Posting-Regeln

| Plattform | Format | Slide-Count | Caption-Stil |
|---|---|---|---|
| Instagram (primary) | 1080x1350 PNG | 7-10 | kurz, Trigger-Wort, max 5 Hashtags |
| LinkedIn (secondary) | 1080x1080 PDF (Document) | 5-12 | laenger, Story-Frame, kein Hashtag-Spam |
| Threads | 1080x1080 PNG | max 5 | Hook-Slide + 2-3 Punkte + CTA-Slide |

Threads-Trick: Karussell als Threads-Post + Slide-Bild macht den Algo glücklich.

---

## Verknuepfungen

- [[playbooks/carousel-brand-rules]] — Design-Lock
- [[playbooks/carousel-patterns]] — Pattern-Bibliothek (wird gerade von Recherche-Agent gebaut)
- [[pipeline/_template-carousel.md]] — Skript-Template
- [[playbooks/brand-rules]] — Voice + Hashtags + Trigger-Words
- [[playbooks/cross-posting-workflow]] — Cross-Posting allgemein
