from datetime import datetime
import re, requests
from bs4 import BeautifulSoup
from helpers.core import BASE

def get_schedule_text(sport_slug: str, year: int):
    url = f"{BASE}/sports/{sport_slug}/schedule/text/{year}"
    html = requests.get(url, timeout=30).text
    soup = BeautifulSoup(html, "html.parser")

    # The text variant renders as simple <li> / text nodes. We'll regex fields.
    text = soup.get_text("\n", strip=True)
    # Example lines resemble: "Mar 29 (Sat) 6:10 p.m. Home No. 7 Texas (DH) Columbia, Mo. ... L, 7-1"
    lines = [ln for ln in text.split("\n") if ln.strip()]
    for ln in lines:
        # very tolerant parse; adjust patterns per sport if needed
        # Find date
        m_date = re.search(r"([A-Z][a-z]{2}\s+\d{1,2})", ln)  # 'Mar 29'
        if not m_date: 
            continue
        month_day = m_date.group(1)
        dt = datetime.strptime(f"{month_day} {year}", "%b %d %Y").date()

        # Location token (Home/Away/Neutral)
        loc = None
        if " Home " in f" {ln} ": loc = "home"
        elif " Away " in f" {ln} ": loc = "away"
        elif " Neutral " in f" {ln} ": loc = "neutral"

        # Opponent: grab chunk after location up to city
        opp = None
        m_opp = re.search(r"(Home|Away|Neutral)\s+(.+?)\s+[A-Z][a-z]+\.,\s+[A-Z][a-z]+\.", ln)
        if m_opp:
            opp = re.sub(r"\s+\(DH\)", "", m_opp.group(2)).strip()

        # City/State
        venue_city, venue_state = None, None
        m_citystate = re.search(r"([A-Z][a-z]+\.),\s+([A-Z][a-z]+)\.", ln)
        if m_citystate:
            venue_city, venue_state = m_citystate.group(1)[:-1], m_citystate.group(2)[:-1]

        # Result (L, 7-1) or (W, 6-2) etc.
        res = None
        m_res = re.search(r"\b([WLT]),\s*(\d+)-(\d+)", ln)
        score_for = score_against = None
        if m_res:
            res = m_res.group(1)
            # For home/away semantics, "score_for" is Mizzou's first number on their site
            score_for, score_against = int(m_res.group(2)), int(m_res.group(3))

        yield {
            "game_date": dt, "location": loc,
            "opponent_name": opp, "venue_city": venue_city, "venue_state": venue_state,
            "result": res, "score_for": score_for, "score_against": score_against,
            "source": url
        }