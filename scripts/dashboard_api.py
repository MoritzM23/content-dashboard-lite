#!/usr/bin/env python3
"""
Dashboard-API (Sprint 4): Mini-HTTP-Server für Creator-Manager und Discovery-Trigger.

Laeuft auf Port 8093 parallel zum statischen Dashboard auf 8090.
Stellt CRUD-Endpoints für die getrackten Creator bereit, plus Trigger
für Tracker und Discovery-Run.

Endpoints:
  GET  /creators                          -> Liste aller getrackten Creator
  POST /creators {handle:"x"}             -> Handle hinzufügen
  DELETE /creators/{handle}               -> Handle entfernen
  POST /tracker/run                       -> Tracker einmal manuell triggern
  GET  /discovery                         -> letzten creator_discovery.json
  POST /discovery/refresh                 -> Discovery einmal manuell triggern

  GET    /calendar/event?account=&calendarId=&eventId=  -> Event-Details live von Google
  POST   /calendar/event                                 -> Neuen Termin anlegen
  PATCH  /calendar/event                                 -> Termin ändern
  DELETE /calendar/event?account=&calendarId=&eventId=  -> Termin löschen

CORS: erlaubt 127.0.0.1/localhost auf allen Ports (Dashboard 8090 + Next.js 3000).
"""

import json
import logging
import re
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import yaml

WORKSPACE = Path(os.environ.get("WORKSPACE_PATH", str(Path(__file__).resolve().parent.parent)))
CONFIG_PATH = WORKSPACE / "scripts" / "instagram_tracker_config.yaml"
DISCOVERY_PATH = WORKSPACE / "data" / "creator_discovery.json"
LOG_PATH = Path.home() / "Library" / "Logs" / "aios" / "dashboard-api.log"
PYTHON_BIN = "python33"

ALLOWED_ORIGINS = {
    "http://127.0.0.1:8090",
    "http://localhost:8090",
    "null",  # file:// origin für lokale Tests
}

HANDLE_RE = re.compile(r"^[a-zA-Z0-9._]{1,30}$")

# Felder, die als Frontmatter-YAML serialisiert werden. Alles andere wird ignoriert.
PLANNING_FRONTMATTER_FIELDS = (
    "platform",
    "status",
    "hook",
    "trigger-word",
    "serie",
    "reel-nummer",
    "hashtags",
    "caption",
    "voice-status",
    "post_url",
    "shortcode",
    "posted_at",
    "created",
)


def _safe_pipeline_path(rel_path: str) -> Path:
    """Validiert, dass rel_path innerhalb 04-areas/content/ und .md ist."""
    if not rel_path or ".." in rel_path.split("/"):
        raise ValueError("ungueltiger Pfad")
    if not rel_path.startswith("04-areas/content/"):
        raise ValueError("Pfad muss in 04-areas/content/ liegen")
    if not rel_path.endswith(".md"):
        raise ValueError("nur .md Files")
    abs_path = (WORKSPACE / rel_path).resolve()
    # Path-Traversal-Schutz: muss unter WORKSPACE liegen
    try:
        abs_path.relative_to(WORKSPACE.resolve())
    except ValueError:
        raise ValueError("Pfad ausserhalb Workspace")
    return abs_path


def _parse_md(text: str):
    """Returnt (frontmatter_dict, body_str). Idempotent."""
    fm = {}
    body = text
    if text.startswith("---"):
        try:
            end = text.index("\n---", 3)
            fm_raw = text[3:end].strip()
            body = text[end + 4:].lstrip("\n")
            fm = yaml.safe_load(fm_raw) or {}
        except Exception:
            fm = {}
            body = text
    return fm, body


def _serialize_md(frontmatter: dict, body: str) -> str:
    """Markdown mit YAML-Frontmatter neu bauen."""
    # Sortierte, deterministische Frontmatter-Keys (in der gewuenschten Reihenfolge)
    ordered = {}
    for key in PLANNING_FRONTMATTER_FIELDS:
        if key in frontmatter and frontmatter[key] not in ("", None):
            ordered[key] = frontmatter[key]
    # Restliche Felder, die der User vielleicht behalten will (z.B. voice-Block, custom)
    for key, val in frontmatter.items():
        if key not in ordered and val not in ("", None):
            ordered[key] = val
    fm_yaml = yaml.safe_dump(
        ordered,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    ).strip()
    return f"---\n{fm_yaml}\n---\n\n{body.lstrip()}"


