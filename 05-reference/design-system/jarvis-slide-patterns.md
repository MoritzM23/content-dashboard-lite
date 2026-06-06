---
tags:
  - design-system
  - ceo-gpt
  - slides
  - presentation
  - reference
erstellt: 2026-04-26
zuletzt-aktualisiert: 2026-05-13
---

# CEO-GPT Slide-Patterns

> **Canonical Brand-System ab 2026-05-13:** `05-reference/design-system/ceo-gpt/` (Tokens, Marken, Imagery, Voice, Hard Rules).
> Bei Konflikten gewinnt **immer der Bundle**. Token-Werte hier sind Slide-Quick-Reference — Single Source of Truth ist `ceo-gpt/colors_and_type.css`.
>
> Hard Rules aus dem Bundle gelten 1:1 für Slides: kein Emoji, kein Pure-White, kein Em-Dash im Lauftext, ein Akzent (Terracotta), Du-Form, Wortmarke `CEO-GPT™`, Mittelpunkt `·` als Voice-Tic. Bronze-Imagery (`brain.png` · `voice.png` · `hand.png`) als Hero-Visuals.
>
> ---
>
> Slide-spezifische Komponenten und Layout-Patterns für HTML-Decks im CEO-GPT-Design (16:9, Chart.js, Jarvis-Voice für Sprecher-Notizen).
>
> **Aufbau:** Erweitert [[jarvis-design-system]] um Patterns, die beim Bau der Sales-Demo-Video-Slideshows entstanden sind. Farben, Fonts und Grundprinzipien siehe Haupt-Design-System.
>
> **Live-Referenz im Vault:**
> - `03-projects/video-demo-sonntag-26-04/slides/index.html` (Block 5 · 5 Schichten · 7 Slides)
> - `03-projects/video-demo-sonntag-26-04/slides/block3-pain.html` (Block 3 · Drei Punkte · 5 Slides)
>
> **Wann verwenden:** Bei Pitch-Decks, Sales-Slideshows, On-Screen-Visuals fürs Video, Walkthrough-Präsentationen, internen Slides für Team-Calls.

---

## 1. Slide-Stage-System (1920×1080 mit Auto-Fit)

**Problem:** Slides sollen pixelgenau auf 1920×1080 designt werden (Recording-Auflösung), müssen aber auf jedem Browser-Fenster sauber dargestellt werden.

**Lösung:** Festes Deck-Element mit `transform: scale()` per JS auf den Viewport gefittet, immer mittig.

```css
html, body {
  width: 100%; height: 100%;
  overflow: hidden;
  background: var(--bg-deep);
  cursor: pointer; /* da Klick = nächste Slide */
}

.stage {
  position: fixed; inset: 0;
  display: flex; align-items: center; justify-content: center;
}

.deck {
  position: relative;
  width: 1920px;
  height: 1080px;
  transform-origin: center center;
  background: var(--bg);
  box-shadow: 0 60px 200px rgba(0, 0, 0, 0.6);
}

.slide {
  position: absolute; inset: 0;
  opacity: 0; visibility: hidden;
  transition: opacity 400ms ease-in-out;
  padding: 72px 120px 88px;
  display: flex; flex-direction: column;
  overflow: hidden;
}
.slide.active { opacity: 1; visibility: visible; }
```

```js
function fit() {
  const deck = document.getElementById('deck');
  const sx = window.innerWidth / 1920;
  const sy = window.innerHeight / 1080;
  deck.style.transform = `scale(${Math.min(sx, sy)})`;
}
window.addEventListener('resize', fit);
fit();
```

**Vorteil:** Auf 4K-Display perfekt, auf iPhone immer noch lesbar, Recording-Output ist immer 1920×1080 ohne Aliasing.

---

## 2. Slide-Backgrounds (zwei Standard-Varianten)

```css
.slide.bg-warm {
  background: linear-gradient(180deg, var(--bg) 0%, var(--bg) 60%, #110D08 100%);
}
.slide.bg-deep {
  background: linear-gradient(180deg, var(--bg) 0%, var(--water) 60%, var(--water-deep) 100%);
}

/* Atmosphärischer Glow auf jeder Slide (per ::before) */
.slide::before {
  content: "";
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse at 12% 18%, rgba(194, 107, 76, 0.06) 0%, transparent 45%),
    radial-gradient(ellipse at 88% 82%, rgba(194, 107, 76, 0.04) 0%, transparent 50%);
  pointer-events: none;
}
```

