---
tags:
  - content
  - reels
  - production
  - playbook
  - instagram
erstellt: 2026-04-19
aktualisiert: 2026-04-19
status: aktiv
---

# Reel Production Playbook

Das ist die produktions-seitige Bedienungsanleitung für jedes einzelne Reel. Basiert auf dem Masterclass-Research (Jade Beason, heyDominik, Torben Platzer, Matt Gray) und dem validierten Morning-Briefing-Format vom 18.04.2026.

> Der Playbook-Grundsatz: Eine Format-Serie, nicht Format-Mix. Stats-Maxing, nicht Trends jagen.

---

## Format-Commitment

**Das eine Format:** Morning Briefing mit Jarvis (Butler-Stimme, Sie-Form, ElevenLabs-Voice auf Telegram/Handy-Screen).

**Warum dieses Format:**
- Bereits validiert mit 30-35% Completion Rate beim ersten Reel
- Entspricht Torbens "Ein Format, dann meistern"-Prinzip
- Entspricht Matt Grays Content-Waterfall (eine Base, viele Varianten)
- Voice + Gesicht schlägt Trending Audio (Brock-Johnson-Studie)
- Serien-fähig: mindestens 30 Varianten ohne kreativen Bruch möglich

**Was NICHT gemacht wird (erst Mal):**
- Kein Format-Wechsel
- Keine Tutorial-Reels
- Keine Talking-Head-Only-Reels ohne Jarvis-Element
- Keine Trends-Reels nur weil sie trending sind

Nach Woche 4 mit Daten wird re-evaluiert, ob ein zweites Format Serie-fähig ist (z.B. Jarvis-Voice-Command-Demo).

---

## Der neue vereinfachte Production Workflow

### Gestorbene Idee: Test-Mode in Jarvis einbauen

Früher war geplant, Jarvis in einen "Scripted-Trigger-Mode" zu schalten, damit beim Filmen 100% vorprogrammierter Text läuft. **Das ist nicht mehr nötig.**

### Neuer Workflow: ElevenLabs-Background-Playback

**Grundidee:** Du generierst vor dem Filmen die Jarvis-Sprachnachricht in ElevenLabs, speicherst das MP3, spielst es beim Filmen im Hintergrund ab (Laptop-Lautsprecher, Bluetooth-Speaker, oder direkt im Telegram-Chat als echte Nachricht).

**Warum das besser ist:**
- Kein Code-Aufwand, kein Test-Mode-Build nötig
- 100% Kontrolle über Timing und Inhalt
- ElevenLabs Creator Plan hast du eh
- Keine Live-AI-Risiken auf Kamera (kein Fehler-Playback, keine Panne)
- Re-Record trivial: Nicht perfekt? Einfach nochmal MP3 abspielen und filmen

**Konkreter Ablauf pro Reel:**

1. **Script schreiben** (2 Min, aus Baukasten, siehe `morning-briefing-series-scripts.md`)
2. **Script in ElevenLabs reinpacken**, Butler-Stimme (die gleiche wie beim ersten Reel), MP3 exportieren
3. **MP3 auf Telegram schicken an dich selbst** oder auf Bluetooth-Speaker vorbereiten
4. **Handy-Kamera stellen** für Telegram-Chat-Shot + ggf. zweite Kamera für Face-Reaction
5. **Aufnahme starten**, MP3 abspielen, Moritz schaut realistisch auf die Sprachnachricht
6. **Schnitt durch Kick** (Rohdatei ohne Watermark + Insta-Ready, siehe `cross-posting-workflow.md`)
7. **Frame-1-Text-Overlay** drauf (Hook)
8. **Upload zu Insta** mit Caption + CTA-Kommentar-Trigger
9. **Parallel-Upload zu YouTube Shorts** (Rohdatei)
10. **Eintrag in Reels-Tracker**

**Zeitaufwand pro Reel:** 20-30 Min inkl. Schnitt-Wartezeit.

