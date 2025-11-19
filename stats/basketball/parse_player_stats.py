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


def parse_player_basketball_stats(payload: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:

    # ---- Game log ----
    gsrc = payload.get("currentStats", {}) or []
    gamelog: List[Dict[str, Any]] = []

    for g in gsrc:
        dt = _parse_dt(g.get("date"))
        
        # Parse made attempted fields first
        fg_made, fg_att = parse_made_attempted(g.get("fieldGoalsMadeAttempted"))
        three_made, three_att = parse_made_attempted(g.get("threePointFieldGoalsMadeAttempted"))
        ft_made, ft_att = parse_made_attempted(g.get("freeThrowsMadeAttempted"))


        row = {
            # ids / linkage
            "source_game_id": _source_game_id_from_url(g.get("boxscoreUrl")),
            "game_date": dt.date().isoformat() if dt else None,
            

            # Stats
            "minutes": _to_int(g.get("minutesPlayed")),
            "fg_made": fg_made,
            "fg_att": fg_att,
            "fg_pct": _to_double(g.get("fieldGoalsPercentage")),
            "three_made": three_made,
            "three_att": three_att,
            "three_pct": _to_double(g.get("threePointFieldGoalsPercentage")),
            "ft_made": ft_made,
            "ft_att": ft_att,
            "ft_pct": _to_double(g.get("freeThrowsPercentage")),
            "off_r": _to_int(g.get("offensiveRebounds")),
            "dr": _to_int(g.get("defensiveRebounds")),
            "tr": _to_int(g.get("totalRebounds")),
            "r_avg": _to_double(g.get("reboundAverage")),
            "pf": _to_int(g.get("personalFouls")),
            "ast": _to_int(g.get("assists")),
            "turnovers": _to_int(g.get("turnovers")),
            "blk": _to_int(g.get("blocks")),
            "stl": _to_int(g.get("steals")),
            "pts": _to_int(g.get("points")),
            "pts_avg": _to_double(g.get("pointsAverage")),


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




def get_player_basketball_mu(sess, roster_player_id: int, year: int, sport) -> Dict[str, List[Dict[str, Any]]]:

    data = fetch_mu_player_json(sess, roster_player_id, year, sport)
    parsed = parse_player_basketball_stats(data)
    print(f"[mu-json] gamelog={len(parsed['gamelog'])} highs={len(parsed['season_highs'])}")
    return parsed