**Faustregel:**
- `bg-warm` für Inhalts- und Cover-Slides (warmes Schwarz, leichter Erdton-Übergang)
- `bg-deep` für Daten- und Tech-Slides (geht ins Water-Blau, schafft visuellen Kontrast)
- Wechsel zwischen den beiden gibt dem Deck visuelle Rhythmus

---

## 3. Reveal-Stagger (gestaffelte Element-Einblendung)

Pro Slide faden Elemente nacheinander ein, 80–100 ms versetzt. Premium-ruhig, kein Pop-In.

```css
.reveal {
  opacity: 0;
  transform: translateY(14px);
  transition: opacity 600ms ease, transform 600ms ease;
}
.slide.active .reveal {
  opacity: 1;
  transform: translateY(0);
}
.slide.active .r1 { transition-delay: 80ms; }
.slide.active .r2 { transition-delay: 180ms; }
.slide.active .r3 { transition-delay: 280ms; }
.slide.active .r4 { transition-delay: 380ms; }
.slide.active .r5 { transition-delay: 480ms; }
.slide.active .r6 { transition-delay: 580ms; }
.slide.active .r7 { transition-delay: 680ms; }
.slide.active .r8 { transition-delay: 780ms; }
```

```html
<h2 class="headline reveal r2">Die <span class="accent">5 Schichten.</span></h2>
<p class="subhead reveal r3">Untertitel kommt 100ms später.</p>
```

**Regel:** Maximal 8 Reveal-Stages pro Slide, sonst wirkt es zu kleinteilig. Faustregel: Overline → Headline → Subhead → 3-5 Body-Elemente.

---

## 4. Slide-Head (Standard-Anatomie)

```html
<div class="slide-head">
  <div class="overline reveal r1">Schicht 03</div>
  <h2 class="headline reveal r2"><span class="accent">Kommunikation.</span><br>In deinem Ton.</h2>
  <p class="subhead reveal r3">Jarvis schreibt nicht generisch. Er kennt dich.</p>
</div>
```

```css
.slide-head { margin-top: 96px; max-width: 1500px; }
.overline {
  font-family: 'Space Grotesk';
  font-size: 13px; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.32em;
  color: var(--terracotta);
  margin-bottom: 18px;
}
.headline {
  font-family: 'Space Grotesk';
  font-size: 80px; font-weight: 500;
  line-height: 0.98; letter-spacing: -0.04em;
  color: var(--cream);
  margin-bottom: 22px;
}
.subhead {
  font-family: 'Inter';
  font-weight: 300; font-size: 24px;
  line-height: 1.45; color: var(--cream-muted);
  max-width: 1100px;
}
```

**Headline-Größen-Skala:**
- 80 px: normale Schicht-Slides
- 96–132 px: Cover, Übergang
- 168 px: Hammer-Statements (eine Zeile, große Wirkung)

---

## 5. Step-Indikator (Bars-Variante, Default)

Für mehrteilige Decks. Zeigt Position im Set, alle Schritte sichtbar, aktiver hervorgehoben.

```html
<div class="layer-indicator" data-active="3">
  <div class="li-meta">
    <span>Schicht <span class="li-active">03</span> von 05</span>
    <span class="li-active">Kommunikation</span>
  </div>
  <div class="li-bars">
    <div class="li-bar dim"></div>
    <div class="li-bar dim"></div>
    <div class="li-bar active"></div>
    <div class="li-bar dim"></div>
    <div class="li-bar dim"></div>
  </div>
  <div class="li-bar-labels">
    <div class="lbl dim">01 Kontext</div>
    <div class="lbl dim">02 Daten</div>
    <div class="lbl active">03 Kommunikation</div>
    <div class="lbl dim">04 Interaktion</div>
    <div class="lbl dim">05 Automation</div>
  </div>
</div>
```

```css
.layer-indicator { position: absolute; top: 44px; left: 120px; right: 120px; }
.li-meta {
  display: flex; justify-content: space-between;
  margin-bottom: 16px;
  font-family: 'Space Grotesk'; font-size: 12px; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.28em;
  color: var(--muted);
}
.li-meta .li-active { color: var(--terracotta); }
.li-bars { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; }
.li-bar {
  height: 6px; border-radius: 999px;
  background: rgba(242, 232, 220, 0.08);
}
.li-bar.dim { opacity: 0.45; }
.li-bar.active {
  background: linear-gradient(90deg, var(--terracotta) 0%, var(--terracotta-glow) 100%);
  box-shadow: 0 0 24px rgba(212, 132, 102, 0.45);
}
```

