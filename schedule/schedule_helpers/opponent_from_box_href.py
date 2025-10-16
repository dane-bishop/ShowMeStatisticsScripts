import re
from schedule.schedule_helpers.title_from_slug import _title_from_slug

def _opponent_from_box_href(href: str | None) -> str | None:
    if not href: 
        return None
    # e.g. /sports/baseball/stats/2025/penn-state/boxscore/32172
    m = re.search(r"/stats/\d{4}/([^/]+)/boxscore", href)
    if not m:
        return None
    return _title_from_slug(m.group(1))