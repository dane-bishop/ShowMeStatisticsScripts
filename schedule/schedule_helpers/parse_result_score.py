import re

def _parse_result_score(result_text: str):
    """
    Examples: 'W, 5-3', 'L, 10-0', 'T, 4-4', 'Canceled', 'Postponed'
    Returns: (result, score_for, score_against)
    """
    if not result_text:
        return (None, None, None)
    t = result_text.strip()
    if re.search(r"cancel|postpone|suspend|no\s*contest", t, re.I):
        # store result words, no scores
        return (t, None, None)
    m = re.search(r"\b([WLT])\s*,\s*(\d+)\s*[-–]\s*(\d+)\b", t, re.I)
    if not m:
        return (None, None, None)
    res = m.group(1).upper()
    a = int(m.group(2))
    b = int(m.group(3))
    # Convention: score_for = Mizzou runs, score_against = opponent runs
    # Cards are from Mizzou perspective:
    #   W, 5-3  -> for=5 against=3
    #   L, 10-0 -> for=0 against=10
    if res == "W":
        return ("W", a, b)
    if res == "L":
        return ("L", b, a)
    if res == "T":
        # tie: numbers equal (usually)
        return ("T", a, b)
    return (res, None, None)