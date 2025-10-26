from typing import Any, Dict, List, Iterable, Optional
from helpers.core import API_TEMPLATE

def fetch_mu_player_json(sess, roster_player_id: int, year: int) -> Dict[str, Any]:
    url = API_TEMPLATE.format(pid=roster_player_id, year=year)
    # headers help some SIDEARM setups
    sess.headers.setdefault("Accept", "application/json, text/plain, */*")
    sess.headers.setdefault("Referer", f"https://mutigers.com/sports/baseball/roster/{roster_player_id}")
    r = sess.get(url, timeout=20)
    r.raise_for_status()
    return r.json()