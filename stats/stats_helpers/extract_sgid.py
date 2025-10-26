import re
from typing import Any, Dict, List, Iterable, Optional

def _extract_sgid(h):
        sgid = h.get("source_game_id") or h.get("game_source_id")
        if sgid:
            try:
                return int(sgid)
            except Exception:
                return None
        url = h.get("boxscoreUrl") or h.get("boxscore_url")
        if url:
            m = re.search(r"/boxscore/(\d+)", url)
            if m:
                return int(m.group(1))
        return None



def _source_game_id_from_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    m = re.search(r'/boxscore/(\d+)', url)
    return m.group(1) if m else None