import re

def strip_label(s, label):
    if not s: return s
    return re.sub(rf"^{label}\s*", "", s, flags=re.I).strip()