from datetime import datetime, date

def _parse_dt(dt_val) -> datetime | None:
    """
    Accepts:
      - str like '5/11/2025 1:00:00 PM' (may contain U+202F narrow NBSP)
      - datetime/date instances
      - dicts that contain a date string under common keys
      - None
    Returns a naive datetime in local time or None.
    """
    if not dt_val:
        return None

    # Already a datetime?
    if isinstance(dt_val, datetime):
        return dt_val

    # A date (no time)?
    if isinstance(dt_val, date):
        return datetime(dt_val.year, dt_val.month, dt_val.day)

    # A dict? try common keys or first str-like value
    if isinstance(dt_val, dict):
        for key in ("date", "game_datetime", "value", "raw"):
            v = dt_val.get(key)
            if isinstance(v, (str, datetime, date)):
                return _parse_dt(v)
        # last resort: look for any string value
        for v in dt_val.values():
            if isinstance(v, (str, datetime, date)):
                return _parse_dt(v)
        return None

    # Must be a string from here
    if isinstance(dt_val, str):
        t = dt_val.replace("\u202f", " ").replace("\xa0", " ").strip()
        # try several formats commonly seen in your feed
        fmts = (
            "%m/%d/%Y %I:%M:%S %p",  # 3/1/2025 1:00:00 PM
            "%m/%d/%Y %H:%M:%S",     # 3/1/2025 13:00:00
            "%Y-%m-%d %H:%M:%S",     # 2025-05-11 13:00:00
            "%Y-%m-%d",              # 2025-05-11
            "%m/%d/%Y",              # 3/1/2025
        )
        for fmt in fmts:
            try:
                return datetime.strptime(t, fmt)
            except ValueError:
                pass
        # ISO-ish fallback
        try:
            # allows '2025-05-11T13:00:00' or similar
            return datetime.fromisoformat(t.replace("Z", ""))
        except Exception:
            return None

    # Unhandled type
    return None



