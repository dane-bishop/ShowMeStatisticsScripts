from datetime import datetime
import re
from schedule.schedule_helpers.clean_opponent import _clean_opponent


def parse_game_card(card, year):
    # date
    dtTxt = card.select_one('[data-test-id="s-game-card-date"]')
    d = (dtTxt.get_text(" ", strip=True) if dtTxt else "").strip()
    # Sidearm often prints like "Mar 29 (Sat)"
    m = re.search(r"([A-Z][a-z]{2})\s+(\d{1,2})", d)
    if not m: 
        return None
    game_date = datetime.strptime(f"{m.group(1)} {m.group(2)} {year}", "%b %d %Y").date()

    # location badge or text
    loc = None
    locNode = card.select_one('[data-test-id="s-game-card-location"]')
    if locNode:
        t = locNode.get_text(" ", strip=True)
        if re.search(r"\bHome\b", t): loc = "home"
        elif re.search(r"\bAway\b", t): loc = "away"
        elif re.search(r"\bNeutral\b", t): loc = "neutral"

    # opponent
    oppNode = card.select_one('[data-test-id="s-game-card-opponent-name"]') \
              or card.select_one('.opponent-name, [data-test-id*="opponent"]')
    opponent = _clean_opponent(oppNode.get_text(" ", strip=True) if oppNode else None)

    # venue city/state (if shown on card)
    locDetail = card.select_one('[data-test-id="s-game-card-location-detail"]')
    venue_city = venue_state = None
    if locDetail:
        t = locDetail.get_text(" ", strip=True)
        m2 = re.search(r"([A-Z][a-z]+),\s*([A-Z][a-z]+)", t)
        if m2: venue_city, venue_state = m2.group(1), m2.group(2)

    # links
    box = card.select_one('a[href*="boxscore"], a[href*="box-score"], a[aria-label*="Box Score" i]')
    game_href = box.get("href") if box else None

    return {
        "game_date": game_date, "location": loc, "opponent_name": opponent,
        "venue_city": venue_city, "venue_state": venue_state,
        "game_href": game_href
    }