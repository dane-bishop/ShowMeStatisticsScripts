import re

def _title_from_slug(slug: str) -> str:
    # "penn-state" -> "Penn State"
    name = re.sub(r"[-_]+", " ", slug).strip()
    return " ".join(w.capitalize() for w in name.split())