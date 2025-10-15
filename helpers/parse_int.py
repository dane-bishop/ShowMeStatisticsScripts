import re

def parse_int(s):
    try: return int(re.sub(r"[^\d]", "", s))
    except: return None