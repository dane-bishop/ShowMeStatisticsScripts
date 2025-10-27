from typing import Optional

def _slugify(first: Optional[str], last: Optional[str]) -> Optional[str]:
    if not first or not last:
        return None
    s = f"{first.strip()}-{last.strip()}".lower()
    out = []
    for ch in s:
        if ch.isalnum() or ch == "-":
            out.append(ch)
        elif ch in (" ", "_"):
            out.append("-")
        # else skip punctuation
    # collapse multiple dashes
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or None