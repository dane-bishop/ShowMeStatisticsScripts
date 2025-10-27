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


def parse_player_football_offense_from_mu(payload: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    # ---- Game log ----
    gsrc = payload.get("currentStats", {}).get("fieldingStats", []) or []
    gamelog: List[Dict[str, Any]] = []

    for g in gsrc:
        dt = _parse_dt(g.get("date"))
        passing = g.get("passing") or {}
        rushing = g.get("rushing") or {}
        receiving = g.get("receiving") or {}
        kr = g.get("kickReturns") or {}
        pr = g.get("puntReturns") or {}



        row = {
            # ids / linkage
            "source_game_id": _source_game_id_from_url(g.get("boxscoreUrl")),
            "game_date": dt.date().isoformat() if dt else None,
            

            # Passing
            "pass_comp": _to_int(passing.get("passingCompletions")),
            "pass_att":  _to_int(passing.get("passingAttempts")),
            "pass_int":  _to_int(passing.get("passingInterceptions")),
            "pass_pct":  _to_double(passing.get("passingPercentage")),  # store 82.1 (no % sign)
            "pass_yds":  _to_int(passing.get("passingYards")),
            "pass_td":   _to_int(passing.get("passingTouchdowns")),
            "pass_long": _to_int(passing.get("passingLongest")),

            # Rushing
            "rush_att":  _to_int(rushing.get("rushingNumber")),
            "rush_yds":  _to_int(rushing.get("rushingYards")),
            "rush_td":   _to_int(rushing.get("rushingTouchdowns")),
            "rush_long": _to_int(rushing.get("rushingLongest")),

            # Receiving
            "rec_rec":   _to_int(receiving.get("recNumber")),
            "rec_yds":   _to_int(receiving.get("recYards")),
            "rec_td":    _to_int(receiving.get("recTouchdowns")),
            "rec_long":  _to_int(receiving.get("recLongest")),

            # Kick Returns
            "kr_ret":    _to_int(kr.get("kickRetNumber") or kr.get("krNumber") or kr.get("retNumber")),
            "kr_yds":    _to_int(kr.get("kickRetYards")  or kr.get("krYards")),
            "kr_td":     _to_int(kr.get("kickRetTouchdowns") or kr.get("krTouchdowns")),
            "kr_long":   _to_int(kr.get("kickRetLongest") or kr.get("krLongest")),

            # Punt Returns
            "pr_ret":    _to_int(pr.get("puntRetNumber")),
            "pr_yds":    _to_int(pr.get("puntRetYards")),
            "pr_td":     _to_int(pr.get("puntRetTouchdowns")),
            "pr_long":   _to_int(pr.get("puntRetLongest")),
            
        }
        gamelog.append(row)

    # ---- Season highs ----
    hsrc = payload.get("seasonHighStats", {}).get("offensive", []) or []
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

def get_player_football_offense_mu(sess, roster_player_id: int, year: int) -> Dict[str, List[Dict[str, Any]]]:
    data = fetch_mu_player_json(sess, roster_player_id, year)
    parsed = parse_player_football_offense_from_mu(data)
    print(f"[mu-json] gamelog={len(parsed['gamelog'])} highs={len(parsed['season_highs'])}")
    return parsed
