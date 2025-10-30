from typing import Optional
from datetime import datetime, time
import re

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



TZ_TOKENS = {"CT","CST","CDT","ET","EST","EDT","MT","MST","MDT","PT","PST","PDT","UTC","Z"}

def _parse_game_time_str(raw: str | None) -> time | None:
    """Accepts '7:00 PM', '11 AM', '11:00AM', 'NOON', 'TBA', 'TBD', etc."""
    if not raw:
        return None
    t = raw.strip().upper().replace(".", "")
    # strip any trailing timezone token (e.g., '3:15 PM CT')
    parts = t.split()
    if parts and parts[-1] in TZ_TOKENS and len(parts) >= 2:
        t = " ".join(parts[:-1])

    # common non-times
    if t in {"TBA", "TBD", "N/A", ""}:
        return None
    if t == "NOON":
        return time(12, 0, 0)
    if t == "MIDNIGHT":
        return time(0, 0, 0)

    # normalize ‘11AM’ -> ‘11 AM’
    t = re.sub(r"^(\d{1,2})(AM|PM)$", r"\1 \2", t)

    # try several formats
    for fmt in ("%I:%M %p", "%I %p", "%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(t, fmt).time()
        except ValueError:
            pass
    return None

def _extract_game_time(game: dict) -> time | None:
    # 1) Use ISO date if present (e.g., '2024-10-19T11:00:00')
    iso = game.get("date")
    if iso:
        try:
            return datetime.fromisoformat(iso).time()
        except Exception:
            pass
    # 2) Fallback to display time (e.g., '11 AM')
    return _parse_game_time_str(game.get("time"))
