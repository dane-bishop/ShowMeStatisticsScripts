from concurrent.futures import ThreadPoolExecutor, as_completed
from helpers.make_session import make_session
from helpers.core import BASE
from urllib.parse import urljoin
from typing import Dict, Any, Generator
from roster.roster_helpers.football.slugify import _slugify
from roster.roster_helpers.football.height_raw import _height_raw
import requests



def get_roster_from_api(sport_slug: str, year: int) -> Generator[Dict[str, Any], None, None]:
    
    sess = make_session()
    url = urljoin(BASE, f"/api/v2/Rosters/bySport/{sport_slug}?season={year}")
    
    # Try to get api data
    try:
        r = sess.get(url, timeout=15)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"[roster] request failed for {url}: {e}; skipping.")
        return  # stop generator

    # Quick content guard: empty body or whitespace-only
    body = (r.text or "").strip()
    if not body:
        print(f"[roster] empty response body for {url}; skipping.")
        return

    # Try to parse JSON; if not JSON, skip
    try:
        data = r.json()
    except ValueError:
        ct = r.headers.get("Content-Type", "unknown")
        print(f"[roster] non-JSON response (Content-Type={ct}) for {url}; skipping.")
        return

    players = (data or {}).get("players") or []
    if not isinstance(players, list) or not players:
        print(f"[roster] no players in payload for {url}; skipping.")
        return
    
    for p in players:
        first = p.get("firstName") or ""
        last  = p.get("lastName") or ""
        full_name = (first + " " + last).strip() or None

        slug = _slugify(first, last)
        mu_player_id = p.get("playerId")  

        jersey = (p.get("jerseyNumber") or "").strip() or None
        position = (p.get("positionShort") or p.get("positionLong") or "").strip() or None
        class_year = (p.get("academicYearShort") or p.get("academicYearLong") or "").strip() or None

        height = _height_raw(p.get("heightFeet"), p.get("heightInches"))
        weight_lbs = p.get("weight")  # already an int in sample; keep as-is or None

        hometown = (p.get("hometown") or "").strip() or None
        high_school = (p.get("highSchool") or "").strip() or None

        roster_player_id = (p.get("rosterPlayerId"))

        yield {
            "full_name": full_name,
            "slug": slug,
            "mu_player_id": mu_player_id,
            "jersey": jersey,
            "position": position,
            "class_year": class_year,
            "height_raw": height,
            "weight_lbs": weight_lbs,
            "bats_throws": None,  # JSON doesn’t supply this for FB
            "hometown": hometown,
            "high_school": high_school,
            "roster_player_id": roster_player_id
        }