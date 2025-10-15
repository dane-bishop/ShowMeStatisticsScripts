from datetime import datetime
from bs4 import BeautifulSoup
from helpers.core import BASE
from schedule.schedule_helpers.clean_opponent import clean_opponent
from schedule.schedule_helpers.parse_game_card import parse_game_card
from helpers.fetch import fetch
from urllib.parse import urljoin


def get_schedule_html(sport_slug: str, year: int, debug=False):
    url = f"{BASE}/sports/{sport_slug}/schedule/{year}"
    soup = BeautifulSoup(fetch(url), "html.parser")
    cards = soup.select('[data-test-id="s-games__list-item"], [data-test-id="s-game-card__root"], li.s-game-card')
    for c in cards:
        row = parse_game_card(c, year)
        if not row:
            if debug: print("[skip:card-parse]")
            continue
        # If opponent missing, try the game page (box score / recap) for the header
        if not row["opponent_name"] and row["game_href"]:
            gh = urljoin(BASE, row["game_href"])
            try:
                gsoup = BeautifulSoup(fetch(gh), "html.parser")
                headOpp = gsoup.select_one('[data-test-id*="opponent-name"], .opponent-name, .team-name')
                row["opponent_name"] = clean_opponent(headOpp.get_text(" ", strip=True)) if headOpp else None
            except Exception:
                if debug: print("[warn:game-follow-failed]", gh)

        yield row