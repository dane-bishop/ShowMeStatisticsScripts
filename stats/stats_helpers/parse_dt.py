from datetime import datetime

def _parse_dt(dt_txt: str) -> datetime | None:
    # examples: "3/1/2025 1:00:00 PM" (note potential narrow no-break space before AM/PM)
    if not dt_txt: return None
    t = dt_txt.replace("\u202f"," ").strip()
    for fmt in ("%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y %H:%M:%S"):
        try: return datetime.strptime(t, fmt)
        except ValueError: pass
    return None




