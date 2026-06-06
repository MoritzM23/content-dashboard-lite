---
name: ceo-gpt-design
description: Use this skill to generate well-branded interfaces and assets for CEO-GPT, either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

Read the `README.md` file within this skill, and explore the other available files.

The system is built around one specific brand: **CEO-GPT™** — a German-language product offering bespoke "AI Mitarbeiter" (AI employees) to executives and high-performers in the DACH region. The visual world is warm-dark + terracotta + cream paper. Two typefaces only (Space Grotesk + Inter). The brand's voice is **ruhig, premium, modern, warm, präzise** — never loud, plakativ, trendy, leger, or pedantisch. Default to German copy in the du-form.

## What's here

- `colors_and_type.css` — CSS custom properties for the full system (colors, type, spacing, radii, shadows, motion). Import this from anything you build.
- `assets/` — logo marks (primary `mark-g.svg` is the recommended brand glyph), wordmark lockups, app icon, in-house icon sprite.
- `preview/` — small specimen cards showing every part of the system in use. Read these to learn the visual rhythm.

## When invoked

If creating visual artifacts (slides, mocks, throwaway prototypes), copy assets out of `assets/` and import `colors_and_type.css`, then write static HTML files for the user to view. If working on production code, copy assets and read the rules in `README.md` to become an expert in designing with this brand.

If the user invokes this skill without other guidance, ask them what they want to build, ask a few short questions (audience, surface, German vs English), and act as an expert designer who outputs HTML artifacts *or* production code, depending on the need.

## Hard rules to never break

- **No emoji. Ever.** Not in copy, not as icons, not as decoration.
- **No pure white** anywhere. Cream `#F2E8DC` is the foreground; black `#0A0805` is the stage.
- **No cool tones.** No blue, no indigo, no slate, no purple, no teal. Semantic colors are warm-shifted (olive / amber / fired-clay).
- **One accent: terracotta.** Don't introduce a second hue.
- **No em-dash in body copy** (`—`). Use a period and start a new sentence, or use the mittelpunkt `·`. Hyphen-as-dash is also out.
- **No hype words** (amazing, revolutionary, game-changing, best-in-class).
- **Two typefaces only:** Space Grotesk (display, 600/700) and Inter (body, 300–600). No serif, no third sans, no mono in production UI.
- **Du-form** in customer-facing copy. Never `Sie`.
- **Imagery placeholders stay** until the brand team supplies real images. Don't draw your own SVG illustrations to fill the gap.
