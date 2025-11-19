import requests, time
from helpers.core import HDRS
from datetime import datetime

# OLD FETCH
'''
def _fetch(url, sess):
    r = sess.get(url, timeout=12)
    r.raise_for_status()
    return r.text
'''


# NEW FETCH
DESKTOP_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

def _fetch(sess, url: str) -> str:
    # Ensure we look like a normal browser
    sess.headers.setdefault("User-Agent", DESKTOP_UA)
    sess.headers.setdefault("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    sess.headers.setdefault("Accept-Language", "en-US,en;q=0.9")
    sess.headers.setdefault("Referer", "https://mutigers.com/sports/baseball/roster")
    r = sess.get(url, timeout=12, allow_redirects=True)
    print("HTTP", r.status_code, "URL:", r.url)
    html = r.text
    print("len(html):", len(html))
    print("has 'Season Highs'?", ("Season Highs" in html))
    print("has c-player-stats__season-high-table?", ("c-player-stats__season-high-table" in html))
    print("has '/boxscore/'?", ("/boxscore/" in html))
    # Save for inspection
    stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    path = f"/tmp/player-{stamp}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("saved to", path)
    return html