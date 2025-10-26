# stats/parse_player_hitting_mu.py
from __future__ import annotations
from typing import Any, Dict, List, Iterable, Optional
from datetime import datetime
import re
from stats.stats_helpers.fetch_mu_player_json import fetch_mu_player_json
from stats.stats_helpers.extract_sgid import _source_game_id_from_url
from stats.stats_helpers.clean_int import _to_double
from stats.stats_helpers.clean_int import _to_int



def _clean_space(s: str) -> str:
    
    return s.replace("\u202f", " ").replace("\xa0", " ").strip()

def _parse_dt(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    s = _clean_space(s)
    for fmt in ("%m/%d/%Y %I:%M:%S %p", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None





def parse_player_hitting_from_mu(payload: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    # ---- Game log ----
    gsrc = payload.get("currentStats", {}).get("hittingStats", []) or []
    gamelog: List[Dict[str, Any]] = []

    for g in gsrc:
        dt = _parse_dt(g.get("date"))
        row = {
            # ids / linkage
            "source_game_id": _source_game_id_from_url(g.get("boxscoreUrl")),
            "game_date": dt.date().isoformat() if dt else None,

            # outcome / started
            "wl": (g.get("result") or "").strip()[:1].upper() or None,
            "gs": _to_int(g.get("gamesStarted")) if g.get("gamesStarted") is not None else None,

            # batting stats (strings -> ints)
            "ab": _to_int(g.get("atBats")),
            "r": _to_int(g.get("runsScored")),
            "h": _to_int(g.get("hits")),
            "rbi": _to_int(g.get("runsBattedIn")),
            "doubles": _to_int(g.get("doubles")),
            "triples": _to_int(g.get("triples")),
            "hr": _to_int(g.get("homeRuns")),
            "bb": _to_int(g.get("walks")),
            "ibb": _to_int(g.get("intentionalWalks")),
            "sb": _to_int(g.get("stolenBases")),
            # MU JSON has no "attempts" field; leave as None or derive if you prefer.
            "sba": None,
            "cs": _to_int(g.get("caughtStealing")),
            "hbp": _to_int(g.get("hitByPitch")),
            "sh": _to_int(g.get("sacrificeHits")),
            "sf": _to_int(g.get("sacrificeFlies")),
            "gdp": _to_int(g.get("groundedIntoDoublePlay")),
            "k": _to_int(g.get("strikeouts")),
            # average comes as ".357" string; store as-is
            "avg": (g.get("battingAverage") or None),
        }
        gamelog.append(row)

    # ---- Season highs ----
    hsrc = payload.get("seasonHighStats", {}).get("hittingStats", []) or []
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

def get_player_hitting_mu(sess, roster_player_id: int, year: int) -> Dict[str, List[Dict[str, Any]]]:
    data = fetch_mu_player_json(sess, roster_player_id, year)
    parsed = parse_player_hitting_from_mu(data)
    print(f"[mu-json] gamelog={len(parsed['gamelog'])} highs={len(parsed['season_highs'])}")
    return parsed
