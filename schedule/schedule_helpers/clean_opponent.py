import re

def clean_opponent(raw: str | None) -> str | None:
    if not raw:
        return None
    s = raw.strip()
    # remove rank, DH tags, extra spaces
    s = re.sub(r"\bNo\.\s*\d+\s*", "", s)   # "No. 7 Texas" -> "Texas"
    s = re.sub(r"\(DH\)", "", s, flags=re.I)
    s = re.sub(r"\s{2,}", " ", s).strip(" -–·")
    return s or None