---
type: playbook
tags: [content, carousel, brand, design, instagram, linkedin, ceo-gpt]
status: aktiv
gilt-für: alle Karussell-Posts auf Instagram und LinkedIn
quelle: 05-reference/design-system/ceo-gpt/README.md
zuletzt-aktualisiert: 2026-05-13
---

# Karussell-Brand-Rules

> Single Source of Truth für das visuelle Design von Karussell-Posts. Pflicht-Lektuere vor jeder Karussell-Erstellung. Basiert auf dem **canonical CEO-GPT-Design-System** (`05-reference/design-system/ceo-gpt/`) und übertraegt es auf das Karussell-Format. Bei Konflikten gewinnt der Bundle.

---

## 1. Format-Spec

| Plattform | Aspect Ratio | Pixel | Anzahl Slides |
|---|---|---|---|
| **Instagram (Portrait)** | 4:5 | 1080 x 1350 | 7-10 (Sweet Spot: 8) |
| **Instagram (Square)** | 1:1 | 1080 x 1080 | 7-10 |
| **LinkedIn Document-Post** | 1:1 | 1080 x 1080 (als PDF) | 5-12 (Sweet Spot: 7) |
| **Threads** | 1:1 | 1080 x 1080 | max 5 |

**Default für CEO-GPT:** Instagram 4:5 Portrait. Bekommt mehr Feed-Real-Estate, hoehere Save-Rate.

**Safe-Area:** Mindestens 80px Padding zum Rand (Instagram blendet auf manchen Geraeten Teile aus). Wichtige Inhalte nie naeher als 120px zum unteren Rand.

---

## 2. Farb-Tokens (aus CEO-GPT-Bundle, Werte aus `ceo-gpt/colors_and_type.css`)

| Token | Hex | Verwendung im Karussell |
|---|---|---|
| `--dark` | `#17130F` | Haupt-Hintergrund jeder Slide |
| `--dark-deep` | `#0A0805` | Slide 1 + Slide 8 für mehr Tiefe |
| `--dark-raised` | `#1B1612` | Innere Tiles, gehobene Karten auf Slides |
| `--cream` | `#F2E8DC` | Haupttext, Headlines |
| `--cream-muted` | `#C9BDAF` | Sekundaertext, Labels, Slide-Nummern |
| `--cream-dim` | `#8C8479` | Metadaten, kleine Annotations, Tertiaerinfo |
| `--terra` | `#C26B4C` | Akzent: einzelne Worte, Number-Badges, CTA-Buttons |
| `--terra-glow` | `#D48466` | Hover/Highlight in interaktiven Layouts (selten), Eyebrow-Farbe |
| `--terra-deep` | `#6E3726` | Tiefere Akzente, Schatten unter Pills, Borders |
| `--terra-ember` | `#3A1A11` | Tiefste Glut, fast schon schwarz |
| Border | `color-mix(in srgb, #6E3726 50%, transparent)` | Trennlinien, Card-Borders (kaum sichtbar) |

**Semantik (warm-shifted, niemals kuehle Toene):**
- Olive `#7A8A4E` (positive), Amber `#D9A24E` (warning), Fired-Clay `#B14A3A` (danger)

**Regel:** Pro Slide HOECHSTENS ein Terracotta-Akzent. Sonst wirkt es zu marketing-laut.

**Eyebrow-Stil:** UPPERCASE, Inter 500, 11–14px, `letter-spacing: 0.32em`, in Terra-Glow `#D48466`. Mit Mittelpunkt `·` separiert: `SLIDE 03 · DENKEN`.

---

## 3. Typografie

### Schriftgroessen für 1080 x 1350

