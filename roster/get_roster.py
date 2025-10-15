import re, requests
from helpers.core import BASE
from bs4 import BeautifulSoup
from helpers.parse_int import parse_int
from urllib.parse import urljoin


def get_roster(sport_slug: str, year: int):
    url = f"{BASE}/sports/{sport_slug}/roster/{year}"
    html = requests.get(url, timeout=30).text
    soup = BeautifulSoup(html, "html.parser")

    cards = soup.select('div[data-test-id="s-person-card-list__root"]')
    for c in cards:
        # Full name + roster URL
        a = c.select_one('a[data-test-id="s-person-details__personal-single-line-person-link"][href*="/roster/"]')
        if not a: 
            continue
        name = a.get_text(strip=True)
        href = a.get("href")
        slug, mu_id = None, None
        m = re.search(r"/roster/([^/]+)/(\d+)$", href)
        if m:
            slug, mu_id = m.group(1), int(m.group(2))

        # Bio stats row (position, class year, height, weight, bats/throws)
        chips = [t.get_text(" ", strip=True) for t in c.select('div[data-test-id="s-person-details__bio-stats"] span.s-person-details__bio-stats-item')]
        # chips often look like: ['INF/OF', 'Jr.', "6' 3''", '185 lbs', 'L/R']
        position     = chips[0] if len(chips) > 0 else None
        class_year   = chips[1] if len(chips) > 1 else None
        height_raw   = chips[2] if len(chips) > 2 else None
        weight_lbs   = parse_int(chips[3]) if len(chips) > 3 else None
        bats_throws  = chips[4] if len(chips) > 4 else None

        hometown = c.select_one('span[data-test-id="s-person-card-list__content-location-person-hometown"]')
        high_school = c.select_one('span[data-test-id="s-person-card-list__content-location-person-high-school"]')
        hometown = hometown.get_text(" ", strip=True) if hometown else None
        high_school = high_school.get_text(" ", strip=True) if high_school else None

        yield {
            "full_name": name,
            "slug": slug,
            "mu_player_id": mu_id,
            "position": position,
            "class_year": class_year,
            "height_raw": height_raw,
            "weight_lbs": weight_lbs,
            "bats_throws": bats_throws,
            "hometown": hometown,
            "high_school": high_school,
            "source_url": urljoin(BASE, href),
        }