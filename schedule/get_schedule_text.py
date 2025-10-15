from datetime import datetime
import re, requests
from bs4 import BeautifulSoup
from helpers.core import BASE
from schedule.schedule_helpers.clean_opponent import clean_opponent
from schedule.schedule_helpers.first_match import first_match

def get_schedule_text(sport_slug: str, year: int, debug=False):
    url = f"{BASE}/sports/{sport_slug}/schedule/text/{year}"
    html = requests.get(url, timeout=30).text
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)

    lines = [ln for ln in text.split("\n") if ln.strip()]
    for ln in lines:
        # date
        m_date = first_match(ln, [r"([A-Z][a-z]{2}\s+\d{1,2})"])
        if not m_date:
            if debug: print("[skip:no-date]", ln)
            continue
        month_day = m_date.group(1)
        try:
            dt = datetime.strptime(f"{month_day} {year}", "%b %d %Y").date()
        except ValueError:
            if debug: print("[skip:bad-date]", ln)
            continue

        # location token
        loc = None
        if re.search(r"\bHome\b", ln): loc = "home"
        elif re.search(r"\bAway\b", ln): loc = "away"
        elif re.search(r"\bNeutral\b", ln): loc = "neutral"

        # opponent (try several shapes)
        # Home/Away/Neutral  <OPP>  City, State.
        m_opp = first_match(ln, [
            r"(?:Home|Away|Neutral)\s+(.+?)\s+[A-Z][a-z]+\.,\s+[A-Z][a-z]+\.",     # basic
            r"(?:Home|Away|Neutral)\s+(.+?)\s+-\s+[A-Z][a-z]+\.,\s+[A-Z][a-z]+\.", # with hyphen
            r"(?:Home|Away|Neutral)\s+(vs\.|at)?\s*(.+?)\s+[A-Z][a-z]+\.,\s+[A-Z][a-z]+\.", # vs./at
        ])
        opp_raw = None
        if m_opp:
            # pick the last non-empty group
            groups = [g for g in m_opp.groups() if g and g.lower() not in ("vs.", "at")]
            opp_raw = groups[-1] if groups else None

        opponent_name = clean_opponent(opp_raw)

        # venue city/state
        m_citystate = first_match(ln, [r"([A-Z][a-z]+)\.,\s+([A-Z][a-z]+)\."])
        venue_city = m_citystate.group(1) if m_citystate else None
        venue_state = m_citystate.group(2) if m_citystate else None

        # result
        m_res = first_match(ln, [r"\b([WLT]),\s*(\d+)-(\d+)", r"\b([WLT])\s+(\d+)-(\d+)"])
        result, score_for, score_against = None, None, None
        if m_res:
            result = m_res.group(1)
            score_for, score_against = int(m_res.group(2)), int(m_res.group(3))

        if not opponent_name:
            if debug: print("[warn:no-opponent]", ln)
            # yield anyway so the caller can decide to skip or handle
            yield {"raw_line": ln, "game_date": dt, "location": loc,
                   "opponent_name": None, "venue_city": venue_city, "venue_state": venue_state,
                   "result": result, "score_for": score_for, "score_against": score_against,
                   "source": url}
            continue

        yield {"game_date": dt, "location": loc,
               "opponent_name": opponent_name, "venue_city": venue_city, "venue_state": venue_state,
               "result": result, "score_for": score_for, "score_against": score_against,
               "source": url}