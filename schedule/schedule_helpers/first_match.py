import re

def first_match(text, patterns):
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return m
    return None