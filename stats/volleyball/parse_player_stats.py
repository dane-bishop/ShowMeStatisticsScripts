# stats/parse_player_hitting_mu.py
from __future__ import annotations
from typing import Any, Dict, List, Iterable, Optional
from datetime import datetime
import re
from stats.stats_helpers.fetch_mu_player_json import fetch_mu_player_json
from stats.stats_helpers.extract_sgid import _source_game_id_from_url
from stats.stats_helpers.clean_int import _to_double
from stats.stats_helpers.clean_int import _to_int
from stats.baseball.parse_player_hitting import _parse_dt
from stats.stats_helpers.parse_made_att import parse_made_attempted


def parse_player_volleyball_stats(payload: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:

    # ---- Game log ----
    gsrc = payload.get("currentStats", {}).get("individualStats", []) or []
    gamelog: List[Dict[str, Any]] = []

    for g in gsrc:
        dt = _parse_dt(g.get("date"))


        row = {
            # ids / linkage
            "source_game_id": _source_game_id_from_url(g.get("boxscoreUrl")),
            "game_date": dt.date().isoformat() if dt else None,
            

            # Stats
            "wl": (g.get("result") or "").strip()[:1].upper() or None,
            "sp": _to_int(g.get("setsPlayed")),
            "k": _to_int(g.get("attackKills")),
            "ae": _to_int(g.get("attackErrors")),
            "ta": _to_int(g.get("attackTotalAttempts")),
            "h_pct": _to_double(g.get("attackHittingPercentage")),
            "ast": _to_int(g.get("setAssists")),
            "e": _to_int(g.get("setErrors")),
            "sa": _to_int(g.get("serveAces")),
            "se": _to_int(g.get("serveErrors")),
            "dre": _to_int(g.get("defensiveReceptionErrors")),
            "dd": _to_int(g.get("defenseDigs")),
            "solo": _to_int(g.get("blockSolos")),
            "blk_ast": _to_int(g.get("blockAssists")),
            "blk_e": _to_int(g.get("blockErrors")),
            "tot_blk": _to_int(g.get("totalBlocks")),
            "bhe": _to_int(g.get("ballHandlingErrors")),
            "pts": _to_double(g.get("points"))

        }
        gamelog.append(row)

    # ---- Season highs ----
    hsrc = payload.get("seasonHighStats", {}) or []
    season_highs: List[Dict[str, Any]] = []
    for h in hsrc:
        dt = _parse_dt(h.get("date"))
        season_highs.append({
            "label": h.get("name"),
            "value": _to_int(h.get("value")) if str(h.get("value", "")).isdigit() else h.get("value"),
            "date": dt.date().isoformat() if dt else None,
            "opponent": h.get("opponent"),
            "source_game_id": _source_game_id_from_url(h.get("boxscoreUrl")),
        })

    return {"gamelog": gamelog, "season_highs": season_highs}




def get_player_volleyball_mu(sess, roster_player_id: int, year: int) -> Dict[str, List[Dict[str, Any]]]:
    sport = 'wvball'
    data = fetch_mu_player_json(sess, roster_player_id, year, sport)
    parsed = parse_player_volleyball_stats(data)
    print(f"[mu-json] gamelog={len(parsed['gamelog'])} highs={len(parsed['season_highs'])}")
    return parsed





