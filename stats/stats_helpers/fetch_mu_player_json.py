from typing import Any, Dict, List, Iterable, Optional
from helpers.core import API_TEMPLATE
import requests

def fetch_mu_player_json(sess, roster_player_id: int, year: int, sport) -> Dict[str, Any]:
    url = API_TEMPLATE.format(pid=roster_player_id, sport=sport, year=year)
    # headers help some SIDEARM setups
    sess.headers.setdefault("Accept", "application/json, text/plain, */*")
    sess.headers.setdefault("Referer", f"https://mutigers.com/sports/{sport}/roster/{roster_player_id}")
    try:
        r = sess.get(url, timeout=15)
        # If upstream says "no content" or missing, just skip
        if r.status_code in (204, 404, 410):
            print(f"[mu-fetch] {r.status_code} rid={roster_player_id} year={year} → skip")
            return None

        r.raise_for_status()

        text = (r.text or "").strip()
        if not text:
            print(f"[mu-fetch] empty body rid={roster_player_id} year={year} → skip")
            return None

        try:
            return r.json()
        except ValueError:
            ct = r.headers.get("Content-Type")
            print(f"[mu-fetch] non-JSON body rid={roster_player_id} year={year} ct={ct} len={len(r.content or b'') } → skip")
            return None

    except requests.RequestException as e:
        print(f"[mu-fetch] request error rid={roster_player_id} year={year}: {e} → skip")
        return None