| Rolle | Font | Weight | Size | Verwendung |
|---|---|---|---|---|
| **Hero-Headline** | Space Grotesk | 500 | 96-128px | Slide 1 Hook |
| **Slide-Headline** | Space Grotesk | 500 | 72-96px | Slide 2-7 Top-Line |
| **Sub-Headline** | Space Grotesk | 600 | 40-56px | Untertitel auf Slide 1 |
| **Body L** | Inter | 400 | 32-40px | Hauptfliesstext |
| **Body** | Inter | 400 | 28px | Bullet-Punkte, Listen |
| **Caption** | Inter | 500 | 22px | Annotation, Quelle, Footnotes |
| **Overline** | Space Grotesk | 600 | 22px, +0.15em letter-spacing | "SLIDE 03", Section-Labels |

**Letter-Spacing:**
- Headlines: `-0.035em` (Display-Tracking, fest)
- Body: `-0.005em`
- Overlines/Slide-Nummern: `+0.15em` (gespreizt, uppercase)

**Line-Height:**
- Headlines: `1.05` (eng)
- Body: `1.5` (atmen)

---

## 4. Layout-Patterns pro Slide

### Slide 1 (Hook)

```
+----------------------------+
|                            |
|  [Overline: SERIE]         |  ← oben links, mini
|                            |
|                            |
|  HOOK-HEADLINE             |  ← gross, 50% der Slide-Hoehe
|  in cream auf bg           |
|                            |
|  optional ein Wort         |
|  in terracotta             |
|                            |
|                            |
|                            |
|  [Iceberg-Mini] [CEO-GPT]  |  ← unten, klein
+----------------------------+
```

### Slide 2-7 (Body)

```
+----------------------------+
|  [03]  [SECTION-LABEL]     |  ← Slide-Nummer + Section
|                            |
|  SLIDE-HEADLINE            |
|  in cream                  |
|                            |
|  Body-Text in cream-muted, |
|  2-4 Zeilen max.           |
|                            |
|  • Bullet 1                |
|  • Bullet 2                |
|                            |
|  [optional: Visual / Photo]|
|                            |
|  [moritzmaaker.com]        |  ← Wordmark Footer
+----------------------------+
```

### Slide 8 (CTA)

```
+----------------------------+
|                            |
|  CTA-HEADLINE              |
|                            |
|  Photo Moritz oder Logo    |
|                            |
|  [TERRACOTTA-PILL-BUTTON]  |  ← "Kommentier BLUEPRINT"
|                            |
|  Folge für mehr           |
|                            |
|  [Iceberg] [CEO-GPT]       |
+----------------------------+
```

---

## 5. Visuelle Elemente

### Number-Badges (Slide-Counter)

Top-Left, klein:
```
[ 03 / 08 ]
```
- Font: Inter 500, 22px, `--cream-muted`
- Background: `--bg-deep`, abgerundet (Pill, `border-radius: 999px`)
- Padding: 6px 14px
- Border: 1px solid `--line`

### Number-Highlights (im Content)

Wenn ein Listenpunkt mit einer Nummer beginnt:
```
01.  Dein Mitarbeiter kennt dein Business.
```
- Number in Space Grotesk 600, 48px, `--terracotta`
- Text danach in Cream

### Iceberg-Signatur

Klein unten links auf Slide 1 und Slide 8. Outline-Variante, 80x80px:
- Stroke: `--terracotta`, 1.5px
- Fill: transparent
- Wasserlinie als feine Cream-Linie

Nicht auf jeder Slide. Nur Slide 1 + Slide 8. Sonst zu viel.

### Wordmark Footer

Bottom-Right, sehr klein:
```
moritzmaaker.com
```
- Inter 400, 18px, `--cream-muted`
- Auf jeder Slide
- Nie größer werden

### Pill-Buttons (CTA-Mockup)

Auf Slide 8:
- Background: `--terracotta`
- Text: `--bg` (warmes Schwarz auf Terracotta)
- Font: Space Grotesk 600, 32px
- Padding: 20px 40px
- Border-Radius: 999px (Pill)
- Optional: leichter Drop-Shadow `0 4px 24px rgba(194,107,76,0.3)`

### Photos

