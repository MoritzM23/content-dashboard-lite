#!/usr/bin/env python3
"""
Creator-Discovery fuer AIOS / Instagram-Tracker.

Findet aufstrebende Creator (DE + EN), die aehnlichen Content wie Moritz
machen, und ranked sie nach Empfehlungs-Score.

Flow:
1. Themen / Hashtags laden (Topic-Cluster -> Top-Hashtags -> Fallback).
2. Pro Hashtag (max 5 Calls): Apify-Hashtag-Scraper, Top-Reels ziehen.
3. Creators einsammeln, schon getrackte und Self herausfiltern.
4. Score: avg_engagement_rate * 0.4 + theme_match * 0.4 + recency * 0.2.
5. Top 15 mit Claude-Haiku-Kontext anreichern (~5 Cents).
6. JSON nach data/creator_discovery.json. Cache: 7 Tage.

Cost-Cap: max 5 Hashtag-Calls / Run = ~$0.50 Apify + ~$0.05 Anthropic.

Manuell: `python scripts/discover_creators.py [--force]`. Cron: 1x / Woche.
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
LOG_PATH = Path.home() / "Library" / "Logs" / "aios" / "creator-discovery.log"

CACHE_TTL_DAYS = 7
HASHTAG_ACTOR_ID = "apify/instagram-hashtag-scraper"
HASHTAG_RESULTS_PER_TAG = 30
MAX_HASHTAG_CALLS = 8  # Hard-Cap, ~$0.80 / Run
TOP_N_OUTPUT = 20
APIFY_TIMEOUT_SECS = 240
TOP_REELS_PER_CREATOR = 3  # pro discovered Creator: Top-N Reels persistieren

# Heuristik: deutsche Stopwoerter fuer Sprache-Erkennung in Captions
DE_STOPWORDS = {
    "und", "der", "die", "das", "ist", "nicht", "mit", "auf", "auch", "nur",
    "ich", "du", "wir", "ihr", "sie", "ein", "eine", "den", "dem", "des",
    "fuer", "fur", "von", "zu", "im", "am", "es", "wie", "was", "wenn",
    "aber", "oder", "weil", "dann", "noch", "schon", "mal", "hier",
}

# Hashtag-Pool wird aus niche.yaml gelesen. Fallback ist eine generische
# Solopreneur-Liste — du solltest sie ueber niche.yaml an deinen Markt anpassen.
def _load_niche_hashtags() -> list[str]:
    niche_path = VAULT_ROOT / "niche.yaml"
    if niche_path.exists():
        try:
            data = yaml.safe_load(niche_path.read_text(encoding="utf-8")) or {}
            tags = data.get("discovery_hashtags") or []
            tags = [str(t).lstrip("#").strip() for t in tags if t]
            if tags:
                return tags
        except Exception as e:
            logging.warning(f"niche.yaml konnte nicht gelesen werden: {e}")
    return [
        "creator", "contentcreator", "socialmedia",
        "marketing", "smallbusiness", "solopreneur",
    ]


FALLBACK_HASHTAGS = _load_niche_hashtags()


def _self_handle() -> str:
    """Liest den eigenen Handle aus niche.yaml (Fallback: self)."""
    niche_path = VAULT_ROOT / "niche.yaml"
    if niche_path.exists():
        try:
            data = yaml.safe_load(niche_path.read_text(encoding="utf-8")) or {}
            h = (data.get("self_handle") or "").strip()
            if h:
                return h
        except Exception:
            pass
    return "self"

load_dotenv(VAULT_ROOT / ".env")


# ---------- Logging / Config ----------

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


def load_tracker_config() -> dict:
    """Liest scripts/instagram_tracker_config.yaml."""
    path = SCRIPT_DIR / "instagram_tracker_config.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------- Themen-Loader ----------

def _load_themes(workspace: Path) -> tuple[list[str], list[str], str]:
    """Laedt Themen + abgeleitete Hashtags.

    Stand 2026-05-15: Die Hashtag-Liste ist HARDCODED auf das fokussierte
    Konkurrenz-Set (siehe FALLBACK_HASHTAGS oben). Themen aus dem Topic-Cluster
    werden nur fuer den semantischen theme_match-Score genutzt, nicht fuer den
    Apify-Hashtag-Call. So bleibt das Konkurrenz-Mapping vorhersagbar.

    Returns: (themes_list, hashtags_list, source)
    """
    themes: list[str] = []
    # Topic-Cluster fuer Theme-Match (nicht fuer Hashtag-Calls)
    cluster_path = (
        workspace
        / "05-reference"
        / "competitor-content"
        / "_ai_analysis"
        / f"{_self_handle()}_topics.json"
    )
    if cluster_path.exists():
        try:
            data = json.loads(cluster_path.read_text(encoding="utf-8"))
            cluster_themes, _ = _extract_themes_from_cluster(data)
            themes = cluster_themes
        except Exception as e:
            logging.warning(f"Topic-Cluster konnte nicht gelesen werden: {e}")

    if not themes:
        themes = list(FALLBACK_HASHTAGS)

    hashtags = list(FALLBACK_HASHTAGS)
    logging.info(f"Themen: {themes} | Hashtag-Calls: {hashtags}")
    return themes, hashtags, "focused_pool"


def _extract_themes_from_cluster(data) -> tuple[list[str], list[str]]:
    """Versucht Themen + Hashtags aus Cluster-JSON zu ziehen.
    Format ist nicht hart spezifiziert; wir akzeptieren mehrere Varianten."""
    themes: list[str] = []
    hashtags: list[str] = []

    # Variante A: Liste von Cluster-Dicts
    if isinstance(data, list):
        for entry in data:
            if isinstance(entry, dict):
                t = entry.get("name") or entry.get("topic") or entry.get("label")
                if t:
                    themes.append(str(t))
                for h in (entry.get("hashtags") or entry.get("tags") or []):
                    hashtags.append(str(h).lstrip("#"))

    # Variante B: Dict mit "clusters" oder "topics"
    elif isinstance(data, dict):
        clusters = data.get("clusters") or data.get("topics") or []
        for entry in clusters:
            if isinstance(entry, dict):
                t = entry.get("name") or entry.get("topic") or entry.get("label")
                if t:
                    themes.append(str(t))
                for h in (entry.get("hashtags") or entry.get("tags") or []):
                    hashtags.append(str(h).lstrip("#"))
        # Falls top-level "hashtags" vorhanden
        for h in (data.get("hashtags") or []):
            hashtags.append(str(h).lstrip("#"))

    # Dedup, Lowercase, Hashtag-Kandidaten saeubern
    themes = _dedup_keep_order([t.strip() for t in themes if t and t.strip()])[:8]
    hashtags = _clean_hashtags(hashtags)[:MAX_HASHTAG_CALLS]
    return themes, hashtags


def _hashtags_from_latest_snapshot(workspace: Path, handle: str) -> list[str]:
    """Liest neuesten _data/<datum>.json und holt top_hashtags fuer handle."""
    data_dir = workspace / "05-reference" / "competitor-content" / "_data"
    if not data_dir.exists():
        return []
    snapshots = sorted(data_dir.glob("*.json"), reverse=True)
    for snap in snapshots:
        try:
            d = json.loads(snap.read_text(encoding="utf-8"))
        except Exception:
            continue
        creator = (d.get("creators") or {}).get(handle) or {}
        top = creator.get("top_hashtags") or []
        if not top:
            continue
        tags = [t.get("tag") if isinstance(t, dict) else t for t in top]
        cleaned = _clean_hashtags([str(t) for t in tags if t])
        if cleaned:
            return cleaned[:MAX_HASHTAG_CALLS]
    return []


def _clean_hashtags(tags: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for t in tags:
        t = re.sub(r"[^a-z0-9_]", "", t.lower().lstrip("#"))
        if not t or len(t) < 2 or len(t) > 50:
            continue
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out


def _dedup_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        k = x.lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(x)
    return out


# ---------- Apify Hashtag-Fetch ----------

def _fetch_hashtag_top_reels(
    client: ApifyClient,
    hashtag: str,
    limit: int = HASHTAG_RESULTS_PER_TAG,
    timeout: int = APIFY_TIMEOUT_SECS,
) -> list[dict]:
    """Apify-Hashtag-Scraper mit 1x Retry. Wirft bei Hard-Error."""
    run_input = {"hashtags": [hashtag], "resultsLimit": limit}
    last_err: Exception | None = None
    for attempt in (1, 2):
        try:
            run = client.actor(HASHTAG_ACTOR_ID).call(
                run_input=run_input, timeout_secs=timeout
            )
            if not run or not run.get("defaultDatasetId"):
                raise RuntimeError(
                    f"Actor-Run ohne Dataset (status={run.get('status') if run else 'None'})"
                )
            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            return items
        except Exception as e:
            last_err = e
            logging.warning(
                f"Hashtag #{hashtag} Versuch {attempt} fehlgeschlagen: {str(e)[:200]}"
            )
            if attempt < 2:
                time.sleep(8)
    raise last_err if last_err else RuntimeError("Hashtag-Fetch fehlgeschlagen")


# ---------- Reel-Helfer ----------

def _get_views(reel: dict) -> int:
    return int(
        reel.get("videoPlayCount")
        or reel.get("videoViewCount")
        or reel.get("playCount")
        or reel.get("viewCount")
        or 0
    )


def _engagement_rate(reel: dict) -> float:
    views = _get_views(reel)
    if not views:
        return 0.0
    likes = reel.get("likesCount") or 0
    comments = reel.get("commentsCount") or 0
    return (likes + comments) / views * 100


def _get_username(reel: dict) -> str:
    return (
        reel.get("ownerUsername")
        or reel.get("owner_username")
        or (reel.get("owner") or {}).get("username")
        or ""
    ).strip().lower()


def _get_caption(reel: dict) -> str:
    return (reel.get("caption") or reel.get("text") or "").strip()


def _get_url(reel: dict) -> str:
    if reel.get("url"):
        return reel["url"]
    sc = reel.get("shortCode") or reel.get("shortcode") or ""
    return f"https://www.instagram.com/reel/{sc}/" if sc else ""


def _get_timestamp(reel: dict):
    raw = reel.get("timestamp") or reel.get("takenAtTimestamp") or reel.get("takenAt")
    if not raw:
        return None
    try:
        if isinstance(raw, (int, float)):
            return datetime.fromtimestamp(raw, tz=timezone.utc)
        if isinstance(raw, str):
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        return None
    return None


def _detect_language(caption: str) -> str:
    """Heuristisch dt./en. ueber Stopword-Treffer."""
    if not caption:
        return "unknown"
    tokens = re.findall(r"[a-zA-Zaeoeueszaeoeue]+", caption.lower())
    if len(tokens) < 5:
        return "unknown"
    de_hits = sum(1 for t in tokens if t in DE_STOPWORDS)
    if de_hits >= 3:
        return "de"
    # Wenig dt. Stopwords + ueberwiegend ASCII -> en
    if de_hits == 0 and len(tokens) >= 8:
        return "en"
    if de_hits >= 1:
        return "de"
    return "unknown"


def _theme_match_score(captions: list[str], themes: list[str]) -> float:
    """Wie stark deckt sich der Caption-Pool des Creators mit den Themen?
    Score 0..1: Anteil der Themen, die mind. 1x in einer Caption vorkommen."""
    if not themes or not captions:
        return 0.0
    blob = " ".join(captions).lower()
    hits = 0
    for t in themes:
        # Einzelne Tokens des Themas pruefen, mind. 1 muss matchen
        parts = [p for p in re.split(r"[\s_\-/]+", t.lower()) if len(p) >= 3]
        if not parts:
            continue
        if any(p in blob for p in parts):
            hits += 1
    return hits / len(themes)


# ---------- Scoring ----------

def _score_candidate(
    creator_data: dict,
    themes: list[str],
    own_creators_set: set[str],
) -> float:
    """Liefert Score 0..100. Themes-Match wird bereits in creator_data['theme_match'] erwartet."""
    if creator_data["handle"].lower() in own_creators_set:
        return 0.0
    er = float(creator_data.get("avg_engagement_rate") or 0.0)
    # ER auf 0..1 normieren: 10% ER = full score
    er_norm = min(er / 10.0, 1.0)
    theme_match = float(creator_data.get("theme_match") or 0.0)  # 0..1
    recency_days = creator_data.get("recency_days")
    if recency_days is None:
        recency_norm = 0.0
    else:
        # 0 Tage = 1.0, 30 Tage = 0.0, linear
        recency_norm = max(0.0, 1.0 - (recency_days / 30.0))
    score = (er_norm * 0.4 + theme_match * 0.4 + recency_norm * 0.2) * 100
    return round(score, 2)


# ---------- AI-Enrichment ----------

def _load_niche_for_prompt() -> dict:
    """Liest Niche-Konfig fuer Sonnet-Prompts. Fallback: generisch."""
    niche_path = VAULT_ROOT / "niche.yaml"
    if niche_path.exists():
        try:
            data = yaml.safe_load(niche_path.read_text(encoding="utf-8")) or {}
            return {
                "name": (data.get("niche_name") or "").strip() or "dem User-Markt",
                "description": (data.get("niche_description") or "").strip(),
            }
        except Exception:
            pass
    return {"name": "dem User-Markt", "description": ""}


def _reel_enrich_system_prompt() -> str:
    niche = _load_niche_for_prompt()
    return (
        f"Du bist ein Content-Analyst fuer Instagram-Reels. Du erhaeltst eine Liste "
        f"von Top-Reels (Caption + KPIs) aus dem Markt: {niche['name']}. Pro Reel "
        "lieferst du eine knappe Analyse, was der Reel zeigt und warum er funktioniert.\n\n"
        "SPRACHE: Deutsch mit echten Umlauten (ae, oe, ue, ss). Keine Gedankenstriche, "
        "keine Floskeln. Du antwortest IMMER mit einem JSON-Array."
    )


REEL_ENRICH_SYSTEM = _reel_enrich_system_prompt()


def _enrich_discovered_top_reels(candidates: list[dict], anthropic_client) -> list[dict]:
    """Haiku-Pass über die top_reels aller Kandidaten. Pro Reel: topic_tag,
    hook_type, hook_score, summary. Auf Fehler: candidates unverändert.

    Batched: alle Reels über alle Kandidaten in einem Call.
    Cost: ~$0.10 für 11 Creators × 3 Reels.
    """
    if not candidates or anthropic_client is None:
        return candidates

    # Sammle alle Reels mit Verweis auf (creator_idx, reel_idx)
    reels_flat: list[tuple[int, int, dict]] = []
    for ci, c in enumerate(candidates):
        for ri, r in enumerate(c.get("top_reels") or []):
            reels_flat.append((ci, ri, r))
    if not reels_flat:
        return candidates

    lines = []
    for i, (ci, ri, r) in enumerate(reels_flat, 1):
        cap = (r.get("caption_snippet") or "").replace("\n", " ")[:220]
        er = r.get("engagement_rate", 0)
        vw = r.get("views", 0)
        handle = candidates[ci].get("handle", "")
        lines.append(
            f"{i}. @{handle} (ER {er}%, {vw} views): {cap}"
        )

    user_msg = (
        f"Hier {len(reels_flat)} Top-Reels aus dem Markt. Pro Reel: kurze Analyse.\n\n"
        + "\n".join(lines)
        + "\n\nOutput: JSON-Array mit genau "
        + str(len(reels_flat))
        + " Objekten in der Reihenfolge oben. Schema pro Objekt:\n"
        '{\n'
        '  "topic_tag": "Hauptthema in 1-2 Worten",\n'
        '  "hook_type": "Frage | Provokation | Pattern-Interrupt | Story | Zahlen-Hook | Visual-Hook | Sonstiges",\n'
        '  "hook_score": 1-10 (int, 5=Standard, 7+=stark),\n'
        '  "summary": "1 Satz max 200 Zeichen: was zeigt/sagt der Reel"\n'
        "}\n\nNur das Array."
    )

    model = "claude-haiku-4-5-20251001"
    try:
        resp = anthropic_client.messages.create(
            model=model,
            max_tokens=4000,
            system=REEL_ENRICH_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = " ".join(
            b.text for b in resp.content if getattr(b, "type", "") == "text"
        ).strip()
        m = re.search(r"\[.*\]", text, re.DOTALL)
        if not m:
            logging.warning("Reel-Enrich: kein JSON-Array")
            return candidates
        parsed = json.loads(m.group(0))
        if not isinstance(parsed, list) or len(parsed) != len(reels_flat):
            logging.warning(
                f"Reel-Enrich: Länge mismatch ({len(parsed)} vs {len(reels_flat)})"
            )
            return candidates
        for (ci, ri, r), obj in zip(reels_flat, parsed):
            if not isinstance(obj, dict):
                continue
            try:
                hs = int(obj.get("hook_score") or 0)
            except (TypeError, ValueError):
                hs = 0
            r["topic_tag"] = str(obj.get("topic_tag") or "").strip()[:40]
            r["hook_type"] = str(obj.get("hook_type") or "").strip()[:40]
            r["hook_score"] = max(0, min(10, hs)) if hs else None
            r["summary"] = str(obj.get("summary") or "").strip()[:300]
        logging.info(
            f"Reel-Enrich: {len(reels_flat)} Reels durch Haiku angereichert"
        )
        return candidates
    except Exception as e:
        logging.warning(f"Reel-Enrich fehlgeschlagen: {str(e)[:200]}")
        return candidates


def _similarity_system_prompt() -> str:
    niche = _load_niche_for_prompt()
    profile_block = ""
    if niche["description"]:
        profile_block = f"\n\nUSER-PROFIL:\n{niche['description']}\n"
    return (
        f"Du bewertest Instagram-Creator als potenzielle Marktanalyse fuer einen "
        f"User im Markt: {niche['name']}.{profile_block}\n"
        "AEHNLICHKEITS-SKALA (0-100, sei konsistent):\n"
        "- 90-100: verkauft ein direktes Konkurrenzprodukt (gleiche Methodik, gleiches Angebot).\n"
        "- 70-89: extrem aehnliche Content-Nische, direkte Inspiration.\n"
        "- 50-69: angrenzender Markt, ueberlappende Themen aber anderes Produkt-Framing.\n"
        "- 30-49: nur teilweise relevant, generischer Content im Umfeld.\n"
        "- 0-29: nicht relevant, anderer Markt.\n\n"
        "Du antwortest IMMER mit einem einzelnen JSON-Array, niemals mit Markdown, "
        "niemals mit Code-Fences. Sprache: Deutsch mit echten Umlauten (ae, oe, ue, ss). "
        "Keine Gedankenstriche."
    )


SIMILARITY_SYSTEM = _similarity_system_prompt()


def _enrich_with_ai(candidates: list[dict], anthropic_client) -> list[dict]:
    """Sonnet bewertet die Top-Liste auf Aehnlichkeit zu Moritz' Profil.

    Pro Creator: similarity_score (0-100) plus 1 Satz Begruendung.
    Output ersetzt das alte ai_reason-Feld. Auf Fehler: candidates unveraendert."""
    if not candidates or anthropic_client is None:
        return candidates

    summary_lines = []
    for i, c in enumerate(candidates, 1):
        cap = (c.get("sample_caption_snippet") or "").replace("\n", " ")[:240]
        # Top-Captions aus den 3 besten Reels als zusaetzlicher Kontext
        top_caps = []
        for tr in (c.get("top_reels") or [])[:2]:
            t = (tr.get("caption_snippet") or "").strip()
            if t:
                top_caps.append(t[:140])
        top_block = " | TOP-REELS: " + " // ".join(top_caps) if top_caps else ""
        summary_lines.append(
            f"{i}. @{c['handle']} (lang={c['language']}, "
            f"ER={c['avg_engagement_rate']}%, "
            f"posts_seen={c['post_count_seen']}, avg_views={c['avg_views']}): "
            f"{cap}{top_block}"
        )

    niche = _load_niche_for_prompt()
    user_msg = (
        f"Bewerte folgende {len(candidates)} Instagram-Creator auf Aehnlichkeit zum "
        f"User-Profil im Markt: {niche['name']}. "
        "Nutze die Skala 0-100 aus deinem System-Prompt.\n\n"
        f"Liste:\n" + "\n".join(summary_lines) + "\n\n"
        "Output: JSON-Array mit genau " + str(len(candidates)) + " Objekten, "
        "Reihenfolge wie oben. Schema pro Objekt:\n"
        "{\n"
        '  "similarity_score": 0-100 (int, Skala siehe System),\n'
        '  "similarity_reason": "1 Satz max 220 Zeichen, sachlich, warum dieser Score"\n'
        "}\n\n"
        "Nur das Array, nichts drumherum."
    )

    model = "claude-sonnet-4-6-20251001"
    last_err: Exception | None = None
    for attempt in (model, "claude-sonnet-4-6"):
        try:
            resp = anthropic_client.messages.create(
                model=attempt,
                max_tokens=2200,
                system=SIMILARITY_SYSTEM,
                messages=[{"role": "user", "content": user_msg}],
            )
            text_parts = []
            for block in resp.content:
                if getattr(block, "type", None) == "text":
                    text_parts.append(block.text)
            text = " ".join(text_parts).strip()
            m = re.search(r"\[.*\]", text, re.DOTALL)
            if not m:
                logging.warning("Similarity-Pass: kein JSON-Array im Output")
                return candidates
            parsed = json.loads(m.group(0))
            if not isinstance(parsed, list) or len(parsed) != len(candidates):
                logging.warning(
                    f"Similarity-Pass: Laenge mismatch ({len(parsed)} vs {len(candidates)})"
                )
                return candidates
            for c, obj in zip(candidates, parsed):
                if not isinstance(obj, dict):
                    continue
                try:
                    sc_val = int(obj.get("similarity_score") or 0)
                except (TypeError, ValueError):
                    sc_val = 0
                c["similarity_score"] = max(0, min(100, sc_val))
                c["similarity_reason"] = str(obj.get("similarity_reason") or "").strip()[:240]
                # Backward-compat: ai_reason mit der Reason fuellen
                c["ai_reason"] = c["similarity_reason"]
            return candidates
        except Exception as e:
            last_err = e
            err_str = str(e).lower()
            if "not_found" in err_str or "404" in err_str:
                logging.warning(f"Sonnet-Modell {attempt} nicht verfuegbar, Fallback")
                continue
            logging.warning(f"Similarity-Pass fehlgeschlagen ({attempt}): {str(e)[:200]}")
            return candidates
    logging.warning(f"Kein Sonnet-Modell verfuegbar: {last_err}")
    return candidates


# ---------- Discovery-Hauptlogik ----------

def discover_creators(
    client: ApifyClient,
    anthropic_client,
    config: dict,
    output_path: Path,
    force: bool = False,
) -> dict:
    """Fuehrt den Discovery-Run aus. Cached 7 Tage in output_path.

    Gibt Dict im definierten Schema zurueck. Schreibt es auch nach output_path.
    """
    # Cache-Check
    if output_path.exists() and not force:
        try:
            stat = output_path.stat()
            age = datetime.now() - datetime.fromtimestamp(stat.st_mtime)
            if age < timedelta(days=CACHE_TTL_DAYS):
                logging.info(
                    f"Cache hit ({age.days}d alt < {CACHE_TTL_DAYS}d), "
                    "skip Discovery. Mit --force zum Erzwingen."
                )
                return json.loads(output_path.read_text(encoding="utf-8"))
        except Exception as e:
            logging.warning(f"Cache-Check fehlgeschlagen: {e}")

    own_creators = [c.lower() for c in (config.get("creators") or [])]
    own_set = set(own_creators)
    logging.info(f"Eigene Creators (filter out): {len(own_set)}")

    themes, hashtags, source = _load_themes(VAULT_ROOT)
    hashtags = hashtags[:MAX_HASHTAG_CALLS]  # Hard-Cap
    logging.info(f"Themen-Source: {source} | Hashtags: {hashtags}")

    discovered_at = datetime.now().replace(microsecond=0).isoformat()
    stats = {"apify_calls": 0, "hashtag_searches": 0, "ai_calls": 0}
    apify_errors: list[str] = []

    # Pro Hashtag: Top-Reels sammeln
    creator_pool: dict[str, dict] = {}
    for tag in hashtags:
        if stats["hashtag_searches"] >= MAX_HASHTAG_CALLS:
            logging.info("Hard-Cap fuer Hashtag-Calls erreicht, stop.")
            break
        logging.info(f"Apify Hashtag-Call: #{tag}")
        try:
            stats["apify_calls"] += 1
            stats["hashtag_searches"] += 1
            reels = _fetch_hashtag_top_reels(client, tag)
            logging.info(f"#{tag}: {len(reels)} Reels erhalten")
        except Exception as e:
            err = f"#{tag}: {str(e)[:200]}"
            apify_errors.append(err)
            logging.error(f"Hashtag-Call gescheitert: {err}")
            # Wenn Apify-Hard-Limit: weitere Calls sind sinnlos
            if "hard limit" in str(e).lower() or "usage" in str(e).lower():
                logging.error("Apify-Limit erreicht, breche Hashtag-Loop ab")
                break
            continue

        # Reels -> Creator-Buckets
        for r in reels:
            user = _get_username(r)
            if not user or user in own_set:
                continue
            bucket = creator_pool.setdefault(
                user,
                {
                    "handle": user,
                    "reels": [],
                    "captions": [],
                },
            )
            bucket["reels"].append(r)
            cap = _get_caption(r)
            if cap:
                bucket["captions"].append(cap)

    creators_total = len(creator_pool)
    logging.info(f"Creators discovered total (vor Filter): {creators_total}")

    # Pro Creator: Aggregat + Score berechnen
    candidates: list[dict] = []
    now = datetime.now(tz=timezone.utc)
    for user, bucket in creator_pool.items():
        reels = bucket["reels"]
        if not reels:
            continue

        ers = [_engagement_rate(r) for r in reels]
        avg_er = round(sum(ers) / len(ers), 2) if ers else 0.0
        views_list = [_get_views(r) for r in reels]
        avg_views = round(sum(views_list) / len(views_list)) if views_list else 0

        # Recency = juengster Post
        timestamps = [_get_timestamp(r) for r in reels]
        timestamps = [t for t in timestamps if t is not None]
        recency_days: int | None = None
        if timestamps:
            newest = max(timestamps)
            recency_days = max(0, (now - newest).days)

        # Sample-Reel = staerkstes ER
        best_idx = max(range(len(reels)), key=lambda i: ers[i]) if reels else 0
        sample_reel = reels[best_idx]
        sample_url = _get_url(sample_reel)
        sample_caption = _get_caption(sample_reel)
        snippet = re.sub(r"\s+", " ", sample_caption).strip()[:180]

        # Sprache aus laengster Caption ableiten
        if bucket["captions"]:
            longest = max(bucket["captions"], key=len)
            language = _detect_language(longest)
        else:
            language = "unknown"

        theme_match = _theme_match_score(bucket["captions"], themes)

        # Top-3 Reels nach ER fuer "Empfehlung-fuers-naechste-Reel"
        scored_reels = sorted(
            zip(reels, ers, views_list),
            key=lambda x: x[1],
            reverse=True,
        )
        top_reels_out = []
        for rl, er, vw in scored_reels[:TOP_REELS_PER_CREATOR]:
            cap = re.sub(r"\s+", " ", _get_caption(rl)).strip()
            top_reels_out.append({
                "url": _get_url(rl),
                "shortcode": rl.get("shortCode") or rl.get("shortcode") or "",
                "views": vw,
                "likes": rl.get("likesCount") or 0,
                "comments": rl.get("commentsCount") or 0,
                "engagement_rate": round(er, 2),
                "caption_snippet": cap[:180],
            })

        cand = {
            "handle": user,
            "follower_count_estimate": 0,  # Hashtag-Scraper liefert das nicht zuverlaessig
            "post_count_seen": len(reels),
            "avg_views": avg_views,
            "avg_engagement_rate": avg_er,
            "theme_match": round(theme_match, 2),
            "recency_days": recency_days,
            "language": language,
            "sample_reel_url": sample_url,
            "sample_caption_snippet": snippet,
            "ai_reason": "",
            "similarity_score": 0,
            "similarity_reason": "",
            "top_reels": top_reels_out,
        }
        cand["score"] = _score_candidate(cand, themes, own_set)
        candidates.append(cand)

    # Sort by score, Top N
    candidates.sort(key=lambda c: c["score"], reverse=True)
    top_candidates = candidates[:TOP_N_OUTPUT]
    logging.info(
        f"Candidates nach Filter: {len(candidates)} | "
        f"Top {TOP_N_OUTPUT}: {[c['handle'] for c in top_candidates]}"
    )

    # AI-Enrichment fuer Top N: Sonnet vergibt similarity_score (0-100) + Begruendung
    dropped_irrelevant = 0
    if top_candidates and anthropic_client is not None:
        stats["ai_calls"] += 1
        top_candidates = _enrich_with_ai(top_candidates, anthropic_client)
        # Final-Ranking: similarity_score gewichtet doppelt zum klassischen Score
        for c in top_candidates:
            sim = c.get("similarity_score", 0) or 0
            base = c.get("score", 0) or 0
            c["final_score"] = round(sim * 0.7 + base * 0.3, 2)
        # Hard-Filter: similarity_score < 40 raus, irrelevant fuer Markt-Analyse
        before = len(top_candidates)
        top_candidates = [c for c in top_candidates if (c.get("similarity_score") or 0) >= 40]
        dropped_irrelevant = before - len(top_candidates)
        top_candidates.sort(key=lambda c: c.get("final_score", 0), reverse=True)
        logging.info(
            f"Hard-Filter similarity<40: {dropped_irrelevant} Kandidaten verworfen, "
            f"{len(top_candidates)} bleiben relevant"
        )

    stats["dropped_irrelevant"] = dropped_irrelevant

    # Haiku-Pass: jedes top_reel der überlebenden Creator bekommt
    # topic_tag, hook_type, hook_score, summary
    if top_candidates and anthropic_client is not None:
        stats["ai_calls"] = (stats.get("ai_calls") or 0) + 1
        top_candidates = _enrich_discovered_top_reels(top_candidates, anthropic_client)

    result = {
        "discovered_at": discovered_at,
        "themes_used": themes,
        "themes_source": source,
        "hashtags_searched": hashtags,
        "creators_discovered_total": creators_total,
        "creators_after_filter": len(candidates),
        "candidates_dropped_irrelevant": dropped_irrelevant,
        "candidates": top_candidates,
        "stats": stats,
        "apify_errors": apify_errors,
    }

    # Schreiben (auch bei leerem Result, damit Datei existiert)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logging.info(f"Discovery-Result geschrieben: {output_path}")
    return result


# ---------- CLI ----------

def main():
    parser = argparse.ArgumentParser(description="Creator-Discovery fuer AIOS")
    parser.add_argument(
        "--force", action="store_true",
        help="Cache ignorieren und Discovery erzwingen.",
    )
    parser.add_argument(
        "--output",
        default=str(VAULT_ROOT / "data" / "creator_discovery.json"),
        help="Output-Pfad fuer die JSON-Datei.",
    )
    args = parser.parse_args()

    setup_logging()

    apify_token = os.getenv("APIFY_API_TOKEN")
    if not apify_token:
        logging.error(f"APIFY_API_TOKEN fehlt in {VAULT_ROOT / '.env'}")
        sys.exit(1)

    config = load_tracker_config()
    client = ApifyClient(apify_token)

    anthropic_client = None
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            from anthropic import Anthropic
            anthropic_client = Anthropic()
        except Exception as e:
            logging.warning(f"Anthropic-Client Init fehlgeschlagen: {e}")
    else:
        logging.warning("ANTHROPIC_API_KEY fehlt, AI-Enrichment deaktiviert")

    output_path = Path(args.output)
    started = time.time()
    try:
        result = discover_creators(
            client, anthropic_client, config, output_path, force=args.force
        )
    except Exception as e:
        # Robuster Fallback: leere Datei + Fehler-Log
        logging.exception(f"Discovery fatal gescheitert: {e}")
        fallback = {
            "discovered_at": datetime.now().replace(microsecond=0).isoformat(),
            "themes_used": [],
            "themes_source": "error",
            "hashtags_searched": [],
            "creators_discovered_total": 0,
            "creators_after_filter": 0,
            "candidates": [],
            "stats": {"apify_calls": 0, "hashtag_searches": 0, "ai_calls": 0},
            "apify_errors": [str(e)[:300]],
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(fallback, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        sys.exit(2)

    duration = time.time() - started
    print(
        f"Done in {int(duration)}s. "
        f"Themes={result['themes_source']} "
        f"Hashtags={len(result['hashtags_searched'])} "
        f"Found={result['creators_discovered_total']} "
        f"Top={len(result['candidates'])} "
        f"Output={output_path}"
    )
    if result.get("apify_errors"):
        print(f"Apify-Errors: {result['apify_errors']}")


if __name__ == "__main__":
    main()
