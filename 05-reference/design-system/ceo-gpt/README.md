# CEO-GPT Design System

> **Maßgeschneiderte KI-Mitarbeiter für Führungskräfte und High-Performer im deutschsprachigen Raum.**
> Ruhig, verlässlich, loyal — wie der beste Mitarbeiter, den du je hattest.

This is the design system for **CEO-GPT™** — a German-language product that delivers bespoke AI "employees" to executives and senior operators. Everything in this folder — colors, type, marks, voice, UI kit — is built to make new CEO-GPT artifacts feel like they belong to that one specific brand.

---

## Sources

This system was reconstructed from a single self-contained brief:

| Source | Path | What it gave us |
|---|---|---|
| Brand Guidelines (HTML bundle) | `uploads/CEO-GPT Brand Guidelines.html` | Tile-grid brand sheet with hero, palette, type, voice, imagery world, logo candidates |
| Extracted template | `uploads/template.html` | Inter + Space Grotesk @font-face declarations, root color tokens |
| Extracted marks | `uploads/script_b84242a8.jsx` | All six logo-mark candidates, with rationale in DE |
| Extracted brand sheet | `uploads/script_5228e740.jsx` | Card composition, voice axes, imagery direction |

No codebase, no Figma, no slide deck were provided. This system covers brand foundations only — marks, color, type, voice, imagery. A product UI kit is intentionally not included.

---

## Index

```
.
├── README.md                  ← you are here
├── SKILL.md                   ← Agent-Skill entry point (mirrors this README)
├── colors_and_type.css        ← all CSS vars: color, type, spacing, radii, motion
├── assets/                    ← logos, app icon, icon sprite, imagery
│   ├── imagery/
│   │   ├── brain.png               ← bronzenes Gehirn   · "Denken"
│   │   ├── voice.png               ← bronzenes Mikrofon · "Stimme"
│   │   └── hand.png                ← bronzene Hand      · "Hand"
│   ├── mark-g.svg                  ← PRIMARY mark · "Das G"
│   ├── mark-cg-nested.svg          ← alt · Verschachteltes CG
│   ├── mark-cg-pair.svg            ← alt · CG nebeneinander
│   ├── mark-inscription.svg        ← alt · stacked CEO/GPT block
│   ├── mark-cartouche.svg          ← alt · Punzierte Meistermarke
│   ├── mark-negative-g.svg         ← alt · Kolophon block
│   ├── wordmark-horizontal.svg     ← G + "CEO-GPT™" horizontal lockup
│   ├── wordmark-stacked.svg        ← stacked CEO / GPT lockup
│   ├── app-icon.svg                ← iOS/macOS squircle (terra gradient)
│   └── icons.svg                   ← UI icon sprite · 24px · stroke 1.6
└── preview/                   ← design-system tab cards (registered as assets)
```

---

## Company & product context

**CEO-GPT** sells *AI Mitarbeiter* — German for "AI employees" — to executives, founders, and high-performers in the DACH region (Germany, Austria, Switzerland). The product positioning is not "another ChatGPT wrapper" but **a bespoke, hand-trained colleague** who knows your business, your tone, and your customers. The category cue is closer to *bespoke suit* or *private banker* than to *productivity SaaS*.

Three things drive every design decision:

1. **Premium, not pop.** No neon, no purple gradients, no emoji explosions, no rocket icons. The visual world is warm-dark, museum-specimen, terracotta-on-felt-black — the inside of an old Munich watchmaker's atelier, rendered in 4K.
2. **German-first.** Copy is German by default. UI labels are German. Tone is *Sie*-formal but warm. English exists only in technical product names (CEO-GPT itself, "App Icon", etc.).
3. **One trusted accent.** A single color does the heavy lifting: **terracotta**. Everything else is cream-on-warm-black. No cool tones anywhere — no blue, no indigo, no slate.

---

## Content fundamentals

How copy is written for CEO-GPT.

### Language
- **German (de-DE)** is the default. Switzerland and Austria are addressed; Hochdeutsch is the register.
- English appears only in (a) product names (`CEO-GPT`), (b) borrowed tech terms when no clean German exists (`App Icon`, `Render`, `KI`), and (c) section labels in internal brand documents (`Primary Mark`, `Color System`, `Brand Voice`).

### Form of address
- **Du** is used for the primary audience. Despite the executive audience, the brand chose `Du` to feel like *a trusted colleague, not a service provider*. ("Wie der beste Mitarbeiter, den du je hattest.")
- Never `Sie`. Never first-person ("ich kann dir helfen…") from the product itself — the AI is positioned as a *colleague*, not an *assistant*, so it speaks plainly without the servile register.

