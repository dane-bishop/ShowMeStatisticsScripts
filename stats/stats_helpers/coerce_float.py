def _coerce_float(x):
    if x is None:
        return None
    try:
        # handles strings like "3", "3.0", ".357"
        return float(str(x).strip())
    except (ValueError, TypeError):
        return None