---

## Hook-Checklist (Frame 1 Text Overlay)

Bei jedem Reel MUSS der Hook diese Kriterien erfüllen, sonst nicht posten:

| Kriterium | Anforderung |
|-----------|-------------|
| Clarity-Test | Kann ein Fremder in 1 Sekunde sagen, worum es geht? |
| Curiosity-Gap | Entsteht im Kopf sofort die Frage "aber wie?" / "warum?" |
| Nicht länger als 8 Wörter | Kurz lesbar in 1 Sekunde |
| Keine Ja/Nein-Frage | "Kennst du das?" ist tot |
| Keine auditive Einleitung | Kein "Hey Leute" ins Mic (Torben-Regel) |
| Keine Insider-Begriffe | "LLM", "RAG", "Agentic" rausstreichen. Außerhalb deiner Bubble sagt das nichts |
| Gesicht in Frame 1-3 | Retention +10% laut Mosseri-Daten |

**Hook-Score vor Upload:** Wenn du den Hook nicht mit 7+ von 10 bewertest, nimmst du eine andere Variante.

**Pro Reel MINDESTENS 3 Hook-Alternativen schreiben**, eine wählen, die anderen für Re-Posts (3-4 Wochen Abstand) parken.

---

## Länge und Struktur

**Primäre Länge (Standard):** 15-25 Sekunden
- Dort ist die Konkurrenz dicht, aber die Audience am größten
- Spaltet sich gut in Hook (0-3s) / Build (3-15s) / Payoff (15-25s)

**Sekundäre Länge (Deep-Dive-Version):** 60-90 Sekunden
- Für Use-Case-Storytelling (z.B. "Mein kompletter Morgen mit Jarvis")
- Konkurrenz dünn in diesem Bereich
- Für später in der Serie, wenn Kurz-Format etabliert ist

**Tote Zone: 30-60 Sekunden.** Nie dort landen.

**Struktur-Template für Kurz-Reels (15-25s):**
```
0-2s:  Frame-1-Text-Overlay + Gesicht + Wakeup/Setup
2-5s:  Jarvis-Sprachnachricht startet (ElevenLabs-Voice)
5-18s: Content (Big Rocks, Wetter-Witz, Kalender-Highlight)
18-22s: Proaktive-Jarvis-Aktion oder finaler Witz
22-25s: Closing-Zeile ("Willkommen zurück am Arbeitsplatz, Master")
```

**Struktur-Template für Long-Reels (60-90s):**
```
0-2s:   Frame-1-Text-Overlay
2-5s:   Wakeup + Hook-Aussage vom Moritz ("Hey Jarvis")
5-15s:  Jarvis-Opening + Big Rocks
15-45s: Kalender + Tages-Kontext + Zahlen
45-65s: Proaktive-Aktion-Block ("Ich habe mir erlaubt...")
65-85s: Optionaler YouTube-Empfehlung oder Insight
85-90s: Closing-Zeile
```

---

## Quality Gates (post-upload)

Nach 24-48h Performance checken. Benchmarks aus Torbens 2-Parameter-Framework:

| Ziel-View-Niveau | Max Übersprung-Rate | Min Watchtime |
|------------------|---------------------|---------------|
| 10.000 Views     | 50%                 | 75%           |
| 50.000+ Views    | 35-40%              | 85%           |
| 1 Mio+ Views     | ~22%                | ~85%          |

**Was tun bei schlechten Stats:**
- **Hohe Übersprung-Rate (>50%):** Hook fixen. Frame-1-Text ist zu schwach oder Gesicht fehlt in Frame 1-3.
- **Niedrige Watchtime (<70%):** Mitte ist langweilig. Radikal kürzen oder mehr Content-Dichte pro Sekunde (Torben: "Reichweite ist Krieg gegen Langeweile").
- **Keine Kommentare:** Caption-CTA nicht klar genug, oder Neugier nicht angeregt.