### Tone
The brand sheet plots tone on five axes. The brand sits on the LEFT side of each:

| Brand is… | …not |
|---|---|
| ruhig | laut |
| premium | plakativ |
| modern | trendy |
| warm | leger |
| präzise | pedantisch |

In practice: short, clean sentences. Specific nouns. No exclamation marks. No hype words ("revolutionary", "game-changing", "10x"). No marketing imperatives ("Jetzt starten!!"). Numbers tabular, prices in `€`, dates in `TT.MM.JJJJ`.

### Casing
- **Headlines:** sentence case in German (i.e. nouns capitalized, everything else lowercase). Never ALL CAPS for headlines.
- **Eyebrows / labels:** UPPERCASE, with `letter-spacing: 0.32em`. This is the *only* place uppercase is used. Eyebrows are usually English ("BRAND VOICE", "APP ICON", "TYPOGRAPHY") because that's the internal-document convention; in customer-facing UI, eyebrows in German work too.
- **Body:** standard German capitalization.
- **Wordmark:** `CEO-GPT` — hyphen-separated, with the standard Unicode trademark glyph `™` (U+2122) as a small superscript when on chrome surfaces. No circle around the TM — the official mark is the bare glyph.

### Punctuation
- German quotation marks: `„abc"` not `"abc"` for in-body quotations.
- The brand's signature glyph is the **mittelpunkt** `·` (U+00B7) between words in eyebrows and metadata: `BRAND GUIDELINES · v1`, `iOS · macOS · Squircle 38px Radius`. This is the brand's voice tic — adopt it.
- **No em dash in body copy.** Use a period and start a new sentence, or use a mittelpunkt. The em dash is reserved for very rare internal/editorial use (and structural notes like this one). Hyphen-as-dash is also forbidden.
- The product's hyphen in `CEO-GPT` is U+002D.

### Vibe — example copy
Live samples from the brief, with notes:

> **„Maßgeschneiderte KI-Mitarbeiter für Führungskräfte und High-Performer im deutschsprachigen Raum. Ruhig, verlässlich, loyal — wie der beste Mitarbeiter, den du je hattest."**
> ↳ Specific audience, three-word value prop, em-dash payoff. Confident, no caveats.

> **„Der beste Mitarbeiter, den du je hattest."**
> ↳ Hero claim. Eight words. No verbs about features. Du-form.

> **„Wortmarke + »G« · auf allen Markenoberflächen"**
> ↳ Internal label. German quotes around the glyph name. Mittelpunkt separator.

> **„Vertikal · für Visitenkarten, Stempel, Auflagen"**
> ↳ Three concrete use-cases, no marketing language. The word "Stempel" (rubber stamp) is the kind of physical-world noun this brand uses on purpose.

### What to never write
- Emojis. None. Not 🚀, not ✨, not 👋.
- Hype superlatives: "amazing", "revolutionary", "best-in-class", "unprecedented".
- Hedging tics: "actually", "just", "simply", "leider".
- Anglicisms when a clean German word exists ("downloaden" → "herunterladen"; but "App" stays).
- ALL CAPS for emphasis. Bold or italic if you must.

---

## Visual foundations

Everything you need to make a new artifact feel on-brand.

### Color
- **Warm-dark stage.** Primary canvas is `#0A0805` (deep), with cards at `#17130F` and raised tiles at `#1B1612`. The deltas between the three are tiny on purpose — depth comes from glow, not contrast.
- **Cream paper.** Foreground is always cream `#F2E8DC`, with `#C9BDAF` for secondary and `#8C8479` for tertiary. Pure white is forbidden — it reads cold against the warm dark.
- **One accent.** Terracotta `#C26B4C`, with `#D48466` for highlight/hover and `#6E3726` for atmosphere (the bottom-anchored radial glow on hero cards). `#3A1A11` is the deepest ember tone, used for borders against the stage.
- **Semantic colors are warm-shifted.** Success is olive `#7A8A4E`, warning is amber `#D9A24E`, danger is fired-clay `#B14A3A`. No green-blue, no cobalt, no purple ever.
- **No gradients except:** (a) the app icon's terra→terra-deep, (b) the radial atmospheric glow at the bottom of hero cards. Never linear gradients across whole pages, never multi-stop rainbows.

