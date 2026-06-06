---
tags:
  - design-system
  - jarvis
  - ceo-gpt
  - branding
  - reference
erstellt: 2026-04-21
zuletzt-aktualisiert: 2026-05-13
---

# Jarvis · CEO-GPT Design-System

> **Canonical Source ab 2026-05-13:** [[ceo-gpt/README]]
>
> Der vollständige Bundle (Tokens-CSS, SVG-Marken, App-Icon, Icon-Sprite, Bronze-Imagery, Preview-Karten, SKILL.md) liegt unter `05-reference/design-system/ceo-gpt/`.
>
> **Token-Werte aus:** `05-reference/design-system/ceo-gpt/colors_and_type.css` (alle CSS-Custom-Properties, Letter-Spacing-Stufen, Spacing-Skala, Radii, Shadows, Motion).
>
> **Marken-Assets aus:** `05-reference/design-system/ceo-gpt/assets/` (`mark-g.svg` ist die Primärmarke, `wordmark-horizontal.svg` für Headers, `app-icon.svg` für iOS/macOS, `icons.svg` als 24px-Sprite, `imagery/brain|voice|hand.png` als Bronze-Serie).
>
> **Hard Rules** (gegen Verstoß: nicht verhandelbar) in `05-reference/design-system/ceo-gpt/SKILL.md`: kein Emoji, kein Pure-White, kein kühler Ton, ein Akzent (Terracotta), kein Em-Dash im Lauftext, zwei Schriften (Space Grotesk + Inter), Du-Form, Imagery-Platzhalter bleiben bis Kunde liefert.
>
> Das Dokument hier bleibt als historische Referenz für die ältere Jarvis-Iteration (Iceberg-Metapher, Loom-Präsentation). Bei Konflikten: **CEO-GPT-Bundle gewinnt**.
>
> ---
>
> **Anwendungsbereich:** moritzmaaker.com, LinkedIn, Instagram, PDFs, Decks, Banner, alle internen Apps (content-app, dashboard, voice-os).

---

## 1. Design-Philosophie

**Warm. Tief. Organisch.**

Das Jarvis-Branding arbeitet mit einer **Iceberg-Metapher**: Was du von einem Geschäft siehst (Meetings, Mails, Kalender) ist die Spitze. Darunter liegt die unsichtbare Masse an Kontext und Wissen. Jarvis macht diese Masse sichtbar und nutzbar.

**Drei Design-Prinzipien:**
1. **Tiefe statt Flächigkeit.** Warme Schwarz-Töne und sanfte Gradienten geben Räumlichkeit. Kein Flat-Design.
2. **Terracotta als Signatur.** Ein warmer, menschlicher Akzent gegen das Dunkle. Terracotta = Handwerk, Erde, Wärme. Nicht Tech-Blue.
3. **Organische Formen.** Gebogene Kurven statt harter Kanten. Icebergs sind nicht polygonal.

**Stimmung:** Ruhig, souverän, premium, leicht mystisch. Wie ein Butler im Schatten. Nicht laut. Nicht aufdringlich.

---

## 2. Farbpalette

### Primär

| Variable | Hex | Verwendung |
|---|---|---|
| `--bg` | `#17130F` | Haupthintergrund (warmes Schwarz) |
| `--bg-deep` | `#0A0805` | Tiefere Sektionen, Schatten |
| `--water` | `#0A0E16` | Sekundär-Hintergrund (Wasser-Look) |
| `--water-deep` | `#030508` | Tiefster Hintergrund |

### Text & Kontent

| Variable | Hex | Verwendung |
|---|---|---|
| `--cream` | `#F2E8DC` | Haupttext, Hero-Headlines |
| `--cream-muted` | `#C9BDAF` | Sekundärtext, Captions |
| `--muted` | `#6B5F54` | Metadaten, Tertiärtext |
| `--line` | `rgba(242, 232, 220, 0.08)` | Trennlinien, Borders |

### Akzent (Terracotta)

| Variable | Hex | Verwendung |
|---|---|---|
| `--terracotta` | `#C26B4C` | Haupt-Akzent, Buttons, Links, Highlights |
| `--terracotta-glow` | `#D48466` | Hover-States, Glows, Heller Akzent |
| `--terracotta-deep` | `#6E3726` | Tiefere Akzente, Schatten |

### Ice-Tones (optional, für tieferen Iceberg-Look)

| Variable | Hex | Verwendung |
|---|---|---|
| `--ice-light` | `#EDF3F6` | Iceberg-Spitze |
| `--ice-mid` | `#B8C9D3` | Iceberg-Mitte |
| `--ice-shadow` | `#6A7C89` | Iceberg-Schatten |
| `--ice-deep` | `#2F4050` | Unter Wasser |
| `--ice-submerged` | `#1A2834` | Tief unten |

---

## 3. Typografie

### Fonts

