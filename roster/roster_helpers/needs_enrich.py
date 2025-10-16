# roster_helpers/enrich_from_bio.py
NEEDED_KEYS = ("bats_throws","hometown","high_school")

def needs_enrich(p):  # make it explicit
    return any(not p.get(k) for k in NEEDED_KEYS) and p.get("slug") and p.get("mu_player_id")
