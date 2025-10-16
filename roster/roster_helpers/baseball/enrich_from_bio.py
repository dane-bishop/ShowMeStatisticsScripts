from urllib.parse import urljoin
from bs4 import BeautifulSoup
from helpers.core import BASE
from helpers._etch import fetch
from roster.roster_helpers.text import text
import re


def enrich_from_bio(p):
    # If any of these are missing, fetch Full Bio and try again
    needed = any(p[k] in (None, "",) for k in ("bats_throws","hometown","high_school"))
    if not needed or not p["slug"] or not p["mu_player_id"]:
        return p

    url = urljoin(BASE, f"/sports/baseball/roster/{p['slug']}/{p['mu_player_id']}")
    try:
        html = fetch(url)
    except Exception:
        return p
    soup = BeautifulSoup(html, "html.parser")

    # Sidearm bio detail blocks vary by theme; try common labels
    def find_label(label):
        lab = soup.find(lambda tag: tag.name in ("dt","div","span","strong") and 
                        re.search(rf"^{label}\s*:?$", text(tag) or "", re.I))
        if not lab:
            return None
        # next sibling text
        sib = lab.find_next_sibling()
        return text(sib) if sib else None

    bats_throws = p["bats_throws"] or find_label("Bats/Throws")
    hometown = p["hometown"] or find_label("Hometown")
    high_school = p["high_school"] or find_label("High School") or find_label("Last School")

    p.update({
        "bats_throws": bats_throws,
        "hometown": hometown,
        "high_school": high_school
    })
    return p