- **Display / Headlines:** `Space Grotesk`, Weights 500 / 600 / 700
- **Body / UI:** `Inter`, Weights 300 / 400 / 500 / 600

**Google Fonts Import:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

### Scale

| Rolle | Font | Weight | Size (Desktop) | Letter-Spacing |
|---|---|---|---|---|
| Hero | Space Grotesk | 500 | 6.5rem (104px) | -0.035em |
| H1 | Space Grotesk | 500 | 4rem (64px) | -0.035em |
| H2 | Space Grotesk | 500 | 2.5rem (40px) | -0.025em |
| H3 | Space Grotesk | 600 | 1.5rem (24px) | -0.015em |
| Body L | Inter | 400 | 1.125rem (18px) | -0.01em |
| Body | Inter | 400 | 1rem (16px) | -0.005em |
| Body S | Inter | 400 | 0.875rem (14px) | 0 |
| Caption | Inter | 500 | 0.75rem (12px) | 0.08em (tracked) |
| Overline (TRACKED) | Space Grotesk | 600 | 0.875rem (14px) | 0.15em |

### Regeln

- **Hero-Text:** Immer `--cream`, nie `--terracotta`. Terracotta bleibt Akzent.
- **Überschriften-Akzent:** Einzelnes Wort kann in `--terracotta` hervorgehoben werden (`<span class="accent">`).
- **Body:** Standard `--cream` oder `--cream-muted`.
- **Letter-Spacing:** Großes negativ für Display, leicht negativ für Body, positiv für Overlines/Captions.
- **Font-Weight:** Headlines eher 500 (nicht 700), für feineren Look. Inter 300 für zarten Body.

---

## 4. Komponenten

### Buttons

**Primary (Terracotta-Fill):**
```css
.btn-primary {
  background: var(--terracotta);
  color: var(--bg);
  font-family: 'Space Grotesk';
  font-weight: 600;
  padding: 14px 28px;
  border-radius: 999px;
  border: none;
  letter-spacing: -0.01em;
  transition: all 0.3s ease;
}
.btn-primary:hover {
  background: var(--terracotta-glow);
  transform: translateY(-1px);
}
```

**Secondary (Outline):**
```css
.btn-secondary {
  background: transparent;
  color: var(--cream);
  border: 1px solid var(--line);
  padding: 14px 28px;
  border-radius: 999px;
  transition: all 0.3s ease;
}
.btn-secondary:hover {
  border-color: var(--terracotta);
  color: var(--terracotta);
}
```

**Wichtig:** Pill-Buttons (`border-radius: 999px`), keine scharfen Ecken. Das ist der Bruch zum alten Minimalist-Black-White-Branding.

### Cards

```css
.card {
  background: rgba(242, 232, 220, 0.02);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 32px;
  backdrop-filter: blur(8px);
}
.card:hover {
  border-color: rgba(194, 107, 76, 0.3);
  background: rgba(242, 232, 220, 0.03);
}
```

### Pills / Labels

```css
.pill {
  background: var(--bg);
  border: 1px solid var(--terracotta-deep);
  color: var(--cream-muted);
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 0.875rem;
  font-family: 'Inter';
}
```

---

## 5. Backgrounds & Texturen

### Atmosphärischer Glow

Radial Gradients mit Terracotta, sehr low-opacity, als Page-Background:

```css
body::before {
  content: "";
  position: fixed;
  inset: 0;
  background:
    radial-gradient(ellipse at 20% 30%, rgba(194, 107, 76, 0.05) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 70%, rgba(194, 107, 76, 0.03) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}
```

### Hero-Gradient (Horizont-Effekt)

```css
.hero {
  background: linear-gradient(
    180deg,
    var(--bg) 0%,
    var(--bg) 28%,
    var(--water) 52%,
    var(--water-deep) 100%
  );
}
```

Simuliert einen Horizont: oben warm (Himmel), unten kühler (Wasser).

### Grain-Overlay (optional)

Subtile SVG-Noise-Textur über dem gesamten Layout:

```css
body::after {
  content: "";
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg ...grain-svg.../%3E");
  opacity: 0.04;
  pointer-events: none;
  mix-blend-mode: overlay;
}
```

---

## 6. Iconografie & Illustration

### Iceberg als Kern-Visual

Die Iceberg-Metapher ist das visuelle Signature-Element. Varianten:

- **Full Iceberg:** Komplett mit Über- und Unterwasser-Teil plus Labels (Meetings, Mails, Kalender etc.)
- **Tip Only:** Nur die Spitze, für kompaktere Formate (z.B. Banner)
- **Outline:** Nur die Silhouette, für Icon-Verwendung

**Stil-Regeln:**
- Organische Kurven, keine Polygone
- Haupt-Teil in `--terracotta`, Highlight in `--terracotta-glow`, Schatten in `--terracotta-deep`
- Unterwasser-Teil größer als Überwasser (typischerweise 1.8x)
- Wasserlinie als feine Cream-Linie mit ~40% Opacity

