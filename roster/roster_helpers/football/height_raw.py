from typing import Optional

def _height_raw(feet: Optional[int], inches: Optional[int]) -> Optional[str]:
    if feet is None and inches is None:
        return None
    # Some APIs send 0, None combos—normalize cleanly.
    f = f"{feet}" if isinstance(feet, int) and feet >= 0 else None
    i = f"{inches}" if isinstance(inches, int) and inches >= 0 else None
    if f and i:
        return f"{f}-{i}"
    if f and not i:
        return f"{f}-0"
    if not f and i:
        return f"0-{i}"
    return None