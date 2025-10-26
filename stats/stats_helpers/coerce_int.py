import re

def _coerce_int(x):
        if x is None:
            return None
        if isinstance(x, int):
            return x
        s = str(x).strip()
        if s == "":
            return None
        m = re.match(r"^\d+", s)
        return int(m.group(0)) if m else None