### Type
- **Display: Space Grotesk** — 600/700 only. Tight tracking (`-0.05em` for hero, `-0.035em` for wordmark, `-0.02em` for h1/h2). Used for the wordmark, hero headlines, and section titles.
- **Body: Inter** — 300/400/500/600. `-0.01em` to `0`. Used for everything else.
- **No serif. No mono in production UI.** Mono (`JetBrains Mono`) is allowed only in (a) eyebrows on placeholder/internal cards, and (b) inline code. Never use a third typeface.
- **Eyebrows are UPPERCASE Inter 500, 11px, `letter-spacing: 0.32em`, in terracotta-glow.** This is a signature.

### Spacing
8pt grid. Tokens `--s-1` through `--s-16` (4 → 64px). Card padding is typically `--s-10` (40px) on the inside, with `--s-4` (16px) gutters between cards in the brand-sheet grid.

### Backgrounds
- **Felt black is the default.** Full-bleed `#0A0805`. No textures, no noise, no gradients across the whole viewport.
- **Imagery world: real photography, to be supplied.** The brand team will provide the production imagery directly — placeholder tiles in this system (dashed border + "Platzhalter · Bild folgt vom Kunden") are intentional and stay in until those files arrive. Direction once images land: photoreal, studio-lit, shallow DoF, warm tungsten grading, collector-cabinet energy. **No people. No screens. No abstract shapes. No clip art.**
- **Imagery is warm-graded.** If a photo is brought in, it should be tungsten/candle warm, never daylight. Black-and-white is acceptable if the warmth is preserved through toning.
- **Backgrounds may carry the signature radial glow** — `radial-gradient(60% 80% at 50% 110%, terraDeep 40% → transparent 65%)` — anchored to the bottom of hero cards. This is the brand's *one* atmospheric effect.
- **Diagonal stripe placeholder** (`repeating-linear-gradient(135deg, dark 0 6px, darkDeep 6px 12px)`) is the official "missing imagery" marker. Always with a terra-glow eyebrow saying "PLATZHALTER".

### Animation
- **Default ease: `cubic-bezier(0.22, 0.61, 0.36, 1)`** — a calm ease-out. The brand's word is *ruhig*.
- **Durations:** 140ms (button press / icon swap), 220ms (default), 420ms (hero / atmospheric).
- **Allowed:** opacity fades, small translate-Y (≤ 4px) for menus, subtle scale (0.98–1.0) on press.
- **Forbidden:** bounces, springs, overshoots, parallax, scroll-jacking. Nothing that draws attention to the motion itself.

### Hover / press states
- **Hover (text links / icons):** color shifts from `--cream-muted` → `--cream`, or background tint `rgba(244,235,223,0.04)`. Never an underline appearing on hover.
- **Hover (primary button):** background `--terra` → `--terra-glow`, 140ms.
- **Press:** scale `0.98` + inset shadow `--shadow-press`. 80ms in, 140ms out.
- **Focus:** 1px terra-glow ring `outline: 1px solid var(--terra-glow); outline-offset: 2px`. No double rings, no glow effects.

### Borders, shadows, elevation
- **Borders are 1px, terracotta-deep at ~50% alpha.** `color-mix(in srgb, var(--terra-deep) 50%, transparent)`. They're almost-invisible — visible only when the surface needs to declare itself against a slightly different background.
- **Card shadow:** `0 6px 18px rgba(0,0,0,0.35)` + 1px white inset highlight at 3%. Tiny. The shadow is for separation, not drama.
- **Raised (app icon, key CTAs):** `0 18px 40px rgba(0,0,0,0.45)` + inset white highlight at 18%. The only place we use a strong shadow.
- **No outer glows.** Light is always *behind* the surface (the radial bottom-anchored glow), never *around* it.

### Corner radii
- **Cards: 22px** (`--r-xl`). This is the brand's signature radius. Larger than typical SaaS, smaller than fully-pill.
- **Inner tiles: 12–14px**.
- **Inputs / chips / small controls: 8–10px**.
- **App icon: 38px squircle** at 200×200 source. Scales proportionally.
- **Pills: 999px** — used for tags and status dots.

### Cards
- Background `--dark` or `--dark-raised`, padding 36–48px, radius 22px.
- Hero cards add the `--glow-terra` radial at the bottom.
- 1px terra-deep border only when the card sits on another dark surface of the same value.
- **Card label** (eyebrow) at top-left; **descriptor** at bottom in `--cream-muted` 12px.

