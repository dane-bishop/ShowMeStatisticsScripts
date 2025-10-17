import re

_BOX_ID_RE = re.compile(r"/boxscore/(\d+)\b")

def extract_box_id(href: str | None) -> int | None:
    if not href:
        return None
    m = _BOX_ID_RE.search(href)
    return int(m.group(1)) if m else None
