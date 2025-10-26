from typing import Optional


def _clean_int(txt: str | None) -> Optional[int]:
    if txt is None: return None
    t = txt.strip()
    if t == "" or t == "-": return None
    try: return int(t)
    except ValueError: return None



def _to_int(x) -> Optional[int]:
    if x is None:
        return None
    try:
        return int(str(x).strip())
    except Exception:
        return None

def _to_double(x) -> Optional[float]:
    if x is None:
        return None
    try:
        return float(str(x).strip())
    except Exception:
        return None