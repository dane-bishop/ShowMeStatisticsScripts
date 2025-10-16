import re
from datetime import datetime

from schedule.schedule_helpers.clean_opponent import _clean_opponent
from schedule.schedule_helpers.opponent_from_box_href import _opponent_from_box_href
from schedule.schedule_helpers.parse_result_score import _parse_result_score
from schedule.schedule_helpers.infer_location import _infer_location

_TIME_SEL = (
    '[data-test-id="s-game-card-standard__header-game-time"]',
    '[aria-label="Event Time"]',
)

def _to_time_24(s: str | None) -> str | None:
    """'3 p.m.' -> '15:00'; returns None if not parseable."""
    if not s:
        return None
    t = s.lower().replace(".", "").strip()   # "3 pm" / "3 p.m." / "12:30 pm"
    m = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b', t)
    if not m:
        return None
    hh = int(m.group(1)) % 12
    mm = int(m.group(2) or 0)
    if m.group(3) == "pm":
        hh += 12
    return f"{hh:02d}:{mm:02d}"

def parse_game_card_any(card, year):
    # ---- Date
    date_el = card.select_one('[data-test-id="s-game-card-standard__header-game-date-details"]')
    date_txt = date_el.get_text(" ", strip=True) if date_el else ""
    m = re.search(r"([A-Z][a-z]{2})\s+(\d{1,2})", date_txt)
    if not m:
        return None
    game_date = datetime.strptime(f"{m.group(1)} {m.group(2)} {year}", "%b %d %Y").date()

    # ---- Opponent
    opp_el = card.select_one('[data-test-id="s-game-card-standard__header-team-opponent-link"]')
    opponent = _clean_opponent(opp_el.get_text(" ", strip=True)) if opp_el else None

    # ---- Venue (name + city/state)
    venue_name_el  = card.select_one('[data-test-id="s-game-card-facility-and-location__standard-facility-title"]')
    venue_place_el = card.select_one('[data-test-id="s-game-card-facility-and-location__standard-location-details"]')
    venue_name  = venue_name_el.get_text(" ", strip=True) if venue_name_el else None
    venue_place = venue_place_el.get_text(" ", strip=True) if venue_place_el else None

    venue_city = venue_state = None
    if venue_place:
        m2 = re.search(r"^\s*([^,]+)\s*,\s*(.+?)\s*$", venue_place)
        if m2:
            venue_city, venue_state = m2.group(1).strip(), m2.group(2).strip()

    # ---- Result + score
    score_el = card.select_one('[data-test-id="s-game-card-standard__header-game-team-score"]')
    res_raw  = score_el.get_text(" ", strip=True) if score_el else None
    result, score_for, score_against = _parse_result_score(res_raw or "")

    # ---- Notes (descriptor + TV/Radio)
    desc_el = card.select_one('a[data-test-id="s-descriptor__root"] [data-test-id="s-descriptor__text"]')
    tv_el   = card.select_one('[data-test-id="s-game-card-standard__header-tv-and-radio"]')
    notes_parts = []
    if desc_el:
        notes_parts.append(desc_el.get_text(" ", strip=True))
    if tv_el:
        notes_parts.append(tv_el.get_text(" ", strip=True))
    notes = " | ".join([p for p in notes_parts if p]) or None

    # ---- Box score link + stable id
    box = card.select_one('a[href*="/boxscore/"]')
    game_href = box.get("href") if box else None
    mbox = re.search(r"/boxscore/(\d+)", game_href or "")
    source_game_id = int(mbox.group(1)) if mbox else None

    # ---- Time (for DH disambiguation)
    time_el = None
    for sel in _TIME_SEL:
        time_el = card.select_one(sel)
        if time_el:
            break
    game_time = _to_time_24(time_el.get_text(" ", strip=True)) if time_el else None

    # ---- DH number from descriptor if no time (e.g., "DH Game 2")
    game_number = None
    if not game_time and desc_el:
        dtxt = desc_el.get_text(" ", strip=True)
        mdh = re.search(r"\b(?:DH|Doubleheader)\b.*?(?:Game\s*(\d))?", dtxt, re.I)
        if mdh and mdh.group(1):
            game_number = int(mdh.group(1))

    # ---- Location inference (home/away/neutral)
    location = _infer_location(venue_name, venue_city, venue_state)

    return {
        "game_date": game_date,
        "location": location,
        "opponent_name": opponent,
        "venue_city": venue_city,
        "venue_state": venue_state,
        "venue_name": venue_name,
        "result": result,
        "score_for": score_for,
        "score_against": score_against,
        "notes": notes,
        "game_href": game_href,
        "source_game_id": source_game_id,   # NEW
        "game_time": game_time,             # NEW ('HH:MM' or None)
        "game_number": game_number,         # NEW (1/2 or None)
    }
