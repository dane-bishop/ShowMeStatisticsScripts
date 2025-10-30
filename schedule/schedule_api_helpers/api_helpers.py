from typing import Optional
from datetime import datetime

def _to_int(x) -> Optional[int]:
    if x is None: return None
    try:
        s = str(x).strip()
        if not s: return None
        return int(s)
    except Exception:
        return None

def _parse_iso_dt(s: Optional[str]) -> Optional[datetime]:
    # API "date": "2024-09-07T18:00:00"  (local)
    # API "dateUtc": "2024-09-07T23:00:00Z"
    if not s: return None
    try:
        # Handle trailing fractional Z (some endpoints have ...0000001Z)
        # Try multiple formats:
        for fmt in ("%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S.%f",
                    "%Y-%m-%dT%H:%M:%SZ",
                    "%Y-%m-%dT%H:%M:%S.%fZ"):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
    except Exception:
        pass
    return None

def _location_indicator_to_text(ind: Optional[str]) -> Optional[str]:
    # H / A / N → home / away / neutral (store whichever you prefer)
    if not ind: return None
    ind = ind.upper().strip()
    if ind == "H": return "HOME"
    if ind == "A": return "AWAY"
    if ind == "N": return "NEUTRAL"
    return ind  # keep as-is if unknown