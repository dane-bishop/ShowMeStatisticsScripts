# stats/parse_player_hitting_mu.py
from __future__ import annotations
from typing import Any, Dict, List, Iterable, Optional
from datetime import datetime
import re

API_TEMPLATE = "https://mutigers.com/api/v2/stats/bio?rosterPlayerId={pid}&sport=baseball&year={year}"

def _clean_space(s: str) -> str:
    # replace narrow/nb spaces commonly found before AM/PM
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

def _to_int(x) -> Optional[int]:
    if x is None:
        return None
    try:
        return int(str(x).strip())
    except Exception:
        return None

def _source_game_id_from_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    m = re.search(r'/boxscore/(\d+)', url)
    return m.group(1) if m else None

def fetch_mu_player_json(sess, roster_player_id: int, year: int) -> Dict[str, Any]:
    url = API_TEMPLATE.format(pid=roster_player_id, year=year)
    # headers help some SIDEARM setups
    sess.headers.setdefault("Accept", "application/json, text/plain, */*")
    sess.headers.setdefault("Referer", f"https://mutigers.com/sports/baseball/roster/{roster_player_id}")
    r = sess.get(url, timeout=20)
    r.raise_for_status()
    return r.json()

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
