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


def parse_player_football_defense_from_mu(payload: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    # ---- Game log ----
    gsrc = payload.get("currentStats", {}).get("defensiveStats", []) or []
    gamelog: List[Dict[str, Any]] = []

    for g in gsrc:
        dt = _parse_dt(g.get("date"))
        



        row = {
            # ids / linkage
            "source_game_id": _source_game_id_from_url(g.get("boxscoreUrl")),
            "game_date": dt.date().isoformat() if dt else None,
            

            # Tackling
            "solo": _to_int(g.get("tacklesSolo")),
            "ast":  _to_int(g.get("tacklesAssist")),
            "ttot":  _to_int(g.get("tacklesTotal")),
            "tfl":  _to_int(g.get("tacklesForLoss")),  # store 82.1 (no % sign)
            "tyds":  _to_int(g.get("tacklesYards")),

            # Sacks
            "stot":   _to_int(g.get("sacksNumber")),
            "syds": _to_int(g.get("sacksYards")),

            # Fumbles
            "ff":  _to_int(g.get("fumblesForces")),
            "fr":  _to_int(g.get("fumblesRecoveries")),
            "fyds":   _to_int(g.get("fumblesYards")),

            #Interceptions
            "ints": _to_int(g.get("intsNumber")),
            "int_yds":   _to_int(g.get("intsYards")),

            # Others
            "qbh":   _to_int(g.get("quarterbackHurries")),
            "brk":    _to_int(g.get("passBreakups")),
            "kick":  _to_int(g.get("blockedKick")),
            "saf":  _to_int(g.get("safeties"))

            
            
        }
        gamelog.append(row)

    # ---- Season highs ----
    hsrc = payload.get("seasonHighStats", {}).get("defensive", []) or []
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

def get_player_football_defense_mu(sess, roster_player_id: int, year: int) -> Dict[str, List[Dict[str, Any]]]:
    data = fetch_mu_player_json(sess, roster_player_id, year)
    parsed = parse_player_football_defense_from_mu(data)
    print(f"[mu-json] gamelog={len(parsed['gamelog'])} highs={len(parsed['season_highs'])}")
    return parsed