import re
from bs4 import BeautifulSoup, NavigableString

def strip_sr_only_value(node) -> str | None:
    """Return the visible text of a chip/span that contains a <span class='sr-only'>Label</span> VALUE."""
    if not node:
        return None
    # Copy to avoid mutating original soup
    node = BeautifulSoup(str(node), "lxml").select_one("*")
    # remove sr-only labels
    for sr in node.select(".sr-only"):
        sr.extract()
    # remaining text is the value
    val = node.get_text(" ", strip=True)
    return val or None