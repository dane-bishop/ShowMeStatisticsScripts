# stats/parse_player_pitching.py
from __future__ import annotations
from typing import Any, Dict, List, Iterable, Optional
from datetime import datetime
import re
from stats.baseball.parse_player_hitting import _parse_dt, _to_int, _source_game_id_from_url, fetch_mu_player_json, _to_double

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
            "sv": _to_int(g.get("saves")),
            "gera": _to_double(g.get("gameEarnedRunAverage")),
            "sera": _to_double(g.get("earnedRunAverage")),  
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


# Create fielding table
"""
CREATE TABLE player_game_fielding (
    id BIGSERIAL PRIMARY KEY, 
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
    source_game_id INTEGER,
    wl TEXT,
    c INT,
    po INT,
    a INT,
    e INT,
    fld DOUBLE PRECISION,
    dp INT, sba INT, csb INT, pb INT, ci INT,
    UNIQUE(player_id, game_id)
    );
    

    
    
    )"""


"""
CREATE TABLE player_game_football_offense (
    id BIGSERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
    source_game_id INTEGER,

    pass_comp INTEGER,
    pass_att INTEGER,
    pass_int INTEGER,
    pass_pct NUMERIC(5,2),
    pass_yds INTEGER,
    pass_tds INTEGER,
    pass_lng INTEGER,

    rush_att INTEGER,
    rush_yds INTEGER,
    rush_tds INTEGER,
    rush_lng INTEGER,

    rec INTEGER,
    rec_yds INTEGER,
    rec_tds INTEGER,
    rec_lng INTEGER,

    kr_ret INTEGER,
    kr_yds INTEGER,
    kr_tds INTEGER,
    kr_lng INTEGER,

    pr_ret INTEGER,
    pr_yds INTEGER,
    pr_tds INTEGER,
    pr_lng INTEGER,
    UNIQUE(player_id, game_id)
    );
"""



"""
passingCompletions
passingAttempts
passingInterceptions
passingYards
passingTouchdowns
passingLongest

rushingNumber
rushingYards
rushingTouchdowns
rushingLongest

recNumber
recYards
recTouchdowns
recLongest

#TRY
kickRetNumber
kickRetYards
kickRetTouchdowns
kickRetLongest

puntRetNumber
puntRetYards
puntRetTouchdowns
puntRetLongest
"""

"""
CREATE TABLE player_game_football_defense (
    id BIGSERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
    source_game_id INTEGER,

    solo INTEGER,
    ast INTEGER,
    ttot INTEGER,
    tfl DOUBLE PRECISION,
    tyds INTEGER,

    stot DOUBLE PRECISION,
    syds INTEGER,

    ff INTEGER,
    fr INTEGER,
    fyds INTEGER,

    ints INTEGER,
    int_yds INTEGER,

    qbh INTEGER,
    brk INTEGER,

    kick INTEGER,
    saf INTEGER,
    UNIQUE(player_id, game_id)
);
"""

"""
tacklesSolo
tacklesAssist
tacklesTotal
tacklesForLoss
tacklesYards
sacksNumber
sacksYards
fumblesForces
fumblesRecoveries
fumblesYards
intsNumber
intsYards
quarterbackHurries
passBreakups
blockedKick
safeties
"""