#!/usr/bin/env python3
"""Time-Series-Persistierung für Instagram-Reels.

Hintergrund: Der Tracker zieht pro Run nur eine begrenzte Anzahl Reels und
schreibt Tages-Snapshots als JSON. Ältere Reels fallen aus dem Tracking-Fenster
und damit ist die View-Akkumulation pro Reel über Wochen nicht direkt sichtbar.

Dieses Modul speichert für jeden Tracker-Run pro Reel die aktuellen
KPI-Zahlen (views, likes, comments) in eine SQLite-DB. Daraus lassen sich
echte rolling 7d/30d-Deltas berechnen, die im Dashboard die korrekte
"neue Views in den letzten N Tagen über ALLE Reels" zeigen.

Schema:
    reel_history (
        shortcode TEXT,
        snapshot_date TEXT,  -- YYYY-MM-DD
        handle TEXT,         -- creator handle (eigene + competitors)
        views INTEGER,
        likes INTEGER,
        comments INTEGER,
        plays INTEGER,
        posted_at TEXT,      -- ISO datetime des Posts (immutable pro shortcode)
        PRIMARY KEY (shortcode, snapshot_date)
    )

Usage:
    from reel_history import upsert_snapshot, view_delta, all_reels_delta
"""
from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

WORKSPACE = Path(__file__).resolve().parent.parent
DB_PATH = WORKSPACE / "data" / "reel_history.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS reel_history (
    shortcode TEXT NOT NULL,
    snapshot_date TEXT NOT NULL,
    handle TEXT NOT NULL,
    views INTEGER,
    likes INTEGER,
    comments INTEGER,
    plays INTEGER,
    posted_at TEXT,
    PRIMARY KEY (shortcode, snapshot_date)
);
CREATE INDEX IF NOT EXISTS idx_reel_history_handle_date
    ON reel_history(handle, snapshot_date);
CREATE INDEX IF NOT EXISTS idx_reel_history_posted
    ON reel_history(posted_at);
