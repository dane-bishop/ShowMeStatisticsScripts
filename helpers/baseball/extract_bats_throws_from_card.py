# helpers/extract_bats_throws_from_card.py
import re

# Accept "/", "|" or the fraction slash \u2044
_BT_ANY_SLASH = r"[\/\|\u2044]"
# Allow Left/Right/Switch -> L/R/S
_WORD_TO_LETTER = {"left":"L","right":"R","switch":"S","both":"S"}

def _normalize_bt(val: str | None) -> str | None:
    if not val:
        return None
    v = (val or "").strip()
    # unify slashes and collapse spaces
    v = v.replace("\u2044", "/").replace("|", "/")
    v = re.sub(r"\s+", "", v)

    # If it looks like words (e.g., "Switch/Right"), map to letters
    parts = v.split("/")
    if len(parts) == 2:
        def to_letter(p: str) -> str:
            p = p.strip().lower()
            if p in _WORD_TO_LETTER:
                return _WORD_TO_LETTER[p]
            # already a single letter?
            return p[:1].upper()
        v = f"{to_letter(parts[0])}/{to_letter(parts[1])}"

    v = v.upper()
    # Validate final form: L/R/S on both sides
    if re.fullmatch(r"[LRS]/[LRS]", v):
        return v
    return None

def _get_val(el) -> str | None:
    return (el.get_text(strip=True) or None) if el else None

BT_LABELS = {
    "custom field 1", "custom field",
    "b/t", "bats/throws", "bats / throws", "bats-throws"
}

def extract_bats_throws_from_card(card) -> str | None:
    # Pass 1: labelled chip → its [data-html-wrapper]
    for val_el in card.select('.s-person-details__bio-stats-item [data-html-wrapper]'):
        sr = val_el.find_previous_sibling('span', class_='sr-only')
        label = (sr.get_text(strip=True).lower() if sr else "")
        if label in BT_LABELS:
            norm = _normalize_bt(_get_val(val_el))
            if norm:
                return norm

    # Pass 2: any [data-html-wrapper] that normalizes to L/R/S
    for val_el in card.select('[data-html-wrapper]'):
        norm = _normalize_bt(_get_val(val_el))
        if norm:
            return norm

    # Pass 3: scan chip text
    for chip in card.select('.s-person-details__bio-stats-item'):
        norm = _normalize_bt(_get_val(chip))
        if norm:
            return norm

    return None

# Export a pattern for bio-page fallback (captures L/R/S after normalization)
BT_PAT = re.compile(r"[LRS]\s*[\/\|\u2044]\s*[LRS]", re.I)