**Anwendung:** 3, 5 oder 7 Schritte sind ideal. Mehr als 7 wird zu schmal.

---

## 6. Step-Indikator (Dots-Variante, Alternative)

Für Decks, in denen die Step-Logik wichtiger ist als die Übersicht. Klassischer wirkend, mehr Process-Look.

```css
.li-dots {
  display: grid; grid-template-columns: repeat(5, 1fr);
  align-items: center; position: relative;
}
.li-dots::before {
  content: "";
  position: absolute; left: 6%; right: 6%; top: 50%;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--line-strong) 20%, var(--line-strong) 80%, transparent);
}
.li-dot {
  width: 36px; height: 36px;
  border-radius: 50%;
  background: var(--bg);
  border: 1px solid var(--line-strong);
  font-family: 'Space Grotesk'; font-size: 13px; font-weight: 600;
  color: var(--muted);
}
.li-dot.active {
  background: var(--terracotta);
  border-color: var(--terracotta-glow);
  color: var(--bg);
  box-shadow: 0 0 0 6px rgba(194, 107, 76, 0.12), 0 0 32px rgba(212, 132, 102, 0.5);
}
```

**Faustregel:** Bars als Default verwenden (kommuniziert Fortschritt + Themen besser). Dots als Alternative für Process-Decks.

---

## 7. Stat-Row (Zahl + Beschreibung)

Für Daten-Statements. Große Terracotta-Zahl links, Text rechts, mit Akzent-Border-Left.

```html
<div class="stat-row">
  <div class="stat-num">8–12</div>
  <div class="stat-text">
    <h5>Tools täglich offen</h5>
    <p>ChatGPT, Notion, ClickUp, WhatsApp und mehr.</p>
  </div>
</div>
```

```css
.stat-row {
  display: flex; align-items: baseline; gap: 18px;
  padding: 22px 28px;
  background: rgba(242, 232, 220, 0.025);
  border: 1px solid var(--line);
  border-left: 2px solid var(--terracotta);
  border-radius: 12px;
}
.stat-num {
  font-family: 'Space Grotesk';
  font-size: 64px; font-weight: 500;
  color: var(--terracotta);
  letter-spacing: -0.04em; line-height: 1;
  min-width: 130px;
}
.stat-num.muted { color: var(--cream-muted); }
.stat-text h5 {
  font-family: 'Space Grotesk';
  font-weight: 600; font-size: 22px;
  color: var(--cream); margin-bottom: 4px;
}
.stat-text p {
  font-size: 15px; color: var(--cream-muted);
  line-height: 1.5; font-weight: 300;
}
```

**Variante:** `stat-num.muted` für Negativ-Statements ("0 davon kennen sich" → grau statt Terracotta).

---

## 8. Card mit Featured-State

```css
.k-card {
  background: rgba(242, 232, 220, 0.025);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 28px;
  backdrop-filter: blur(8px);
}
.k-card .k-num {
  font-family: 'Space Grotesk'; font-size: 12px; font-weight: 600;
  color: var(--terracotta); letter-spacing: 0.18em;
  margin-bottom: 16px;
}
.k-card.featured {
  background: linear-gradient(180deg, rgba(194, 107, 76, 0.08) 0%, rgba(194, 107, 76, 0.02) 100%);
  border-color: rgba(194, 107, 76, 0.28);
}
```

Featured-Card zieht Aufmerksamkeit auf den wichtigsten Punkt im Grid (z.B. die letzte Card im 5er-Set).

---

## 9. WhatsApp/Chat-Mockup

Für Kommunikations-Slides. Zeigt Bubble in Brand-Farben statt grünem Original.

```html
<div class="wa-mock">
  <div class="wa-head">
    <div class="wa-avatar">M</div>
    <div>
      <div class="wa-name">Max Mustermann</div>
      <div class="wa-status">online</div>
    </div>
  </div>
  <div class="wa-bubble user">User-Nachricht hier.<span class="wa-time">09:42</span></div>
  <div class="wa-bubble">
    Antwort von Jarvis.
    <span class="wa-time">09:43</span>
    <div class="wa-typing"><span></span><span></span><span></span></div>
  </div>
</div>
```

