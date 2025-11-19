import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

def make_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "ShowMeScripts/1.0 (+contact@example.com)",
        "Accept-Language": "en-US,en;q=0.8",
    })
    retry = Retry(
        total=5, backoff_factor=0.3,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False,
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://",  HTTPAdapter(max_retries=retry))
    return s