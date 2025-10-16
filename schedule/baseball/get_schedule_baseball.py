from datetime import datetime
from bs4 import BeautifulSoup
from helpers.core import BASE
from schedule.schedule_helpers.clean_opponent import _clean_opponent
from schedule.schedule_helpers.parse_game_card import parse_game_card
from helpers.fetch import _fetch
from urllib.parse import urljoin
import re
from helpers.make_session import make_session
from schedule.schedule_helpers.parse_game_card_any import parse_game_card_any
from schedule.schedule_helpers.parse_text_schedule import parse_text_schedule


def get_schedule_baseball(sport_slug: str, year: int, debug=False):
    sess = make_session()
    url = f"{BASE}/sports/{sport_slug}/schedule/{year}"
    soup = BeautifulSoup(_fetch(url, sess), "lxml")

    # Broad container set to catch your theme
    cards = soup.select(
        '[data-test-id="s-games__list-item"], '
        '[data-test-id="s-game-card__root"], '
        'li.s-game-card, '
        '.s-game-card'  # your snippet fits inside this
    )
    if debug: print(f"[schedule] cards={len(cards)} url={url}")

    had_row = False
    for c in cards:
        row = parse_game_card_any(c, year)
        if not row:
            if debug: print("[schedule] skip: parse failed")
            continue

        # If opponent still None, try inside linked pages as last resort
        if not row["opponent_name"] and row["game_href"]:
            gh = urljoin(BASE, row["game_href"])
            try:
                gsoup = BeautifulSoup(_fetch(gh, sess), "lxml")
                headOpp = gsoup.select_one(
                    '[data-test-id*="opponent-name"], '
                    '.opponent-name, '
                    '.team-name, '
                    '[itemprop="name"]'
                )
                row["opponent_name"] = _clean_opponent(headOpp.get_text(" ", strip=True)) if headOpp else None
            except Exception as e:
                if debug: print("[schedule] follow fail", gh, e)

        had_row = True
        yield row

    # Fallback to text endpoint only if absolutely nothing parsed
    if not had_row:
        turl = f"{BASE}/sports/{sport_slug}/schedule/text/{year}"
        try:
            tsoup = BeautifulSoup(_fetch(turl, sess), "lxml")
            text = tsoup.get_text("\n", strip=True)
            lines = [ln for ln in text.split("\n") if ln.strip()]
            for ln in lines:
                m = re.search(r"([A-Z][a-z]{2})\s+(\d{1,2})", ln)
                if not m: 
                    continue
                game_date = datetime.strptime(f"{m.group(1)} {m.group(2)} {year}", "%b %d %Y").date()
                m_opp = re.search(r"(?:Home|Away|Neutral)\s+(.+?)\s+[A-Z][a-z]+\.,\s+[A-Z][a-z]+\.", ln)
                opponent = _clean_opponent(m_opp.group(1)) if m_opp else None
                m_city = re.search(r"([A-Z][a-z]+)\.,\s+([A-Z][a-z]+)\.", ln)
                venue_city = m_city.group(1) if m_city else None
                venue_state = m_city.group(2) if m_city else None
                yield {"game_date": game_date, "location": None, "opponent_name": opponent,
                       "venue_city": venue_city, "venue_state": venue_state, "venue_name": None, "game_href": None}
        except Exception as e:
            if debug: print("[schedule] text fail", e)