```css
.wa-mock {
  background: #0E1418;
  border: 1px solid var(--line-strong);
  border-radius: 28px;
  padding: 28px;
  box-shadow: 0 40px 120px rgba(0, 0, 0, 0.5), 0 0 80px rgba(194, 107, 76, 0.06);
}
.wa-avatar {
  width: 44px; height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--terracotta) 0%, var(--terracotta-deep) 100%);
  display: flex; align-items: center; justify-content: center;
  font-family: 'Space Grotesk'; font-weight: 600;
  color: var(--bg); font-size: 18px;
}
.wa-bubble {
  background: linear-gradient(135deg, rgba(194, 107, 76, 0.18) 0%, rgba(194, 107, 76, 0.08) 100%);
  border: 1px solid rgba(194, 107, 76, 0.22);
  border-radius: 18px 18px 4px 18px;
  padding: 18px 20px;
  margin-left: auto; max-width: 85%;
  color: var(--cream); font-size: 15.5px; line-height: 1.55;
}
.wa-bubble.user {
  background: rgba(242, 232, 220, 0.04);
  border-color: var(--line-strong);
  border-radius: 18px 18px 18px 4px;
  margin-left: 0;
}
.wa-typing { display: inline-flex; gap: 4px; margin-top: 4px; }
.wa-typing span {
  width: 5px; height: 5px; border-radius: 50%;
  background: var(--cream-muted);
  animation: typing 1.4s ease-in-out infinite;
}
.wa-typing span:nth-child(2) { animation-delay: 0.2s; }
.wa-typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing {
  0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
  30% { opacity: 1; transform: translateY(-3px); }
}
```

**Regel:** In Demos immer "Max Mustermann" als Empfänger nutzen, nicht echte Kundennamen.

---

## 10. Annotation-Card (mit Icon + Border-Left)

Erklärt visuell, was woher kommt. Wird neben Mockups platziert.

```html
<div class="anno">
  <div class="anno-icon">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
      <path d="..."/>
    </svg>
  </div>
  <div class="anno-text">
    <h5>Schreibstil aus Schicht 01</h5>
    <p>Direkt, kurz, kein Corporate-Sprech.</p>
  </div>
</div>
```

```css
.anno {
  display: grid; grid-template-columns: 36px 1fr;
  gap: 18px; padding: 18px 22px;
  background: rgba(242, 232, 220, 0.025);
  border: 1px solid var(--line);
  border-left: 2px solid var(--terracotta);
  border-radius: 10px;
}
.anno-icon {
  width: 36px; height: 36px; border-radius: 50%;
  background: rgba(194, 107, 76, 0.12);
  border: 1px solid rgba(194, 107, 76, 0.3);
  display: flex; align-items: center; justify-content: center;
  color: var(--terracotta);
}
```

---

## 11. Frontend-Mock-Cards (Phone, Voice, Browser)

Drei Varianten für "Wo läuft das Produkt?"-Slides.

### Phone-Mini
```css
.phone-mini {
  width: 220px;
  max-height: 240px;
  aspect-ratio: 11/12;
  background: var(--bg-deep);
  border-radius: 18px;
  border: 1px solid var(--line-strong);
  padding: 14px 12px;
  display: flex; flex-direction: column; gap: 7px;
  overflow: hidden;
}
.phone-msg { font-size: 11px; padding: 7px 10px; border-radius: 9px; }
.phone-msg.them { background: rgba(242, 232, 220, 0.05); align-self: flex-start; }
.phone-msg.me {
  background: rgba(194, 107, 76, 0.18);
  border: 1px solid rgba(194, 107, 76, 0.25);
  align-self: flex-end;
}
```

### Voice-Wave
```html
<div class="voice-wave">
  <div class="vbar" style="animation-delay:0.0s"></div>
  <div class="vbar" style="animation-delay:0.1s"></div>
  <!-- 9-11 Bars -->
</div>
```

```css
.voice-wave {
  display: flex; align-items: center; justify-content: center;
  gap: 6px; height: 120px;
}
.voice-wave .vbar {
  width: 6px;
  background: linear-gradient(180deg, var(--terracotta-glow), var(--terracotta));
  border-radius: 999px;
  animation: voice 1.6s ease-in-out infinite;
  box-shadow: 0 0 10px rgba(212, 132, 102, 0.4);
}
@keyframes voice {
  0%, 100% { height: 18%; }
  50% { height: 100%; }
}
```

