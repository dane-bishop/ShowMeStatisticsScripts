def season_to_year(season_str: str, use="start") -> int:
    """
    Convert 'YYYY-YY' -> an integer year for DB.
    use='start' -> 2024
    use='end'   -> 2025 (assumes two-digit end and 2000s)
    """
    left, right = season_str.split("-")
    start = int(left)
    if use == "end":
        # handle '25' -> 2025; adjust if your data ever spans centuries
        end = int(right)
        end += 2000 if end < 100 else 0
        return end
    return start