**Re-Post-Regel:** Ein Reel darf maximal 3x neu gepostet werden, mit Mindestabstand 2 Wochen, jedes Mal anderem Hook und anderer Caption.

---

## Caption-Template Instagram

```
[Kurz-Hook-Echo, 1 Zeile, z.B. "Aus Claude wurde Jarvis."]

[1-2 Sätze Kontext, was der Zuschauer gerade gesehen hat]

Kommentier [Trigger-Wort] und ich schick dir den 
Onepager wie das System aufgebaut ist.

#ki #claude #jarvis #aibutler #automation
```

**Hashtag-Wahrheit (heyDominik-Daten):** 0 Korrelation mit Views. Trotzdem 3-5 setzen, weil sie Discovery-Pfade für Suchende öffnen. Keine Mega-Tags ("#fyp") und keine >10.

---

## CreatorFlow Trigger-Wort pro Reel

Pro Reel sollte das Trigger-Wort leicht variieren, damit du die Leads in CreatorFlow nach Reel zuordnen kannst.

**Base-Trigger:** "Jarvis" (bleibt Standard)

**Optionale Trigger-Varianten für Serie-Differenzierung:**
- "Butler" (für Wakeup-Prank-Variante)
- "Morgen" (für klassische Morning-Briefing-Varianten)
- "Brain" (für "Second-Brain"-Hook-Varianten)
- "Call" (für Call-pushende Varianten)

Die CreatorFlow-DM-Automation und der Onepager-Link bleiben gleich, nur das Trigger-Wort pro Reel wird angepasst.

---

## Kreativ-Regeln aus der Masterclass

**Aus Torben Platzer:**
- Jedes Füllwort raus
- Loop > CTA (Video-Ende führt zurück zum Anfang)
- Visuell brisant in 2 Sek, kein "Hey Leute"
- Mittelwert der Kommentare lesen (nicht Hater/Fans extrem)

**Aus heyDominik:**
- 3 Hooks pro Reel schreiben, beste wählen
- Keine Yes/No-Fragen ohne Payoff
- Insider-Lingo raus, für Fremde schreiben
- Secondary Hook nach 3 Sek ("doorway effect"-Prinzip)

**Aus Matt Gray:**
- Content-Waterfall: eine Reel-Idee geht später auch als Carousel, LinkedIn-Post, YouTube Short, Newsletter
- Email-Signups pro Post ist die echte Metrik, nicht Likes

**Aus Brock Johnson / Mosseri:**
- Shares > Saves > Likes > Comments für Non-Follower-Reach
- Jeder Share = +7 Views (Robert Benjamin)
- Gesicht in Frame 1-3 bringt +10% Retention

**Aus Jade Beason:**
- Instagram tracked die 3-Sek-Skip-Rate direkt, das ist der härteste Hebel

---

## Wöchentliche Review (jeden Sonntag)

1. Reels-Tracker updaten mit 24-48h-Performance aller Reels der Woche
2. Top-Performer identifizieren (Completion > 30%)
3. Flops analysieren: Wo wurde gewischt? (Insta-Insights-Graph)
4. Hook-Mittelwert checken: Welche Frame-1-Texte haben gezogen?
5. Nächste 7 Reel-Scripts schreiben basierend auf Learnings
6. CreatorFlow-DM-Leads durchgehen und qualifizieren

---

## Verknüpfungen
- [[Content-Operating-State]]
- [[morning-briefing-series-scripts]]
- [[Reels-Tracker]]
- [[2026-04-18-morning-briefing-jarvis]]
- [[00 - README - Instagram Reels Masterclass Übersicht]]
- [[11 - Torben Platzer - Instagram 0 bis 10k Follower 2026]]
- [[07 - heyDominik - ONLY Hook Formula That Works 2026]]
- [[cross-posting-workflow]]
- [[dm-funnel-creatorflow]]