### Browser-Mini
```html
<div class="browser-mini">
  <div class="browser-bar">
    <div class="browser-dot"></div>
    <div class="browser-dot"></div>
    <div class="browser-dot"></div>
  </div>
  <div class="browser-content">
    <div class="br-tile">
      <div class="br-num acc">12</div>
      <div class="br-line acc"></div>
    </div>
    <!-- weitere Tiles -->
  </div>
</div>
```

```css
.browser-mini {
  width: 100%; max-width: 280px;
  aspect-ratio: 16/11;
  background: var(--bg-deep);
  border: 1px solid var(--line-strong);
  border-radius: 12px; overflow: hidden;
}
.browser-bar {
  height: 22px;
  background: rgba(242, 232, 220, 0.04);
  border-bottom: 1px solid var(--line);
  display: flex; align-items: center; padding: 0 10px; gap: 6px;
}
.browser-dot { width: 7px; height: 7px; border-radius: 50%; background: rgba(242, 232, 220, 0.16); }
.br-tile {
  background: rgba(242, 232, 220, 0.03);
  border: 1px solid var(--line);
  border-radius: 6px; padding: 10px;
}
.br-line { height: 4px; border-radius: 999px; background: rgba(242, 232, 220, 0.1); }
.br-line.acc { background: var(--terracotta); width: 60%; }
```

---

## 12. Animierte Timeline mit Cursor-Sweep

Für Automation/24h-Slides. Cursor läuft horizontal, Trigger zünden nacheinander.

```html
<div class="auto-timeline" id="autoTimeline">
  <div class="auto-track"></div>
  <div class="auto-track-fill" id="autoTrackFill"></div>

  <div class="auto-trigger above" data-pos="6" style="left:6%">
    <div class="trig-card">...</div>
    <div class="trig-dot"></div>
    <div class="trig-time">06:45</div>
  </div>
  <!-- weitere Trigger, abwechselnd above / default -->

  <div class="auto-cursor" id="autoCursor"></div>
</div>
```

```css
.auto-timeline { position: relative; height: 380px; }
.auto-track {
  position: absolute; top: 50%; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent 0%, var(--line-strong) 6%, var(--line-strong) 94%, transparent 100%);
}
.auto-track-fill {
  position: absolute; top: 50%; left: 6%;
  height: 2px;
  background: linear-gradient(90deg, var(--terracotta), var(--terracotta-glow));
  box-shadow: 0 0 20px rgba(212, 132, 102, 0.5);
  width: 0;
  /* WICHTIG: keine CSS-Transition — wird per RAF im JS synchron mit Cursor geupdated */
}
.auto-cursor {
  position: absolute; top: 50%; left: 6%;
  width: 14px; height: 14px;
  border-radius: 50%;
  background: var(--terracotta-glow);
  transform: translate(-50%, -50%);
  box-shadow: 0 0 0 6px rgba(212, 132, 102, 0.18), 0 0 30px rgba(212, 132, 102, 0.7);
}
.auto-trigger {
  position: absolute; top: 50%;
  transform: translate(-50%, -50%);
  display: flex; flex-direction: column; align-items: center;
  gap: 26px; /* viel vertikaler Atem zwischen Card und Dot */
}
.auto-trigger .trig-dot {
  width: 18px; height: 18px; border-radius: 50%;
  background: var(--bg);
  border: 2px solid var(--terracotta-deep);
}
.auto-trigger.fired .trig-dot {
  background: var(--terracotta);
  border-color: var(--terracotta-glow);
  box-shadow: 0 0 0 5px rgba(194, 107, 76, 0.18), 0 0 24px rgba(212, 132, 102, 0.6);
}
```

```js
function startAutoTimeline() {
  const cursor = document.getElementById('autoCursor');
  const fill = document.getElementById('autoTrackFill');
  const triggers = Array.from(document.querySelectorAll('#autoTimeline .auto-trigger'));
  const cycle = 9000; // 9s Sweep
  const start = performance.now();

  function step(now) {
    const t = ((now - start) % cycle) / cycle;
    const pct = 6 + (94 - 6) * t;
    cursor.style.left = pct + '%';
    fill.style.width = (pct - 6) + '%';
    triggers.forEach(tr => {
      const pos = parseFloat(tr.dataset.pos);
      tr.classList.toggle('fired', pct >= pos - 0.5);
    });
    requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}
```