def _sync_tiktok_folder(ig_folder: Path, status: str, fm_body: str):
    """Haelt library/tiktok/{gepostet,postbar}/<slug>/ synchron.

    status=posted -> Ordner liegt unter gepostet/
    status=open   -> Ordner liegt unter postbar/
    Das Video wird gehardlinkt (gleiche Datei, kein Extra-Speicher).
    """
    import os
    slug = ig_folder.name
    tt_root = WORKSPACE / "04-areas" / "content" / "library" / "tiktok"
    kind = "gepostet" if status == "posted" else "postbar"
    other = "postbar" if status == "posted" else "gepostet"
    target = tt_root / kind / slug
    old = tt_root / other / slug

    # Falls der Ordner im anderen Bucket liegt: rausraeumen
    if old.exists():
        try:
            for f in old.iterdir():
                f.unlink()
            old.rmdir()
        except OSError as e:
            logging.warning(f"tiktok-folder cleanup fehlgeschlagen: {e}")

    target.mkdir(parents=True, exist_ok=True)
    ig_mp4 = ig_folder / "final.mp4"
    tt_mp4 = target / "final.mp4"
    if ig_mp4.exists() and not tt_mp4.exists():
        try:
            os.link(ig_mp4, tt_mp4)  # Hardlink, kein Speicher-Duplikat
        except OSError as e:
            logging.warning(f"tiktok hardlink fehlgeschlagen: {e}")

    hook = ""
    posted = slug[:10]
    for line in fm_body.split("\n"):
        hm = re.match(r'^hook:\s*"?([^"\n]*)"?', line)
        if hm:
            hook = hm.group(1).strip()
        pm = re.match(r"^posted(?:_at)?:\s*(\S+)", line)
        if pm and pm.group(1) not in ("~", "null"):
            posted = pm.group(1)

    posted_line = f"posted_at: {posted}" if kind == "gepostet" else "posted_at: ~"
    meta = (
        "---\n"
        "type: tiktok-post\n"
        "platform: tiktok\n"
        f"crosspost_status: {kind}\n"
        f"source_instagram: {slug}\n"
        f'hook: "{hook}"\n'
        f"{posted_line}\n"
        "tiktok_url: ~\n"
        "video: final.mp4\n"
        "---\n\n"
        f"# TikTok: {hook or slug}\n\n"
        f"Cross-Post von Instagram-Reel `{slug}`.\n\n"
        f"- **Video:** `final.mp4` (Hardlink auf `library/instagram/{slug}/final.mp4`)\n"
        f"- **Status:** {'auf TikTok gepostet' if kind == 'gepostet' else 'noch postbar'}\n\n"
        "## Notizen\n\n"
        "_Manueller Eintrag — TikTok-Caption, Hashtags, Performance._\n"
    )
    (target / "meta.md").write_text(meta, encoding="utf-8")


def _trigger_dashboard_refresh():
    """Generate-Dashboard-Script asynchron triggern."""
    try:
        subprocess.Popen(
            [PYTHON_BIN, str(WORKSPACE / "scripts" / "generate_dashboard_data.py")],
            cwd=str(WORKSPACE),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception as e:
        logging.warning(f"Dashboard-Refresh-Trigger fehlgeschlagen: {e}")


def _setup_logging():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
    )


def _load_config():
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def _save_config(config):
    """YAML schreiben mit Erhalt der lesbaren Formatierung. Inline-Kommentare gehen verloren,
    daher loggen wir die Änderung und behalten die Datei via re-write so kompakt wie möglich.
    """
    CONFIG_PATH.write_text(
        yaml.safe_dump(config, sort_keys=False, allow_unicode=True, default_flow_style=False),
        encoding="utf-8",
    )


# ── Google Calendar Helper ──────────────────────────────────────────────────

def _calendar_service(account: str):
    """Calendar-Service-Wrapper. Importiert lazy, sodass dashboard_api
    auch laeuft wenn google_auth nicht eingerichtet ist."""
    sys.path.insert(0, str(WORKSPACE / "scripts"))
    from google_auth import get_calendar_service  # type: ignore
    return get_calendar_service(account=account or "primary", interactive=False)