### Transparency, blur
- **Sparingly.** Modal scrims are `rgba(10,8,5,0.75)` + `backdrop-filter: blur(12px)`. Floating toolbars at the bottom of the chat use `rgba(23,19,15,0.85) + blur(20px)`.
- **No frosted-glass for whole panels** — the brand is grounded, not floaty.

### Layout rules
- **Max content width: 1480px** (from the brand sheet itself).
- **Page padding: 56px top / 32px sides** on desktop.
- **12-column grid** with 16px gutters for the brand sheet; 8-column for product pages.
- **Sidebars** in product UI are 280px wide, dark-deep background, full bleed top-to-bottom.
- **Bottom-fixed elements** (chat composer, save bar) sit with the same blur treatment as modals.

---

## Iconography

CEO-GPT does not ship an icon font and the brief did not include a third-party icon set. We made conservative choices:

- **A small in-house sprite ships at `assets/icons.svg`.** 24px grid, 1.6px stroke, `butt` caps, `miter` joins — the same drawing tone as the brand mark (which is also a 12px butt/miter stroke). Set covers chat, navigation, file/doc, user, settings, status, mic, send, and a small handful of action verbs. ~25 icons total.
- **Stroke style only.** No filled icons. This matches the calligraphic, cut-not-stamped character of the wordmark.
- **No emoji, ever.** The brief is explicit: this is a brand of physical-world nouns (Stempel, Holzsockel, Messingschild). Emoji break the register.
- **No Unicode pictograms either** — `★ ✓ ✗` etc. Use the sprite. The single exception is the brand's signature **mittelpunkt `·`** and the **em dash `—`**, both of which are typographic, not pictographic.
- **`™`** (U+2122) is used on the wordmark on official surfaces (hero, footer, business cards). Internal/secondary uses can drop it. Never `®` — the mark is trademark, not registered.
- **The G mark itself is used in places a typical brand would use an icon** — the bottom-right of the app, the favicon, the chat composer's send avatar. Treat the G as the brand's only proprietary glyph.

**Substitution note for downstream agents:** if the in-house sprite is missing an icon you need, prefer **Lucide** (`https://unpkg.com/lucide-static@latest/icons/`) — closest stroke style and weight match. Pick the stroke variant, never the filled one. **Flag the substitution** when you do it.

---

## Logo marks

Six candidate marks live in `assets/`. The brief did not declare a winner. Our recommendation, used as primary throughout this kit:

| File | Name | Use |
|---|---|---|
| `mark-g.svg` | **Das G** ← PRIMARY | App icon, chat composer, favicon, places that need a single glyph |
| `wordmark-horizontal.svg` | G + CEO-GPT™ horizontal | Headers, business cards, signature lockup |
| `wordmark-stacked.svg` | Stacked CEO/GPT | Vertical surfaces, stamps, embossing |
| `mark-cg-nested.svg` | Verschachteltes CG | Alternative monogram |
| `mark-cg-pair.svg` | CG nebeneinander | Alternative pair |
| `mark-inscription.svg` | CEO/GPT inscription block | Favicon-as-typography |
| `mark-cartouche.svg` | Punzierte Meistermarke | "Maker's stamp" treatment |
| `mark-negative-g.svg` | Kolophon-Block | Negative-space G in a square |

All marks use `fill="currentColor"` so you can drop them into any color context — cream on dark, dark on terra, white on cream.

---

## Caveats

Things you should know before extending this system.

1. **Fonts are CDN-loaded from Google Fonts**, not bundled. The original brief used the same Google Fonts hosts. If we need offline-safe self-hosted woff2, ask the brand team for the licensed copies.
3. **Imagery world: Bronze-Serie geliefert.** Drei freigestellte Studio-Objekte in Bronze — `brain.png` (Denken), `voice.png` (Stimme), `hand.png` (Hand) — leben in `assets/imagery/`. Tonalität (terracotta-on-warm-dark, warmes Tungsten-Licht, freigestellt vor Schwarz, kein Kontext) und Material sind damit final gesetzt. Weitere Motive sollten dieselbe Bronze-auf-Schwarz-Logik fortführen.
4. **Six logo candidates, no winner declared.** We promoted `mark-g.svg` to primary because it's referenced most in the brief; the brand team should confirm.
5. **Semantic colors (success/warning/danger) were invented** to fit the warm palette. Brand team should sign off.
6. **No legal/footer-copy guidance** — Impressum, DSGVO, AGB, etc. were not in the brief. UI kit uses placeholder German legal links.
