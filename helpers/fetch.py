import requests, time
from helpers.core import HDRS


def _fetch(url, sess):
    r = sess.get(url, timeout=12)
    r.raise_for_status()
    return r.text