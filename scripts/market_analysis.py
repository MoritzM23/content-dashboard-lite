#!/usr/bin/env python3
"""
Market-Analyse: Sonnet schreibt eine knappe Uebersicht des Marktes,
basierend auf market_creators (tracked + discovered). Cache 24h.

Output `data/market_analysis.json`:
{
  "generated_at": "2026-05-15T12:00:00",
  "creators_input": ["mavgpt", "okemon.kosei", ...],
  "summary": "4-5 Saetze Markt-Stand",
  "themes": ["Dominante Themen im Markt", ...],
  "top_performers": ["@handle — Views, was sie machen", ...],
  "gaps": ["Was der User noch besetzen koennte"],
  "_model": "claude-sonnet-4-6"
}
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

VAULT_ROOT = Path(os.environ.get("WORKSPACE_PATH", str(Path(__file__).resolve().parent.parent)))
CACHE_PATH = VAULT_ROOT / "data" / "market_analysis.json"
CACHE_TTL_HOURS = 24
DEFAULT_MODEL = "claude-sonnet-4-6-20251001"
FALLBACK_MODEL = "claude-sonnet-4-6"

logger = logging.getLogger("market_analysis")


def _load_niche() -> dict:
    """Liest niche.yaml und gibt name + description zurueck (mit Fallback)."""
    niche_path = VAULT_ROOT / "niche.yaml"
    if niche_path.exists():
        try:
            import yaml
            data = yaml.safe_load(niche_path.read_text(encoding="utf-8")) or {}
            return {
                "name": (data.get("niche_name") or "").strip() or "deinem Markt",
                "description": (data.get("niche_description") or "").strip(),
            }
        except Exception as e:
            logger.warning(f"niche.yaml konnte nicht gelesen werden: {e}")
    return {"name": "deinem Markt", "description": ""}


def _build_system_prompt() -> str:
    niche = _load_niche()
    extra = f"\n\nKontext zu deinem Profil:\n{niche['description']}" if niche["description"] else ""
    return (
        f"Du bist ein Markt-Analyst fuer den Markt: {niche['name']}. "
        "Du erhaeltst eine Liste relevanter Instagram-Creator aus diesem Markt — "
        "getrackte Konkurrenz und neu entdeckte. Pro Creator: Aehnlichkeits-Score "
        "(0-100), Stats, Top-Reel-Captions.\n\n"
        "Schreibe eine knappe Markt-Uebersicht (4-5 Saetze) sachlich und konkret. "
        "Was sind die dominanten Themen, welche Formate funktionieren (anhand der "
        "Top-Reels), wer sticht raus und warum. Identifiziere 2-3 Themen, die der "
        "User aktiv besetzt, und 1-2 Luecken, die er noch besetzen koennte.\n\n"
        "SPRACHE: Deutsch mit echten Umlauten (ae, oe, ue, ss). Keine Gedankenstriche, "
        "kein Marketing-Sprech. Du antwortest IMMER mit einem einzelnen JSON-Objekt."
        f"{extra}"
    )


SYSTEM_PROMPT = _build_system_prompt()


def _build_anthropic_client():
    if not os.getenv("ANTHROPIC_API_KEY"):
        try:
            from dotenv import load_dotenv
            load_dotenv(VAULT_ROOT / ".env")
        except Exception:
            pass
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY nicht gesetzt")
    from anthropic import Anthropic
    return Anthropic()


def _build_user_prompt(market_creators: List[Dict[str, Any]]) -> str:
    lines = []
    for c in market_creators[:30]:  # max 30 für Context-Budget
        handle = c.get("handle")
        sim = c.get("similarity_score", 0)
        source = c.get("source", "")
        avg_v = c.get("avg_views") or 0
        avg_er = c.get("avg_engagement_rate") or 0
        reason = (c.get("similarity_reason") or "")[:150]
        top_reels = c.get("top_reels") or []
        top_block = []
        for r in top_reels[:2]:
            cap = (r.get("caption_snippet") or "")[:140]
            er = r.get("engagement_rate") or 0
            top_block.append(f"     · {er}% ER: {cap}")
        top_str = "\n".join(top_block) if top_block else ""
        lines.append(
            f"@{handle} [sim={sim} {source}] Ø {avg_v}v, ER {avg_er}% — {reason}"
            + ("\n" + top_str if top_str else "")
        )
    creators_block = "\n\n".join(lines)

    schema = (
        "{\n"
        '  "summary": "4-5 Sätze Markt-Übersicht, sachlich, konkret",\n'
        '  "themes": ["3-5 dominante Themen im Markt, kurz benannt"],\n'
        '  "top_performers": ["3-5 Bullet-Liste der besten mit @handle und 1-Wort warum"],\n'
        '  "gaps": ["1-3 Luecken die der User besetzen koennte"]\n'
        "}"
    )

    niche = _load_niche()
    return (
        f"Hier {len(market_creators)} Creator aus dem Markt: {niche['name']}.\n\n"
        f"{creators_block}\n\n"
        f"Output-Schema (nur JSON, keine Markdown-Fences):\n{schema}"
    )


def _is_cache_valid(market_creators: List[Dict[str, Any]]) -> bool:
    if not CACHE_PATH.exists():
        return False
    try:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return False
    # TTL prüfen
    gen = data.get("generated_at")
    if not gen:
        return False
    try:
        gen_dt = datetime.fromisoformat(gen)
    except Exception:
        return False
    if datetime.now() - gen_dt > timedelta(hours=CACHE_TTL_HOURS):
        return False
    # Creator-Set vergleichen (falls neue Discovery-Daten, neu rechnen)
    cached_handles = sorted(data.get("creators_input") or [])
    current_handles = sorted(c.get("handle") for c in market_creators)
    return cached_handles == current_handles


def generate(market_creators: List[Dict[str, Any]], force: bool = False) -> Optional[Dict[str, Any]]:
    if not market_creators:
        return None
    if not force and _is_cache_valid(market_creators):
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

    try:
        client = _build_anthropic_client()
    except Exception as e:
        logger.warning(f"Anthropic-Init fehlgeschlagen: {e}")
        return None

    user_msg = _build_user_prompt(market_creators)

    for model in (DEFAULT_MODEL, FALLBACK_MODEL):
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=1200,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
            )
            text = " ".join(
                b.text for b in resp.content if getattr(b, "type", "") == "text"
            ).strip()
            m = re.search(r"\{.*\}", text, re.DOTALL)
            if not m:
                logger.warning("Markt-Analyse: kein JSON-Objekt im Output")
                return None
            parsed = json.loads(m.group(0))
            out = {
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "creators_input": sorted(c.get("handle") for c in market_creators),
                "summary": str(parsed.get("summary") or "").strip(),
                "themes": list(parsed.get("themes") or [])[:6],
                "top_performers": list(parsed.get("top_performers") or [])[:6],
                "gaps": list(parsed.get("gaps") or [])[:4],
                "_model": model,
            }
            CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            CACHE_PATH.write_text(
                json.dumps(out, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return out
        except Exception as e:
            err = str(e).lower()
            if "not_found" in err or "404" in err:
                logger.warning(f"Sonnet-Modell {model} nicht verfügbar, Fallback")
                continue
            logger.warning(f"Markt-Analyse-Call fehlgeschlagen ({model}): {str(e)[:200]}")
            return None
    return None


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    dash = VAULT_ROOT / "data" / "dashboard-data.json"
    if not dash.exists():
        print("data/dashboard-data.json fehlt, erst Dashboard refreshen")
        return 1
    d = json.loads(dash.read_text(encoding="utf-8"))
    mc = (d.get("content_intel") or {}).get("market_creators") or []
    force = "--force" in sys.argv
    result = generate(mc, force=force)
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    print("Markt-Analyse fehlgeschlagen")
    return 1


if __name__ == "__main__":
    sys.exit(main())