- **Slide 1 (optional):** Photo Moritz als Background mit Overlay-Gradient `bg-bottom → transparent`
- **Slide 8 (oft):** Photo Moritz portrait, neben oder unter dem CTA
- **Slides 3-7 (selten):** Photo nur wenn es den Content-Punkt unterstuetzt, nicht als Deko
- Tonalitaet der Photos: warm (Terracotta-Lichter), nicht kalt, leicht filmisch
- Filter: Wenn noetig, leichter Warm-Filter (z.B. Lightroom Preset "Warm Earth")

### Iconografie

Lucide oder Heroicons, stroke-width 1.5, in `--cream-muted` oder `--terracotta`. Nie gefuellt, nie bunt.

---

## 6. Background-Treatments

### Standard

`--bg` (`#17130F`) flat. Funktioniert immer.

### Atmospheric-Glow (für Hook + CTA-Slide)

Radial-Gradient subtil:
```css
background:
  radial-gradient(ellipse at 30% 20%, rgba(194, 107, 76, 0.08) 0%, transparent 60%),
  #17130F;
```

### Horizont-Gradient (für Story-Karussells)

```css
background: linear-gradient(180deg, #17130F 0%, #0A0E16 70%, #030508 100%);
```

### Grain-Overlay (optional)

SVG-Noise 4% Opacity, mix-blend-mode `overlay`. Macht das Karussell weniger flat, mehr "Print".

---

## 7. Pattern-Templates (Naming-Convention)

Diese Template-Slugs verweisen auf konkrete HTML-Renderer-Templates (kommt in einem zweiten Build-Schritt):

| Template-Slug | Verwendung |
|---|---|
| `framework-list` | Numerierte Punkte, je Slide ein Punkt |
| `quote` | Breaking-News-Format, grosse Quote + Foto + Quelle |
| `photo-overlay` | Photo Background + Text-Overlay (Slide 1 + 8 typisch) |
| `split-screen` | Vertikaler Split, links/rechts oder oben/unten Vergleich |
| `listicle` | Mehrere Bullets pro Slide, mehr Inhalt pro Slide |
| `story-arc` | Drei-Akt-Struktur, Story-Beats |
| `mistake-better` | Slide N "Mistake" rot, Slide N+1 "Better" terracotta |
| `cheat-sheet` | Tabellarisch, viele kleine Infos pro Slide |
| `data-reveal` | Grosse Zahl pro Slide, Mini-Kontext |
| `hot-take` | Statement-Slides, polarisierend, kein Visual |

---

## 8. Pflicht-Checks vor dem Posten

- [ ] Slide 1 funktioniert als Standalone (Save-Test)
- [ ] Slide 8 hat klaren CTA
- [ ] Kein Gedankenstrich `—` irgendwo
- [ ] Echte Umlaute (`ä ö ü ß`), keine ASCII-Substitute
- [ ] Max 1 Terracotta-Akzent pro Slide
- [ ] Wordmark `moritzmaaker.com` auf jeder Slide
- [ ] Safe-Area eingehalten (120px unten frei)
- [ ] Photos warm-toned, nicht kalt
- [ ] LinkedIn-Variante als PDF gerendert wenn Cross-Posting

---

## 9. Was wir NIE machen

- Helle Hintergruende (Cream-BG kommt nicht in Karussells)
- Neon-Farben, Tech-Blau, hartes Pink
- Stockfotos von "Business-Leuten" mit Suits
- Comic-Sans-Vibes, Handschrift-Fonts auf der Hook
- Mehr als 6 Hashtags in der Caption
- Slide ohne Headline (jede Slide MUSS einen Anchor haben)
- Whitespace-Geiz (lieber weniger Worte als Wand-aus-Text)
- Kreis-Bullets in Magenta oder so. Wenn Bullets, dann Inter `•` in `--cream-muted`

---

## 10. Verknuepfungen

- [[05-reference/design-system/jarvis-design-system]] — Vollstaendiges Design-System
- [[playbooks/carousel-patterns]] — Pattern-Bibliothek (was wann verwenden)
- [[playbooks/brand-rules]] — Caption + Hashtag + Voice-Regeln (gilt auch für Karussells)
- [[pipeline/_template-carousel.md]] — Skript-Template