"""


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)
    return con


def upsert_snapshot(handle: str, reels: Iterable[dict], snapshot_date: str) -> int:
    """Schreibt eine Tages-Zeile pro Reel. Idempotent dank PRIMARY KEY.

    Returns: Anzahl geschriebener/aktualisierter Rows.
    """
    con = _connect()
    rows = []
    for r in reels:
        sc = r.get("shortcode")
        if not sc:
            continue
        rows.append((
            sc,
            snapshot_date,
            handle,
            int(r.get("views") or 0),
            int(r.get("likes") or 0),
            int(r.get("comments") or 0),
            int(r.get("plays") or 0),
            r.get("posted_at") or r.get("posted") or "",
        ))
    if not rows:
        con.close()
        return 0
    con.executemany(
        """INSERT INTO reel_history
           (shortcode, snapshot_date, handle, views, likes, comments, plays, posted_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(shortcode, snapshot_date) DO UPDATE SET
              views=excluded.views,
              likes=excluded.likes,
              comments=excluded.comments,
              plays=excluded.plays,
              posted_at=COALESCE(NULLIF(excluded.posted_at,''), reel_history.posted_at)
        """,
        rows,
    )
    con.commit()
    n = con.total_changes
    con.close()
    return n


def _latest_snapshot_at_or_before(con, handle: str, target_date: str) -> dict[str, dict]:
    """Pro Reel die jüngste Zeile <= target_date. Key: shortcode."""
    cur = con.execute(
        """SELECT shortcode, views, likes, comments, plays, posted_at, snapshot_date
           FROM reel_history
           WHERE handle = ? AND snapshot_date <= ?
           ORDER BY shortcode, snapshot_date DESC""",
        (handle, target_date),
    )
    seen = {}
    for sc, v, l, c, p, posted, sd in cur:
        if sc not in seen:
            seen[sc] = {
                "views": v or 0,
                "likes": l or 0,
                "comments": c or 0,
                "plays": p or 0,
                "posted_at": posted,
                "snapshot_date": sd,
            }
    return seen


def all_reels_delta(handle: str, days: int, today: str | None = None) -> dict:
    """Berechnet "neue Views/Likes/Comments in den letzten `days` Tagen" über
    alle bekannten Reels von `handle`.

    Logik pro Reel:
      - Vorzustand = letzter Snapshot <= (today - days). Wenn keiner: 0.
      - Aktuell    = jüngster Snapshot überhaupt.
      - Delta      = max(0, aktuell - vorzustand)  (kein negativer Delta)

    Reels die in den letzten `days` Tagen gepostet wurden zählen mit ihren
    AKTUELLEN absoluten Zahlen (Vorzustand 0), was korrekt ist.

    Returns: {"count_reels": int, "views_delta": int, "likes_delta": int,
              "comments_delta": int, "window_start": date, "window_end": date}
    """
    today_dt = datetime.strptime(today, "%Y-%m-%d").date() if today else datetime.now().date()
    cutoff = today_dt - timedelta(days=days)
    today_s = today_dt.strftime("%Y-%m-%d")
    cutoff_s = cutoff.strftime("%Y-%m-%d")

    con = _connect()
    current = _latest_snapshot_at_or_before(con, handle, today_s)
    # Vorzustand: alles bis EINSCHLIESSLICH cutoff_s
    prior = _latest_snapshot_at_or_before(con, handle, cutoff_s)
    con.close()

    views_d = likes_d = comments_d = 0
    for sc, cur in current.items():
        pr = prior.get(sc)
        if pr is None:
            # Reel war am cutoff noch nicht da -> alle aktuellen Zahlen sind "neu"
            views_d += cur["views"]
            likes_d += cur["likes"]
            comments_d += cur["comments"]
        else:
            views_d += max(0, cur["views"] - pr["views"])
            likes_d += max(0, cur["likes"] - pr["likes"])
            comments_d += max(0, cur["comments"] - pr["comments"])

    return {
        "count_reels": len(current),
        "views_delta": views_d,
        "likes_delta": likes_d,
        "comments_delta": comments_d,
        "window_start": cutoff_s,
        "window_end": today_s,
    }


def view_delta(shortcode: str, days: int, today: str | None = None) -> int | None:
    """Views-Delta für ein einzelnes Reel über die letzten `days` Tage."""
    today_dt = datetime.strptime(today, "%Y-%m-%d").date() if today else datetime.now().date()
    cutoff_s = (today_dt - timedelta(days=days)).strftime("%Y-%m-%d")
    today_s = today_dt.strftime("%Y-%m-%d")

    con = _connect()
    cur_row = con.execute(
        """SELECT views FROM reel_history
           WHERE shortcode = ? AND snapshot_date <= ?
           ORDER BY snapshot_date DESC LIMIT 1""",
        (shortcode, today_s),
    ).fetchone()
    prior_row = con.execute(
        """SELECT views FROM reel_history
           WHERE shortcode = ? AND snapshot_date <= ?
           ORDER BY snapshot_date DESC LIMIT 1""",
        (shortcode, cutoff_s),
    ).fetchone()
    con.close()
    if cur_row is None:
        return None
    cur_v = cur_row[0] or 0
    prior_v = (prior_row[0] or 0) if prior_row else 0
    return max(0, cur_v - prior_v)


def backfill_from_snapshots(snapshot_dir: Path | None = None) -> dict:
    """Liest alle Tages-JSON-Snapshots aus 05-reference/competitor-content/_data
    und schreibt sie in die DB. Idempotent.
    """
    if snapshot_dir is None:
        snapshot_dir = WORKSPACE / "05-reference" / "competitor-content" / "_data"
    if not snapshot_dir.exists():
        return {"error": f"Snapshot-Dir nicht gefunden: {snapshot_dir}"}

    files = sorted(snapshot_dir.glob("*.json"))
    total_rows = 0
    snapshots_processed = 0
    creators_processed: set[str] = set()
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  skip {f.name}: {e}", file=sys.stderr)
            continue
        snap_date = data.get("date") or f.stem
        creators = data.get("creators") or {}
        for handle, c in creators.items():
            reels = c.get("reels") or []
            if not reels:
                continue
            n = upsert_snapshot(handle, reels, snap_date)
            total_rows += n
            creators_processed.add(handle)
        snapshots_processed += 1

    return {
        "snapshots_processed": snapshots_processed,
        "creators_processed": len(creators_processed),
        "rows_upserted": total_rows,
        "first_snapshot": files[0].stem if files else None,
        "last_snapshot": files[-1].stem if files else None,
    }


def stats() -> dict:
    """Quick-Look auf den DB-Zustand."""
    con = _connect()
    n_rows = con.execute("SELECT COUNT(*) FROM reel_history").fetchone()[0]
    n_reels = con.execute("SELECT COUNT(DISTINCT shortcode) FROM reel_history").fetchone()[0]
    n_handles = con.execute("SELECT COUNT(DISTINCT handle) FROM reel_history").fetchone()[0]
    date_range = con.execute(
        "SELECT MIN(snapshot_date), MAX(snapshot_date) FROM reel_history"
    ).fetchone()
    con.close()
    return {
        "rows": n_rows,
        "distinct_reels": n_reels,
        "distinct_handles": n_handles,
        "first_snapshot": date_range[0],
        "last_snapshot": date_range[1],
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("backfill", help="Liest alle vorhandenen JSON-Snapshots in die DB")
    sub.add_parser("stats", help="DB-Zustand anzeigen")
    d = sub.add_parser("delta", help="View-Delta für einen Handle berechnen")
    d.add_argument("--handle", required=True)
    d.add_argument("--days", type=int, default=30)
    args = p.parse_args()

    if args.cmd == "backfill":
        print(json.dumps(backfill_from_snapshots(), indent=2, ensure_ascii=False))
    elif args.cmd == "stats":
        print(json.dumps(stats(), indent=2, ensure_ascii=False))
    elif args.cmd == "delta":
        print(json.dumps(all_reels_delta(args.handle, args.days), indent=2, ensure_ascii=False))
