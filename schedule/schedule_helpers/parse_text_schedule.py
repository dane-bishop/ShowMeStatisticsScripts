from bs4 import BeautifulSoup
import re
from schedule.schedule_helpers.clean_opponent import _clean_opponent


def parse_text_schedule(html, year):
    """Fallback: /schedule/text/{year} simple text page."""
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text("\n", strip=True)
    lines = [ln for ln in text.split("\n") if ln.strip()]
    from datetime import datetime
    out = []
    for ln in lines:
        m = re.search(r"([A-Z][a-z]{2})\s+(\d{1,2})", ln)
        if not m: 
            continue
        game_date = datetime.strptime(f"{m.group(1)} {m.group(2)} {year}", "%b %d %Y").date()
        loc = "home" if " Home " in f" {ln} " else "away" if " Away " in f" {ln} " else "neutral" if " Neutral " in f" {ln} " else None
        # Opponent between location and city
        m_opp = re.search(r"(?:Home|Away|Neutral)\s+(.+?)\s+[A-Z][a-z]+\.,\s+[A-Z][a-z]+\.", ln)
        opp = _clean_opponent(m_opp.group(1)) if m_opp else None
        m_city = re.search(r"([A-Z][a-z]+)\.,\s+([A-Z][a-z]+)\.", ln)
        venue_city = m_city.group(1) if m_city else None
        venue_state = m_city.group(2) if m_city else None
        out.append({
            "game_date": game_date, "location": loc, "opponent_name": opp,
            "venue_city": venue_city, "venue_state": venue_state, "game_href": None
        })
    return out