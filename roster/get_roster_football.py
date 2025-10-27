from concurrent.futures import ThreadPoolExecutor, as_completed
from helpers.make_session import make_session
from helpers.core import BASE
from urllib.parse import urljoin
from typing import Dict, Any, Generator
from roster.roster_helpers.football.slugify import _slugify
from roster.roster_helpers.football.height_raw import _height_raw



def get_roster_from_api(sport_slug: str, year: int) -> Generator[Dict[str, Any], None, None]:
    
    sess = make_session()
    url = urljoin(BASE, f"/api/v2/Rosters/bySport/{sport_slug}?season={year}")
    r = sess.get(url, timeout=15)
    r.raise_for_status()
    data = r.json() or {}
    players = data.get("players") or []
    
    for p in players:
        first = p.get("firstName") or ""
        last  = p.get("lastName") or ""
        full_name = (first + " " + last).strip() or None

        slug = _slugify(first, last)
        mu_player_id = p.get("playerId")  # your players.player_id

        jersey = (p.get("jerseyNumber") or "").strip() or None
        position = (p.get("positionShort") or p.get("positionLong") or "").strip() or None
        class_year = (p.get("academicYearShort") or p.get("academicYearLong") or "").strip() or None

        height = _height_raw(p.get("heightFeet"), p.get("heightInches"))
        weight_lbs = p.get("weight")  # already an int in sample; keep as-is or None

        hometown = (p.get("hometown") or "").strip() or None
        high_school = (p.get("highSchool") or "").strip() or None

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
        }