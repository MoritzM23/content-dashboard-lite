#!/usr/bin/env python3
"""TikTok-Tracker: Pendant zum Instagram-Tracker.

Holt die Videos eines (oder mehrerer) TikTok-Profile via Apify-Actor
`clockworks/tiktok-scraper`, normalisiert sie ins selbe Reel-Schema wie der
Instagram-Tracker (views, likes, comments, shares, posted_at, ...) und
schreibt:
  1. Tages-JSON-Snapshot nach `output_dir/_data/<date>.json`
  2. Time-Series in `data/reel_history.db` (Handle bekommt Suffix '@tiktok'
     damit IG- und TT-Shortcodes nicht kollidieren)

Default-Cadence: 1x/Tag morgens via launchd (com.aios.tiktok-tracker.plist).
Kosten (Apify-Guthaben): ca. 0,01 USD pro Run bei ~30 eigenen Videos.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml
from apify_client import ApifyClient

WORKSPACE = Path(__file__).resolve().parent.parent
CONFIG_PATH = WORKSPACE / "scripts" / "tiktok_tracker_config.yaml"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)


def load_dotenv():
    """Laedt .env aus dem Workspace-Root, damit APIFY_API_TOKEN verfuegbar ist."""
    env_path = WORKSPACE / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        if k and k.strip() not in os.environ:
            os.environ[k.strip()] = v.strip().strip("'\"")


def load_config() -> dict:
    """Liest tracker-config + ueberschreibt self_handle aus niche.yaml."""
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    niche_path = WORKSPACE / "niche.yaml"
    if niche_path.exists():
        niche = yaml.safe_load(niche_path.read_text(encoding="utf-8")) or {}
        tt = (niche.get("tiktok_handle") or "").strip()
        if tt:
            config["self_handle"] = tt
    return config


def normalize_video(raw: dict, handle: str) -> dict:
    """Apify-Actor-Output -> unser Reel-Schema.

    Felder die clockworks/tiktok-scraper zurueckgibt (Auszug):
      id, text, createTime, playCount, diggCount, commentCount, shareCount,
      collectCount (Saves!), webVideoUrl, authorMeta, videoMeta, hashtags, ...
    """
    shortcode = raw.get("id") or ""
    created_ts = raw.get("createTime") or 0
    posted_dt = (
        datetime.fromtimestamp(int(created_ts), tz=timezone.utc)
        if created_ts
        else None
    )

    return {
        "shortcode": str(shortcode),
        "url": raw.get("webVideoUrl") or "",
        "posted": posted_dt.strftime("%Y-%m-%d") if posted_dt else "",
        "posted_at": posted_dt.isoformat() if posted_dt else "",
        "posted_hour": posted_dt.hour if posted_dt else None,
        "posted_dayofweek": posted_dt.strftime("%A") if posted_dt else "",
        "views": int(raw.get("playCount") or 0),
        "plays": int(raw.get("playCount") or 0),
        "likes": int(raw.get("diggCount") or 0),
        "comments": int(raw.get("commentCount") or 0),
        "shares": int(raw.get("shareCount") or 0),
        # collectCount = TikTok-Saves. Im Gegensatz zu Instagram public verfuegbar.
        "saves": int(raw.get("collectCount") or 0),
        "video_duration": (raw.get("videoMeta") or {}).get("duration"),
        "hashtags": [
            h.get("name") for h in (raw.get("hashtags") or []) if h.get("name")
        ],
        "caption_full": raw.get("text") or "",
        "caption_snippet": (raw.get("text") or "")[:300],
        "handle": handle,
        "engagement_rate": _compute_er(raw),
    }


def _compute_er(raw: dict) -> float:
    views = int(raw.get("playCount") or 0)
    if not views:
        return 0.0
    likes = int(raw.get("diggCount") or 0)
    comments = int(raw.get("commentCount") or 0)
    return round((likes + comments) / views * 100, 2)


def scrape_handle(client: ApifyClient, handle: str, limit: int, actor: str, timeout_s: int) -> list[dict]:
    logging.info(f"Scrape @{handle} (limit={limit}) via {actor}")
    run_input = {
        "profiles": [handle],
        "resultsPerPage": limit,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSubtitles": False,
        "shouldDownloadSlideshowImages": False,
        "proxyConfiguration": {"useApifyProxy": True},
    }
    run = client.actor(actor).call(run_input=run_input, timeout_secs=timeout_s)
    if not run:
        logging.error(f"Apify-Run fuer @{handle} hat kein Ergebnis geliefert")
        return []
    dataset_id = run.get("defaultDatasetId")
    if not dataset_id:
        logging.error(f"Kein dataset_id in Apify-Run-Antwort fuer @{handle}")
        return []
    items = list(client.dataset(dataset_id).iterate_items())
    logging.info(f"@{handle}: {len(items)} Videos vom Actor")
    return items


def write_snapshot(all_data: dict, output_dir: Path, date_str: str, run_started_iso: str, duration_s: float, self_handle: str) -> Path:
    data_dir = output_dir / "_data"
    data_dir.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "date": date_str,
        "run_started": run_started_iso,
        "run_duration_seconds": round(duration_s, 1),
        "platform": "tiktok",
        "self_handle": self_handle,
        "creators_total": len(all_data),
        "videos_total": sum(len(v) for v in all_data.values()),
        "creators": {
            handle: {
                "handle": handle,
                "reels": reels,  # gleicher Key wie Instagram, damit Downstream
                                 # einheitlich konsumieren kann
                "reels_count": len(reels),
            }
            for handle, reels in all_data.items()
        },
    }
    path = data_dir / f"{date_str}.json"
    path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main():
    load_dotenv()
    config = load_config()
    self_handle = config["self_handle"]
    all_handles = [self_handle] + list(config.get("tracked_handles") or [])
    limit = int(config.get("videos_per_handle", 50))
    actor = config["apify_actor"]
    timeout_s = int(config.get("apify_run_timeout", 300))
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    token = os.getenv("APIFY_API_TOKEN")
    if not token:
        print("FEHLER: APIFY_API_TOKEN nicht in .env gefunden", file=sys.stderr)
        sys.exit(1)
    client = ApifyClient(token)

    started = time.time()
    run_started_iso = datetime.now(timezone.utc).isoformat()
    date_str = datetime.now().strftime("%Y-%m-%d")

    all_data: dict[str, list[dict]] = {}
    for handle in all_handles:
        try:
            raw_items = scrape_handle(client, handle, limit, actor, timeout_s)
            normalized = [normalize_video(r, handle) for r in raw_items if r.get("id")]
            all_data[handle] = normalized
            logging.info(f"@{handle}: {len(normalized)} normalisierte Videos")
        except Exception as e:
            logging.error(f"@{handle} fehlgeschlagen: {str(e)[:200]}")
            all_data[handle] = []

    duration = time.time() - started
    snapshot_path = write_snapshot(
        all_data, output_dir, date_str, run_started_iso, duration, self_handle
    )
    logging.info(f"Snapshot: {snapshot_path}")

    # Time-Series in reel_history.db schreiben. Handle bekommt '@tiktok'-Suffix,
    # damit derselbe Shortcode auf IG und TT nicht kollidiert (auch wenn das in
    # der Praxis nicht vorkommt, sauberer Namespacing).
    try:
        sys.path.insert(0, str(WORKSPACE / "scripts"))
        from reel_history import upsert_snapshot as _rh_upsert  # type: ignore
        rh_rows = 0
        for handle, reels in all_data.items():
            if reels:
                rh_rows += _rh_upsert(f"{handle}@tiktok", reels, date_str)
        logging.info(f"Reel-History: {rh_rows} Rows (TikTok)")
    except Exception as e:
        logging.warning(f"Reel-History-Write (TikTok) fehlgeschlagen: {str(e)[:160]}")

    total_videos = sum(len(v) for v in all_data.values())
    logging.info(f"FERTIG. {len(all_handles)} Handles, {total_videos} Videos, {round(duration,1)}s")


if __name__ == "__main__":
    main()
