from helpers.core import BASE
from bs4 import BeautifulSoup
from helpers.fetch import fetch
from roster.roster_helpers.parse_player_row import parse_player_row
from roster.roster_helpers.enrich_from_bio import enrich_from_bio

def get_roster(sport_slug: str, year: int):
    url = f"{BASE}/sports/{sport_slug}/roster/{year}"
    soup = BeautifulSoup(fetch(url), "html.parser")
    cards = soup.select('div[data-test-id="s-person-card-list__root"]')
    for c in cards:
        row = parse_player_row(c)
        if not row:
            continue
        yield enrich_from_bio(row)