**Wichtig:** Keine `transition: width` auf den Track-Fill setzen, sonst läuft der Balken hinter dem Cursor her. Beide werden per RAF gleichzeitig geupdated.

---

## 13. Driftende Pill-Cloud (Tool-Chaos / Idea-Chaos)

Für "Verstreut"-Visuals. Pills/Cards floaten leicht, durchgezogene oder gestrichelte Linien zwischen ihnen.

```html
<div class="tool-cloud">
  <svg class="tool-svg" viewBox="0 0 600 480" preserveAspectRatio="none">
    <g stroke="url(#lineFade)" stroke-width="1" fill="none" stroke-dasharray="3 4">
      <line x1="80" y1="60" x2="200" y2="180"/>
      <!-- weitere Linien zwischen den Pills -->
    </g>
  </svg>

  <div class="tool-pill" style="top:6%;left:8%;animation-delay:.2s">ChatGPT</div>
  <div class="tool-pill" style="top:8%;right:6%;animation-delay:.5s">Notion</div>
  <!-- 8-12 Pills -->

  <div class="tool-center">
    <div class="tc-label">Du</div>
    <div class="tc-name">die Brücke</div>
  </div>
</div>
```

```css
.tool-cloud { position: relative; height: 480px; }
.tool-pill {
  position: absolute;
  background: var(--bg-deep);
  border: 1px solid var(--line-strong);
  border-radius: 999px;
  padding: 10px 18px;
  font-family: 'Space Grotesk'; font-size: 14px; font-weight: 500;
  color: var(--cream);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  animation: drift 8s ease-in-out infinite;
}
.tool-pill:nth-child(odd) { animation-direction: alternate; }
@keyframes drift {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}
.tool-center {
  width: 130px; height: 130px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--terracotta) 0%, var(--terracotta-deep) 100%);
  color: var(--bg);
  box-shadow: 0 0 0 8px rgba(194, 107, 76, 0.12), 0 0 60px rgba(194, 107, 76, 0.4);
  z-index: 2;
}
```

**Variante Idea-Cards:** Statt Pills kleine Cards mit Label + Text, gekippt mit `transform: rotate(-3deg/3deg)` für Zettel-Look.

---

## 14. Hub-Diagramm (Tools → Zentraler Knoten)

Für Daten-Slides. SVG mit Bezier-Kurven von Quellen zum zentralen Hub. Animierte Datenpunkte fließen entlang der Pfade.

```html
<svg viewBox="0 0 1500 600">
  <defs>
    <radialGradient id="hubGrad">
      <stop offset="0%" stop-color="#D48466" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#6E3726" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <!-- Connection lines -->
  <path id="line1" d="M 200 110 Q 500 200 750 300" fill="none" stroke="#C26B4C"/>
  <!-- weitere Lines -->

  <!-- Hub -->
  <circle cx="750" cy="300" r="180" fill="url(#hubGrad)" opacity="0.35"/>
  <circle cx="750" cy="300" r="120" fill="#1A120D" stroke="#C26B4C" stroke-width="1.5"/>
  <text x="750" y="296" text-anchor="middle">Jarvis</text>

  <!-- Animated flow dot -->
  <circle r="4" fill="#D48466">
    <animateMotion dur="3.6s" repeatCount="indefinite">
      <mpath href="#line1"/>
    </animateMotion>
  </circle>
</svg>
```

**Trick:** Mehrere `<animateMotion>` mit unterschiedlichen `begin`-Werten und `dur` zwischen 3.6 und 4.3s. Erzeugt organisches Gefühl, nicht synchron.

---

## 15. Hammer-Slide (2-Spalten-Vergleich)

Für "Wer macht / Wer nicht macht"-Statements am Ende eines Pain-Blocks.

```html
<div class="hammer-body">
  <div class="hammer-col">
    <div class="hc-label">Wer den Layer baut</div>
    <h3>Drei Schritte<br>voraus.</h3>
    <ul class="hammer-list">
      <li>Jeder Call macht das Gerüst klüger</li>
      <li>Jede Idee macht es schärfer</li>
    </ul>
    <div class="hammer-arrow">↑ Wächst mit</div>
  </div>

  <div class="hammer-divider"></div>

  <div class="hammer-col dim">
    <div class="hc-label">Wer weiter sammelt</div>
    <h3>Sammelt Tools.<br>Bleibt stehen.</h3>
    <!-- ... -->
  </div>
</div>
```

