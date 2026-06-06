---
tags:
  - design-system
  - pdf
  - one-pager
  - ceo-gpt
  - reference
erstellt: 2026-04-21
zuletzt-aktualisiert: 2026-05-13
---

# CEO-GPT One-Pager / PDF-Layout

> **Canonical Brand-System ab 2026-05-13:** `05-reference/design-system/ceo-gpt/` (Tokens, Marken, Imagery, Voice).
> Bei Konflikten zwischen Werten in dieser Datei und dem Bundle gewinnt **immer der Bundle**. Token-Werte (Farben, Spacing, Radii, Typo) hier sind nur als Print-Quick-Reference da — Single Source of Truth ist `ceo-gpt/colors_and_type.css`.
>
> Hard Rules aus dem Bundle gelten 1:1 auch für PDFs: kein Emoji, kein Pure-White, kein Em-Dash im Lauftext, ein Akzent (Terracotta), Du-Form, Wortmarke `CEO-GPT™` mit Unicode-TM (kein Kreis, kein ®), Mittelpunkt `·` als Voice-Tic.
>
> ---
>
> **Zweck:** Print-spezifische Layout-Regeln für CEO-GPT-Onepager (PDF), der im DM-Funnel nach Reel-Kommentaren versendet wird. Ergänzt den canonical Bundle um Print-Spezifika (DIN A4, Bleed, Print-Safe-Area, Schriftgrößen-Skala für Druck).
>
> **Aktuelle Version:** [DM-Funnel-Drive-Link](https://drive.google.com/file/d/12JIqhUmYSf9-5P_G5b00aLsA0cNs17B-/view)
> **Verwendet in:** [[dm-funnel-creatorflow]] Stufe 4 ("Jarvis Onepager öffnen")

---

## 1. Grundrahmen

| Parameter | Wert |
|---|---|
| Format | A4 Hochformat (210 x 297 mm) |
| Seiten | 2 bis 4 (aktuell ein Onepager im Geist, darf aber mehrseitig sein) |
| Rand | 24 mm oben/unten, 20 mm links/rechts |
| Hintergrund | `#17130F` vollflächig (warmes Schwarz) |
| Auflösung | 300 dpi Export, für Screen zusätzlich 1x RGB-Version |

---

## 2. Farben (Print-optimiert)

Die Design-System-Farben werden für Print leicht angepasst (sonst saufen Töne ab):

| Rolle | Screen (Hex) | Print (Hex) | Einsatz |
|---|---|---|---|
| BG | `#17130F` | `#17130F` | Hintergrund ganzseitig |
| BG-Deep | `#0A0805` | `#0A0805` | Footer, tiefe Panels |
| Cream | `#F2E8DC` | `#F2E8DC` | Haupttext |
| Cream-Muted | `#C9BDAF` | `#BFB2A3` | Caption, Meta (auf Print leicht dunkler) |
| Terracotta | `#C26B4C` | `#B55F40` | Akzente, Buttons, Highlights (Print leicht desaturiert) |
| Terracotta-Glow | `#D48466` | `#D48466` | Nur Screen, nicht in Print verwenden (verliert Glow) |

**Wichtig:** Text nie in Terracotta setzen (Lesbarkeit im Print). Cream auf Dark bleibt die Lese-Achse.

---

## 3. Typografie (Print-Scale)

Print-Sizes sind kleiner als Screen, weil der Leser näher dran sitzt.

| Rolle | Font | Weight | Size | Leading |
|---|---|---|---|---|
| Cover-Titel "Jarvis" | Space Grotesk | 500 | 72 pt | 1.0 |
| Section-Headline | Space Grotesk | 500 | 28 pt | 1.1 |
| Subhead | Space Grotesk | 600 | 16 pt | 1.2 |
| Body | Inter | 400 | 11 pt | 1.5 |
| Body-L (Intro) | Inter | 300 | 13 pt | 1.45 |
| Caption / Footer | Inter | 500 | 9 pt | 1.3 |
| Overline (TRACKED) | Space Grotesk | 600 | 10 pt, 0.15 em tracking, UPPERCASE | 1.0 |

**Fallback-Fonts im PDF:** Wenn Space Grotesk nicht embeddet werden kann, fallback auf `Inter 500 / 600`. Nie System-Fonts wie Helvetica nehmen, das bricht den Brand-Look.

---

## 4. Seiten-Architektur (Empfehlung 3-Seiter)

### Seite 1: Cover / Hook
- **Oben:** Moritz-Logomark / Name in Cream (klein, oben links)
- **Mitte:** Overline "DEIN ZWEITES GEHIRN" in Terracotta, darunter riesige "Jarvis"-Headline
- **Unter Headline:** Tagline "Dein zweites Gehirn, das nie schläft."
- **Rechts oder Mitte unten:** Iceberg-Illustration in Terracotta
- **Unten:** Meta-Zeile "Moritz Maaker ∙ AW ONE Limited ∙ Berlin" in Cream-Muted
- **Ziel:** Einziehen, neugierig machen, klar dass es nicht um einen Chatbot geht

### Seite 2: Das System (Die 5 Layer)
- **Overline:** "DIE 5 LAYER"
- **H2:** "So wird Kontext zu einem System, das arbeitet."
- **Grid 2x3** oder **vertikale Liste** mit den 5 Cards:
  - 01 / CONTEXT
  - 02 / DATA
  - 03 / INTELLIGENCE
  - 04 / AUTOMATE
  - 05 / BUILD
- Cards haben dünne Terracotta-Outline, Nummer in Terracotta, Titel in Cream, Body in Cream-Muted
- **Ziel:** System-Verständnis, nicht nur "ein Tool"

### Seite 3: Zwei Wege (CTA-Seite)
- **Overline:** "ZWEI WEGE ZU DEINEM JARVIS"
- **Split-Layout links/rechts:**
  - **Links (Card):** Second Brain Jarvis (Done-with-you), ab 5.000 €, 3 Bullet-Features, CTA-Pill "Call buchen →"
  - **Rechts (Card):** Second Brain Jarvis Community, 14 €/Monat, 3 Bullet-Features, CTA-Pill "Community beitreten"
- **Unten:** Kontakt-Zeile (Email, Website moritzmaaker.com/jarvis, Instagram @moritzmaaker)
- **Ziel:** Conversion, zwei klare Pfade

### Optional Seite 4: Über Moritz (nur wenn sinnvoll)
- Foto klein, Bio kurz (4 Sätze), Call-Link als Pill

---

## 5. Komponenten für Print

### Pill-Button (als gerenderte Form, nicht klickbar)
- Terracotta-Fill, Cream-Text, Padding 12 pt vertikal / 22 pt horizontal
- Border-Radius so groß dass es rund wirkt (mindestens Höhe / 2)
- Text in Space Grotesk 600, 12 pt, tracking -0.01 em

### Card
- Background: 2 % Cream auf Dark (sehr subtil) oder komplett transparent
- Border: 0.5 pt in `rgba(242, 232, 220, 0.1)`
- Border-Radius: 8 pt (im Print kleiner als Web, sonst wirkt es übertrieben)
- Padding: 18 pt

### Iceberg-Illustration
- Als SVG oder PNG mit mindestens 300 dpi eingebettet
- Organische Terracotta-Kurven, siehe [[jarvis-design-system]] §6
- Im Print besser mit klarer Wasserlinie (feine Cream-Linie, 50 % Opacity)

---

## 6. Whitespace & Rhythmus

Print braucht mehr Atem als Screen. Großzügig.

| Element | Abstand zu nächstem Element |
|---|---|
| Overline → Headline | 8 pt |
| Headline → Body | 16 pt |
| Body-Absatz → Body-Absatz | 10 pt |
| Section → Section | 36 pt |
| Cover-Mitte Headline → Tagline | 24 pt |

**Goldene Regel:** Lieber weniger Content pro Seite als zu dichte Seiten. Der One-Pager darf Ruhe ausstrahlen.

---

## 7. Export & Distribution

### PDF-Export
- **Embed Fonts:** Ja, beide (Space Grotesk + Inter)
- **Kompression:** Bilder 300 dpi, keine JPG-Artefakte
- **Farbprofil:** sRGB (Screen), bei echtem Print-Einsatz CMYK-Version separat anlegen
- **Metadaten:** Titel "Jarvis Onepager", Autor "Moritz Maaker", Subject "Second Brain Jarvis"

### Distributions-Kanäle
- **Google Drive (Hauptlink):** [Drive-File](https://drive.google.com/file/d/12JIqhUmYSf9-5P_G5b00aLsA0cNs17B-/view) → wird im DM-Funnel verwendet
- **LinkedIn Featured Section:** direkt als Media-Upload
- **Website Download:** später als Lead-Magnet mit Email-Capture

---

## 8. Quality-Checkliste vor Versand

- [ ] Keine Gedankenstriche (—) im Text, auch nicht in Captions
- [ ] Cover-Headline "Jarvis" zentriert und groß genug
- [ ] Farben matchen Design-System (Hex-Codes verifiziert)
- [ ] Fonts embedded, nicht als System-Fallback
- [ ] Alle CTAs zeigen auf aktuelle URLs (Calendly, Skool, Website)
- [ ] Iceberg-Illustration in 300 dpi und Terracotta-Ton korrekt
- [ ] Kontakt-Infos aktuell (Email, Instagram, LinkedIn)
- [ ] Footer enthält AW ONE Limited (Firma) + Impressum-Hinweis
- [ ] Smartphone-Test: lässt sich auf 6"-Display gut lesen (DM-Funnel-Anwendung)
- [ ] Print-Test (wenn relevant): Grauwerte nicht absaufend, Terracotta nicht zu pink

---

## 9. Ableitungen auf andere Formate

### Instagram Post-Visual (aus Onepager-Screen)
- 1080 x 1350 px (4:5)
- Gleiche Typografie, gleiche Farben
- Iceberg vertikal (Portrait-Orientierung)
- Keine CTAs einblenden (Post-Caption übernimmt das)

### LinkedIn Document-Post (PDF als Karussell)
- A4 Hochformat funktioniert direkt
- 5-10 Seiten maximal, jede Seite ein einzelner Key-Point
- Cover-Seite mit Hook, letzte Seite mit CTA

### Story / Reel Still
- 1080 x 1920 px (9:16)
- Nur 1-2 Elemente pro Still, viel Whitespace
- Safe-Zone oben und unten 220 px (UI-Overlays von Instagram)

---

## 10. Verknüpfungen

- [[jarvis-design-system]] — Basis-Design-System (Screen-first)
- [[branding]] — Messaging und Brand-Positionierung
- [[writing-style]] — Tonalität für den Textinhalt
- [[dm-funnel-creatorflow]] — Wo der Onepager im DM-Funnel landet
- [[03-projects/website-jarvis-pivot/claude-code-prompt]] — Website-Umsetzung (gleiches Design)
- [[linkedin-profile]] — LinkedIn-Anwendung

---

*Halte diese Datei aktuell, wenn sich Onepager-Layout, Distribution oder Drive-Link ändern.*
