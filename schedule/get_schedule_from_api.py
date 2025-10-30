from __future__ import annotations
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin
from datetime import datetime
import json
import psycopg2
import re
from helpers.make_session import make_session
from helpers.core import BASE
from schedule.schedule_api_helpers.api_helpers import _to_int, _parse_iso_dt, _location_indicator_to_text


def fetch_schedule_json(season_id: int | str) -> Dict[str, Any]:
    """GET https://mutigers.com/api/v2/Schedule/<season_id> and return parsed JSON."""
    sess = make_session()
    url = urljoin(BASE, f"/api/v2/Schedule/{season_id}")
    r = sess.get(url, headers={"Accept": "application/json, text/plain, */*"}, timeout=20)
    r.raise_for_status()
    try:
        return json.loads(r.text.strip())  # more tolerant than r.json()
    except json.JSONDecodeError:
        preview = (r.text or "")[:200]
        raise RuntimeError(f"Schedule API did not return JSON. URL={url} "
                           f"CT={r.headers.get('Content-Type')} body[:200]={preview!r}")
    


_NORM_SPACE = re.compile(r"\s+")
_NORM_CHARS = re.compile(r"[^a-z0-9 ]+")

def _norm_name_py(s: str) -> str:
    s = (s or "").lower().strip()
    s = _NORM_CHARS.sub("", s)           # keep only letters/digits/spaces
    s = _NORM_SPACE.sub(" ", s)          # collapse spaces
    return s

def ensure_opponent(conn, *, title: str) -> int:
    if not title:
        title = "TBD"

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO opponents (name)
            VALUES (%s)
            ON CONFLICT (name_norm)
            DO UPDATE SET
                name = EXCLUDED.name
            RETURNING id
        """, (title,))
        return cur.fetchone()[0]

        
    




def upsert_games_from_schedule(conn, team_season_id: int, season_id: int | str) -> Dict[str, int]:

    data = fetch_schedule_json(season_id)
    gsrc = data.get("games") or []

    inserted = updated = skipped = 0

    with conn:
        with conn.cursor() as cur:
            for g in gsrc:
                # --- identify and normalize ---
                source_game_id = _to_int(g.get("id"))
                if not source_game_id:
                    # if we cannot uniquely identify a game, skip
                    skipped += 1
                    continue

                # date/time
                dt_local = _parse_iso_dt(g.get("date"))  # prefer local "date"
                game_date = dt_local.date().isoformat() if dt_local else None
                game_time = g.get("time") or (dt_local.strftime("%-I:%M %p") if dt_local else None)

                # location & venue
                indicator = (g.get("locationIndicator") or "").upper().strip()
                loc_map = {"H": "home", "A": "away", "N": "neutral"}
                location_value = loc_map.get(indicator)

                # Fallback if your source sometimes has words like "HOME"/"Away"
                if not location_value:
                    raw_loc = (g.get("location") or "").strip().lower()
                    if raw_loc in {"home", "away", "neutral"}:
                        location_value = raw_loc

                # Now use location_value for games.location

                venue_title = (g.get("facility") or {}).get("title")
                venue_id = None
                # If you have a venues table/ensure_venue, wire it here:
                # venue_id = ensure_venue(conn, title=venue_title) if venue_title else None

                # opponent
                opp = g.get("opponent") or {}
                opp_title = (opp.get("title") or "").strip() or "TBD"
                opponent_id = ensure_opponent(conn, title=opp_title)

                # result and scores (can be missing for future games)
                res = g.get("result") or {}
                result_flag = (res.get("status") or "").strip().upper() or None  # "W", "L", "T", ""...
                score_for = _to_int(res.get("teamScore"))
                score_against = _to_int(res.get("opponentScore"))

                # notes / links
                notes = g.get("gamePromotionText") or None
                # Prefer absolute boxscore URL as a canonical source_url if available
                box_rel = ((res.get("boxscore") or {}).get("url")) if res else None
                source_url = urljoin(BASE, box_rel) if box_rel else urljoin(BASE, f"/api/v2/Schedule/{season_id}")

                # doubleheader indicator
                game_number = None
                if g.get("isADoubleheader"):
                    # The API doesn't always provide a number; you can derive one if schedule has 2 games same date.
                    # For now, store 1 for the first we see that day, else 2—optional logic:
                    game_number = None  # keep null unless you have deterministic numbering

                # --- UPSERT ---
                # RECOMMENDED unique index:
                #   CREATE UNIQUE INDEX IF NOT EXISTS ux_games_tsid_source ON games(team_season_id, source_game_id);
                cur.execute("""
                    INSERT INTO games (
                        team_season_id, game_date, location, opponent_id, venue_id,
                        result, score_for, score_against, notes, source_url, source_game_id,
                        game_time, game_number
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (team_season_id, source_game_id)
                    DO UPDATE SET
                        game_date     = COALESCE(EXCLUDED.game_date,     games.game_date),
                        location      = COALESCE(EXCLUDED.location,      games.location),
                        opponent_id   = COALESCE(EXCLUDED.opponent_id,   games.opponent_id),
                        venue_id      = COALESCE(EXCLUDED.venue_id,      games.venue_id),
                        result        = COALESCE(EXCLUDED.result,        games.result),
                        score_for     = COALESCE(EXCLUDED.score_for,     games.score_for),
                        score_against = COALESCE(EXCLUDED.score_against, games.score_against),
                        notes         = COALESCE(EXCLUDED.notes,         games.notes),
                        source_url    = COALESCE(EXCLUDED.source_url,    games.source_url),
                        game_time     = COALESCE(EXCLUDED.game_time,     games.game_time),
                        game_number   = COALESCE(EXCLUDED.game_number,   games.game_number)
                """, (
                    team_season_id,              # team_season_id
                    game_date,                   # game_date (YYYY-MM-DD)
                    location_value,                # location (HOME/AWAY/NEUTRAL or H/A/N)
                    opponent_id,                 # opponent_id
                    venue_id,                    # venue_id (or None)
                    result_flag,                 # result (W/L/T/etc.)
                    score_for,                   # score_for
                    score_against,               # score_against
                    notes,                       # notes
                    source_url,                  # source_url
                    source_game_id,              # source_game_id (API id)
                    game_time,                   # game_time ("7:00 PM" etc.)
                    game_number                  # game_number (optional)
                ))
                was_inserted = cur.fetchone()[0]
                if was_inserted:
                    inserted += 1
                else:
                    updated += 1

    return {"inserted": inserted, "updated": updated, "skipped": skipped}