from decimal import Decimal
from typing import Optional


def _clean_dec(txt: str | None) -> Optional[Decimal]:
    if txt is None: return None
    t = txt.strip().replace("%","")
    if t == "" or t == "-": return None
    try: return Decimal(t)
    except Exception: return None