from roster.roster_helpers.text import text
from helpers.core import COACH_WORDS
from roster.roster_helpers.strip_label import strip_label
import re


def parse_player_row(card):
    # name + link
    a = card.select_one('a[data-test-id="s-person-details__personal-single-line-person-link"][href*="/roster/"]')
    if not a: 
        return None

    name = text(a.select_one("h3")) or text(a)
    href = a.get("href", "")
    m = re.search(r"/roster/([^/]+)/(\d+)$", href)
    slug, mu_id = (m.group(1), int(m.group(2))) if m else (None, None)

    # role detection (coaches often show a title instead of position/class)
    role = text(card.select_one('[data-test-id="s-person-details__bio-stats-person-title"]'))
    if role and COACH_WORDS.search(role):
        return None  # skip staff

    jersey = text(card.select_one('[data-test-id="s-stamp__root"] .s-stamp__text'))
    if jersey:
        jersey = jersey.strip()

    position   = text(card.select_one('[data-test-id="s-person-details__bio-stats-person-position-short"]'))
    class_year = text(card.select_one('[data-test-id="s-person-details__bio-stats-person-title"]'))
    height_raw = text(card.select_one('[data-test-id="s-person-details__bio-stats-person-season"]'))
    weight_raw = text(card.select_one('[data-test-id="s-person-details__bio-stats-person-weight"]'))
    weight_lbs = int(re.sub(r"[^\d]", "", weight_raw)) if weight_raw and re.search(r"\d", weight_raw) else None

    hometown = text(card.select_one('[data-test-id="s-person-card-list__content-location-person-hometown"]'))
    hometown = strip_label(hometown, "Hometown")

    high_school = text(card.select_one('[data-test-id="s-person-card-list__content-location-person-high-school"]'))
    high_school = strip_label(high_school, "Last School")

    return {
        "full_name": name, "slug": slug, "mu_player_id": mu_id,
        "jersey": jersey, "position": position, "class_year": class_year,
        "height_raw": height_raw, "weight_lbs": weight_lbs,
        "bats_throws": None,  # some sports show here; for baseball it's the 5th chip—see bio fallback below
        "hometown": hometown, "high_school": high_school,
        "roster_href": href
    }