### Labels um den Iceberg

Pills mit dünner Terracotta-Outline, dunklem BG, Cream-muted Text. Dünne Verbindungslinien zum Iceberg (`--muted`, 1px).

### Icons

Empfohlen: **Lucide** oder **Heroicons** in `--cream-muted`, stroke-width 1.5.

---

## 7. Animation

### Mikrointeraktionen

- **Hover-Lift:** `transform: translateY(-1px)` bei Buttons
- **Border-Glow:** Bei Cards, Transition auf Border-Color
- **Smooth-Scroll:** `scroll-behavior: smooth`

### Hero-Animation

Langsame, organische Bewegung. Keine harten Transitions. Beispiel: Iceberg leicht auf-und-ab floaten mit `@keyframes` (6s ease-in-out infinite).

### Scroll-Reveal

Elemente faden bei Scroll-in sanft ein (0.8s ease). Nie poppig, nie schnell.

---

## 8. Layout-Prinzipien

### Spacing

Basis-Einheit: **8px**. Alles ist ein Vielfaches davon.

| Name | Wert |
|---|---|
| xs | 4px |
| sm | 8px |
| md | 16px |
| lg | 24px |
| xl | 48px |
| 2xl | 96px |

### Container

- Max-width: **1200px** für Content
- Max-width: **1440px** für Hero/Banner
- Padding: **60px** Desktop, **24px** Mobile

### Sections

- Min-height: **100vh** für Hero
- Min-height: **auto** für Content-Sections, aber großzügiges Padding (mind. 120px vertikal)
- Transition zwischen Sections: leichter Gradient oder Farbwechsel

---

## 9. Responsive

### Breakpoints

| Name | min-width |
|---|---|
| xs | 0 |
| sm | 640px |
| md | 768px |
| lg | 1024px |
| xl | 1280px |
| 2xl | 1536px |

### Mobile-Anpassungen

- Hero font-size: 3rem (statt 6.5rem)
- Padding: 24px statt 60px
- Navigation als Burger
- Iceberg-Visual vertikal statt horizontal

---

## 10. Assets & Ressourcen

**Im Vault:**
- `05-reference/assets/jarvis-loom-presentation.html` — Referenz-HTML mit vollem Design
- `08-attachments/linkedin-banner-jarvis.png` — LinkedIn Banner (1584x396)

**Externe Libraries (für Website):**
- [Google Fonts: Space Grotesk + Inter](https://fonts.google.com)
- [Lucide Icons](https://lucide.dev)
- [Tailwind CSS](https://tailwindcss.com) (optional als Utility-Framework)

---

## 11. Do's & Don'ts

### Do's
- Warme, dunkle Hintergründe mit subtilen Terracotta-Glows
- Viel Whitespace, großzügige Proportionen
- Organische Kurven, Pill-Buttons, abgerundete Cards
- Cream-Text auf Dark-BG (nie umgekehrt)
- Terracotta als Akzent, nicht als Hauptfarbe

### Don'ts
- Keine harten, kantigen Buttons (das alte Design)
- Keine hellen Weiß-Hintergründe
- Keine Neon-Farben, keine harten Primärfarben außer Terracotta
- Keine Gedankenstriche im Text
- Keine steifen Corporate-Fotos
- Kein Flat-Design ohne Tiefe
- Keine Icons in Terracotta-Fill (sieht zu "marketing" aus)

---

## 12. Verwendung in verschiedenen Formaten

### Website (moritzmaaker.com)
→ Siehe [[03-projects/website-jarvis-pivot/claude-code-prompt]]

### LinkedIn
→ Banner in `08-attachments/linkedin-banner-jarvis.png`, Headline + About in [[linkedin-profile]]

### Instagram
→ Feed-Posts in warmen Terracotta-Tönen, Reels-Hooks in Cream auf Dark-BG

### PDFs & Decks
→ Space Grotesk / Inter, Terracotta-Akzente, viel Whitespace. Detaillierte Print-Spec: [[jarvis-onepager-layout]]

### HTML-Slideshows / On-Screen-Visuals
→ Komponenten-Library für Decks (Step-Indikatoren, Stat-Rows, Mockups, Timelines, Hub-Diagramme, Hammer-Slides): [[jarvis-slide-patterns]]

### E-Mail-Templates
→ Max. 600px Content-Breite, Terracotta für CTAs, sonst Cream auf Dark-BG

---

## Verknüpfungen

- [[branding]] — Brand-Positioning (Messaging-Ebene)
- [[writing-style]] — Tonalität
- [[offer]] — Produktangebot
- [[linkedin-profile]] — LinkedIn-Umsetzung
- [[jarvis-persona]] — TTS-Persona und Verhalten
- [[jarvis-onepager-layout]] — PDF- und One-Pager-spezifische Spec
- [[jarvis-slide-patterns]] — HTML-Slide-Komponenten (Decks, Pitch-Slides, Recording-Visuals)
