import re

def only_digits(s):
    return re.sub(r"[^\d]", "", s or "") or None