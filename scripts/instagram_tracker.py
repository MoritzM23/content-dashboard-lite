#!/usr/bin/env python3
"""
Instagram Creator Tracker
Scraped tägliche Reels von definierten Creators via Apify und legt
Markdown-Reports im Obsidian-Vault ab.
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml
from apify_client import ApifyClient
from dotenv import load_dotenv

VAULT_ROOT = Path(os.environ.get("WORKSPACE_PATH", str(Path(__file__).resolve().parent.parent)))
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_PATH = Path.home() / "Library" / "Logs" / "aios" / "instagram-tracker.log"

load_dotenv(VAULT_ROOT / ".env")

# Optionale neue Module (V3-Architektur). Wenn nicht da: Tracker fällt zurück.
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from transcribe_local import transcribe_reel_local  # noqa: E402
except Exception:
    transcribe_reel_local = None

try:
    from instagram_graph_api import fetch_self_reels as graph_fetch_self_reels  # noqa: E402
except Exception:
    graph_fetch_self_reels = None

try:
    from scrape_comments import (  # noqa: E402
        fetch_comments_for_reel as _fetch_comments_for_reel,
        compute_comment_stats as _compute_comment_stats,
    )
except Exception:
    _fetch_comments_for_reel = None
    _compute_comment_stats = None

try:
    from content_ai_analysis import (  # noqa: E402
        analyze_reel_standard as _analyze_reel_standard,
        analyze_reel_deep as _analyze_reel_deep,
        cluster_topics as _cluster_topics,
    )
except Exception:
    _analyze_reel_standard = None
    _analyze_reel_deep = None
    _cluster_topics = None


def setup_logging():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def load_config():
    """Liest tracker-config + ueberschreibt self_handle/creators aus niche.yaml.

    niche.yaml ist die Single Source of Truth fuer User-spezifische Werte.
    Das Tracker-Config-File enthaelt nur Tuning-Knobs (Limits, Caches, Modelle).
    """
    config_path = SCRIPT_DIR / "instagram_tracker_config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # niche.yaml laden (Pflicht-File im Lite-Modul)
    niche_path = SCRIPT_DIR.parent / "niche.yaml"
    if niche_path.exists():
        with open(niche_path, "r", encoding="utf-8") as f:
            niche = yaml.safe_load(f) or {}
        self_handle = (niche.get("self_handle") or "").strip()
        competitors = niche.get("tracked_competitors") or []
        if self_handle:
            config["self_handle"] = self_handle
            creators = [self_handle]
            for c in competitors:
                c = str(c).strip()
                if c and c not in creators:
                    creators.append(c)
            config["creators"] = creators
        else:
            print("WARNUNG: niche.yaml hat keinen self_handle gesetzt.", file=sys.stderr)
    else:
        print("WARNUNG: niche.yaml nicht gefunden, Tracker laeuft eventuell nicht.", file=sys.stderr)

    return config


def fetch_creator_reels(client, handle, limit, include_transcripts, actor_id, timeout_secs):
    """Holt Reels für einen Creator via Apify Actor. Versucht 1x Retry bei Fehler."""
    run_input = {
        "username": [handle],
        "resultsLimit": limit,
    }
    if include_transcripts:
        # Reel-Scraper holt Transkripte standardmäßig wenn vorhanden;
        # explizit als Hint mitgeben falls Actor das Feld nutzt.
        run_input["scrapeTranscript"] = True

    last_err = None
    last_items = []
    # Bis zu 3 Versuche: Hard-Errors UND leere Ergebnisse retryen
    # (Apify-Actor liefert manchmal sporadisch 0 Items für Profile, die normal 10 hätten)
    for attempt in (1, 2, 3):
        try:
            run = client.actor(actor_id).call(run_input=run_input, timeout_secs=timeout_secs)
            if not run or not run.get("defaultDatasetId"):
                raise RuntimeError(f"Actor-Run ohne Dataset (status={run.get('status') if run else 'None'})")
            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            if items:
                return items
            last_items = items
            logging.warning(f"@{handle} Versuch {attempt} lieferte 0 Items, retry...")
            if attempt < 3:
                time.sleep(20)
        except Exception as e:
            last_err = e
            logging.warning(f"@{handle} Versuch {attempt} fehlgeschlagen: {e}")
            if attempt < 3:
                time.sleep(10)
    if last_err is not None:
        raise last_err
    return last_items


def get_views(reel):
    return (
        reel.get("videoPlayCount")
        or reel.get("videoViewCount")
        or reel.get("playCount")
        or reel.get("viewCount")
        or 0
    )


def calculate_engagement(reel):
    views = get_views(reel)
    if not views:
        return 0.0
    likes = reel.get("likesCount") or 0
    comments = reel.get("commentsCount") or 0
    return ((likes + comments) / views) * 100


def get_inline_transcript(reel):
    """Reel-Scraper liefert in manchen Versionen ein Inline-Transkript-Feld.
    Als Fallback nutzen, falls der separate Transcript-Actor nichts liefert."""
    candidates = [
        reel.get("transcript"),
        reel.get("transcripts"),
        reel.get("videoTranscript"),
    ]
    for c in candidates:
        if isinstance(c, str) and c.strip():
            return c.strip()
        if isinstance(c, list) and c:
            parts = []
            for item in c:
                if isinstance(item, dict):
                    txt = item.get("text") or item.get("transcript") or ""
                    if txt:
                        parts.append(txt)
                elif isinstance(item, str):
                    parts.append(item)
            joined = " ".join(parts).strip()
            if joined:
                return joined
    return None


def get_effective_transcript(reel):
    """Bevorzugt den per Transcript-Actor geholten Text (im Reel als
    `_transcript_text` gespeichert), fällt auf inline zurück."""
    t = reel.get("_transcript_text")
    if isinstance(t, str) and t.strip():
        return t.strip()
    return get_inline_transcript(reel)


def fetch_transcript_for_reel(client, shortcode, url, cache_dir, actor_id, timeout_secs):
    """Holt Transkript via separatem Apify-Actor mit File-Cache.

    Cache-Hit: liest `cache_dir/[shortcode].txt` und returnt String.
    Cache-Miss: ruft Actor auf, schreibt erfolgreichen Output in Cache.
    Bei Fehler oder leerem Transkript: return None und NICHT cachen."""
    if not shortcode:
        return None

    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{shortcode}.txt"

    if cache_file.exists():
        try:
            text = cache_file.read_text(encoding="utf-8").strip()
            if text:
                return text
        except Exception as e:
            logging.warning(f"Cache lesen fehlgeschlagen für {shortcode}: {e}")

    if not url:
        return None

    try:
        run = client.actor(actor_id).call(
            run_input={"videoUrls": [url]},
            timeout_secs=timeout_secs,
        )
        if not run or not run.get("defaultDatasetId"):
            logging.warning(f"Transcript-Actor ohne Dataset für {shortcode}")
            return None

        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        if not items:
            logging.info(f"Transcript-Actor lieferte 0 Items für {shortcode}")
            return None

        # Items sind Segmente desselben Reels; alle haben fullText.
        first = items[0]
        if first.get("errMsg"):
            logging.info(f"Transcript-Actor errMsg für {shortcode}: {first['errMsg']}")
            return None

        full = (first.get("fullText") or "").strip()
        if not full:
            # Fallback: Segmente zusammenbauen
            parts = [it.get("segmentText") or "" for it in items]
            full = " ".join(p.strip() for p in parts if p).strip()

        if not full:
            return None

        try:
            cache_file.write_text(full, encoding="utf-8")
        except Exception as e:
            logging.warning(f"Cache schreiben fehlgeschlagen für {shortcode}: {e}")

        return full
    except Exception as e:
        logging.warning(f"Transcript-Fetch fehlgeschlagen für {shortcode}: {str(e)[:200]}")
        return None


def get_caption(reel):
    return (reel.get("caption") or reel.get("text") or "").strip()


def get_shortcode(reel):
    return reel.get("shortCode") or reel.get("shortcode") or ""


def get_url(reel):
    url = reel.get("url")
    if url:
        return url
    sc = get_shortcode(reel)
    return f"https://www.instagram.com/reel/{sc}/" if sc else ""


def get_posted_date(reel):
    raw = reel.get("timestamp") or reel.get("takenAtTimestamp") or reel.get("takenAt")
    if not raw:
        return ""
    try:
        if isinstance(raw, (int, float)):
            return datetime.fromtimestamp(raw).strftime("%Y-%m-%d")
        if isinstance(raw, str):
            cleaned = raw.replace("Z", "+00:00")
            return datetime.fromisoformat(cleaned).strftime("%Y-%m-%d")
    except Exception:
        return str(raw)[:10]
    return ""


def get_posted_datetime(reel):
    """Volle ISO-Timestamp inklusive Uhrzeit, fuer Posting-Time-Analyse."""
    raw = reel.get("timestamp") or reel.get("takenAtTimestamp") or reel.get("takenAt")
    if not raw:
        return None
    try:
        if isinstance(raw, (int, float)):
            return datetime.fromtimestamp(raw)
        if isinstance(raw, str):
            cleaned = raw.replace("Z", "+00:00")
            return datetime.fromisoformat(cleaned)
    except Exception:
        return None
    return None


def get_audio_info(reel):
    """Extrahiert Audio-ID + Titel aus Apify-Output. Apify nennt das je nach Variante
    `musicInfo`, `originalSoundInfo` oder `audioInfo`. Fallback: leere Strings.
    """
    for key in ("musicInfo", "originalSoundInfo", "audioInfo", "music"):
        info = reel.get(key)
        if isinstance(info, dict):
            audio_id = (
                info.get("audio_id")
                or info.get("id")
                or info.get("musicId")
                or info.get("music_canonical_id")
                or ""
            )
            title = (
                info.get("title")
                or info.get("song_name")
                or info.get("displayName")
                or info.get("musicName")
                or ""
            )
            artist = (
                info.get("artist")
                or info.get("artist_name")
                or info.get("displayArtist")
                or ""
            )
            is_original = bool(info.get("uses_original_audio") or info.get("isOriginal") or False)
            return {
                "audio_id": str(audio_id) if audio_id else "",
                "title": str(title)[:120],
                "artist": str(artist)[:80],
                "is_original": is_original,
            }
    return {"audio_id": "", "title": "", "artist": "", "is_original": False}


def caption_snippet(caption, max_len=80):
    if not caption:
        return "(kein Text)"
    flat = re.sub(r"\s+", " ", caption).strip()
    if len(flat) <= max_len:
        return flat
    cut = flat[:max_len]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut + "…"


def blockquote(text):
    if not text:
        return "> (leer)"
    lines = text.splitlines() or [text]
    return "\n".join(f"> {line}" if line else ">" for line in lines)


def fmt_int(n):
    try:
        return f"{int(n):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "0"


def yaml_escape(value):
    if value is None:
        return ""
    s = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return s


def write_creator_report(handle, reels, output_dir, date_str, run_started):
    creator_dir = Path(output_dir) / handle
    creator_dir.mkdir(parents=True, exist_ok=True)
    file_path = creator_dir / f"{date_str}.md"

    n = len(reels)
    if n == 0:
        avg_views = 0
        avg_er = 0.0
    else:
        avg_views = sum(get_views(r) for r in reels) / n
        avg_er = sum(r.get("engagement_rate", 0.0) for r in reels) / n

    lines = []
    lines.append("---")
    lines.append(f'creator: "{yaml_escape(handle)}"')
    lines.append(f'date: "{date_str}"')
    lines.append("type: instagram-tracking")
    lines.append("tags: [content, competitor, instagram]")
    lines.append(f"reels_count: {n}")
    lines.append(f'run_started: "{run_started}"')
    lines.append("---")
    lines.append("")
    lines.append(f"# @{handle} – {date_str}")
    lines.append("")
    lines.append(f"**Profil:** https://instagram.com/{handle}")
    lines.append(f"**Letzte {n} Reels gescraped am:** {date_str} {run_started}")
    lines.append(f"**Avg Views:** {fmt_int(avg_views)}  ·  **Avg Engagement:** {avg_er:.2f}%")
    lines.append("")
    lines.append("---")
    lines.append("")

    if n == 0:
        lines.append("## Reels")
        lines.append("")
        lines.append("Keine Reels gefunden.")
    else:
        lines.append("## Reels (sortiert nach Engagement-Rate)")
        lines.append("")
        for i, reel in enumerate(reels, start=1):
            caption = get_caption(reel)
            transcript = get_effective_transcript(reel)
            lines.append(f"### {i}. {caption_snippet(caption)}")
            lines.append("")
            lines.append(f"- **URL:** {get_url(reel)}")
            lines.append(f"- **Posted:** {get_posted_date(reel) or 'unbekannt'}")
            lines.append(f"- **Views:** {fmt_int(get_views(reel))}")
            lines.append(f"- **Likes:** {fmt_int(reel.get('likesCount') or 0)}")
            lines.append(f"- **Kommentare:** {fmt_int(reel.get('commentsCount') or 0)}")
            lines.append(f"- **Engagement-Rate:** {reel.get('engagement_rate', 0.0):.2f}%")
            lines.append("")
            lines.append("**Caption:**")
            lines.append(blockquote(caption or "(keine Caption)"))
            lines.append("")
            lines.append("**Transkript:**")
            lines.append(blockquote(transcript or "Kein Transkript verfügbar"))
            lines.append("")
            lines.append("---")
            lines.append("")

    file_path.write_text("\n".join(lines), encoding="utf-8")
    return file_path


def write_daily_overview(all_data, errors, output_dir, date_str, duration_secs):
    overview_dir = Path(output_dir) / "_daily-overview"
    overview_dir.mkdir(parents=True, exist_ok=True)
    file_path = overview_dir / f"{date_str}.md"

    success_handles = [h for h, reels in all_data.items() if reels]
    total_reels = sum(len(r) for r in all_data.values())
    failed_count = len(errors)

    flat_reels = []
    for handle, reels in all_data.items():
        for r in reels:
            flat_reels.append((handle, r))
    flat_reels.sort(key=lambda x: x[1].get("engagement_rate", 0.0), reverse=True)
    top10 = flat_reels[:10]

    lines = []
    lines.append("---")
    lines.append(f'date: "{date_str}"')
    lines.append("type: instagram-daily-overview")
    lines.append("tags: [content, competitor, daily]")
    lines.append("---")
    lines.append("")
    lines.append(f"# Instagram-Tracking Übersicht – {date_str}")
    lines.append("")
    lines.append(f"**Creators getrackt:** {len(all_data) + failed_count}")
    lines.append(f"**Reels analysiert:** {total_reels}")
    lines.append(f"**Run-Dauer:** {int(duration_secs)} Sekunden")
    lines.append(f"**Erfolgreich:** {len(success_handles)}  ·  **Fehlgeschlagen:** {failed_count}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Top 10 des Tages (über alle Creators, sortiert nach Engagement-Rate)")
    lines.append("")
    if not top10:
        lines.append("_Keine Reels._")
    else:
        for i, (handle, reel) in enumerate(top10, start=1):
            cap = caption_snippet(get_caption(reel), max_len=80)
            lines.append(f"{i}. **@{handle}:** \"{cap}\"")
            lines.append(
                f"   {fmt_int(get_views(reel))} views · "
                f"{fmt_int(reel.get('likesCount') or 0)} likes · "
                f"{reel.get('engagement_rate', 0.0):.2f}% ER · "
                f"[Link]({get_url(reel)})"
            )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Pro Creator")
    lines.append("")
    lines.append("| Creator | Reels | Ø Views | Ø ER | Top-Reel |")
    lines.append("|---------|-------|---------|------|----------|")
    for handle, reels in all_data.items():
        n = len(reels)
        if n == 0:
            lines.append(f"| @{handle} | 0 | – | – | – |")
            continue
        avg_v = sum(get_views(r) for r in reels) / n
        avg_er = sum(r.get("engagement_rate", 0.0) for r in reels) / n
        top = max(reels, key=lambda r: r.get("engagement_rate", 0.0))
        lines.append(
            f"| @{handle} | {n} | {fmt_int(avg_v)} | {avg_er:.2f}% | "
            f"[Link]({get_url(top)}) |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Errors / Skipped")
    lines.append("")
    if not errors:
        lines.append("Keine.")
    else:
        for handle, reason in errors.items():
            lines.append(f"- @{handle}: {reason}")
    lines.append("")

    file_path.write_text("\n".join(lines), encoding="utf-8")
    return file_path


def fetch_summary_for_reel(anthropic_client, model, max_chars, shortcode, caption, transcript, cache_dir):
    """Generiert eine 1-2-Satz-Zusammenfassung via Claude und cached sie pro Shortcode.

    Cache-Hit: liest Datei, returnt String.
    Cache-Miss: ruft API, schreibt erfolgreich in Cache.
    Bei Fehler oder leerem Output: return None und NICHT cachen."""
    if not shortcode:
        return None

    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{shortcode}.txt"

    if cache_file.exists():
        try:
            text = cache_file.read_text(encoding="utf-8").strip()
            if text:
                return text
        except Exception as e:
            logging.warning(f"Summary-Cache lesen fehlgeschlagen für {shortcode}: {e}")

    if anthropic_client is None:
        return None

    caption = (caption or "").strip()
    transcript = (transcript or "").strip()
    if not caption and not transcript:
        return None

    # Caption oft sehr lang, kürzen für Token-Effizienz
    caption_short = caption[:1500]
    transcript_short = transcript[:3000]

    user_msg = (
        "Schreibe in 1-2 deutschen Sätzen worum es in diesem Instagram-Reel inhaltlich "
        f"geht. Maximal {max_chars} Zeichen. Nur den Inhalt zusammenfassen, keine "
        "Hooks/Calls-to-Action wiederholen, keine Hashtags. Nüchtern, sachlich.\n\n"
        f"CAPTION:\n{caption_short or '(keine)'}\n\n"
        f"TRANSKRIPT:\n{transcript_short or '(kein Transkript)'}"
    )

    try:
        resp = anthropic_client.messages.create(
            model=model,
            max_tokens=200,
            messages=[{"role": "user", "content": user_msg}],
        )
        parts = []
        for block in resp.content:
            if getattr(block, "type", None) == "text":
                parts.append(block.text)
        text = " ".join(parts).strip()
        if not text:
            return None
        # Hard-Cap und auf Wortgrenze kürzen
        if len(text) > max_chars:
            cut = text[:max_chars]
            if " " in cut:
                cut = cut.rsplit(" ", 1)[0]
            text = cut + "…"
        try:
            cache_file.write_text(text, encoding="utf-8")
        except Exception as e:
            logging.warning(f"Summary-Cache schreiben fehlgeschlagen für {shortcode}: {e}")
        return text
    except Exception as e:
        logging.warning(f"Summary-Call fehlgeschlagen für {shortcode}: {str(e)[:200]}")
        return None


def extract_hashtags(caption):
    if not caption:
        return []
    tags = re.findall(r"#(\w+)", caption)
    seen, out = set(), []
    for t in tags:
        tl = t.lower()
        if tl in seen:
            continue
        seen.add(tl)
        out.append(t)
    return out


def reel_to_json(reel):
    """Konvertiert ein Reel-Dict in das schlanke JSON-Schema fürs Dashboard."""
    caption = get_caption(reel)
    transcript = get_effective_transcript(reel)
    summary = reel.get("_summary_text") or ""
    duration = reel.get("videoDuration") or 0
    try:
        duration = float(duration) if duration else 0.0
    except (TypeError, ValueError):
        duration = 0.0

    # Plays = Video-Starts (videoPlayCount). Viewed = ≥3s angesehen (videoViewCount).
    # Bounce-Rate = (Plays - Viewed) / Plays — wie viele haben kurz gestartet & weggewischt.
    # `views` bleibt = videoPlayCount für historische Konsistenz der ER.
    views = get_views(reel)
    plays = reel.get("videoPlayCount") or 0
    viewed = reel.get("videoViewCount") or 0
    bounce_rate = None
    if plays and viewed and viewed <= plays:
        bounce_rate = round((plays - viewed) / plays * 100, 1)

    likes = reel.get("likesCount") or 0
    comments = reel.get("commentsCount") or 0
    like_rate = round(likes / views * 100, 2) if views else 0.0
    comment_rate = round(comments / views * 100, 2) if views else 0.0
    comment_to_like = round(comments / likes * 100, 1) if likes else 0.0

    posted_dt = get_posted_datetime(reel)
    audio = get_audio_info(reel)

    # Sprint-1: Comments-Stats und AI-Analyse werden vom Tracker spaeter angereichert.
    comments_stats = reel.get("_comments_stats") or {}
    ai_standard = reel.get("_ai_standard") or {}
    ai_deep = reel.get("_ai_deep") or {}

    return {
        "shortcode": get_shortcode(reel),
        "url": get_url(reel),
        "posted": get_posted_date(reel),
        "posted_at": posted_dt.isoformat() if posted_dt else "",
        "posted_hour": posted_dt.hour if posted_dt else None,
        "posted_dayofweek": posted_dt.strftime("%A") if posted_dt else "",
        "views": views,
        "plays": plays,
        "viewed_count": viewed,
        "bounce_rate": bounce_rate,
        "likes": likes,
        "comments": comments,
        "engagement_rate": round(reel.get("engagement_rate", 0.0), 2),
        "like_rate": like_rate,
        "comment_rate": comment_rate,
        "comment_to_like_ratio": comment_to_like,
        "video_duration": round(duration, 1),
        "hashtags": extract_hashtags(caption),
        "caption_full": caption,
        "caption_snippet": caption_snippet(caption),
        "caption_length": len(caption or ""),
        "transcript": transcript or "",
        "transcript_snippet": caption_snippet(transcript, max_len=180) if transcript else "",
        "summary": summary,
        # Sprint-1 V3 Felder:
        "audio": audio,
        "comments_stats": comments_stats,
        "ai_standard": ai_standard,
        "ai_deep": ai_deep,
    }


def compute_creator_stats(handle, reels_json):
    """Berechnet eine breite Stat-Palette für einen Creator (auf Reel-JSON-Liste)."""
    n = len(reels_json)
    if n == 0:
        return {
            "handle": handle, "reels_count": 0,
            "avg_views": 0, "avg_likes": 0, "avg_comments": 0, "avg_engagement_rate": 0.0,
            "total_views": 0, "total_likes": 0, "total_comments": 0,
            "max_views": 0, "max_likes": 0, "max_engagement_rate": 0.0,
            "min_views": 0, "min_likes": 0, "min_engagement_rate": 0.0,
            "median_engagement_rate": 0.0,
            "avg_like_rate": 0.0, "avg_comment_rate": 0.0, "avg_comment_to_like_ratio": 0.0,
            "max_like_rate": 0.0, "max_comment_rate": 0.0,
            "avg_bounce_rate": None, "bounce_coverage": 0.0,
            "avg_video_duration": 0.0, "avg_caption_length": 0,
            "transcript_coverage": 0.0,
            "summary_coverage": 0.0,
            "post_frequency_days": 0.0,
            "top_hashtags": [],
            "best_reel_er": None, "best_reel_views": None, "worst_reel_er": None,
            "top_reel": None, "reels": [],
        }

    views = [r.get("views", 0) or 0 for r in reels_json]
    likes = [r.get("likes", 0) or 0 for r in reels_json]
    comments = [r.get("comments", 0) or 0 for r in reels_json]
    ers = [r.get("engagement_rate", 0.0) or 0.0 for r in reels_json]
    like_rates = [r.get("like_rate", 0.0) or 0.0 for r in reels_json]
    comment_rates = [r.get("comment_rate", 0.0) or 0.0 for r in reels_json]
    cl_ratios = [r.get("comment_to_like_ratio", 0.0) or 0.0 for r in reels_json]
    bounce_vals = [r.get("bounce_rate") for r in reels_json if isinstance(r.get("bounce_rate"), (int, float))]
    durations = [r.get("video_duration", 0.0) or 0.0 for r in reels_json]
    caplens = [r.get("caption_length", 0) or 0 for r in reels_json]

    # Posting-Frequenz: durchschnittliche Tage zwischen aufeinanderfolgenden Posts
    posted_dates = []
    for r in reels_json:
        p = r.get("posted") or ""
        try:
            posted_dates.append(datetime.strptime(p[:10], "%Y-%m-%d").date())
        except (ValueError, TypeError):
            continue
    posted_dates.sort()
    freq_days = 0.0
    if len(posted_dates) >= 2:
        deltas = [
            (posted_dates[i + 1] - posted_dates[i]).days
            for i in range(len(posted_dates) - 1)
        ]
        if deltas:
            freq_days = sum(deltas) / len(deltas)

    # Top-Hashtags (über alle Reels des Creators, nach Häufigkeit)
    tag_count = {}
    for r in reels_json:
        for t in (r.get("hashtags") or []):
            k = t.lower()
            tag_count[k] = tag_count.get(k, 0) + 1
    top_tags = sorted(tag_count.items(), key=lambda kv: kv[1], reverse=True)[:10]
    top_hashtags = [{"tag": t, "count": c} for t, c in top_tags]

    # Hashtag-Performance: pro Hashtag durchschnittliche ER, Views, Top-Reel.
    # Nur Hashtags mit min. 2 Vorkommen, sonst zu wenig Sample.
    hashtag_perf_raw = {}
    for r in reels_json:
        for t in (r.get("hashtags") or []):
            k = t.lower()
            entry = hashtag_perf_raw.setdefault(k, {"ers": [], "views": [], "reels": []})
            entry["ers"].append(r.get("engagement_rate", 0.0) or 0.0)
            entry["views"].append(r.get("views", 0) or 0)
            entry["reels"].append({"shortcode": r.get("shortcode"), "er": r.get("engagement_rate", 0.0) or 0.0})
    hashtag_performance = []
    for tag, vals in hashtag_perf_raw.items():
        cnt = len(vals["ers"])
        if cnt < 2:
            continue
        top_reel = max(vals["reels"], key=lambda x: x["er"])
        hashtag_performance.append({
            "tag": tag,
            "count": cnt,
            "avg_er": round(sum(vals["ers"]) / cnt, 2),
            "avg_views": round(sum(vals["views"]) / cnt),
            "top_reel_shortcode": top_reel["shortcode"],
            "top_reel_er": round(top_reel["er"], 2),
        })
    hashtag_performance.sort(key=lambda x: x["avg_er"], reverse=True)
    hashtag_performance = hashtag_performance[:15]

    # Posting-Time-Pattern: Stunde + Wochentag aggregiert ueber alle Reels.
    hour_buckets = {}
    dow_buckets = {}
    for r in reels_json:
        h = r.get("posted_hour")
        dow = r.get("posted_dayofweek")
        er = r.get("engagement_rate", 0.0) or 0.0
        if h is not None:
            b = hour_buckets.setdefault(h, [])
            b.append(er)
        if dow:
            b = dow_buckets.setdefault(dow, [])
            b.append(er)
    posting_pattern_hours = sorted(
        [
            {"hour": h, "count": len(ers), "avg_er": round(sum(ers) / len(ers), 2)}
            for h, ers in hour_buckets.items()
        ],
        key=lambda x: x["hour"],
    )
    posting_pattern_dow = sorted(
        [
            {"day": d, "count": len(ers), "avg_er": round(sum(ers) / len(ers), 2)}
            for d, ers in dow_buckets.items()
        ],
        key=lambda x: x["avg_er"],
        reverse=True,
    )
    best_hour = max(posting_pattern_hours, key=lambda x: x["avg_er"])["hour"] if posting_pattern_hours else None
    best_dow = posting_pattern_dow[0]["day"] if posting_pattern_dow else None

    # Top-Audio: welche Audios kommen mehrfach vor + Performance.
    audio_buckets = {}
    for r in reels_json:
        a = r.get("audio") or {}
        aid = a.get("audio_id") or ""
        if not aid:
            continue
        b = audio_buckets.setdefault(aid, {
            "audio_id": aid,
            "title": a.get("title") or "",
            "artist": a.get("artist") or "",
            "is_original": a.get("is_original", False),
            "ers": [],
            "reels": [],
        })
        b["ers"].append(r.get("engagement_rate", 0.0) or 0.0)
        b["reels"].append(r.get("shortcode"))
    top_audio = []
    for aid, b in audio_buckets.items():
        cnt = len(b["ers"])
        top_audio.append({
            "audio_id": b["audio_id"],
            "title": b["title"],
            "artist": b["artist"],
            "is_original": b["is_original"],
            "count": cnt,
            "avg_er": round(sum(b["ers"]) / cnt, 2),
            "reels": b["reels"],
        })
    top_audio.sort(key=lambda x: (x["count"], x["avg_er"]), reverse=True)
    top_audio = top_audio[:10]

    # Coverage neue Felder (Sprint 1)
    comments_coverage = sum(1 for r in reels_json if r.get("comments_stats", {}).get("total_count", 0) > 0) / n
    ai_standard_coverage = sum(1 for r in reels_json if r.get("ai_standard", {}).get("topic_tag")) / n
    ai_deep_coverage = sum(1 for r in reels_json if r.get("ai_deep", {}).get("why_it_worked")) / n

    transcript_coverage = sum(1 for r in reels_json if (r.get("transcript") or "").strip()) / n
    summary_coverage = sum(1 for r in reels_json if (r.get("summary") or "").strip()) / n

    sorted_by_er = sorted(reels_json, key=lambda r: r.get("engagement_rate", 0.0), reverse=True)
    sorted_by_views = sorted(reels_json, key=lambda r: r.get("views", 0), reverse=True)

    sorted_ers = sorted(ers)
    median_er = sorted_ers[n // 2] if n % 2 else (sorted_ers[n // 2 - 1] + sorted_ers[n // 2]) / 2

    return {
        "handle": handle,
        "reels_count": n,
        "avg_views": round(sum(views) / n),
        "avg_likes": round(sum(likes) / n),
        "avg_comments": round(sum(comments) / n),
        "avg_engagement_rate": round(sum(ers) / n, 2),
        "total_views": sum(views),
        "total_likes": sum(likes),
        "total_comments": sum(comments),
        "max_views": max(views),
        "max_likes": max(likes),
        "max_engagement_rate": round(max(ers), 2),
        "min_views": min(views),
        "min_likes": min(likes),
        "min_engagement_rate": round(min(ers), 2),
        "median_engagement_rate": round(median_er, 2),
        "avg_like_rate": round(sum(like_rates) / n, 2),
        "avg_comment_rate": round(sum(comment_rates) / n, 2),
        "avg_comment_to_like_ratio": round(sum(cl_ratios) / n, 1),
        "max_like_rate": round(max(like_rates), 2) if like_rates else 0.0,
        "max_comment_rate": round(max(comment_rates), 2) if comment_rates else 0.0,
        "avg_bounce_rate": round(sum(bounce_vals) / len(bounce_vals), 1) if bounce_vals else None,
        "bounce_coverage": round(len(bounce_vals) / n, 2),
        "avg_video_duration": round(sum(durations) / n, 1),
        "avg_caption_length": round(sum(caplens) / n),
        "transcript_coverage": round(transcript_coverage, 2),
        "summary_coverage": round(summary_coverage, 2),
        "post_frequency_days": round(freq_days, 1),
        "top_hashtags": top_hashtags,
        "best_reel_er": sorted_by_er[0] if sorted_by_er else None,
        "best_reel_views": sorted_by_views[0] if sorted_by_views else None,
        "worst_reel_er": sorted_by_er[-1] if sorted_by_er else None,
        "top_reel": sorted_by_er[0] if sorted_by_er else None,  # Backward-compat
        # Sprint-1 V3 Aggregate:
        "hashtag_performance": hashtag_performance,
        "posting_pattern_hours": posting_pattern_hours,
        "posting_pattern_dow": posting_pattern_dow,
        "best_hour": best_hour,
        "best_dayofweek": best_dow,
        "top_audio": top_audio,
        "comments_coverage": round(comments_coverage, 2),
        "ai_standard_coverage": round(ai_standard_coverage, 2),
        "ai_deep_coverage": round(ai_deep_coverage, 2),
        "reels": reels_json,
    }


def write_json_snapshot(all_data, errors, output_dir, date_str, run_started_iso, duration_secs, self_handle=None):
    """Schreibt einen Tages-Snapshot als JSON für die Dashboard-Integration.

    Merge-Verhalten: wenn schon eine JSON für heute existiert mit erfolgreichen
    Creator-Einträgen (reels_count > 0), die NICHT in all_data stehen, übernimm
    sie unverändert. So überlebt ein Teil-Run die guten Daten eines Vor-Runs.

    Format siehe Plan 2026-05-05-instagram-tracker-v2.md."""
    data_dir = Path(output_dir) / "_data"
    data_dir.mkdir(parents=True, exist_ok=True)
    file_path = data_dir / f"{date_str}.json"

    existing_creators = {}
    if file_path.exists():
        try:
            existing = json.loads(file_path.read_text(encoding="utf-8"))
            for h, c in (existing.get("creators") or {}).items():
                if c and c.get("reels_count", 0) > 0:
                    existing_creators[h] = c
        except Exception as e:
            logging.warning(f"Bestehenden Snapshot lesen fehlgeschlagen: {e}")

    reels_total = sum(len(r) for r in all_data.values())

    creators_block = {}
    for handle, reels in all_data.items():
        if not reels:
            if handle in existing_creators:
                creators_block[handle] = existing_creators[handle]
                continue
            creators_block[handle] = compute_creator_stats(handle, [])
            continue
        reels_json = [reel_to_json(r) for r in reels]
        creators_block[handle] = compute_creator_stats(handle, reels_json)

    # Existing Creators aus Vorlauf, die in diesem Run gar nicht angefasst wurden
    for handle, c in existing_creators.items():
        if handle not in creators_block:
            creators_block[handle] = c

    flat = []
    for handle, reels in all_data.items():
        for r in reels:
            j = reel_to_json(r)
            j["handle"] = handle
            flat.append(j)
    # Bei den Existing-Creators die Reels aus den existing_creators-Daten ergänzen
    for handle, c in existing_creators.items():
        if handle in all_data and all_data[handle]:
            continue  # Aktueller Run hat frische Daten, die sind schon in flat
        for r in (c.get("reels") or []):
            j = dict(r)
            j["handle"] = handle
            flat.append(j)
    flat.sort(key=lambda x: x.get("engagement_rate", 0.0), reverse=True)
    top10 = flat[:10]

    creators_total = sum(1 for c in creators_block.values() if c.get("reels_count", 0) > 0) + len(errors)
    reels_total_combined = sum(c.get("reels_count", 0) for c in creators_block.values())

    snapshot = {
        "date": date_str,
        "run_started": run_started_iso,
        "run_duration_seconds": int(duration_secs),
        "creators_total": creators_total,
        "reels_total": reels_total_combined,
        "errors": len(errors),
        "errors_detail": errors,
        "self_handle": self_handle or "",
        "top10_overall": top10,
        "creators": creators_block,
    }

    file_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    return file_path


def main():
    parser = argparse.ArgumentParser(description="Instagram-Tracker (Apify-basiert)")
    parser.add_argument(
        "--mode",
        choices=["full", "self-hot"],
        default="full",
        help=(
            "full: alle Creators inkl. Transcripts/Comments/AI (taeglich 06:00). "
            "self-hot: nur self_handle, nur Reels juenger als 7 Tage, "
            "keine Comments/Transcripts/AI, fuer stuendlichen KPI-Refresh."
        ),
    )
    parser.add_argument(
        "--self-hot-max-age-days",
        type=int,
        default=7,
        help="Self-Hot: maximales Reel-Alter in Tagen (Default 7).",
    )
    args = parser.parse_args()

    setup_logging()
    mode = args.mode
    self_hot_max_age_days = int(args.self_hot_max_age_days)
    started = time.time()
    run_started = datetime.now().strftime("%H:%M")
    run_started_iso = datetime.now().replace(microsecond=0).isoformat()
    date_str = datetime.now().strftime("%Y-%m-%d")

    token = os.getenv("APIFY_API_TOKEN")
    if not token:
        msg = (
            "FEHLER: APIFY_API_TOKEN fehlt in "
            f"{VAULT_ROOT / '.env'}. Eintrag hinzufügen und erneut starten."
        )
        logging.error(msg)
        print(msg)
        sys.exit(1)

    config = load_config()
    output_dir = config["output_dir"]
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Self-Hot-Modus: nur self_handle, alle teuren Sub-Calls aus.
    # Erlaubt stuendlichen KPI-Refresh ohne Apify/Anthropic-Kostenexplosion.
    if mode == "self-hot":
        sh = config.get("self_handle")
        if not sh:
            logging.error("self-hot Modus aber kein self_handle in Config")
            sys.exit(1)
        config["creators"] = [sh]
        config["transcript_enabled"] = False
        config["local_transcripts_enabled"] = False
        config["summary_enabled"] = False
        config["comments_enabled"] = False
        config["ai_analysis_enabled"] = False
        # Auch fuer Self im Hot-Mode runter: nur die juengsten 20 Reels holen,
        # Age-Filter unten reduziert das weiter.
        config["self_reels_per_run"] = min(int(config.get("self_reels_per_run", 50)), 20)
        logging.info(
            f"Self-Hot-Modus aktiv: nur @{sh}, "
            f"max {config['self_reels_per_run']} Reels, "
            f"Age-Filter <={self_hot_max_age_days}d, "
            f"keine Comments/Transcripts/AI"
        )

    client = ApifyClient(token)
    all_data = {}
    errors = {}

    transcript_enabled = config.get("transcript_enabled", False)
    transcript_actor_id = config.get("transcript_actor_id", "crawlerbros/instagram-transcript-scraper")
    transcript_cache_dir = config.get(
        "transcript_cache_dir",
        str(Path(output_dir) / "_transcripts"),
    )
    transcript_max_per_run = int(config.get("transcript_max_per_run", 50))
    transcript_timeout = int(config.get("transcript_timeout", 300))
    transcript_calls_used = 0

    # V3: lokale Whisper-Pipeline (yt-dlp + OpenAI Whisper API / mlx-whisper).
    # Wenn aktiv, ersetzt sie den Apify-Transcript-Actor.
    local_transcripts_enabled = config.get("local_transcripts_enabled", False) and transcribe_reel_local is not None
    local_transcripts_max_per_run = int(config.get("local_transcripts_max_per_run", 200))
    local_transcripts_used = 0

    # V3: eigene KPIs via Instagram Graph API (kostenlos), statt Apify für self_handle.
    self_handle = config.get("self_handle")
    graph_token = os.getenv("INSTAGRAM_GRAPH_TOKEN")
    graph_user_id = os.getenv("INSTAGRAM_BUSINESS_USER_ID")
    use_graph_api_for_self = bool(
        self_handle and graph_token and graph_user_id and graph_fetch_self_reels is not None
    )

    # V3 Comments
    comments_enabled = config.get("comments_enabled", False) and _fetch_comments_for_reel is not None
    comments_max_per_reel = int(config.get("comments_max_per_reel", 50))
    comments_cache_dir = config.get(
        "comments_cache_dir", str(Path(output_dir) / "_comments")
    )
    comments_max_per_run = int(config.get("comments_max_per_run", 50))
    comments_timeout = int(config.get("comments_timeout", 120))
    comments_calls_used = 0

    # V3 AI-Analyse (Setup nach summary_enabled-Block weiter unten, weil dort
    # der anthropic_client zuerst initialisiert wird).
    ai_analysis_enabled = config.get("ai_analysis_enabled", False) and _analyze_reel_standard is not None
    ai_analysis_cache_dir = Path(config.get(
        "ai_analysis_cache_dir", str(Path(output_dir) / "_ai_analysis")
    ))
    ai_standard_max_per_run = int(config.get("ai_standard_max_per_run", 200))
    ai_deep_max_per_run = int(config.get("ai_deep_max_per_run", 12))
    ai_standard_used = 0
    ai_deep_used = 0

    summary_enabled = config.get("summary_enabled", False)
    summary_model = config.get("summary_model", "claude-haiku-4-5-20251001")
    summary_cache_dir = config.get(
        "summary_cache_dir",
        str(Path(output_dir) / "_summaries"),
    )
    summary_max_per_run = int(config.get("summary_max_per_run", 150))
    summary_max_chars = int(config.get("summary_max_chars", 240))
    summary_calls_used = 0
    anthropic_client = None
    if summary_enabled:
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                from anthropic import Anthropic
                anthropic_client = Anthropic()
            except Exception as e:
                logging.warning(f"Anthropic-Client Init fehlgeschlagen, Summaries deaktiviert: {e}")
                summary_enabled = False
        else:
            logging.warning("ANTHROPIC_API_KEY nicht gesetzt — Summaries deaktiviert")
            summary_enabled = False

    # V3 AI-Analyse: Anthropic-Client sicherstellen, falls Summaries deaktiviert sind.
    if ai_analysis_enabled and anthropic_client is None:
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                from anthropic import Anthropic
                anthropic_client = Anthropic()
            except Exception as e:
                logging.warning(f"Anthropic-Client Init fehlgeschlagen, AI-Analyse deaktiviert: {e}")
                ai_analysis_enabled = False
        else:
            logging.warning("ANTHROPIC_API_KEY fehlt — AI-Analyse deaktiviert")
            ai_analysis_enabled = False

    logging.info(
        f"Starte Run für {len(config['creators'])} Creators "
        f"(apify_transcripts={transcript_enabled}, local_transcripts={local_transcripts_enabled}, "
        f"graph_api_for_self={use_graph_api_for_self}, "
        f"comments={comments_enabled}, ai_analysis={ai_analysis_enabled})"
    )
    for handle in config["creators"]:
        # Self-Handle bekommt eigenen Limit (mehr Reels fuer eigene Deep-Dive-Analyse).
        is_self = (handle == self_handle)
        reels_limit = int(config.get("self_reels_per_run", config["reels_per_creator"])) if is_self else int(config["reels_per_creator"])
        print(f"Scrape @{handle} ({reels_limit} reels)...")
        logging.info(f"Scrape @{handle} (limit={reels_limit})")
        try:
            # V3: eigener Account via offizielle Graph API (kostenlos, präziser).
            if use_graph_api_for_self and is_self:
                logging.info(f"@{handle}: nutze Instagram Graph API statt Apify")
                reels = graph_fetch_self_reels(
                    access_token=graph_token,
                    ig_user_id=graph_user_id,
                    limit=reels_limit,
                )
            else:
                reels = fetch_creator_reels(
                    client,
                    handle,
                    reels_limit,
                    config.get("include_transcripts", True),
                    config.get("actor_id", "apify/instagram-reel-scraper"),
                    config.get("timeout_per_creator", 180),
                )
            # Self-Hot: nur Reels innerhalb des Age-Fensters behalten.
            # Aeltere Reels bewegen sich kaum noch in den KPIs, sparen Folge-Cost.
            if mode == "self-hot":
                # get_posted_datetime liefert tz-aware (UTC), also Cutoff auch UTC.
                cutoff = datetime.now(timezone.utc) - timedelta(days=self_hot_max_age_days)
                before = len(reels)
                kept = []
                for r in reels:
                    posted = get_posted_datetime(r)
                    if posted is None:
                        kept.append(r)
                        continue
                    if posted.tzinfo is None:
                        posted = posted.replace(tzinfo=timezone.utc)
                    if posted >= cutoff:
                        kept.append(r)
                reels = kept
                logging.info(
                    f"@{handle} self-hot Age-Filter: {before} -> {len(reels)} "
                    f"(cutoff {cutoff.strftime('%Y-%m-%d')})"
                )

            for r in reels:
                r["engagement_rate"] = calculate_engagement(r)
            reels.sort(key=lambda x: x.get("engagement_rate", 0.0), reverse=True)

            # Transcript-Pass V3: bevorzugt lokal (gratis via OpenAI API/mlx),
            # Apify nur als Fallback wenn explizit aktiv.
            if local_transcripts_enabled:
                for r in reels:
                    sc = get_shortcode(r)
                    url = get_url(r)
                    if not sc or not url:
                        continue
                    cache_file = Path(transcript_cache_dir) / f"{sc}.txt"
                    is_cached = cache_file.exists()
                    if not is_cached and local_transcripts_used >= local_transcripts_max_per_run:
                        logging.warning(
                            f"Lokales Transcript-Budget aufgebraucht "
                            f"({local_transcripts_max_per_run}); skip {sc}"
                        )
                        continue
                    if not is_cached:
                        local_transcripts_used += 1
                    text = transcribe_reel_local(sc, url, Path(transcript_cache_dir))
                    if text:
                        r["_transcript_text"] = text
            elif transcript_enabled:
                for r in reels:
                    sc = get_shortcode(r)
                    url = get_url(r)
                    if not sc:
                        continue
                    cache_file = Path(transcript_cache_dir) / f"{sc}.txt"
                    if cache_file.exists():
                        text = fetch_transcript_for_reel(
                            client, sc, url, transcript_cache_dir,
                            transcript_actor_id, transcript_timeout,
                        )
                        if text:
                            r["_transcript_text"] = text
                        continue
                    if transcript_calls_used >= transcript_max_per_run:
                        logging.warning(
                            f"Transcript-Budget aufgebraucht ({transcript_max_per_run}); "
                            f"skip {sc}"
                        )
                        continue
                    transcript_calls_used += 1
                    text = fetch_transcript_for_reel(
                        client, sc, url, transcript_cache_dir,
                        transcript_actor_id, transcript_timeout,
                    )
                    if text:
                        r["_transcript_text"] = text

            # Summary-Pass: gleicher Cache-First-Pattern.
            if summary_enabled:
                for r in reels:
                    sc = get_shortcode(r)
                    if not sc:
                        continue
                    cap = get_caption(r)
                    tx = get_effective_transcript(r) or ""
                    cache_file = Path(summary_cache_dir) / f"{sc}.txt"
                    if cache_file.exists():
                        s = fetch_summary_for_reel(
                            None, summary_model, summary_max_chars,
                            sc, cap, tx, summary_cache_dir,
                        )
                        if s:
                            r["_summary_text"] = s
                        continue
                    if summary_calls_used >= summary_max_per_run:
                        logging.warning(
                            f"Summary-Budget aufgebraucht ({summary_max_per_run}); skip {sc}"
                        )
                        continue
                    summary_calls_used += 1
                    s = fetch_summary_for_reel(
                        anthropic_client, summary_model, summary_max_chars,
                        sc, cap, tx, summary_cache_dir,
                    )
                    if s:
                        r["_summary_text"] = s

            # V3 Comments-Pass: Inhalte ziehen, Stats berechnen, an Reel anhaengen.
            if comments_enabled:
                Path(comments_cache_dir).mkdir(parents=True, exist_ok=True)
                for r in reels:
                    sc = get_shortcode(r)
                    url = get_url(r)
                    if not sc or not url:
                        continue
                    cache_file = Path(comments_cache_dir) / f"{sc}.json"
                    is_cached = cache_file.exists()
                    if not is_cached and comments_calls_used >= comments_max_per_run:
                        logging.warning(
                            f"Comments-Budget aufgebraucht ({comments_max_per_run}); skip {sc}"
                        )
                        continue
                    if not is_cached:
                        comments_calls_used += 1
                    try:
                        comments_list = _fetch_comments_for_reel(
                            client, sc, url, Path(comments_cache_dir),
                            max_comments=comments_max_per_reel,
                            timeout_secs=comments_timeout,
                        )
                    except Exception as e:
                        logging.warning(f"Comments-Fetch failed for {sc}: {str(e)[:120]}")
                        comments_list = None
                    if comments_list:
                        r["_comments"] = comments_list
                        try:
                            r["_comments_stats"] = _compute_comment_stats(comments_list)
                        except Exception as e:
                            logging.warning(f"Comments-Stats failed for {sc}: {str(e)[:120]}")

            # V3 AI-Standard-Pass: Sentiment, Hook, Themen pro Reel.
            if ai_analysis_enabled:
                ai_analysis_cache_dir.mkdir(parents=True, exist_ok=True)
                for r in reels:
                    sc = get_shortcode(r)
                    if not sc:
                        continue
                    cache_file = ai_analysis_cache_dir / f"{sc}_standard.json"
                    is_cached = cache_file.exists()
                    if not is_cached and ai_standard_used >= ai_standard_max_per_run:
                        logging.warning(
                            f"AI-Standard-Budget aufgebraucht ({ai_standard_max_per_run}); skip {sc}"
                        )
                        continue
                    if not is_cached:
                        ai_standard_used += 1
                    # Reel ins erwartete Format mappen (analyze_reel_standard nimmt unser
                    # JSON-Schema; wir uebergeben den noch nicht konvertierten Apify-Reel,
                    # also baue ad-hoc ein passendes Dict).
                    reel_for_ai = {
                        "shortcode": sc,
                        "caption": get_caption(r),
                        "transcript": get_effective_transcript(r) or "",
                        "views": get_views(r),
                        "likes": r.get("likesCount") or 0,
                        "comments": r.get("commentsCount") or 0,
                        "engagement_rate": r.get("engagement_rate", 0.0),
                    }
                    try:
                        result = _analyze_reel_standard(
                            reel_for_ai, r.get("_comments"),
                            anthropic_client, ai_analysis_cache_dir,
                        )
                        if result:
                            r["_ai_standard"] = result
                    except Exception as e:
                        logging.warning(f"AI-Standard failed for {sc}: {str(e)[:120]}")

            write_creator_report(handle, reels, output_dir, date_str, run_started)
            all_data[handle] = reels
            print(f"  ok: {len(reels)} Reels")
            logging.info(f"@{handle}: {len(reels)} Reels gespeichert")
        except Exception as e:
            err_msg = str(e)[:200]
            errors[handle] = err_msg
            all_data[handle] = []
            logging.error(f"@{handle} fehlgeschlagen: {err_msg}")
            print(f"  fehler: {err_msg}")

        # Inkrementelles JSON-Write nach jedem Creator: damit das Dashboard
        # während des Runs schon Zwischenstand zeigen kann.
        try:
            partial_duration = time.time() - started
            write_json_snapshot(
                all_data, errors, output_dir, date_str,
                run_started_iso, partial_duration,
                self_handle=config.get("self_handle"),
            )
        except Exception as e:
            logging.warning(f"Inkrementelles JSON-Write fehlgeschlagen: {e}")

    # V3 AI-Deep-Pass: Top 10 Reels across all creators by ER, Sonnet-Tiefenanalyse.
    if ai_analysis_enabled and _analyze_reel_deep is not None:
        ai_analysis_cache_dir.mkdir(parents=True, exist_ok=True)
        # Flatten + Top 10 by ER
        flat_for_deep = []
        for h, rs in all_data.items():
            for r in rs:
                flat_for_deep.append((h, r))
        flat_for_deep.sort(key=lambda x: x[1].get("engagement_rate", 0.0), reverse=True)
        top_for_deep = flat_for_deep[:ai_deep_max_per_run]

        # Comparable-Pool: alle eigenen Reels als Vergleichsbasis
        own_reels_pool = []
        if self_handle and self_handle in all_data:
            for r in all_data[self_handle]:
                own_reels_pool.append({
                    "shortcode": get_shortcode(r),
                    "caption": get_caption(r)[:300],
                    "transcript": (get_effective_transcript(r) or "")[:500],
                    "views": get_views(r),
                    "engagement_rate": r.get("engagement_rate", 0.0),
                })

        for h, r in top_for_deep:
            sc = get_shortcode(r)
            if not sc:
                continue
            cache_file = ai_analysis_cache_dir / f"{sc}_deep.json"
            is_cached = cache_file.exists()
            if not is_cached and ai_deep_used >= ai_deep_max_per_run:
                break
            if not is_cached:
                ai_deep_used += 1
            reel_for_ai = {
                "shortcode": sc,
                "caption": get_caption(r),
                "transcript": get_effective_transcript(r) or "",
                "views": get_views(r),
                "likes": r.get("likesCount") or 0,
                "comments": r.get("commentsCount") or 0,
                "engagement_rate": r.get("engagement_rate", 0.0),
                "handle": h,
            }
            try:
                deep = _analyze_reel_deep(
                    reel_for_ai, r.get("_comments"),
                    own_reels_pool[:5], anthropic_client, ai_analysis_cache_dir,
                )
                if deep:
                    r["_ai_deep"] = deep
            except Exception as e:
                logging.warning(f"AI-Deep failed for {sc}: {str(e)[:120]}")

    # V3 Topic-Clustering: nur fuer self_handle, einmal pro Run.
    if (
        ai_analysis_enabled
        and _cluster_topics is not None
        and self_handle
        and self_handle in all_data
        and all_data[self_handle]
    ):
        ai_analysis_cache_dir.mkdir(parents=True, exist_ok=True)
        try:
            own = all_data[self_handle]
            reels_for_cluster = [
                {
                    "shortcode": get_shortcode(r),
                    "caption": get_caption(r)[:400],
                    "transcript": (get_effective_transcript(r) or "")[:600],
                    "engagement_rate": r.get("engagement_rate", 0.0),
                    "views": get_views(r),
                }
                for r in own
            ]
            analyses = [r.get("_ai_standard") or {} for r in own]
            clusters = _cluster_topics(
                reels_for_cluster, analyses, anthropic_client, ai_analysis_cache_dir,
            )
            if clusters:
                # An eigenen Creator-Stats anhaengen, wird nach write_json_snapshot
                # ueber compute_creator_stats nicht weitergereicht. Daher direkt im
                # JSON-Snapshot-Schreiber via Side-Channel.
                # Workaround: Wir schreiben es als eigene Datei daneben.
                cluster_path = ai_analysis_cache_dir / f"{self_handle}_topics.json"
                cluster_path.write_text(
                    json.dumps(clusters, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                logging.info(f"Topic-Cluster fuer {self_handle} geschrieben: {cluster_path}")
        except Exception as e:
            logging.warning(f"Topic-Clustering failed: {str(e)[:120]}")

    duration = time.time() - started

    # Self-Hot: Daily-Overview nicht neu schreiben (sonst zerschiesst es die
    # Wettbewerber-Sicht aus dem 06:00-Full-Run). JSON-Snapshot mergt eh.
    if mode == "self-hot":
        logging.info("Self-Hot-Modus: ueberspringe write_daily_overview")
        overview_path = None
    else:
        overview_path = write_daily_overview(all_data, errors, output_dir, date_str, duration)
        logging.info(f"Daily Overview: {overview_path}")

    json_path = write_json_snapshot(
        all_data, errors, output_dir, date_str, run_started_iso, duration,
        self_handle=config.get("self_handle"),
    )
    logging.info(f"JSON Snapshot: {json_path}")

    # Time-Series-Persistierung: Pro Reel eine Tages-Zeile in reel_history.db.
    # Erlaubt View-Deltas über beliebige Zeitfenster, unabhängig davon ob ein
    # Reel im aktuellen Tracker-Window noch erscheint.
    try:
        from reel_history import upsert_snapshot as _rh_upsert
        rh_rows = 0
        for handle, reels in all_data.items():
            if reels:
                rh_rows += _rh_upsert(handle, reels, date_str)
        logging.info(f"Reel-History: {rh_rows} Rows in data/reel_history.db geschrieben")
    except Exception as e:
        logging.warning(f"Reel-History-Write fehlgeschlagen: {str(e)[:160]}")
    if local_transcripts_enabled:
        logging.info(
            f"Lokale Transcript-Calls (gratis): {local_transcripts_used}/{local_transcripts_max_per_run}"
        )
    if transcript_enabled:
        logging.info(f"Apify-Transcript-Calls genutzt: {transcript_calls_used}/{transcript_max_per_run}")
    if comments_enabled:
        logging.info(f"Comments-Calls genutzt: {comments_calls_used}/{comments_max_per_run}")
    if ai_analysis_enabled:
        logging.info(
            f"AI-Standard genutzt: {ai_standard_used}/{ai_standard_max_per_run}, "
            f"AI-Deep genutzt: {ai_deep_used}/{ai_deep_max_per_run}"
        )
    if summary_enabled:
        logging.info(f"Summary-Calls genutzt: {summary_calls_used}/{summary_max_per_run}")
    print(f"Done in {int(duration)}s. Output: {output_dir}")

    # Post-Tracker-Sync: pipeline/bereit/ -> library/ fuer frisch gepostete Reels,
    # danach meta_refresh um meta.md mit Live-KPIs zu fuellen. Beide sind Apify-frei
    # und idempotent, also bei jedem Tracker-Run sicher.
    try:
        import subprocess as _sp
        from pathlib import Path as _P
        _scripts = _P(__file__).resolve().parent
        _py = "python33"
        for _name in ("content_pipeline_move.py", "content_meta_refresh.py"):
            _path = _scripts / _name
            if not _path.exists():
                continue
            try:
                _sp.run(
                    [_py, str(_path)],
                    cwd=str(_scripts.parent),
                    timeout=180,
                    check=False,
                )
                logging.info(f"Post-Tracker-Sync ausgefuehrt: {_name}")
            except Exception as _e:
                logging.warning(f"Post-Tracker-Sync {_name} fehlgeschlagen: {_e}")
    except Exception as _e:
        logging.warning(f"Post-Tracker-Sync nicht moeglich: {_e}")


if __name__ == "__main__":
    main()
