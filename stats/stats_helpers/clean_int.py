from typing import Optional


def _clean_int(txt: str | None) -> Optional[int]:
    if txt is None: return None
    t = txt.strip()
    if t == "" or t == "-": return None
    try: return int(t)
    except ValueError: return None