def _serialize_event(ev: dict, account: str, calendar_id: str) -> dict:
    """Rohes Google-Calendar-Event in unser CalendarEventDetail-Format konvertieren."""
    start = ev.get("start", {}) or {}
    end = ev.get("end", {}) or {}
    start_iso = start.get("dateTime") or start.get("date") or ""
    end_iso = end.get("dateTime") or end.get("date") or ""
    is_all_day = "date" in start and "dateTime" not in start

    def _hhmm(s: str) -> str:
        if "T" in s:
            return s[11:16]
        return ""

    attendees = []
    for a in ev.get("attendees", []):
        attendees.append({
            "email": a.get("email", ""),
            "name": a.get("displayName", ""),
            "status": a.get("responseStatus", ""),
        })

    meet_link = ""
    conf = ev.get("conferenceData", {}) or {}
    for ep in conf.get("entryPoints", []) or []:
        if ep.get("entryPointType") == "video":
            meet_link = ep.get("uri", "")
            break

    organizer = ev.get("organizer", {}) or {}
    creator_email = (ev.get("creator", {}) or {}).get("email", "")
    # Writable wenn du Organizer bist ODER der Kalender guestsCanModify=true hat
    can_modify_guests = bool(ev.get("guestsCanModify"))
    is_organizer = bool(organizer.get("self"))
    writable = is_organizer or can_modify_guests or organizer.get("email", "").lower() == creator_email.lower()

    return {
        "event_id": ev.get("id", ""),
        "account": account,
        "calendar_id": calendar_id,
        "title": ev.get("summary", "(Kein Titel)"),
        "date": (start.get("date") or start_iso)[:10],
        "start": _hhmm(start_iso),
        "end": _hhmm(end_iso),
        "start_iso": start_iso,
        "end_iso": end_iso,
        "all_day": is_all_day,
        "location": ev.get("location", "") or "",
        "description": ev.get("description", "") or "",
        "attendees": attendees,
        "organizer": {
            "email": organizer.get("email", ""),
            "name": organizer.get("displayName", ""),
        },
        "html_link": ev.get("htmlLink", "") or "",
        "meet_link": meet_link,
        "recurring": bool(ev.get("recurringEventId")),
        "writable": writable,
    }


