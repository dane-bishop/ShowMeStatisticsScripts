# stats/parse_player_pitching.py
from __future__ import annotations
from typing import Any, Dict, List, Iterable, Optional
from datetime import datetime
import re
from stats.parse_player_hitting import _parse_dt, _to_int, _source_game_id_from_url, fetch_mu_player_json, _to_double, API_TEMPLATE

def parse_player_pitching_from_mu(payload: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    # ---- Game log ----
    gsrc = payload.get("currentStats", {}).get("pitchingStats", []) or []
    gamelog: List[Dict[str, Any]] = []

    for g in gsrc:
        dt = _parse_dt(g.get("date"))
        row = {

            

            # ids / linkage
            "source_game_id": _source_game_id_from_url(g.get("boxscoreUrl")),
            "game_date": dt.date().isoformat() if dt else None,

            # outcome / started
            "wl": (g.get("result") or "").strip()[:1].upper() or None,

            # "gs": _to_int(g.get("gamesStarted")) if g.get("gamesStarted") is not None else None,

            # batting stats (strings -> ints)
            "ip": _to_double(g.get("inningsPitched")),        # potentially change to storing as-is, remove the _to_double method, add or None
            "h": _to_int(g.get("hitsAllowed")),
            "r": _to_int(g.get("runsAllowed")),
            "er": _to_int(g.get("earnedRunsAllowed")),
            "bb": _to_int(g.get("walksAllowed")),
            "so": _to_int(g.get("strikeouts")),
            "doubles": _to_int(g.get("doublesAllowed")),
            "triples": _to_int(g.get("triplesAllowed")),
            "hr": _to_int(g.get("homeRunsAllowed")),
            "wp": _to_int(g.get("wildPitches")),
            "bk": _to_int(g.get("balks")),
            "hbp": _to_int(g.get("hitBatters")),
            "ibb": _to_int(g.get("intentionalWalks")),
            "np": _to_int(g.get("pitches")),
            "w": _to_int(g.get("pitchingWins")),
            "l": _to_int(g.get("pitchingLosses")),
            "s": _to_int(g.get("saves")),
            "gera": _to_int(g.get("gameEarnedRunAverage")),
            "sera": _to_int(g.get("earnedRunAverage")),  
        }
        gamelog.append(row)


    # ---- Season highs ----
    hsrc = payload.get("seasonHighStats", {}).get("pitchingStats", []) or []
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






def get_player_pitching_mu(sess, roster_player_id: int, year: int) -> Dict[str, List[Dict[str, Any]]]:
    data = fetch_mu_player_json(sess, roster_player_id, year)
    parsed = parse_player_pitching_from_mu(data)
    print(f"[mu-json] gamelog={len(parsed['gamelog'])} highs={len(parsed['season_highs'])}")
    return parsed






# Create pitching table
"""
CREATE TABLE player_game_pitching (
id BIGSERIAL PRIMARY KEY,
player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
source_game_id INTEGER,
wl TEXT,
ip DOUBLE PRECISION,
h INTEGER, r INTEGER, er INTEGER, bb INTEGER, so INTEGER, doubles INTEGER, triples INTEGER, hr INTEGER,
wp INTEGER, bk INTEGER, hbp INTEGER, ibb INTEGER, np INTEGER,
w INTEGER, l INTEGER, sv INTEGER,
gera DOUBLE PRECISION, sera DOUBLE PRECISION,
UNIQUE(player_id, game_id)
)
"""