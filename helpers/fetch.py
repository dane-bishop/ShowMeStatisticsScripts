import requests, time
from helpers.core import HDRS


def fetch(url, tries=3, sleep=0.7):
    for i in range(tries):
        r = requests.get(url, headers=HDRS, timeout=30)
        if r.status_code == 200:
            return r.text
        time.sleep(sleep * (i+1))
    raise RuntimeError(f"GET {url} failed with {r.status_code}")