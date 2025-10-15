import re

def clean_opponent(s):
    if not s: return None
    s = re.sub(r"\bNo\.\s*\d+\s*", "", s)     # remove rankings
    s = re.sub(r"\(DH\)", "", s, flags=re.I)  # doubleheader tag
    return re.sub(r"\s{2,}", " ", s).strip(" -–·")