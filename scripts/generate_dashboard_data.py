#!/usr/bin/env python3
"""
Dashboard Data Generator

Liest alle Datenquellen aus dem Vault und baut data/dashboard-data.json für das Web-Dashboard.

Quellen:
- 06-daily-notes/YYYY-MM-DD.md (Tagesplan, To-Dos)
- 05-reference/insights/Daily Research/YYYY-MM-DD.md (News)
- 04-areas/business/Finances.md (Umsatz-Historie)
- 04-areas/business/WhatsApp Komplett-Kontext.md (WhatsApp Chats)
- 04-areas/contacts/*.md (Kontaktprofile)
- outputs/daily-brief/YYYY-MM-DD.md (Morning Brief)
- data/data.db (YouTube Metrics)

Usage:
    python scripts/generate_dashboard_data.py
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

WORKSPACE = Path(__file__).resolve().parent.parent
load_dotenv(WORKSPACE / ".env")

DB_PATH = WORKSPACE / "data" / "data.db"
OUTPUT_PATH = WORKSPACE / "data" / "dashboard-data.json"

TODAY = datetime.now().strftime("%Y-%m-%d")
WEEKDAYS_DE = {
    0: "Montag", 1: "Dienstag", 2: "Mittwoch", 3: "Donnerstag",
    4: "Freitag", 5: "Samstag", 6: "Sonntag"
}

MONTHS_DE_TO_NUM = {
    "januar": 1, "februar": 2, "märz": 3, "maerz": 3, "april": 4,
    "mai": 5, "juni": 6, "juli": 7, "august": 8, "september": 9,
    "oktober": 10, "november": 11, "dezember": 12,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_db(path):
    if not path.exists():
        return None
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def read_daily_note(date_str: str) -> str:
    p = WORKSPACE / "06-daily-notes" / f"{date_str}.md"
    if p.exists():
        return p.read_text(encoding="utf-8")
    return None


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_weather():
    try:
        r = requests.get("https://wttr.in/Berlin?format=j1", timeout=10)
        d = r.json()
        c = d["current_condition"][0]
        f = d["weather"][0]
        desc_map = {
            "Sunny": "Sonnig", "Clear": "Klar", "Partly cloudy": "Teilweise bewölkt",
            "Cloudy": "Bewölkt", "Overcast": "Bedeckt", "Mist": "Neblig",
            "Light rain": "Leichter Regen", "Rain": "Regen",
            "Moderate rain": "Mäßiger Regen", "Heavy rain": "Starker Regen",
            "Light snow": "Leichter Schnee", "Snow": "Schnee",
        }
        emoji_map = {
            "113": "☀️", "116": "⛅", "119": "☁️", "122": "☁️",
            "143": "🌫️", "176": "🌦️", "266": "🌦️", "263": "🌦️",
            "293": "🌧️", "296": "🌧️", "302": "🌧️", "308": "🌧️",
            "332": "❄️", "335": "❄️",
        }
        code = c["weatherCode"]
        return {
            "temp": c["temp_C"],
            "feels_like": c["FeelsLikeC"],
            "condition": desc_map.get(c["weatherDesc"][0]["value"], c["weatherDesc"][0]["value"]),
            "icon": emoji_map.get(code, "⛅"),
            "humidity": c["humidity"],
            "wind": c["windspeedKmph"],
            "high": f["maxtempC"],
            "low": f["mintempC"],
        }
    except Exception as e:
        print(f"Weather fetch failed: {e}")
        return {"temp": "--", "condition": "Keine Daten", "icon": "⛅"}


def load_call_prep(title: str, attendees: list):
    """Sucht in data/call-preps/ nach einer Prep-Datei, die zum Event passt.

    Matcht auf Attendee-Namen (aus Titel oder E-Mail-Liste). Dateiname erwartet
    als slugified-name, z. B. 'sebastian-gehmert.json'.
    """
    preps_dir = WORKSPACE / "data" / "call-preps"
    if not preps_dir.exists():
        return None

    candidates = []
    name_match = re.search(r"und\s+([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)*)", title)
    if name_match:
        candidates.append(name_match.group(1))

    for att in attendees or []:
        local = att.split("@")[0] if "@" in att else att
        candidates.append(local.replace(".", " ").replace("_", " "))

    def slugify(s):
        s = s.lower()
        umlaut_map = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
        for k, v in umlaut_map.items():
            s = s.replace(k, v)
        return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

    for cand in candidates:
        slug = slugify(cand)
        if not slug:
            continue
        prep_file = preps_dir / f"{slug}.json"
        if prep_file.exists():
            try:
                return json.loads(prep_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
    return None


def load_schedule_from_calendar_db(conn, date_str: str) -> list[dict]:
    """Liest Kalender-Events direkt aus der calendar_events Tabelle."""
    if not conn:
        return []

    color_map = {
        "deep work": "deep_work", "work": "deep_work", "focus": "deep_work",
        "call": "meeting", "meeting": "meeting", "update": "meeting",
        "sport": "sport", "gym": "sport", "training": "sport", "pull": "sport", "push": "sport",
        "content": "content", "video": "content", "reel": "content",
        "lernen": "lesen", "lesen": "lesen", "weiterbildung": "lesen",
        "pause": "pause", "mittag": "pause", "lunch": "pause",
        "abend": "abend", "dinner": "abend",
    }

    def classify(title):
        t = title.lower()
        for key, typ in color_map.items():
            if key in t:
                return typ
        return "other"

    try:
        rows = conn.execute(
            "SELECT title, start_time, end_time, attendees FROM calendar_events WHERE date=? ORDER BY start_time",
            (date_str,)
        ).fetchall()
    except Exception as e:
        print(f"  Calendar DB read failed: {e}")
        return []

    events = []
    for row in rows:
        title = row["title"] or ""
        start = row["start_time"] or ""
        end = row["end_time"] or ""

        # Skip events without title or overnight sleep blocks
        if not title or title == "(Kein Titel)":
            continue
        # Skip events that span overnight (end < start means next day)
        if start and end and end < start:
            continue
        attendees_raw = row["attendees"] or "[]"
        try:
            import json as _json
            attendees = _json.loads(attendees_raw)
        except Exception:
            attendees = []

        typ = classify(title)
        detail = ""
        if attendees:
            names = [a.split("@")[0] for a in attendees if a]
            detail = ", ".join(names)

        prep = load_call_prep(title, attendees)

        events.append({
            "title": title,
            "start": start,
            "end": end,
            "type": typ,
            "color": "",
            "detail": detail,
            "attendees": attendees,
            "source": "google_calendar",
            "prep": prep,
        })

    return events


def load_schedule_by_date(conn, start_date: str, days: int = 30) -> dict[str, list[dict]]:
    """Liest Kalender-Events für die nächsten N Tage ab start_date.

    Returns Mapping date_iso -> events[], inkl. leerer Tage.
    """
    result: dict[str, list[dict]] = {}
    if not conn:
        return result

    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    except Exception:
        return result

    # Alle Datums-Keys vorbereiten (damit auch leere Tage als [] erscheinen)
    for i in range(days):
        d = (start_dt + timedelta(days=i)).strftime("%Y-%m-%d")
        result[d] = []

    end_date = (start_dt + timedelta(days=days)).strftime("%Y-%m-%d")

    try:
        rows = conn.execute(
            "SELECT date, title, start_time, end_time, attendees, "
            "id, account, calendar_id, calendar_name, html_link, "
            "location, description "
            "FROM calendar_events WHERE date >= ? AND date < ? "
            "ORDER BY date, start_time",
            (start_date, end_date),
        ).fetchall()
    except Exception as e:
        print(f"  load_schedule_by_date failed: {e}")
        return result

    # Spalten koennen je nach DB-Stand fehlen (Migration), defensiv zugreifen
    def col(row, name, default=""):
        try:
            v = row[name]
            return v if v is not None else default
        except Exception:
            return default

    import json as _json

    color_map = {
        "deep work": "deep_work", "work": "deep_work", "focus": "deep_work",
        "call": "meeting", "meeting": "meeting", "update": "meeting",
        "sport": "sport", "gym": "sport", "training": "sport", "pull": "sport", "push": "sport",
        "content": "content", "video": "content", "reel": "content",
        "lernen": "lesen", "lesen": "lesen", "weiterbildung": "lesen",
        "pause": "pause", "mittag": "pause", "lunch": "pause",
        "abend": "abend", "dinner": "abend",
    }

    def classify(title: str) -> str:
        t = (title or "").lower()
        for key, typ in color_map.items():
            if key in t:
                return typ
        return "other"

    for row in rows:
        date = row["date"]
        title = row["title"] or ""
        start = row["start_time"] or ""
        end = row["end_time"] or ""

        if not title or title == "(Kein Titel)":
            continue
        if start and end and end < start:
            continue  # Skip übernacht-bloecke

        try:
            attendees = _json.loads(row["attendees"] or "[]")
        except Exception:
            attendees = []

        detail = ""
        if attendees:
            names = [a.split("@")[0] for a in attendees if a]
            detail = ", ".join(names)

        prep = load_call_prep(title, attendees)

        if date not in result:
            # Event liegt ausserhalb des Window-Keys (z.B. negative Stunden-Edge)
            result[date] = []

        result[date].append({
            "title": title,
            "start": start,
            "end": end,
            "type": classify(title),
            "color": "",
            "detail": detail,
            "attendees": attendees,
            "source": "google_calendar",
            "prep": prep,
            # Edit-Routing-Felder: Identitaet des Events für Google Calendar API
            "event_id": col(row, "id"),
            "account": col(row, "account", "primary"),
            "calendar_id": col(row, "calendar_id"),
            "calendar_name": col(row, "calendar_name"),
            "html_link": col(row, "html_link"),
            "location": col(row, "location"),
            "description": col(row, "description"),
        })

    return result


def load_schedule_from_daily_note(note_text: str) -> list[dict]:
    """Parst den Tagesplan-Block aus der Daily Note."""
    if not note_text:
        return []

    # Finde die Tagesplan-Section (stoppt an nächstem H2 oder H3 oder ---)
    match = re.search(r"###\s*Tagesplan\s*\n(.+?)(?=\n##\s|\n###\s|\n---|\Z)", note_text, re.DOTALL)
    if not match:
        return []

    block = match.group(1)
    schedule = []
    color_map = {
        "deep work": "#6366f1", "deep-work": "#6366f1", "work": "#6366f1",
        "pause": "#d1d5db", "mittag": "#d1d5db",
        "call": "#f97316", "meeting": "#f97316",
        "sport": "#22c55e", "pull": "#22c55e", "push": "#22c55e", "training": "#22c55e",
        "content": "#a855f7", "video": "#a855f7",
        "bod": "#fbbf24", "eod": "#fbbf24", "lesen": "#fbbf24",
        "abend": "#64748b",
    }

    def classify(title: str) -> tuple[str, str]:
        t = title.lower()
        for key, color in color_map.items():
            if key in t:
                return key.replace(" ", "_").replace("-", "_"), color
        return "other", "#94a3b8"

    for line in block.split("\n"):
        line = line.strip()
        # Matches "- 08:00 Titel" oder "- 08:30-09:00 Titel"
        m = re.match(r"^-\s*(\d{1,2}:\d{2})(?:\s*[-–]\s*(\d{1,2}:\d{2}))?\s+(.+)$", line)
        if not m:
            continue
        start, end, title = m.groups()
        # Normalisiere HH:MM (führende Null)
        start = start.zfill(5)
        if end:
            end = end.zfill(5)
        else:
            # Kein End angegeben: +30 Min als Default
            h, mm = map(int, start.split(":"))
            end_dt = datetime(2000, 1, 1, h, mm) + timedelta(minutes=30)
            end = end_dt.strftime("%H:%M")
        block_type, color = classify(title)
        schedule.append({
            "title": title.strip(),
            "start": start,
            "end": end,
            "type": block_type,
            "color": color,
        })

    return schedule


def _parse_todos_block(note_text: str) -> list[dict]:
    """Parst die Todo-Box (offene + erledigte) aus einem Daily-Note-Text.

    Sucht die '## Offene To-Dos' Section. Wenn fehlt: scant das ganze File
    nach Checkbox-Items, weil viele Daily Notes den Block nicht haben.
    """
    if not note_text:
        return []

    items: list[dict] = []

    match = re.search(r"##\s*Offene To-Dos\s*\n(.+?)(?=\n##\s|\Z)", note_text, re.DOTALL)
    scope = match.group(1) if match else note_text

    current_person = "Moritz"
    current_section = ""

    for line in scope.split("\n"):
        if line.startswith("###"):
            section = line.lstrip("#").strip().lower()
            current_section = section
            if "aurelien" in section or "aurélien" in section:
                current_person = "Aurelien"
            elif "kick" in section:
                current_person = "Kick"
            elif "team" in section:
                current_person = "Team"
            else:
                current_person = "Moritz"
            continue

        open_match = re.match(r"^\s*-\s*\[\s*\]\s*(.+)", line)
        done_match = re.match(r"^\s*-\s*\[x\]\s*(.+)", line, re.IGNORECASE)

        if open_match:
            items.append({
                "text": open_match.group(1).strip(),
                "done": False,
                "source": current_section,
                "person": current_person,
            })
        elif done_match:
            items.append({
                "text": done_match.group(1).strip(),
                "done": True,
                "source": current_section,
                "person": current_person,
            })

    return items


def load_todos_from_daily_note(note_text: str) -> dict:
    """Backwards-compat: alter Single-File-Parser, gibt {person: [items]} zurück."""
    todos = {"Moritz": [], "Aurelien": [], "Kick": [], "Team": []}
    for item in _parse_todos_block(note_text):
        person = item.pop("person", "Moritz")
        todos.setdefault(person, []).append(item)
    return todos


def load_todos_multi_day(today_iso: str, lookback_days: int = 7) -> dict:
    """Holt Tasks aus heutiger + bis zu 7 älteren Daily Notes.

    Logik:
    - Heutige Note: offene UND erledigte Tasks
    - Ältere Notes: nur OFFENE Tasks (die also nie abgehakt wurden)
    - Dedup nach Text (case-insensitive). Heute gewinnt bei Konflikt.
    - Tasks aus älteren Notes bekommen 'carry_over_from' Datum als source.
    """
    todos = {"Moritz": [], "Aurelien": [], "Kick": [], "Team": []}

    def add(item: dict, person: str, seen: set):
        key = item["text"].lower().strip()
        if key in seen:
            return
        seen.add(key)
        todos.setdefault(person, []).append(item)

    seen: set[str] = set()

    # Heute
    today_file = WORKSPACE / "06-daily-notes" / f"{today_iso}.md"
    if today_file.exists():
        for item in _parse_todos_block(today_file.read_text(encoding="utf-8")):
            person = item.pop("person", "Moritz")
            add(item, person, seen)

    # Vorherige Tage (offene only)
    try:
        today_dt = datetime.strptime(today_iso, "%Y-%m-%d")
    except Exception:
        return todos
    for back in range(1, lookback_days + 1):
        day = (today_dt - timedelta(days=back)).strftime("%Y-%m-%d")
        f = WORKSPACE / "06-daily-notes" / f"{day}.md"
        if not f.exists():
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        for item in _parse_todos_block(text):
            if item.get("done"):
                continue  # ältere erledigte: ignorieren
            person = item.pop("person", "Moritz")
            item["carry_over_from"] = day
            item["source"] = f"{item.get('source', '')} · aus {day}".strip(" ·")
            add(item, person, seen)

    return todos


def load_youtube_metrics(conn):
    if not conn:
        return {"yt_subs": 0, "yt_views_week": 0}, [], []

    try:
        row = conn.execute(
            "SELECT subscribers, total_views, total_videos FROM youtube_daily ORDER BY date DESC LIMIT 1"
        ).fetchone()
    except Exception:
        row = None

    metrics = {
        "yt_subs": row["subscribers"] if row else 0,
        "yt_views_week": row["total_views"] if row else 0,
    }

    try:
        videos = [
            dict(r) for r in conn.execute(
                "SELECT title, views, likes, comments, published_date as date "
                "FROM youtube_videos ORDER BY views DESC LIMIT 5"
            ).fetchall()
        ]
    except Exception:
        videos = []

    try:
        rows = conn.execute(
            "SELECT date, total_views FROM youtube_daily ORDER BY date DESC LIMIT 7"
        ).fetchall()
        views_7d = [r["total_views"] for r in reversed(rows)]
    except Exception:
        views_7d = [0] * 7

    return metrics, videos, views_7d


def load_whatsapp():
    """Parst WhatsApp Komplett-Kontext.md in Chat-Liste."""
    wa_path = WORKSPACE / "04-areas" / "business" / "WhatsApp Komplett-Kontext.md"
    if not wa_path.exists():
        return {"chats": [], "stats": {"total_chats": 0, "unread": 0, "clients": 0, "team": 0}}

    text = wa_path.read_text(encoding="utf-8")

    chats = []
    current_section = ""

    # Split by H2 (##) blocks, then parse H3 (###) within
    blocks = re.split(r"\n##\s+", text)
    for block in blocks[1:]:  # skip preamble before first ##
        lines = block.split("\n")
        section_title = lines[0].strip()
        section_lower = section_title.lower()

        # Klassifizieren
        if "testkunden" in section_lower:
            chat_type = "client"
        elif "team" in section_lower:
            chat_type = "team"
        elif "sentrovo" in section_lower or "aktiv" in section_lower or "weniger" in section_lower:
            chat_type = "other"
        else:
            chat_type = "other"

        current_section = section_title
        rest = "\n".join(lines[1:])

        # Split by H3 innerhalb
        chat_blocks = re.split(r"\n###\s+", rest)
        for cb in chat_blocks[1:]:
            clines = cb.split("\n")
            name_line = clines[0].strip()
            # Namen von Nummerierungen befreien
            name_clean = re.sub(r"^\d+\.\s*", "", name_line)

            body = "\n".join(clines[1:])

            # Status
            status_match = re.search(r"\*\*Status:\*\*\s*(.+)", body)
            status = status_match.group(1).strip() if status_match else ""

            # Letzte Aktivität
            activity_match = re.search(r"\*\*Letzte\s+Aktivit[aä]t:\*\*\s*(.+)", body)
            last_activity = activity_match.group(1).strip() if activity_match else ""

            # Kurze Summary: erster Fließtext-Absatz
            summary = ""
            for paragraph in re.split(r"\n\n", body):
                p = paragraph.strip()
                if not p or p.startswith("**") or p.startswith("-") or p.startswith("#"):
                    continue
                summary = p[:300]
                break

            # Sentrovo-Kunden als "legacy" markieren (kein client, sondern other)
            this_type = chat_type
            if "sentrovo" in name_clean.lower() or "sentrovo" in current_section.lower():
                this_type = "legacy"

            chats.append({
                "name": name_clean,
                "category": current_section,
                "type": this_type,
                "status": status,
                "last_activity": last_activity,
                "summary": summary,
                "recent_messages": [],
            })

    # Lade recent_messages aus Cache (geschrieben von sync_whatsapp.py)
    msg_cache = WORKSPACE / "data" / "whatsapp_messages.json"
    if msg_cache.exists():
        try:
            cached = json.loads(msg_cache.read_text(encoding="utf-8"))
            # Matche Cache-Eintraege auf Chats anhand des Namens
            for chat in chats:
                chat_name_lower = chat["name"].lower()
                for cached_chat in cached:
                    if cached_chat.get("name", "").lower() in chat_name_lower or \
                       chat_name_lower in cached_chat.get("name", "").lower():
                        chat["recent_messages"] = cached_chat.get("messages", [])[:50]
                        break
        except (json.JSONDecodeError, Exception):
            pass

    stats = {
        "total_chats": len(chats),
        "clients": sum(1 for c in chats if c["type"] == "client"),
        "team": sum(1 for c in chats if c["type"] == "team"),
        "legacy": sum(1 for c in chats if c["type"] == "legacy"),
        "unread": 0,
    }

    return {"chats": chats, "stats": stats}


def load_finance():
    """Parst Finances.md für echte Umsatz-Historie."""
    fin_path = WORKSPACE / "04-areas" / "business" / "Finances.md"
    if not fin_path.exists():
        return {
            "revenue_mtd": 0, "revenue_target": 10000,
            "open_invoices": [], "expenses_mtd": 0,
            "monthly_history": [], "yearly_history": [],
        }

    text = fin_path.read_text(encoding="utf-8")
    monthly_history = []  # [{month: "2026-04", amount: float}, ...]

    # Tabellenzeilen: | Monat Jahr | ... | **Gesamt** |
    # Erwischt: "| April 2025 | 556 + 840 | **1.396,00** |"
    table_line_re = re.compile(
        r"\|\s*([A-Za-zÄÖÜäöüß]+)\s+(\d{4})\s*\|.*?\|\s*\**([\d.]+,\d{2})\**\s*\|"
    )

    for m in table_line_re.finditer(text):
        month_de, year, amount_str = m.groups()
        month_num = MONTHS_DE_TO_NUM.get(month_de.lower())
        if not month_num:
            continue
        amount = float(amount_str.replace(".", "").replace(",", "."))
        monthly_history.append({
            "month": f"{year}-{month_num:02d}",
            "label": f"{month_de} {year}",
            "amount": amount,
        })

    # Sortiert nach Monat (chronologisch)
    monthly_history.sort(key=lambda x: x["month"])

    # MTD: aktueller Monat
    current_key = datetime.now().strftime("%Y-%m")
    revenue_mtd = next((m["amount"] for m in monthly_history if m["month"] == current_key), 0)

    # Yearly aggregation
    yearly = {}
    for m in monthly_history:
        year = m["month"][:4]
        yearly[year] = yearly.get(year, 0) + m["amount"]
    yearly_history = [{"year": y, "amount": round(a, 2)} for y, a in sorted(yearly.items())]

    # Weekly: wir haben nur Monatsdaten, also aus aktuellem Monat gleichmäßig verteilen (Schätzung)
    weeks_in_month = 4
    weekly_history = []
    if revenue_mtd > 0:
        # letzte 8 Wochen: aktuelle 4 aus revenue_mtd, davor aus Vormonat
        prev_key = (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
        prev_amount = next((m["amount"] for m in monthly_history if m["month"] == prev_key), 0)
        weekly_avg_current = revenue_mtd / weeks_in_month
        weekly_avg_prev = prev_amount / weeks_in_month
        for i in range(8):
            week_date = datetime.now() - timedelta(weeks=7 - i)
            amt = weekly_avg_prev if i < 4 else weekly_avg_current
            weekly_history.append({
                "week": week_date.strftime("%Y-W%V"),
                "amount": round(amt, 2),
            })

    # Daily: keine Daten, leere Liste
    daily_history = []

    return {
        "revenue_mtd": revenue_mtd,
        "revenue_target": 10000,
        "open_invoices": [],
        "expenses_mtd": 0,  # keine echten Ausgabendaten verfügbar
        "monthly_history": monthly_history,
        "yearly_history": yearly_history,
        "weekly_history": weekly_history,
        "daily_history": daily_history,
    }


def load_brief():
    brief_path = WORKSPACE / "outputs" / "daily-brief" / f"{TODAY}.md"
    if not brief_path.exists():
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        brief_path = WORKSPACE / "outputs" / "daily-brief" / f"{yesterday}.md"

    text = ""
    date = TODAY
    audio_url = ""
    if brief_path.exists():
        text = brief_path.read_text(encoding="utf-8")
        date = brief_path.stem
        audio_file = brief_path.parent / f"{date}-voice.mp3"
        if audio_file.exists():
            audio_url = f"/outputs/daily-brief/{date}-voice.mp3"

    return {"text": text[:8000], "date": date, "audio_url": audio_url}


def load_contacts():
    contacts_dir = WORKSPACE / "04-areas" / "contacts"
    if not contacts_dir.exists():
        return []

    contacts = []
    for f in sorted(contacts_dir.glob("*.md")):
        if f.name.startswith("_") or f.name == "template.md":
            continue
        name = f.stem
        text = f.read_text(encoding="utf-8")
        role_match = re.search(r"\*\*Rolle:\*\*\s*(.+)", text)
        role = role_match.group(1).strip() if role_match else ""
        contacts.append({"name": name, "role": role, "location": ""})

    return contacts


def load_news_from_research() -> list[dict]:
    """Liest echte News aus 05-reference/insights/Daily Research/YYYY-MM-DD.md.

    Fällt auf gestern zurück falls heute noch keine Research existiert.
    """
    research_dir = WORKSPACE / "05-reference" / "insights" / "Daily Research"
    if not research_dir.exists():
        return []

    # Neueste Research-Datei finden
    files = sorted(research_dir.glob("*.md"), reverse=True)
    if not files:
        return []

    research_file = files[0]
    research_date = research_file.stem
    text = research_file.read_text(encoding="utf-8")

    news = []
    # Kategorien (H2)
    category_blocks = re.split(r"\n##\s+", text)
    for block in category_blocks[1:]:
        blines = block.split("\n")
        category = blines[0].strip()
        rest = "\n".join(blines[1:])

        # News-Items (H3)
        item_blocks = re.split(r"\n###\s+", rest)
        for ib in item_blocks[1:]:
            ilines = ib.split("\n")
            title = ilines[0].strip()
            body_lines = ilines[1:]
            body = "\n".join(body_lines).strip()

            # Quelle extrahieren
            source_match = re.search(r"Quelle:\s*\[\[([^\|]+)\|([^\]]+)\]\]", body)
            source_name = ""
            source_url = ""
            if source_match:
                source_name = source_match.group(1).strip()
                source_url = source_match.group(2).strip()

            # Body ohne Quelle-Zeile für Summary
            summary = re.sub(r"Quelle:\s*\[\[.+?\]\].*?\n?", "", body, flags=re.DOTALL).strip()
            # Relevanz-Zeilen reinlassen (enthalten Kontext)

            if not title:
                continue

            news.append({
                "title": title,
                "summary": summary,
                "source": source_name or "Research",
                "source_url": source_url,
                "category": category,
                "date": research_date,
            })

    return news


def load_projects() -> list:
    """Liest alle Projekte aus 03-projects/ (inkl. Unterordner mit Hauptdatei)."""
    projects_dir = WORKSPACE / "03-projects"
    if not projects_dir.exists():
        return []

    files = []
    for p in projects_dir.iterdir():
        if p.is_file() and p.suffix == ".md" and p.name != "project-template.md":
            files.append(p)
        elif p.is_dir():
            # Suche Hauptdatei im Unterordner
            for inner in p.iterdir():
                if inner.suffix == ".md":
                    files.append(inner)
                    break

    projects = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        # Frontmatter
        fm_match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        fm = {}
        if fm_match:
            fm_lines = fm_match.group(1).split("\n")
            current_key = None
            for line in fm_lines:
                # List item (indented "- value")
                list_match = re.match(r"^\s+-\s+(.+)$", line)
                if list_match and current_key:
                    fm.setdefault(current_key + "_list", []).append(list_match.group(1).strip())
                    continue
                if ":" in line:
                    k, _, v = line.partition(":")
                    key = k.strip().lower()
                    val = v.strip()
                    fm[key] = val
                    current_key = key
            body = text[fm_match.end():]
        else:
            body = text

        # Ziel extrahieren (erster Absatz nach "## Ziel")
        ziel_match = re.search(r"##\s*Ziel\s*\n+(.+?)(?=\n##|\Z)", body, re.DOTALL)
        ziel = ""
        if ziel_match:
            ziel = ziel_match.group(1).strip().split("\n\n")[0].strip()
            ziel = re.sub(r"\s+", " ", ziel)[:260]

        # Nächste Schritte (Bullets)
        next_steps = []
        ns_match = re.search(r"##\s*N[aä]chste Schritte\s*\n(.+?)(?=\n##|\Z)", body, re.DOTALL)
        if ns_match:
            for line in ns_match.group(1).split("\n"):
                m = re.match(r"^-\s*(?:\[\s*\]\s*)?(.+)", line.strip())
                if m:
                    txt = m.group(1).strip()
                    if txt and not txt.startswith("["):
                        next_steps.append(txt[:120])
                if len(next_steps) >= 3:
                    break

        title = f.stem.replace("-", " ").replace("_", " ")
        # Heading-Titel bevorzugen
        h1 = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        if h1:
            title = h1.group(1).strip()

        status = fm.get("status", "aktiv").strip().strip('"').lower()
        status_notiz = fm.get("status-notiz", fm.get("status_notiz", "")).strip().strip('"')
        priority = fm.get("priorität", fm.get("prioritat", fm.get("priority", ""))).strip().strip('"').lower()
        deadline = fm.get("deadline", "").strip().strip('"')
        created = fm.get("erstellt", "").strip().strip('"')

        # Kategorie aus Inhalt raten
        lower = (title + " " + ziel).lower()
        if any(k in lower for k in ["deinmarkt"]):
            category = "Produkt"
        elif any(k in lower for k in ["youtube", "content", "reel", "video", "thumbnail", "creator"]):
            category = "Content"
        elif any(k in lower for k in ["website", "landingpage", "pivot", "freemium"]):
            category = "Go-to-Market"
        elif any(k in lower for k in ["rolle", "aw one", "team"]):
            category = "Organisation"
        else:
            category = "Sonstiges"

        clients = fm.get("beispiel_kunden_list", []) or fm.get("kunden_list", [])

        projects.append({
            "title": title,
            "file": str(f.relative_to(WORKSPACE)),
            "status": status or "aktiv",
            "status_notiz": status_notiz,
            "priority": priority or "mittel",
            "deadline": deadline,
            "created": created,
            "category": category,
            "goal": ziel,
            "next_steps": next_steps,
            "clients": clients,
        })

    # Sortierung: aktiv > idee > paused > archiviert; danach Prio
    status_order = {"aktiv": 0, "idee": 1, "paused": 2, "archiviert": 3}
    prio_order = {"hoch": 0, "high": 0, "mittel": 1, "medium": 1, "niedrig": 2, "low": 2, "": 3}
    projects.sort(key=lambda p: (status_order.get(p["status"], 9), prio_order.get(p["priority"], 9), p["title"]))
    return projects


def run_sibling_collectors():
    """Trigger build_sales_pipeline.py + build_system_health.py + build_knowledge_library.py vor dem Dashboard-Build."""
    for script in ("build_sales_pipeline.py", "build_system_health.py", "build_knowledge_library.py"):
        path = WORKSPACE / "scripts" / script
        if not path.exists():
            continue
        try:
            subprocess.run([sys.executable, str(path)], timeout=30, check=False)
        except subprocess.TimeoutExpired:
            print(f"  {script} timeout")


def load_json(relative_path: str):
    p = WORKSPACE / relative_path
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def load_self_tracker_metrics():
    """Liest Moritz' eigene Reel-Metriken aus dem Instagram-Tracker-Snapshot.

    Quelle: 05-reference/competitor-content/_data/<heute>.json (oder bis zu 7 Tage rückwärts).
    Liefert dasselbe Format wie das frühere data/content-metrics.json · damit das Dashboard-HTML
    keine Code-Änderung braucht. Wenn kein Snapshot innerhalb der letzten 7 Tage gefunden wird,
    None zurück.
    """
    base = WORKSPACE / "05-reference" / "competitor-content" / "_data"
    if not base.exists():
        return None

    snapshot = None
    snapshot_date = None
    moritz = None
    for i in range(14):
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        p = base / f"{d}.json"
        if not p.exists():
            continue
        try:
            candidate = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        candidate_moritz = candidate.get("creators", {}).get("moritz.maaker")
        if candidate_moritz and candidate_moritz.get("reels"):
            snapshot = candidate
            snapshot_date = d
            moritz = candidate_moritz
            break

    if not moritz:
        return None

    reels = moritz["reels"]
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=7)

    def _to_post(r: dict) -> dict:
        return {
            "platform": "Instagram",
            "type": "reel",
            "title": (r.get("caption_snippet") or "").strip()[:80],
            "posted": r.get("posted", ""),
            "views": r.get("views", 0),
            "likes": r.get("likes", 0),
            "comments": r.get("comments", 0),
            "engagement_rate": r.get("engagement_rate", 0),
            "shortcode": r.get("shortcode", ""),
            "url": r.get("url", ""),
            "hashtags": r.get("hashtags", []),
        }

    posts = [_to_post(r) for r in reels]

    # Hero = Reel mit max views
    hero_reel = max(reels, key=lambda r: r.get("views", 0))
    hero = {
        "platform": "Instagram",
        "title": (hero_reel.get("caption_snippet") or "").strip()[:80],
        "posted": hero_reel.get("posted", ""),
        "shortcode": hero_reel.get("shortcode", ""),
        "url": hero_reel.get("url", ""),
        "status": "🔥 hero" if hero_reel.get("views", 0) > 100000 else "top",
        "metrics": {
            "views": hero_reel.get("views", 0),
            "likes": hero_reel.get("likes", 0),
            "comments": hero_reel.get("comments", 0),
            "engagement_rate": hero_reel.get("engagement_rate", 0),
            "bounce_rate": hero_reel.get("bounce_rate", 0),
        },
    }

    # 7-Tage-Aggregate (Reels gepostet in den letzten 7 Tagen)
    def _is_recent(r: dict) -> bool:
        try:
            return datetime.strptime(r.get("posted", ""), "%Y-%m-%d").date() >= seven_days_ago
        except (ValueError, TypeError):
            return False

    recent = [r for r in reels if _is_recent(r)]
    fallback = recent or reels  # falls keine in letzten 7 Tagen, nimm alle

    stats = {
        "total_views_7d": sum(r.get("views", 0) for r in fallback),
        "total_likes_7d": sum(r.get("likes", 0) for r in fallback),
        "total_comments_7d": sum(r.get("comments", 0) for r in fallback),
        "posts_7d": len(recent),
        "engagement_rate": moritz.get("avg_engagement_rate") or 0,
        "avg_views": moritz.get("avg_views", 0),
        "avg_likes": moritz.get("avg_likes", 0),
        "avg_comments": moritz.get("avg_comments", 0),
    }

    return {
        "_source": f"instagram_tracker snapshot {snapshot_date}",
        "updated_at": snapshot.get("run_started", snapshot_date),
        "hero": hero,
        "posts": posts,
        "stats": stats,
    }


def _strip_inline_comment(v: str) -> str:
    """Entfernt YAML-Inline-Kommentar: alles ab ' # ' (Space-Hash-Space) am
    Ende. Beachtet Quotes nicht — wir nutzen Inline-Comments nur in einfachen
    Wertzeilen. '# foo' am ZeilenANFANG wird vorher schon geskippt."""
    if not v:
        return v
    # Suche " #" gefolgt von Space ODER Ende
    idx = v.find(" #")
    if idx >= 0:
        return v[:idx].rstrip()
    return v


def _parse_frontmatter(text: str) -> dict:
    """Mini-YAML-Frontmatter-Parser. Liest nur den Block zwischen --- und ---.
    Unterstuetzt key: value (skalar), key: |  blockstring, key: - liste.
    Inline-Kommentare (' # ...' am Zeilenende) werden entfernt.
    Reicht für unsere Reel-Scripts."""
    if not text.startswith("---"):
        return {}
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return {}
    block = text[4:end]
    result = {}
    lines = block.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val == "|":
            # Block-Scalar
            i += 1
            collected = []
            while i < len(lines) and (lines[i].startswith("  ") or lines[i].strip() == ""):
                collected.append(lines[i][2:] if lines[i].startswith("  ") else "")
                i += 1
            result[key] = "\n".join(collected).rstrip()
            continue
        if val == "":
            # Liste oder nested dict folgt evtl.
            i += 1
            items = []
            nested = {}
            while i < len(lines):
                nxt = lines[i]
                if nxt.lstrip().startswith("- "):
                    items.append(nxt.lstrip()[2:].strip())
                    i += 1
                    continue
                # nested dict: genau 2 Spaces Einrueckung + key: value
                if nxt.startswith("  ") and not nxt.startswith("   ") and ":" in nxt:
                    sub = nxt[2:]
                    sk, _, sv = sub.partition(":")
                    sk = sk.strip()
                    sv = _strip_inline_comment(sv.strip()).strip("\"'")
                    if sv in ("~", "null", ""):
                        sv = None
                    nested[sk] = sv
                    i += 1
                    continue
                if nxt.strip() == "":
                    i += 1
                    continue
                break
            if items:
                result[key] = items
                continue
            if nested:
                result[key] = nested
                continue
            result[key] = ""
            continue
        # Inline-Wert (Inline-Kommentar abschneiden, dann Quotes entfernen)
        v = _strip_inline_comment(val.strip()).strip("\"'")
        if v in ("~", "null"):
            v = None
        result[key] = v
        i += 1
    return result


def load_tiktok_intel():
    """Liest den letzten TikTok-Snapshot aus 05-reference/tiktok-tracker/_data/
    und bereitet ihn fürs Dashboard auf. Schema bewusst parallel zu
    load_content_intel(), damit das Frontend dieselbe KPI-Card-Logik nutzen kann.

    Liefert:
      - all_self_videos: Liste normalisierter TikTok-Videos
      - range_kpis: today / 7d / 30d / all mit View-Deltas aus reel_history.db
      - totals: handle, snapshot_date, videos_count
    """
    base = WORKSPACE / "05-reference" / "tiktok-tracker" / "_data"
    if not base.exists():
        return {"available": False, "note": "TikTok-Tracker hat noch keinen Snapshot geschrieben"}

    snapshot = None
    snapshot_date = None
    for i in range(7):
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        p = base / f"{d}.json"
        if not p.exists():
            continue
        try:
            cand = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if cand.get("videos_total", 0) > 0:
            snapshot = cand
            snapshot_date = d
            break
    if not snapshot:
        return {"available": False, "note": "Kein TikTok-Snapshot mit Videos in den letzten 7 Tagen"}

    self_handle = snapshot.get("self_handle") or "moritz.maaker"
    creators = snapshot.get("creators", {}) or {}
    own = creators.get(self_handle) or {}
    videos = own.get("reels") or []

    # Sort: neueste zuerst
    videos.sort(key=lambda r: r.get("posted_at") or "", reverse=True)

    today_str = datetime.now().strftime("%Y-%m-%d")
    today_dt = datetime.now().date()

    def _in_range(reel, days):
        p = (reel.get("posted") or "")[:10]
        if not p:
            return False
        try:
            posted = datetime.strptime(p, "%Y-%m-%d").date()
        except Exception:
            return False
        return (today_dt - posted).days <= days

    def _agg(reels):
        n = len(reels)
        if n == 0:
            return {
                "count": 0, "total_views": 0, "total_likes": 0, "total_comments": 0,
                "total_shares": 0, "total_saves": 0,
                "avg_views": 0, "avg_engagement_rate": 0.0,
                "avg_save_rate": 0.0, "avg_share_rate": 0.0,
            }
            # avg_save_rate = saves/views, der Kaufabsichts-Proxy aus dem PDF
        views = [r.get("views", 0) or 0 for r in reels]
        likes = [r.get("likes", 0) or 0 for r in reels]
        comments = [r.get("comments", 0) or 0 for r in reels]
        shares = [r.get("shares", 0) or 0 for r in reels]
        saves = [r.get("saves", 0) or 0 for r in reels]
        ers = [r.get("engagement_rate", 0.0) or 0.0 for r in reels]
        save_rates = [
            (s / v * 100 if v else 0.0) for s, v in zip(saves, views)
        ]
        share_rates = [
            (s / v * 100 if v else 0.0) for s, v in zip(shares, views)
        ]
        return {
            "count": n,
            "total_views": sum(views),
            "total_likes": sum(likes),
            "total_comments": sum(comments),
            "total_shares": sum(shares),
            "total_saves": sum(saves),
            "avg_views": round(sum(views) / n),
            "avg_engagement_rate": round(sum(ers) / n, 2),
            "avg_save_rate": round(sum(save_rates) / n, 2),
            "avg_share_rate": round(sum(share_rates) / n, 2),
        }

    range_kpis = {
        "today": _agg([r for r in videos if (r.get("posted") or "")[:10] == today_str]),
        "7d": _agg([r for r in videos if _in_range(r, 7)]),
        "30d": _agg([r for r in videos if _in_range(r, 30)]),
        "all": _agg(videos),
    }
    # View-Deltas aus reel_history.db, gleiche Logik wie Instagram. Handle hat
    # '@tiktok'-Suffix damit IG- und TT-Shortcodes nicht kollidieren.
    try:
        sys.path.insert(0, str(WORKSPACE / "scripts"))
        from reel_history import all_reels_delta as _rh_delta  # type: ignore
        from reel_history import stats as _rh_stats  # type: ignore
        for window_key, days in (("7d", 7), ("30d", 30)):
            d = _rh_delta(f"{self_handle}@tiktok", days, today=today_str)
            range_kpis[window_key]["views_delta_total"] = d["views_delta"]
            range_kpis[window_key]["reels_tracked"] = d["count_reels"]
            range_kpis[window_key]["window_start"] = d["window_start"]
        # First snapshot bezogen auf alle Handles, hilft beim UI-Hinweis
        range_kpis["history_first_snapshot"] = _rh_stats().get("first_snapshot")
    except Exception as e:
        print(f"WARNING: TikTok-Deltas nicht verfuegbar: {e}", file=sys.stderr)

    return {
        "available": True,
        "platform": "tiktok",
        "self_handle": self_handle,
        "snapshot_date": snapshot_date,
        "all_self_videos": videos,
        "range_kpis": range_kpis,
        "totals": {
            "videos_total": len(videos),
        },
    }


def load_marketing_scorecard():
    """Einfache Ziel-Tracker pro Plattform. Aktuell: Reels/Woche-Ziel für
    Instagram + Videos/Woche-Ziel für TikTok. Ist-Werte werden automatisch aus
    dem Vault (library/<platform>/) gezählt. Manuelle Ziele aus
    04-areas/content/scorecard.md Frontmatter.

    Bewusst minimal gehalten — alle anderen KPIs (Views, Likes, ER, ...) siehst
    du in den KPI-Cards der jeweiligen Plattform-Sicht.
    """
    base = WORKSPACE / "04-areas" / "content"
    sc_path = base / "scorecard.md"
    manual = {}
    if sc_path.exists():
        try:
            manual = _parse_frontmatter(sc_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"WARNING: scorecard.md nicht lesbar: {e}", file=sys.stderr)

    today_dt = datetime.now().date()
    # Kalenderwoche Mo-So: bei Montag 0 zaehlen, bei Sonntag 6.
    # Posts ab "Montag dieser Woche 00:00" zaehlen mit. Damit wirkt
    # "5/7 Reels diese Woche, heute Samstag" intuitiv richtig.
    days_since_monday = today_dt.weekday()  # Mo=0, So=6
    week_start_s = (today_dt - timedelta(days=days_since_monday)).strftime("%Y-%m-%d")
    today_s = today_dt.strftime("%Y-%m-%d")

    def _count_this_week(platform_dir: Path) -> int:
        if not platform_dir.exists():
            return 0
        n = 0
        for entry in platform_dir.iterdir():
            if not entry.is_dir() or entry.name.startswith(("_", ".")):
                continue
            d = entry.name[:10]
            try:
                datetime.strptime(d, "%Y-%m-%d")
            except ValueError:
                continue
            # Zukunfts-Folder (geplant aber noch nicht gepostet) raus.
            if d >= week_start_s and d <= today_s:
                n += 1
        return n

    ig_count = _count_this_week(base / "library" / "instagram")

    # TikTok-Ist aus dem echten Tracker-Snapshot, nicht aus dem manuellen
    # Cross-Post-Folder. Damit zaehlt was auf TikTok tatsaechlich live ist.
    tt_count = 0
    tt_snap_dir = WORKSPACE / "05-reference" / "tiktok-tracker" / "_data"
    if tt_snap_dir.exists():
        tt_files = sorted(tt_snap_dir.glob("*.json"))
        if tt_files:
            try:
                tt_snap = json.loads(tt_files[-1].read_text(encoding="utf-8"))
                tt_handle = tt_snap.get("self_handle") or ""
                tt_videos = (tt_snap.get("creators", {}).get(tt_handle, {}) or {}).get("reels") or []
                tt_count = sum(
                    1 for v in tt_videos
                    if week_start_s <= (v.get("posted") or "")[:10] <= today_s
                )
            except Exception as e:
                print(f"WARNING: TikTok-Ist nicht lesbar: {e}", file=sys.stderr)

    def _i(v, default):
        try:
            return int(v) if v not in (None, "", "~") else default
        except (ValueError, TypeError):
            return default

    ig_goals = manual.get("instagram") or {}
    tt_goals = manual.get("tiktok") or {}
    ig_target = _i(ig_goals.get("reels_per_week_target"), 7)
    tt_target = _i(tt_goals.get("videos_per_week_target"), 7)

    return {
        "available": True,
        "last_updated": manual.get("last_updated") or "",
        "goals": {
            "instagram": {
                "label": "Reels pro Woche",
                "value": ig_count,
                "target": ig_target,
                "period": "diese Woche (Mo–So)",
            },
            "tiktok": {
                "label": "Videos pro Woche",
                "value": tt_count,
                "target": tt_target,
                "period": "diese Woche (Mo–So)",
            },
        },
    }


def load_content_planning():
    """Liest die Content-Planung aus dem Vault:
       - 04-areas/content/pipeline/<datum>_<slug>/script.md (Pipeline-Reels)
       - 04-areas/content/pipeline/ideas/*.md (Ideen)
       - 04-areas/content/library/<platform>/...  (gepostete Posts)

    Output:
      {
        "instagram": { "planned": [...], "posted": [...] },
        "linkedin":  { "planned": [...], "posted": [...] },
        "youtube":   { "planned": [],     "posted": [] },
        "ideas":     [...],
        "stats":     { ... }
      }
    """
    base = WORKSPACE / "04-areas" / "content"
    if not base.exists():
        return {"available": False, "note": "04-areas/content fehlt"}

    def _read_text(p: Path) -> str:
        try:
            return p.read_text(encoding="utf-8")
        except Exception:
            return ""

    def _build_piece(folder, platform, kind):
        # Sucht script.md im Folder; bei Top-Level-MD-Files (LinkedIn) nimmt die selbst.
        if folder.is_file() and folder.suffix == ".md":
            md = folder
            slug_root = folder.stem
        else:
            md = folder / "script.md"
            if not md.exists():
                # Fallback: erste .md im Folder
                mds = sorted(folder.glob("*.md"))
                if not mds:
                    return None
                md = mds[0]
            slug_root = folder.name
        raw = _read_text(md)
        fm = _parse_frontmatter(raw)
        # Body ohne Frontmatter
        body = raw
        if raw.startswith("---"):
            try:
                end = raw.index("\n---", 3)
                body = raw[end + 4:].lstrip()
            except ValueError:
                body = raw
        # Title aus erstem H1 oder Slug
        title = slug_root
        for line in body.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break

        # final.mp4 vorhanden? (fuer Inline-Video-Preview im Dashboard)
        final_mp4 = ""
        # Cover-Bild fuer LinkedIn-Posts (manuell abgelegt): cover.png/jpg/jpeg.
        cover_image = ""
        if folder.is_dir():
            mp4 = folder / "final.mp4"
            if mp4.exists():
                final_mp4 = str(mp4.relative_to(WORKSPACE))
            for ext in ("png", "jpg", "jpeg", "webp"):
                cov = folder / f"cover.{ext}"
                if cov.exists():
                    cover_image = str(cov.relative_to(WORKSPACE))
                    break

        # Post-Text extrahieren (LinkedIn-Detail-Modal). Priorität:
        # 1. Frontmatter-Feld `post_text` (Block-Scalar)
        # 2. Erster Code-Fence-Block im Body (```...```)
        # 3. Erster zusammenhaengender Blockquote-Run (> ...)
        post_text = (fm.get("post_text") or "").strip()
        if not post_text and body:
            lines_body = body.split("\n")
            # Code-Fence-Block
            in_block = False
            collected = []
            for ln in lines_body:
                if ln.strip().startswith("```"):
                    if in_block:
                        break
                    in_block = True
                    continue
                if in_block:
                    collected.append(ln)
            if collected:
                post_text = "\n".join(collected).strip()
        if not post_text and body:
            # Blockquote-Run
            quote_lines = []
            for ln in body.split("\n"):
                if ln.startswith(">"):
                    quote_lines.append(ln.lstrip("> ").rstrip())
                elif quote_lines:
                    break
            if quote_lines:
                post_text = "\n".join(quote_lines).strip()

        # KPIs aus verschachteltem kpis-Block lesen (LinkedIn-Phase-1-Tracking, manuell)
        kpis_raw = fm.get("kpis") if isinstance(fm.get("kpis"), dict) else {}
        def _kpi_int(key):
            v = kpis_raw.get(key)
            if v is None or v == "~" or v == "":
                return None
            try:
                return int(v)
            except (ValueError, TypeError):
                return None
        kpis = {
            "impressions": _kpi_int("impressions"),
            "views": _kpi_int("views"),
            "likes": _kpi_int("likes"),
            "comments": _kpi_int("comments"),
            "reposts": _kpi_int("reposts"),
            "profile_visits": _kpi_int("profile_visits"),
            "last_updated": kpis_raw.get("last_updated") if kpis_raw.get("last_updated") not in ("~", None, "") else None,
        }

        yt_video_id = fm.get("video_id") if fm.get("video_id") not in ("~", None, "") else ""
        yt_url = fm.get("url") if fm.get("url") not in ("~", None, "") else ""
        yt_duration_s = fm.get("duration_s") if fm.get("duration_s") not in ("~", None, "") else None

        return {
            "id": f"{platform}-{slug_root}",
            "platform": platform,
            "kind": kind,  # "konzept" | "bereit" | "posted" | "idea"
            "title": title,
            "slug": slug_root,
            "status": fm.get("status") or "",
            "hook": fm.get("hook") or "",
            "trigger_word": fm.get("trigger-word") or "",
            "serie": fm.get("serie") or "",
            "bucket": fm.get("bucket") or "",
            "reel_number": fm.get("reel-nummer") or "",
            "hashtags": fm.get("hashtags") if isinstance(fm.get("hashtags"), list) else [],
            "caption": fm.get("caption") or "",
            "voice_status": fm.get("voice-status") or "",
            "post_url": fm.get("post_url") or yt_url or "",
            "shortcode": fm.get("shortcode") or "",
            "posted_at": fm.get("posted_at") or fm.get("posted") or "",
            "video_id": yt_video_id,
            "url": yt_url,
            "duration_s": yt_duration_s,
            "created": fm.get("created") or fm.get("erstellt") or fm.get("datum") or "",
            "vault_path": str(md.relative_to(WORKSPACE)),
            "folder": str(folder.relative_to(WORKSPACE)) if folder.is_dir() else "",
            "body_preview": body[:400] if body else "",
            "post_text": post_text,
            "final_mp4": final_mp4,
            "cover_image": cover_image,
            "kpis": kpis,
            # Cross-Posting-Status pro Plattform (Quelle: Frontmatter crosspost_*)
            "crosspost_tiktok": fm.get("crosspost_tiktok") or "open",
            "crosspost_youtube_shorts": fm.get("crosspost_youtube_shorts") or "open",
        }

    out = {
        "instagram": {"konzept": [], "bereit": [], "planned": [], "posted": []},
        "linkedin": {"konzept": [], "bereit": [], "planned": [], "posted": []},
        "youtube": {"konzept": [], "bereit": [], "planned": [], "posted": []},
        # TikTok ist Cross-Post-View, kein eigener Content. Wird unten aus
        # Instagram-Posts mit final.mp4 + crosspost_tiktok-Status abgeleitet.
        "tiktok": {"konzept": [], "bereit": [], "planned": [], "posted": []},
        "ideas": [],
    }

    def _platform_of(piece, md_path):
        fm = _parse_frontmatter(_read_text(md_path))
        plat = (fm.get("platform") or "").strip().lower()
        if plat in ("instagram", "linkedin", "youtube"):
            return plat
        # Fallback: aus Slug-Praefix ableiten
        slug = piece.get("slug", "")
        if "linkedin" in slug.lower():
            return "linkedin"
        if "youtube" in slug.lower() or slug.lower().startswith("yt"):
            return "youtube"
        return "instagram"

    # Pipeline neu: pipeline/konzept/<slug>/ + pipeline/bereit/<slug>/
    pipeline_dir = base / "pipeline"
    for kind_name, sub in (("konzept", "konzept"), ("bereit", "bereit")):
        sub_dir = pipeline_dir / sub
        if not sub_dir.exists():
            continue
        for entry in sorted(sub_dir.iterdir()):
            if not entry.is_dir() or entry.name.startswith(("_", ".")):
                continue
            piece = _build_piece(entry, "instagram", kind_name)
            if not piece:
                continue
            md_path = WORKSPACE / piece["vault_path"]
            plat = _platform_of(piece, md_path)
            piece["platform"] = plat
            piece["id"] = f"{plat}-{piece['slug']}"
            out[plat][kind_name].append(piece)
            # Backwards-compat: planned ist konzept+bereit zusammen
            out[plat]["planned"].append(piece)

    # Legacy: Fallback fuer alte Folder direkt unter pipeline/ (waehrend Migration)
    if pipeline_dir.exists():
        for entry in sorted(pipeline_dir.iterdir()):
            if not entry.is_dir():
                continue
            if entry.name in ("konzept", "bereit", "ideas") or entry.name.startswith(("_", ".")):
                continue
            piece = _build_piece(entry, "instagram", "konzept")
            if not piece:
                continue
            md_path = WORKSPACE / piece["vault_path"]
            plat = _platform_of(piece, md_path)
            piece["platform"] = plat
            piece["id"] = f"{plat}-{piece['slug']}"
            out[plat]["konzept"].append(piece)
            out[plat]["planned"].append(piece)

    # Ideas: jetzt 04-areas/content/ideas/ (top-level), Fallback pipeline/ideas/
    for ideas_root in (base / "ideas", pipeline_dir / "ideas"):
        if not ideas_root.exists():
            continue
        for entry in sorted(ideas_root.iterdir()):
            if entry.suffix == ".md" and not entry.name.startswith(("_", ".")):
                piece = _build_piece(entry, "instagram", "idea")
                if piece:
                    out["ideas"].append(piece)

    # Library pro Plattform
    library_dir = base / "library"
    if library_dir.exists():
        for platform in ("instagram", "linkedin", "youtube"):
            pdir = library_dir / platform
            if not pdir.exists():
                continue
            for entry in sorted(pdir.iterdir(), reverse=True):
                if entry.name.startswith(".") or entry.name.startswith("_"):
                    continue
                # IG hat Folder-Struktur, LinkedIn/YouTube duerfen auch flache .md sein
                piece = _build_piece(entry, platform, "posted")
                if piece:
                    out[platform]["posted"].append(piece)

    # TikTok-Cross-Post-View ableiten: alle Instagram-Posts mit final.mp4.
    # Status aus Frontmatter crosspost_tiktok: 'posted' -> tiktok.posted, 'open' -> tiktok.bereit.
    for ig_post in out["instagram"]["posted"]:
        if not ig_post.get("final_mp4"):
            continue
        # Flache Kopie, damit Edits in der TikTok-View die IG-Repräsentation nicht
        # mutieren (z.B. wenn Frontend `platform` umschreibt).
        tt_piece = dict(ig_post)
        tt_piece["platform"] = "tiktok"
        tt_piece["id"] = f"tiktok-{ig_post['slug']}"
        if ig_post.get("crosspost_tiktok") == "posted":
            out["tiktok"]["posted"].append(tt_piece)
        else:
            # 'open' oder leer: noch postbar -> in 'bereit'
            out["tiktok"]["bereit"].append(tt_piece)
    # planned = bereit (TikTok hat keine Konzept-Phase, weil kein eigener Content)
    out["tiktok"]["planned"] = list(out["tiktok"]["bereit"])

    # Stats
    out["stats"] = {
        "ig_konzept": len(out["instagram"]["konzept"]),
        "ig_bereit": len(out["instagram"]["bereit"]),
        "ig_planned": len(out["instagram"]["planned"]),
        "ig_posted": len(out["instagram"]["posted"]),
        "li_konzept": len(out["linkedin"]["konzept"]),
        "li_bereit": len(out["linkedin"]["bereit"]),
        "li_planned": len(out["linkedin"]["planned"]),
        "li_posted": len(out["linkedin"]["posted"]),
        "yt_konzept": len(out["youtube"]["konzept"]),
        "yt_bereit": len(out["youtube"]["bereit"]),
        "yt_planned": len(out["youtube"]["planned"]),
        "yt_posted": len(out["youtube"]["posted"]),
        "tt_bereit": len(out["tiktok"]["bereit"]),
        "tt_posted": len(out["tiktok"]["posted"]),
        "ideas": len(out["ideas"]),
    }
    out["available"] = True
    return out


def _is_meaningful(v) -> bool:
    """True wenn das Feld nicht-leer ist. Strings: > 0 Zeichen nach strip.
    Dicts/Lists: nicht-leer."""
    if v is None:
        return False
    if isinstance(v, str):
        return bool(v.strip())
    if isinstance(v, (list, dict)):
        return bool(v)
    return True


def _hydrate_transcripts_from_cache(reels: list) -> None:
    """Letzter Fallback: wenn `transcript` im Reel leer ist, aber die Datei
    `05-reference/competitor-content/_transcripts/<shortcode>.txt` existiert,
    Inhalt laden + auf Reel-Dict setzen. Loest das Problem dass der Self-Hot-Cron
    KPIs ohne Transcript schreibt und der Dedup-Merge das Full-Run-Transcript
    nicht zuverlaessig vererbt hat."""
    tdir = WORKSPACE / "05-reference" / "competitor-content" / "_transcripts"
    if not tdir.exists():
        return
    for r in reels:
        if _is_meaningful(r.get("transcript")):
            continue
        sc = r.get("shortcode") or ""
        if not sc:
            continue
        f = tdir / f"{sc}.txt"
        if not f.exists():
            continue
        try:
            text = f.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if not text:
            continue
        r["transcript"] = text
        if not _is_meaningful(r.get("transcript_snippet")):
            r["transcript_snippet"] = text[:300] + ("…" if len(text) > 300 else "")


def load_content_intel():
    """Sprint-2-5 V3: vollumfaenglicher Content-Intelligence-Block für das Dashboard.

    Liefert:
      - mein_account: alle V3-Felder von moritz.maaker (Stats + Reels mit AI-Analyse + Comments)
      - competitors: Liste aller anderen Creators mit Stats + Reels
      - topic_clusters: aus _ai_analysis/<self>_topics.json
      - discovery: aus data/creator_discovery.json
      - meta: snapshot_date, generated_at
    """
    base = WORKSPACE / "05-reference" / "competitor-content" / "_data"
    if not base.exists():
        return {"available": False, "note": "Tracker-Daten nicht gefunden"}

    # Letzten nicht-leeren Snapshot finden
    snapshot = None
    snapshot_date = None
    for i in range(14):
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        p = base / f"{d}.json"
        if not p.exists():
            continue
        try:
            cand = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if cand.get("reels_total", 0) > 0:
            snapshot = cand
            snapshot_date = d
            break

    if not snapshot:
        return {"available": False, "note": "Kein Snapshot mit Reels in den letzten 14 Tagen"}

    self_handle = snapshot.get("self_handle") or "moritz.maaker"
    creators = snapshot.get("creators", {}) or {}
    mein = creators.get(self_handle) or {}
    competitors = {h: c for h, c in creators.items() if h != self_handle}

    # AI-Analyse pro Reel anreichern (aus _ai_analysis/ Cache)
    ai_dir = WORKSPACE / "05-reference" / "competitor-content" / "_ai_analysis"

    # Library-Folder pro Shortcode cachen (fuer final.mp4-Lookup)
    lib_ig = WORKSPACE / "04-areas" / "content" / "library" / "instagram"
    shortcode_to_final = {}
    if lib_ig.exists():
        for fol in lib_ig.iterdir():
            if not fol.is_dir():
                continue
            mp4 = fol / "final.mp4"
            if not mp4.exists():
                continue
            # Bevorzugt: shortcode aus script.md oder meta.md (Frontmatter ist Quelle der Wahrheit)
            sc = ""
            for fname in ("script.md", "meta.md"):
                p = fol / fname
                if not p.exists():
                    continue
                try:
                    m = re.search(r"^shortcode:\s*(\S+)", p.read_text(encoding="utf-8"), re.MULTILINE)
                    if m and m.group(1) not in ("~", "null", ""):
                        sc = m.group(1).strip().strip('"')
                        break
                except OSError:
                    continue
            # Fallback: Folder-Name endet auf _<shortcode> (mind. 6 alphanumeric)
            if not sc:
                m2 = re.search(r"_([A-Za-z0-9_-]{7,})$", fol.name)
                if m2:
                    sc = m2.group(1)
            if sc:
                shortcode_to_final[sc] = str(mp4.relative_to(WORKSPACE))

    def _enrich_reels(reels):
        for r in reels:
            sc = r.get("shortcode") or ""
            if not sc:
                continue
            std = ai_dir / f"{sc}_standard.json"
            deep = ai_dir / f"{sc}_deep.json"
            if std.exists():
                try:
                    r["ai_standard"] = json.loads(std.read_text(encoding="utf-8"))
                except Exception:
                    pass
            if deep.exists():
                try:
                    r["ai_deep"] = json.loads(deep.read_text(encoding="utf-8"))
                except Exception:
                    pass
            # final.mp4-Pfad im Vault (fuer Inline-Video im Reel-Dialog)
            if sc in shortcode_to_final:
                r["final_mp4"] = shortcode_to_final[sc]
        return reels

    if mein and mein.get("reels"):
        mein["reels"] = _enrich_reels(mein["reels"])

    for h, c in competitors.items():
        if c.get("reels"):
            c["reels"] = _enrich_reels(c["reels"])

    # all_self_reels: aggregiert über alle 60 Tage Snapshots, dedupliziert per shortcode.
    # Merge-Logik: nimm das Reel mit den hoechsten Views als Basis (KPIs sind frischer),
    # ABER preserve transcript/summary/comments/AI aus aelteren Snapshots wenn die
    # frischere Version diese Felder leer hat. Hintergrund: der Self-Hot-Cron (stuendlich)
    # zieht KPIs ohne Transcript/Summary, der 06:00-Full-Run schreibt beides. Ohne dieses
    # Merge wuerden die Self-Hot-Snapshots die Full-Run-Transkripte ueberschreiben.
    _PRESERVE_FIELDS = (
        "transcript", "transcript_snippet", "summary",
        "comments_stats", "ai_standard", "ai_deep",
    )
    all_self_reels_map = {}
    for i in range(60):
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        p = base / f"{d}.json"
        if not p.exists():
            continue
        try:
            snap = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        own = (snap.get("creators", {}) or {}).get(self_handle) or {}
        for r in (own.get("reels") or []):
            sc = r.get("shortcode")
            if not sc:
                continue
            existing = all_self_reels_map.get(sc)
            if not existing:
                all_self_reels_map[sc] = dict(r)
                continue
            r_views = r.get("views", 0) or 0
            e_views = existing.get("views", 0) or 0
            if r_views > e_views:
                merged = dict(r)
                # Wertvolle Felder aus altem behalten, wenn neuer leer ist
                for key in _PRESERVE_FIELDS:
                    new_val = merged.get(key)
                    old_val = existing.get(key)
                    if not _is_meaningful(new_val) and _is_meaningful(old_val):
                        merged[key] = old_val
                all_self_reels_map[sc] = merged
            else:
                # Existing bleibt Basis — aber falls neuer Snapshot ein Feld hat das
                # im existing fehlt (z.B. Transcript wurde nachgezogen), uebernehmen.
                for key in _PRESERVE_FIELDS:
                    if not _is_meaningful(existing.get(key)) and _is_meaningful(r.get(key)):
                        existing[key] = r[key]
    all_self_reels = list(all_self_reels_map.values())
    # Letzter Fallback: Transcript-Cache-Datei laden falls vorhanden
    _hydrate_transcripts_from_cache(all_self_reels)
    # Anreichern mit AI-Analyse aus Cache
    all_self_reels = _enrich_reels(all_self_reels)
    # Sort: neueste zuerst
    def _posted_key(r):
        p = r.get("posted_at") or r.get("posted") or ""
        return p
    all_self_reels.sort(key=_posted_key, reverse=True)

    # KPI-Aggregate pro Zeitraum (today / 7d / 30d / all).
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_dt = datetime.now().date()

    def _in_range(reel, days):
        p = (reel.get("posted") or "")[:10]
        if not p:
            return False
        try:
            posted = datetime.strptime(p, "%Y-%m-%d").date()
        except Exception:
            return False
        if days is None:
            return True
        return (today_dt - posted).days <= days

    def _agg(reels):
        n = len(reels)
        if n == 0:
            return {
                "count": 0, "total_views": 0, "total_likes": 0, "total_comments": 0,
                "avg_views": 0, "avg_likes": 0, "avg_comments": 0,
                "avg_engagement_rate": 0.0, "avg_comment_rate": 0.0,
                "best_reel_shortcode": None, "best_reel_er": 0.0,
                "best_comment_rate": 0.0,
            }
        views = [r.get("views", 0) or 0 for r in reels]
        likes = [r.get("likes", 0) or 0 for r in reels]
        comments = [r.get("comments", 0) or 0 for r in reels]
        ers = [r.get("engagement_rate", 0.0) or 0.0 for r in reels]
        # Comment-Rate = comments/views * 100 pro Reel; manche Snapshots haben das
        # Feld bereits (V3), bei alten faellt es auf Berechnung zurück.
        comment_rates = [
            (r.get("comment_rate") if r.get("comment_rate") is not None
             else (((r.get("comments") or 0) / (r.get("views") or 1)) * 100 if r.get("views") else 0.0))
            for r in reels
        ]
        best = max(reels, key=lambda r: r.get("engagement_rate", 0.0) or 0.0)
        return {
            "count": n,
            "total_views": sum(views),
            "total_likes": sum(likes),
            "total_comments": sum(comments),
            "avg_views": round(sum(views) / n),
            "avg_likes": round(sum(likes) / n),
            "avg_comments": round(sum(comments) / n),
            "avg_engagement_rate": round(sum(ers) / n, 2),
            "avg_comment_rate": round(sum(comment_rates) / n, 2),
            "best_reel_shortcode": best.get("shortcode"),
            "best_reel_er": round(best.get("engagement_rate", 0.0) or 0.0, 2),
            "best_comment_rate": round(max(comment_rates), 2),
        }

    # range_kpis: zwei verschiedene Sichten kombiniert:
    #   - "today": Reels die HEUTE gepostet wurden (Aktivitäts-Sicht, klein)
    #   - "all":   absolute Summe aller akkumulierten Views/Likes/Comments
    #              über ALLE Reels (Total-Reach-Sicht)
    #   - "7d", "30d": View-Deltas aus reel_history.db
    #                  ("neue Views in den letzten 7/30 Tagen über alle Reels")
    #                  Das ist die korrekte Reach-pro-Zeitfenster-Zahl, die mit
    #                  Instagram-Insights vergleichbar ist.
    range_kpis = {
        "today": _agg([r for r in all_self_reels if (r.get("posted") or "")[:10] == today_str]),
        "7d": _agg([r for r in all_self_reels if _in_range(r, 7)]),
        "30d": _agg([r for r in all_self_reels if _in_range(r, 30)]),
        "all": _agg(all_self_reels),
    }
    # View-Deltas aus History-DB als zusätzliche Felder. Verändert die alte
    # Form NICHT (Backwards-Compat fürs Frontend), sondern erweitert sie.
    try:
        sys.path.insert(0, str(WORKSPACE / "scripts"))
        from reel_history import all_reels_delta as _rh_delta  # type: ignore
        for window_key, days in (("7d", 7), ("30d", 30)):
            d = _rh_delta(self_handle, days, today=today_str)
            range_kpis[window_key]["views_delta_total"] = d["views_delta"]
            range_kpis[window_key]["likes_delta_total"] = d["likes_delta"]
            range_kpis[window_key]["comments_delta_total"] = d["comments_delta"]
            range_kpis[window_key]["reels_tracked"] = d["count_reels"]
            range_kpis[window_key]["window_start"] = d["window_start"]
        # History-Coverage als eigenes Top-Level-Feld: ermöglicht UI-Hinweis
        # "Daten erst seit X" bevor genug Snapshots da sind.
        from reel_history import stats as _rh_stats  # type: ignore
        range_kpis["history_first_snapshot"] = _rh_stats().get("first_snapshot")
    except Exception as e:
        print(f"WARNING: reel_history-Deltas nicht verfuegbar: {e}", file=sys.stderr)

    # Topic-Cluster für eigenen Account
    cluster_path = ai_dir / f"{self_handle}_topics.json"
    topic_clusters = None
    if cluster_path.exists():
        try:
            topic_clusters = json.loads(cluster_path.read_text(encoding="utf-8"))
        except Exception:
            topic_clusters = None

    # Discovery
    discovery_path = WORKSPACE / "data" / "creator_discovery.json"
    discovery = None
    if discovery_path.exists():
        try:
            discovery = json.loads(discovery_path.read_text(encoding="utf-8"))
        except Exception:
            discovery = None

    # Top-10-overall direkt aus Snapshot, plus AI-Anreicherung
    top10 = snapshot.get("top10_overall", []) or []
    top10 = _enrich_reels(top10)

    # Unified Markt-View: Tracked + Discovered, sortiert nach similarity_score.
    # Tracked = Score 100 ("Manuell getrackt"), Discovered nutzt Sonnet-Score (>=40).
    market_creators = _build_market_creators(competitors, discovery)
    # Cross-cutting Top-Reels-Feed quer durch den ganzen Markt.
    market_top_reels = _build_market_top_reels(market_creators)

    # Markt-Analyse via Sonnet, gecacht 24h in data/market_analysis.json
    market_analysis = None
    try:
        sys.path.insert(0, str(WORKSPACE / "scripts"))
        import market_analysis as _ma  # type: ignore
        market_analysis = _ma.generate(market_creators)
    except Exception as e:
        print(f"WARNING: market_analysis konnte nicht geladen werden: {e}", file=sys.stderr)

    return {
        "available": True,
        "snapshot_date": snapshot_date,
        "self_handle": self_handle,
        "mein_account": mein,
        "all_self_reels": all_self_reels,
        "range_kpis": range_kpis,
        "competitors": competitors,
        "competitor_handles": sorted(competitors.keys()),
        "topic_clusters": topic_clusters,
        "discovery": discovery,
        "market_creators": market_creators,
        "market_top_reels": market_top_reels,
        "market_analysis": market_analysis,
        "top10_overall": top10,
        "totals": {
            "creators": len(creators),
            "reels_total": snapshot.get("reels_total", 0),
            "errors": snapshot.get("errors", 0),
        },
    }


def _build_market_creators(competitors: dict, discovery: dict | None) -> list:
    """Merged getrackte Konkurrenz und discovered Creators in einen einheitlichen
    Markt-View. Tracked-Creators bekommen similarity_score 100, Discovered haben
    bereits >=40 (Hard-Filter in discover_creators.py).

    Sortierung: similarity_score desc, dann avg_engagement_rate desc.
    Pro Eintrag: handle, source, similarity_score, similarity_reason, KPIs, top_reels[3].
    """
    out = []

    def _normalize_tracked_reel(r):
        ai_std = r.get("ai_standard") or {}
        ai_dp = r.get("ai_deep") or {}
        return {
            "shortcode": r.get("shortcode") or "",
            "url": r.get("url") or "",
            "posted": r.get("posted") or r.get("posted_at") or "",
            "views": r.get("views") or 0,
            "likes": r.get("likes") or 0,
            "comments": r.get("comments") or 0,
            "engagement_rate": round(r.get("engagement_rate") or 0, 2),
            "caption_snippet": (r.get("caption_snippet") or r.get("caption_full") or "")[:240],
            "summary": (r.get("summary") or "")[:400],
            "transcript_snippet": (r.get("transcript_snippet") or r.get("transcript") or "")[:300],
            "topic_tag": ai_std.get("topic_tag") or "",
            "hook_type": ai_std.get("hook_type") or "",
            "hook_score": ai_std.get("hook_score"),
            "sentiment": ai_std.get("sentiment") or "",
            "key_observation": (ai_std.get("key_observations") or [""])[0],
            "why_it_worked": (ai_dp.get("why_it_worked") or "")[:400],
        }

    # Tracked Konkurrenz
    for handle, c in (competitors or {}).items():
        reels = c.get("reels") or []
        top3 = sorted(reels, key=lambda r: r.get("engagement_rate", 0) or 0, reverse=True)[:3]
        # Sprache aus erster Reel-Caption schaetzen, oder unknown
        lang = "unknown"
        for r in reels:
            cap = (r.get("caption_full") or r.get("caption_snippet") or "").lower()
            if any(w in cap for w in (" und ", " der ", " ist ", " ich ", " nicht ")):
                lang = "de"
                break
            if any(w in cap for w in (" the ", " and ", " is ", " you ", " your ")):
                lang = "en"
                break
        out.append({
            "handle": handle,
            "source": "tracked",
            "similarity_score": 100,
            "similarity_reason": "Manuell getrackt",
            "avg_views": c.get("avg_views"),
            "avg_engagement_rate": c.get("avg_engagement_rate"),
            "reels_count": c.get("reels_count"),
            "language": lang,
            "top_reels": [_normalize_tracked_reel(r) for r in top3],
        })

    # Discovered: zusaetzlicher Defensiv-Filter auf similarity >= 40, damit alte
    # Discovery-Snapshots (vor Hard-Filter-Einfuehrung) nicht den Markt verwaessern.
    candidates = ((discovery or {}).get("candidates") or [])
    for cand in candidates:
        sim = cand.get("similarity_score", 0) or 0
        if sim < 40:
            continue
        out.append({
            "handle": cand.get("handle"),
            "source": "discovered",
            "similarity_score": sim,
            "similarity_reason": cand.get("similarity_reason") or cand.get("ai_reason") or "",
            "avg_views": cand.get("avg_views"),
            "avg_engagement_rate": cand.get("avg_engagement_rate"),
            "language": cand.get("language") or "unknown",
            "top_reels": cand.get("top_reels") or [],
            "final_score": cand.get("final_score"),
        })

    out.sort(
        key=lambda x: (
            x.get("similarity_score") or 0,
            x.get("avg_engagement_rate") or 0,
        ),
        reverse=True,
    )
    return out


def _build_market_top_reels(market_creators: list, limit: int = 24) -> list:
    """Flacher Feed der besten Reels quer durch den ganzen Markt.

    Sortiert nach engagement_rate desc. Pro Eintrag: handle, source,
    similarity_score, plus alle relevanten Reel-Felder. Damit kann das
    Dashboard 'Was geht gerade ab' zeigen, ohne erst den Creator zu oeffnen.
    """
    feed = []
    for c in market_creators or []:
        handle = c.get("handle")
        src = c.get("source")
        sim = c.get("similarity_score") or 0
        for r in (c.get("top_reels") or []):
            if not r.get("url"):
                continue
            feed.append({
                "handle": handle,
                "source": src,
                "similarity_score": sim,
                "url": r.get("url"),
                "shortcode": r.get("shortcode") or "",
                "views": r.get("views") or 0,
                "likes": r.get("likes") or 0,
                "comments": r.get("comments") or 0,
                "engagement_rate": round(r.get("engagement_rate") or 0, 2),
                # posted-Datum mitführen, damit das Frontend "letzte 7 Tage"
                # filtern kann (Trend-Hooks-Feed in Phase 5).
                "posted": r.get("posted") or r.get("posted_at") or "",
                "caption_snippet": (r.get("caption_snippet") or "")[:240],
                "topic_tag": r.get("topic_tag") or "",
                "hook_type": r.get("hook_type") or "",
                "hook_score": r.get("hook_score"),
                "summary": (r.get("summary") or "")[:300],
                "why_it_worked": (r.get("why_it_worked") or "")[:300],
            })
    feed.sort(key=lambda r: r.get("engagement_rate") or 0, reverse=True)
    return feed[:limit]


def load_self_tracker_summary():
    """Aggregat über Moritz' eigenes Profil für den dashboard.content.instagram-Block.

    Liefert avg_reach, avg_engagement etc. aus dem Tracker (statt Mock-Daten).
    """
    metrics = load_self_tracker_metrics()
    if not metrics:
        return None
    stats = metrics.get("stats", {})
    return {
        "posts_tracked": len(metrics.get("posts", [])),
        "avg_views": int(stats.get("avg_views", 0)),
        "avg_likes": int(stats.get("avg_likes", 0)),
        "avg_comments": int(stats.get("avg_comments", 0)),
        "avg_engagement": stats.get("engagement_rate", 0),
        "source": metrics.get("_source", ""),
    }


def _parse_de_number(s: str):
    """Parst Zahlen aus den meta.md KPI-Tabellen.

    Konventionen in den Tabellen:
    - Counts (z.B. '9.071') → Punkt als Tausender-Trenner
    - Rates ('49.1 %', '1.46 %') und Sekunden ('38.7 s') → Punkt als Dezimaltrenner
    - Deutsches Komma-Format (z.B. '9.071,5') wenn Komma drin
    """
    s = s.strip().replace("**", "")
    if not s:
        return None
    has_pct = "%" in s
    has_unit = bool(re.search(r"\b[a-zA-Z]\b", s))  # 's' für Sekunden etc.
    s = s.replace("%", "").strip()
    s = re.sub(r"\s*[a-zA-Z]+\s*$", "", s).strip()  # Einheiten am Ende strippen
    if not s:
        return None
    if "," in s:
        # Deutsches Format: '.' = Tausender, ',' = Dezimal
        s = s.replace(".", "").replace(",", ".")
    elif has_pct or has_unit:
        # Englisches Format mit Dezimal-Punkt · nichts ändern
        pass
    else:
        # Reine Ganzzahl mit Tausender-Punkt
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


def _parse_meta_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    block = text[3:end].strip()
    out = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        k = k.strip()
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1].strip()
            items = []
            for part in inner.split(","):
                part = part.strip().strip('"').strip("'")
                if part:
                    items.append(part)
            out[k] = items
        elif v in ("~", "null", ""):
            out[k] = None
        else:
            v = v.strip('"').strip("'")
            try:
                if "." in v:
                    out[k] = float(v)
                else:
                    out[k] = int(v)
            except ValueError:
                out[k] = v
    return out


_KPI_LABEL_MAP = {
    "Views": "views",
    "Plays": "plays",
    "Viewed (unique)": "viewed_unique",
    "Bounce-Rate": "bounce_rate",
    "Likes": "likes",
    "Kommentare": "comments",
    "Engagement-Rate": "engagement_rate",
    "Like-Rate": "like_rate",
    "Comment-Rate": "comment_rate",
    "Comment-to-Like-Ratio": "comment_to_like_ratio",
    "Video-Dauer": "video_duration_s",
}


def _parse_kpi_table(text: str) -> dict:
    out = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 2:
            continue
        label, value = cells
        if label not in _KPI_LABEL_MAP:
            continue
        n = _parse_de_number(value)
        if n is None:
            continue
        out[_KPI_LABEL_MAP[label]] = n
    return out


def _parse_h1(text: str):
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def load_content_ops() -> dict:
    """Content-Operations-Cockpit-Daten: Recent + Top + Trend für Moritz' eigene Reels.

    Quellen:
    - 04-areas/content/library/instagram/<date>_<slug>/meta.md (Frontmatter + Live-KPI-Tabelle)
    - 05-reference/competitor-content/_data/<date>.json (für 30-Tage-Trend-Aggregate)
    """
    library = WORKSPACE / "04-areas" / "content" / "library" / "instagram"
    snapshots = WORKSPACE / "05-reference" / "competitor-content" / "_data"

    reels = []
    if library.exists():
        for folder in sorted(library.iterdir()):
            if not folder.is_dir():
                continue
            meta = folder / "meta.md"
            if not meta.exists():
                continue
            try:
                text = meta.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            fm = _parse_meta_frontmatter(text)
            kpis = _parse_kpi_table(text)
            title = _parse_h1(text) or folder.name
            if title.startswith("Reel: "):
                title = title[6:]
            reels.append({
                "shortcode": fm.get("shortcode") or "",
                "posted": fm.get("posted") or "",
                "url": fm.get("url") or "",
                "hashtags": fm.get("hashtags") or [],
                "video_duration_s": fm.get("video_duration_s") or kpis.get("video_duration_s") or 0,
                "title": title[:120],
                "folder": folder.name,
                "views": int(kpis.get("views") or 0),
                "plays": int(kpis.get("plays") or 0),
                "likes": int(kpis.get("likes") or 0),
                "comments": int(kpis.get("comments") or 0),
                "engagement_rate": kpis.get("engagement_rate") or 0,
                "bounce_rate": kpis.get("bounce_rate") or 0,
                "like_rate": kpis.get("like_rate") or 0,
                "comment_rate": kpis.get("comment_rate") or 0,
            })

    today = datetime.now().date()
    cutoff_14 = today - timedelta(days=14)

    def _date(r):
        try:
            return datetime.strptime(r.get("posted", ""), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    recent = sorted(
        [r for r in reels if (d := _date(r)) and d >= cutoff_14],
        key=lambda r: _date(r) or today, reverse=True,
    )

    top = sorted(reels, key=lambda r: r.get("views", 0), reverse=True)[:10]

    trend = []
    if snapshots.exists():
        snap_files = sorted(snapshots.glob("*.json"))[-30:]
        for snap_path in snap_files:
            try:
                snap = json.loads(snap_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            own = snap.get("creators", {}).get("moritz.maaker", {})
            if not own or not own.get("reels_count"):
                continue
            trend.append({
                "date": snap.get("date") or snap_path.stem,
                "total_views": int(own.get("total_views") or 0),
                "total_likes": int(own.get("total_likes") or 0),
                "total_comments": int(own.get("total_comments") or 0),
                "avg_engagement_rate": own.get("avg_engagement_rate") or 0,
                "reels_count": int(own.get("reels_count") or 0),
            })

    avg_views_recent = (sum(r["views"] for r in recent) / len(recent)) if recent else 0
    avg_eng_recent = (sum(r["engagement_rate"] for r in recent) / len(recent)) if recent else 0
    best_recent = max(recent, key=lambda r: r["views"], default=None)

    return {
        "updated_at": datetime.now().isoformat(),
        "library_total": len(reels),
        "summary": {
            "posts_14d": len(recent),
            "avg_views_14d": round(avg_views_recent),
            "avg_engagement_14d": round(avg_eng_recent, 2),
            "best_recent_views": best_recent["views"] if best_recent else 0,
            "best_recent_shortcode": best_recent["shortcode"] if best_recent else "",
        },
        "my_reels_recent": recent,
        "my_top_performers": top,
        "performance_trend": trend,
    }


def load_api_status() -> dict:
    """Prüft welche API Keys in .env gesetzt sind."""
    keys = [
        "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY",
        "TELEGRAM_BOT_TOKEN", "YOUTUBE_API_KEY", "ELEVENLABS_API_KEY",
        "FIREFLIES_API_KEY", "FIRECRAWL_API_KEY", "SUPADATA_API_KEY",
    ]
    status = {}
    for k in keys:
        v = os.environ.get(k, "")
        status[k] = {
            "set": bool(v) and v not in ("", "your_key_here", "..."),
            "preview": (v[:8] + "...") if v else "",
        }
    # Google OAuth extra
    status["GOOGLE_OAUTH"] = {
        "set": (WORKSPACE / "config" / "google_token.json").exists(),
        "preview": "token.json" if (WORKSPACE / "config" / "google_token.json").exists() else "fehlt",
    }
    return status


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"Generating dashboard data for {TODAY}...")

    run_sibling_collectors()

    conn = get_db(DB_PATH)

    today_note = read_daily_note(TODAY)
    if not today_note:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        today_note = read_daily_note(yesterday)

    weather = load_weather()

    # Schedule: DB-Events first (echte Kalender-Daten), Daily-Note als Fallback
    cal_events = load_schedule_from_calendar_db(conn, TODAY)
    note_events = load_schedule_from_daily_note(today_note)
    if cal_events:
        schedule = cal_events
        print(f"  Calendar: {len(cal_events)} events from Google Calendar DB (today)")
    else:
        schedule = note_events
        print(f"  Calendar: {len(note_events)} events from Daily Note (no DB events)")

    # 30-Tage-Window für Dashboard-Day-Tabs
    schedule_by_date = load_schedule_by_date(conn, TODAY, days=30)
    total_upcoming = sum(len(v) for v in schedule_by_date.values())
    days_with_events = sum(1 for v in schedule_by_date.values() if v)
    print(f"  Calendar: {total_upcoming} upcoming events über {days_with_events} Tage (30-Tage-Window)")
    # Falls die DB leer ist, mindestens heute mit Daily-Note-Events befuellen
    if not any(schedule_by_date.values()) and note_events:
        schedule_by_date[TODAY] = note_events

    todos = load_todos_multi_day(TODAY, lookback_days=7)
    open_count = sum(1 for t in todos.get("Moritz", []) if not t.get("done"))
    print(f"  Todos: {open_count} offen (Moritz, Multi-Day-Lookup über 7 Tage)")
    yt_metrics, yt_videos, yt_views_7d = load_youtube_metrics(conn)
    whatsapp = load_whatsapp()
    finance = load_finance()
    brief = load_brief()
    contacts = load_contacts()
    news = load_news_from_research()
    projects = load_projects()
    sales_pipeline = load_json("data/sales_pipeline.json") or {"leads": [], "stats": {}}
    content_metrics = load_self_tracker_metrics() or {"posts": [], "stats": {}}
    instagram_summary = load_self_tracker_summary()
    content_intel = load_content_intel()
    content_planning = load_content_planning()
    tiktok_intel = load_tiktok_intel()
    marketing_scorecard = load_marketing_scorecard()
    system_health = load_json("data/system_health.json") or {"overall": "unknown", "jobs": [], "summary": {}}
    knowledge_library = load_json("data/knowledge_library.json") or {"tiles": [], "total_files": 0}
    knowledge_hub = load_json("data/knowledge_hub.json") or {"top_news": [], "topics": []}
    content_ops = load_content_ops()
    api_status = load_api_status()

    labels = []
    for i in range(6, -1, -1):
        d = datetime.now() - timedelta(days=i)
        labels.append(WEEKDAYS_DE[d.weekday()][:2])

    data = {
        "generated_at": datetime.now().isoformat(),
        "user": "Moritz",
        "date": TODAY,
        "weekday": WEEKDAYS_DE[datetime.now().weekday()],
        "gemini_api_key": os.environ.get("GEMINI_API_KEY", ""),
        "weather": weather,
        "schedule": schedule,
        "schedule_by_date": schedule_by_date,
        "todos": todos,
        "metrics": {
            "yt_subs": yt_metrics["yt_subs"],
            "yt_views_week": yt_metrics["yt_views_week"],
            "ig_followers": 13,  # Platzhalter bis Instagram API angebunden
            "customers": 7,
            "revenue_mtd": finance["revenue_mtd"],
        },
        "charts": {
            "yt_views_7d": yt_views_7d if len(yt_views_7d) == 7 else [0] * 7,
            "ig_followers_7d": [13] * 7,
            "yt_labels": labels,
        },
        "whatsapp": whatsapp,
        "finance": finance,
        "content": {
            "youtube": {
                "total_subs": yt_metrics["yt_subs"],
                "total_views": yt_metrics["yt_views_week"],
                "total_videos": len(yt_videos),
                "recent_videos": yt_videos,
            },
            "instagram": instagram_summary or {
                "note": "Tracker-Snapshot der letzten 7 Tage nicht gefunden",
            },
        },
        "health": {
            # Alles Platzhalter bis Apple Health / WHOOP Integration steht
            "available": False,
            "note": "Apple Health Integration noch nicht angebunden",
            "metrics": {},
        },
        "news": news,
        "projects": projects,
        "sales_pipeline": sales_pipeline,
        "content_metrics": content_metrics,
        "content_intel": content_intel,
        "content_planning": content_planning,
        "tiktok_intel": tiktok_intel,
        "marketing_scorecard": marketing_scorecard,
        "system_health": system_health,
        "knowledge_library": knowledge_library,
        "knowledge_hub": knowledge_hub,
        "content_ops": content_ops,
        "brief": brief,
        "contacts": contacts,
        "api_status": api_status,
    }

    if conn:
        conn.close()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Dashboard data saved to {OUTPUT_PATH}")
    print(f"  Schedule: {len(schedule)} Blöcke aus Daily Note")
    print(f"  Todos: {sum(len(v) for v in todos.values())} total (Moritz: {len(todos['Moritz'])})")
    print(f"  YouTube: {yt_metrics['yt_subs']} subs, {len(yt_videos)} videos")
    print(f"  WhatsApp: {whatsapp['stats']['total_chats']} chats ({whatsapp['stats']['clients']} Kunden)")
    print(f"  Finance: {finance['revenue_mtd']}€ MTD, {len(finance['monthly_history'])} Monate Historie")
    print(f"  News: {len(news)} aus Daily Research")
    print(f"  Projects: {len(projects)} aus 03-projects/")
    print(f"  Pipeline: {len(sales_pipeline.get('leads', []))} Leads, "
          f"{sales_pipeline.get('stats', {}).get('pipeline_value', 0)}€ total")
    print(f"  Content: {len(content_metrics.get('posts', []))} Posts, "
          f"{content_metrics.get('stats', {}).get('total_views_7d', 0):,} Views 7d")
    print(f"  Health: {system_health.get('overall', '?')} · "
          f"{system_health.get('summary', {}).get('running', 0)} Jobs aktiv")
    print(f"  Contacts: {len(contacts)}")
    print(f"  Content-Ops: library={content_ops['library_total']}, "
          f"recent14d={content_ops['summary']['posts_14d']}, "
          f"trend-points={len(content_ops['performance_trend'])}")


if __name__ == "__main__":
    main()