```css
.hammer-body {
  display: grid; grid-template-columns: 1fr 1px 1fr;
  gap: 60px;
}
.hammer-divider {
  background: linear-gradient(180deg, transparent, var(--line-strong) 20%, var(--line-strong) 80%, transparent);
}
.hammer-list li::before { content: "→"; color: var(--terracotta); }
.hammer-col.dim .hammer-list li::before { content: "×"; color: var(--muted); }
.hammer-col.dim h3 { color: var(--cream-muted); }
```

**Regel:** Linke Spalte = Positiv-Pfad (Pfeile, voller Cream-Text), rechte Spalte = `dim` (Cross-Marks, Cream-Muted). Optisch klar wer der "Held" ist.

---

## 16. Navigation & Bedienung

Standard-Tasten und Klick-Verhalten für alle Decks:

```js
document.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') next();
  else if (e.key === 'ArrowLeft' || e.key === 'PageUp') prev();
  else if (e.key === 'Home') show(0);
  else if (e.key === 'End') show(total - 1);
  else if (e.key === 'f' || e.key === 'F') {
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen?.();
  }
});

document.addEventListener('click', e => {
  if (e.target.closest('a, button, kbd')) return;
  next();
});
```

**HUD unten rechts (Slide-Indicator):**
```html
<div class="indicator">
  <div class="dot"></div>
  <div class="num"><span id="curNum">01</span> / 07</div>
  <div class="deck-label">Block 05</div>
</div>
```

**HUD unten links (Tasten-Hint):**
```html
<div class="hint">
  <kbd>→</kbd> next · <kbd>←</kbd> back · <kbd>F</kbd> fullscreen
</div>
```

---

## 17. Animations-Prinzipien für Decks

- **Slide-Crossfade:** 400 ms ease-in-out, kein Slide-Slide
- **Reveal-Stagger:** 80–100 ms zwischen Elementen, max. 8 Stages
- **Mikrointeraktionen:** drift (8–10s), float (12–14s), shimmer (4–5s), voice-wave (1.6s), typing (1.4s)
- **Datenfluss-Animationen:** SVG `animateMotion`, 3.6–4.3 s, asynchrone `begin`-Werte
- **Hover-Lift:** `translateY(-1px)` auf Cards/Buttons, 0.4 s ease
- **Keine harten Pop-Ins, keine Spring-Easings, keine Bounce-Effekte**

---

## 18. Recording-Setup (Cmd+Shift+5)

- Browser im Vollbild öffnen → `F` drücken für True-Fullscreen ohne Browser-Chrome
- Cmd+Shift+5 → "Gesamten Bildschirm aufnehmen"
- Picture-in-Picture (Sprecher) oben rechts platzieren, ca. 10–15% Bildgröße
- Audio separat aufnehmen (Lavalier oder Shotgun) und im Schnitt synchen
- Slide-Wechsel mit Pfeiltasten, nicht Klick (Maus-Cursor sieht im Recording unsauber aus, oder Cursor vorher per macOS-Setting verstecken)

---

## 19. Live-Decks im Vault

Aktuell zwei produktive Beispiele:

| Deck | Pfad | Slides | Status |
|---|---|---|---|
| Block 5 · Die 5 Schichten | `03-projects/video-demo-sonntag-26-04/slides/index.html` | 7 | Production |
| Block 3 · Drei Punkte | `03-projects/video-demo-sonntag-26-04/slides/block3-pain.html` | 5 | Production |

Index mit URLs und Bedienungsanleitung: [[03-projects/video-demo-sonntag-26-04/slides/README]]

---

## Verknüpfungen

- [[jarvis-design-system]] — Basis-System (Farben, Fonts, Komponenten)
- [[jarvis-onepager-layout]] — Print/PDF-Pendant
- [[branding]] — Brand-Voice und Messaging
- [[jarvis-persona]] — TTS-Persona und Verhalten
- [[03-projects/video-demo-sonntag-26-04/slides/README]] — Index der aktuellen Slides

---

*Diese Datei aktuell halten, wenn neue Slide-Patterns entstehen. Anwendungsbereich: alle HTML-Decks, Pitch-Slides, On-Screen-Visuals, Walkthroughs.*
