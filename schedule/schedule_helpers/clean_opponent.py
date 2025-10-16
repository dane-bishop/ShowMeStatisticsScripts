import re

def _clean_opponent(s):
    if not s: return None
    s = re.sub(r"\bNo\.\s*\d+\s*", "", s)       # remove rankings
    s = re.sub(r"\(DH\)", "", s, flags=re.I)    # doubleheader note
    s = re.sub(r"\s{2,}", " ", s).strip(" -–·")
    return s or None