def _trigger_calendar_resync():
    """Calendar-Collector + Dashboard-Generator im Hintergrund neu laufen lassen.
    Stellt sicher dass der nächste Page-Load die neuen Daten sieht.
    """
    try:
        subprocess.Popen(
            [PYTHON_BIN, str(WORKSPACE / "scripts" / "collect.py"), "--sources", "calendar"],
            cwd=str(WORKSPACE),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        # generate_dashboard_data laeuft danach via Cron alle 30 Min, aber wir
        # triggern ihn separat damit die UI nicht warten muss.
        subprocess.Popen(
            [PYTHON_BIN, str(WORKSPACE / "scripts" / "generate_dashboard_data.py")],
            cwd=str(WORKSPACE),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception as e:
        logging.warning(f"Calendar-Resync-Trigger fehlgeschlagen: {e}")


class DashboardAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        logging.info(f"{self.address_string()} {fmt % args}")

    def _set_cors(self):
        origin = self.headers.get("Origin", "")
        if origin in ALLOWED_ORIGINS or origin.startswith("http://127.0.0.1") or origin.startswith("http://localhost"):
            self.send_header("Access-Control-Allow-Origin", origin)
        else:
            self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:8090")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._set_cors()
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors()
        self.end_headers()

    def do_PATCH(self):
        path = urlparse(self.path).path
        if path == "/calendar/event":
            return self._calendar_patch()
        return self._json(404, {"error": "not found"})

    def do_PUT(self):
        path = urlparse(self.path).path
        if path == "/content/planning/file":
            return self._planning_put_file()
        return self._json(404, {"error": "not found"})

    # ── Content-Planning Endpoints ──────────────────────────────────────────

    def _planning_get_file(self):
        qs = parse_qs(urlparse(self.path).query)
        rel = (qs.get("path") or [""])[0]
        try:
            abs_path = _safe_pipeline_path(rel)
        except ValueError as e:
            return self._json(400, {"error": str(e)})
        if not abs_path.exists():
            return self._json(404, {"error": "file not found"})
        try:
            text = abs_path.read_text(encoding="utf-8")
        except Exception as e:
            return self._json(500, {"error": str(e)})
        fm, body = _parse_md(text)
        # H1-Title aus Body extrahieren (falls vorhanden)
        title = ""
        body_no_title = body
        for line in body.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                # Title-Zeile aus Body entfernen (wird separat editiert)
                body_no_title = body.replace(line + "\n", "", 1).lstrip("\n")
                break
        return self._json(200, {
            "path": rel,
            "title": title,
            "frontmatter": fm,
            "body": body_no_title,
        })

    def _planning_put_file(self):
        qs = parse_qs(urlparse(self.path).query)
        rel = (qs.get("path") or [""])[0]
        try:
            abs_path = _safe_pipeline_path(rel)
        except ValueError as e:
            return self._json(400, {"error": str(e)})
        if not abs_path.exists():
            return self._json(404, {"error": "file not found"})
        data = self._read_json_body()
        # Bestehende Frontmatter+Body laden, dann mergen
        existing = abs_path.read_text(encoding="utf-8")
        fm, _ = _parse_md(existing)
        new_fm = data.get("frontmatter") or {}
        if not isinstance(new_fm, dict):
            return self._json(400, {"error": "frontmatter muss Object sein"})
        # Hashtags-Sonderfall: kann String (comma-sep) oder Liste sein
        if "hashtags" in new_fm and isinstance(new_fm["hashtags"], str):
            new_fm["hashtags"] = [
                t.strip().lstrip("#")
                for t in re.split(r"[,\s]+", new_fm["hashtags"])
                if t.strip()
            ]
        # Bestehende FM mit neuen Werten ueberschreiben (None/leere Strings = loeschen)
        for key, val in new_fm.items():
            if val in (None, ""):
                fm.pop(key, None)
            else:
                fm[key] = val
        title = (data.get("title") or "").strip()
        body = data.get("body") or ""
        # Body wieder mit H1-Title vorne aufbauen
        body_full = f"# {title}\n\n{body.lstrip()}" if title else body
        new_text = _serialize_md(fm, body_full)
        try:
            abs_path.write_text(new_text, encoding="utf-8")
        except Exception as e:
            return self._json(500, {"error": str(e)})
        logging.info(f"Pipeline-File aktualisiert: {rel}")
        _trigger_dashboard_refresh()
        return self._json(200, {"ok": True, "path": rel})

    # ── Calendar Endpoints ──────────────────────────────────────────────────

    def _calendar_get_event(self):
        qs = parse_qs(urlparse(self.path).query)
        account = (qs.get("account", ["primary"])[0] or "primary").strip()
        calendar_id = (qs.get("calendarId", [""])[0] or "").strip()
        event_id = (qs.get("eventId", [""])[0] or "").strip()
        if not calendar_id or not event_id:
            return self._json(400, {"error": "calendarId und eventId sind Pflicht"})
        try:
            svc = _calendar_service(account)
            if not svc:
                return self._json(503, {"error": f"Account '{account}' nicht verfügbar"})
            ev = svc.events().get(calendarId=calendar_id, eventId=event_id).execute()
            return self._json(200, _serialize_event(ev, account, calendar_id))
        except Exception as e:
            logging.warning(f"calendar.get failed: {e}")
            return self._json(500, {"error": str(e)})

    def _calendar_create(self):
        data = self._read_json_body()
        account = (data.get("account") or "primary").strip()
        calendar_id = (data.get("calendar_id") or "primary").strip()
        title = (data.get("title") or "").strip()
        if not title:
            return self._json(400, {"error": "title fehlt"})

        body = {"summary": title}
        if data.get("description"):
            body["description"] = data["description"]
        if data.get("location"):
            body["location"] = data["location"]

        # Start/Ende: ISO mit TZ (z.B. "2026-05-12T14:00:00+02:00") oder all-day "2026-05-12"
        start = data.get("start_iso") or data.get("start")
        end = data.get("end_iso") or data.get("end")
        if not start or not end:
            return self._json(400, {"error": "start und end (ISO) sind Pflicht"})
        if "T" in start:
            body["start"] = {"dateTime": start}
            body["end"] = {"dateTime": end}
        else:
            body["start"] = {"date": start}
            body["end"] = {"date": end}

        attendees = data.get("attendees") or []
        if attendees:
            body["attendees"] = [
                {"email": a} if isinstance(a, str) else a for a in attendees
            ]

        try:
            svc = _calendar_service(account)
            if not svc:
                return self._json(503, {"error": f"Account '{account}' nicht verfügbar"})
            created = svc.events().insert(calendarId=calendar_id, body=body).execute()
            _trigger_calendar_resync()
            return self._json(200, _serialize_event(created, account, calendar_id))
        except Exception as e:
            logging.warning(f"calendar.insert failed: {e}")
            return self._json(500, {"error": str(e)})

    def _calendar_patch(self):
        data = self._read_json_body()
        account = (data.get("account") or "primary").strip()
        calendar_id = (data.get("calendar_id") or "").strip()
        event_id = (data.get("event_id") or "").strip()
        if not calendar_id or not event_id:
            return self._json(400, {"error": "calendar_id und event_id sind Pflicht"})

        # Nur explizit gesetzte Felder patchen
        body = {}
        if "title" in data:
            body["summary"] = data["title"]
        if "description" in data:
            body["description"] = data["description"]
        if "location" in data:
            body["location"] = data["location"]
        if data.get("start_iso"):
            s = data["start_iso"]
            body["start"] = {"dateTime": s} if "T" in s else {"date": s}
        if data.get("end_iso"):
            e = data["end_iso"]
            body["end"] = {"dateTime": e} if "T" in e else {"date": e}

        if not body:
            return self._json(400, {"error": "Keine Felder zu ändern"})

        try:
            svc = _calendar_service(account)
            if not svc:
                return self._json(503, {"error": f"Account '{account}' nicht verfügbar"})
            updated = svc.events().patch(
                calendarId=calendar_id, eventId=event_id, body=body
            ).execute()
            _trigger_calendar_resync()
            return self._json(200, _serialize_event(updated, account, calendar_id))
        except Exception as e:
            logging.warning(f"calendar.patch failed: {e}")
            return self._json(500, {"error": str(e)})

    def _calendar_delete(self):
        qs = parse_qs(urlparse(self.path).query)
        account = (qs.get("account", ["primary"])[0] or "primary").strip()
        calendar_id = (qs.get("calendarId", [""])[0] or "").strip()
        event_id = (qs.get("eventId", [""])[0] or "").strip()
        if not calendar_id or not event_id:
            return self._json(400, {"error": "calendarId und eventId sind Pflicht"})
        try:
            svc = _calendar_service(account)
            if not svc:
                return self._json(503, {"error": f"Account '{account}' nicht verfügbar"})
            svc.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            _trigger_calendar_resync()
            return self._json(200, {"ok": True, "deleted": event_id})
        except Exception as e:
            logging.warning(f"calendar.delete failed: {e}")
            return self._json(500, {"error": str(e)})

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/creators":
            cfg = _load_config()
            return self._json(200, {
                "creators": cfg.get("creators", []),
                "self_handle": cfg.get("self_handle", ""),
            })
        if path == "/discovery":
            if not DISCOVERY_PATH.exists():
                return self._json(200, {"available": False, "note": "Noch kein Discovery-Run gemacht"})
            try:
                return self._json(200, json.loads(DISCOVERY_PATH.read_text(encoding="utf-8")))
            except Exception as e:
                return self._json(500, {"error": str(e)})
        if path == "/health":
            return self._json(200, {"ok": True, "service": "dashboard_api"})
        if path == "/calendar/event":
            return self._calendar_get_event()
        if path == "/calendar/prep":
            return self._calendar_prep_get()
        if path == "/content/planning/file":
            return self._planning_get_file()
        if path == "/content/file":
            return self._content_file_stream()
        return self._json(404, {"error": "not found"})

    def _content_file_stream(self):
        """GET /content/file?path=04-areas/content/.../final.mp4
        Streamt Mediendateien aus 04-areas/content/ fuer Inline-Preview.
        Path-Traversal-sicher. Erlaubte Extensions: mp4/mov/m4v/webm/pdf/png/jpg/jpeg/mp3.
        Unterstuetzt HTTP Range fuer Video-Seek."""
        qs = parse_qs(urlparse(self.path).query)
        rel = (qs.get("path") or [""])[0]
        if not rel or ".." in rel.split("/"):
            return self._json(400, {"error": "ungueltiger Pfad"})
        if not rel.startswith("04-areas/content/"):
            return self._json(400, {"error": "Pfad muss in 04-areas/content/ liegen"})
        allowed_ext = {".mp4", ".mov", ".m4v", ".webm", ".pdf", ".png", ".jpg", ".jpeg", ".mp3", ".m4a"}
        abs_path = (WORKSPACE / rel).resolve()
        try:
            abs_path.relative_to(WORKSPACE.resolve())
        except ValueError:
            return self._json(400, {"error": "Pfad ausserhalb Workspace"})
        if abs_path.suffix.lower() not in allowed_ext:
            return self._json(400, {"error": f"extension {abs_path.suffix} nicht erlaubt"})
        if not abs_path.exists() or not abs_path.is_file():
            return self._json(404, {"error": "file not found"})

        mime_map = {
            ".mp4": "video/mp4", ".mov": "video/quicktime", ".m4v": "video/x-m4v",
            ".webm": "video/webm", ".pdf": "application/pdf",
            ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".mp3": "audio/mpeg", ".m4a": "audio/mp4",
        }
        ctype = mime_map.get(abs_path.suffix.lower(), "application/octet-stream")
        size = abs_path.stat().st_size

        # Range-Support fuer Video-Seek
        range_header = self.headers.get("Range") or ""
        start, end = 0, size - 1
        is_partial = False
        if range_header.startswith("bytes="):
            try:
                rng = range_header.split("=", 1)[1].split(",")[0]
                s, _, e = rng.partition("-")
                if s:
                    start = int(s)
                if e:
                    end = int(e)
                if start > end or end >= size:
                    end = size - 1
                is_partial = True
            except ValueError:
                pass
        length = end - start + 1

        self.send_response(206 if is_partial else 200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(length))
        if is_partial:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self._set_cors()
        self.end_headers()
        try:
            with open(abs_path, "rb") as f:
                f.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = f.read(min(64 * 1024, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/creators":
            data = self._read_json_body()
            handle = (data.get("handle") or "").strip().lstrip("@")
            if not HANDLE_RE.match(handle):
                return self._json(400, {"error": "ungültiger Handle"})
            cfg = _load_config()
            existing = [c.lower() for c in (cfg.get("creators") or [])]
            if handle.lower() in existing:
                return self._json(409, {"error": f"@{handle} bereits getrackt"})
            cfg.setdefault("creators", []).append(handle)
            _save_config(cfg)
            logging.info(f"Creator hinzugefügt: @{handle}")
            return self._json(200, {"ok": True, "handle": handle, "creators": cfg["creators"]})

        if path == "/tracker/run":
            try:
                subprocess.Popen(
                    [PYTHON_BIN, str(WORKSPACE / "scripts" / "instagram_tracker.py")],
                    cwd=str(WORKSPACE),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
                return self._json(200, {"ok": True, "msg": "Tracker im Hintergrund gestartet"})
            except Exception as e:
                return self._json(500, {"error": str(e)})

        if path == "/calendar/event":
            return self._calendar_create()

        if path == "/calendar/prep/generate":
            return self._calendar_prep_generate()

        if path == "/todos/toggle":
            return self._todos_toggle()

        if path == "/calendar/sync":
            # Live-Refresh fuer den Kalender: holt Events aus Google + baut Dashboard neu.
            # Synchron, damit Frontend warten und dann router.refresh() machen kann.
            try:
                r1 = subprocess.run(
                    [PYTHON_BIN, str(WORKSPACE / "scripts" / "collect.py"),
                     "--sources", "calendar"],
                    cwd=str(WORKSPACE),
                    capture_output=True,
                    timeout=120,
                )
                r2 = subprocess.run(
                    [PYTHON_BIN, str(WORKSPACE / "scripts" / "generate_dashboard_data.py")],
                    cwd=str(WORKSPACE),
                    capture_output=True,
                    timeout=60,
                )
                ok = r1.returncode == 0 and r2.returncode == 0
                return self._json(200 if ok else 500, {
                    "ok": ok,
                    "collect_rc": r1.returncode,
                    "generate_rc": r2.returncode,
                })
            except subprocess.TimeoutExpired:
                return self._json(504, {"error": "Sync timeout"})
            except Exception as e:
                return self._json(500, {"error": str(e)})

        if path == "/dashboard/refresh":
            # Apify-freier Refresh: triggert nur generate_dashboard_data.py.
            # Schneller als tracker/run + keine Cost. Fuer Vault-Sync-Trigger.
            try:
                subprocess.Popen(
                    [PYTHON_BIN, str(WORKSPACE / "scripts" / "generate_dashboard_data.py")],
                    cwd=str(WORKSPACE),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
                return self._json(200, {"ok": True, "msg": "Dashboard-Refresh gestartet (Apify-frei)"})
            except Exception as e:
                return self._json(500, {"error": str(e)})

        if path == "/coach/chat":
            return self._coach_chat()

        if path == "/content/crosspost":
            return self._content_crosspost()

        if path == "/discovery/refresh":
            try:
                subprocess.Popen(
                    [PYTHON_BIN, str(WORKSPACE / "scripts" / "discover_creators.py"), "--force"],
                    cwd=str(WORKSPACE),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
                return self._json(200, {"ok": True, "msg": "Discovery im Hintergrund gestartet"})
            except Exception as e:
                return self._json(500, {"error": str(e)})

        return self._json(404, {"error": "not found"})

    def do_DELETE(self):
        path = urlparse(self.path).path
        if path == "/calendar/event":
            return self._calendar_delete()
        m = re.match(r"^/creators/(.+)$", path)
        if m:
            handle = m.group(1).lstrip("@")
            cfg = _load_config()
            creators = cfg.get("creators") or []
            new = [c for c in creators if c.lower() != handle.lower()]
            if len(new) == len(creators):
                return self._json(404, {"error": f"@{handle} nicht in Liste"})
            if cfg.get("self_handle", "").lower() == handle.lower():
                return self._json(400, {"error": "self_handle kann nicht entfernt werden"})
            cfg["creators"] = new
            _save_config(cfg)
            logging.info(f"Creator entfernt: @{handle}")
            return self._json(200, {"ok": True, "creators": new})
        return self._json(404, {"error": "not found"})

    # ── Lead-Prep Endpoints ─────────────────────────────────────────────────

    def _calendar_prep_get(self):
        """GET /calendar/prep?eventId=... — Sucht im Cache anhand Event-ID oder Slug.

        Strategie:
          1. Event aus DB laden → Name parsen → Slug
          2. data/call-preps/<slug>.json zurückgeben, wenn vorhanden
          3. Sonst 404
        """
        qs = parse_qs(urlparse(self.path).query)
        event_id = (qs.get("eventId", [""])[0] or "").strip()
        if not event_id:
            return self._json(400, {"error": "eventId fehlt"})

        try:
            sys.path.insert(0, str(WORKSPACE / "scripts"))
            from generate_lead_prep import (  # type: ignore
                load_event_from_db, parse_lead_info, slugify, CALL_PREPS, is_lead_call,
            )
            event = load_event_from_db(event_id)
            if not event:
                return self._json(404, {"error": "Event nicht in DB"})

            title = event.get("title", "") or ""
            trigger = is_lead_call(title)

            lead = parse_lead_info(event)
            slug = slugify(lead.get("name") or event_id)
            cache_file = CALL_PREPS / f"{slug}.json"

            if cache_file.exists():
                data = json.loads(cache_file.read_text(encoding="utf-8"))
                data["_cache"] = {"hit": True, "slug": slug}
                data["_trigger"] = trigger
                return self._json(200, data)

            return self._json(404, {
                "error": "Noch keine Prep generiert",
                "slug": slug,
                "trigger": trigger,
                "lead_preview": {
                    "name": lead.get("name", ""),
                    "email": lead.get("email", ""),
                    "phone": lead.get("phone", ""),
                },
            })
        except Exception as e:
            logging.warning(f"calendar.prep.get failed: {e}")
            return self._json(500, {"error": str(e)})

    def _content_crosspost(self):
        """POST /content/crosspost {vault_path, platform, status}
        Setzt crosspost_<platform> im Frontmatter einer library-script.md.
        platform: tiktok | youtube_shorts. status: posted | open.
        """
        data = self._read_json_body()
        rel = (data.get("vault_path") or "").strip()
        platform = (data.get("platform") or "").strip()
        status = (data.get("status") or "").strip()
        if platform not in ("tiktok", "youtube_shorts"):
            return self._json(400, {"error": "platform: tiktok|youtube_shorts"})
        if status not in ("posted", "open"):
            return self._json(400, {"error": "status: posted|open"})
        try:
            abs_path = _safe_pipeline_path(rel)
        except ValueError as e:
            return self._json(400, {"error": str(e)})
        if not abs_path.exists():
            return self._json(404, {"error": "script.md nicht gefunden"})
        try:
            text = abs_path.read_text(encoding="utf-8")
            field = f"crosspost_{platform}"
            m = re.match(r"^(---\n)(.*?)(\n---\n)", text, re.DOTALL)
            if not m:
                return self._json(400, {"error": "kein Frontmatter"})
            head, body, tail = m.groups()
            if re.search(rf"^{field}:", body, re.MULTILINE):
                body = re.sub(rf"^{field}:.*$", f"{field}: {status}", body,
                              count=1, flags=re.MULTILINE)
            else:
                body = body + f"\n{field}: {status}"
            abs_path.write_text(head + body + tail + text[m.end():], encoding="utf-8")
            # Bei TikTok: library/tiktok/<slug>/-Ordner anlegen oder entfernen
            if platform == "tiktok":
                _sync_tiktok_folder(abs_path.parent, status, body)
            # Overview-Markdown + Dashboard-JSON neu bauen
            subprocess.Popen(
                [PYTHON_BIN, str(WORKSPACE / "scripts" / "content_crosspost_overview.py")],
                cwd=str(WORKSPACE), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            _trigger_dashboard_refresh()
            return self._json(200, {"ok": True, "field": field, "status": status})
        except Exception as e:
            logging.exception("content.crosspost failed")
            return self._json(500, {"error": str(e)})

    def _coach_chat(self):
        """POST /coach/chat {messages: [{role, content}, ...]} -> Content-Coach-Response.
        Nutzt System-Prompt aus ~/.claude/agents/content-coach.md + dynamischen Vault-Kontext.
        """
        data = self._read_json_body()
        messages = data.get("messages")
        scene = data.get("scene") or "planung"
        if scene not in ("planung", "analytics"):
            scene = "planung"
        if not isinstance(messages, list) or not messages:
            return self._json(400, {"error": "messages: list erforderlich"})
        try:
            sys.path.insert(0, str(WORKSPACE / "scripts"))
            from content_coach import chat as coach_chat  # type: ignore
            result = coach_chat(messages, scene=scene)
            if "error" in result:
                return self._json(502, result)
            return self._json(200, result)
        except Exception as e:
            logging.exception("coach.chat failed")
            return self._json(500, {"error": str(e)})

    def _calendar_prep_generate(self):
        """POST /calendar/prep/generate {event_id, force?} — Triggert Generation synchron.

        Achtung: dauert ~30-60s wegen Firecrawl + Anthropic.
        Frontend sollte Loading-Spinner zeigen.
        """
        data = self._read_json_body()
        event_id = (data.get("event_id") or "").strip()
        force = bool(data.get("force"))
        if not event_id:
            return self._json(400, {"error": "event_id fehlt"})

        try:
            sys.path.insert(0, str(WORKSPACE / "scripts"))
            from generate_lead_prep import generate  # type: ignore
            result = generate(event_id, force=force)
            if "error" in result and "contact" not in result:
                return self._json(422, result)
            return self._json(200, result)
        except Exception as e:
            logging.exception("calendar.prep.generate failed")
            return self._json(500, {"error": str(e)})

    # ── Todo-Toggle ────────────────────────────────────────────────────────

    def _todos_toggle(self):
        """POST /todos/toggle {text, done, source_date?}

        Findet die Task in der Daily Note (heute oder source_date) und togglet
        die Checkbox `- [ ]` ↔ `- [x]`. Text-Match ist exakt (gestrippt).
        """
        from datetime import datetime as _dt, timedelta as _td
        data = self._read_json_body()
        text = (data.get("text") or "").strip()
        done = bool(data.get("done"))
        source_date = (data.get("source_date") or "").strip()
        if not text:
            return self._json(400, {"error": "text fehlt"})

        # Such-Reihenfolge: source_date (wenn gegeben), dann heute, dann letzte 7 Tage
        candidates: list[str] = []
        if source_date:
            candidates.append(source_date)
        today = _dt.now().strftime("%Y-%m-%d")
        if today not in candidates:
            candidates.append(today)
        try:
            today_dt = _dt.strptime(today, "%Y-%m-%d")
            for back in range(1, 8):
                d = (today_dt - _td(days=back)).strftime("%Y-%m-%d")
                if d not in candidates:
                    candidates.append(d)
        except Exception:
            pass

        for cand in candidates:
            note_file = WORKSPACE / "06-daily-notes" / f"{cand}.md"
            if not note_file.exists():
                continue
            try:
                content = note_file.read_text(encoding="utf-8")
            except Exception:
                continue

            # Suche nach exakter Zeile mit Checkbox + Text
            new_marker = "[x]" if done else "[ ]"
            lines = content.split("\n")
            changed = False
            for i, line in enumerate(lines):
                m = re.match(r"^(\s*-\s*\[)([ xX])(\]\s*)(.+)$", line)
                if not m:
                    continue
                line_text = m.group(4).strip()
                if line_text == text:
                    lines[i] = f"{m.group(1)}{'x' if done else ' '}{m.group(3)}{m.group(4)}"
                    changed = True
                    break
            if changed:
                note_file.write_text("\n".join(lines), encoding="utf-8")
                logging.info(f"Todo getoggelt in {cand}.md → {new_marker} '{text[:40]}'")
                # Dashboard async neu bauen
                self._trigger_dashboard()
                return self._json(200, {"ok": True, "file": cand, "done": done})

        return self._json(404, {"error": "Task nicht gefunden in Daily Notes"})

    def _trigger_dashboard(self):
        try:
            subprocess.Popen(
                [PYTHON_BIN, str(WORKSPACE / "scripts" / "generate_dashboard_data.py")],
                cwd=str(WORKSPACE),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except Exception:
            pass


def main():
    _setup_logging()
    port = 8093
    server = HTTPServer(("127.0.0.1", port), DashboardAPIHandler)
    logging.info(f"Dashboard-API laeuft auf http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Server gestoppt")


if __name__ == "__main__":
    main()
