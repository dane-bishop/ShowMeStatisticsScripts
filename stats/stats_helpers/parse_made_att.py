from stats.stats_helpers.clean_int import _to_int

def parse_made_attempted(value: str):
    """
    Parse strings like '5-7' into (made, attempted).

    Returns (made, attempted) as ints or (None, None) if invalid/empty.
    """
    if value is None:
        return None, None

    value = value.strip()
    if not value:
        return None, None

    # split only once; if something weird like "5-7-1", we still get two parts
    parts = value.split('-', 1)
    if len(parts) != 2:
        return None, None

    made_str, att_str = parts
    made = _to_int(made_str)   # your existing int parser
    attempted = _to_int(att_str)

    return made, attempted