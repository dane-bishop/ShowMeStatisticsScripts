from concurrent.futures import ThreadPoolExecutor, as_completed
from helpers.make_session import make_session
import time, random
from helpers.core import BASE
from bs4 import BeautifulSoup
from roster.roster_helpers.parse_player_row import parse_player_row
from urllib.parse import urljoin
from roster.roster_helpers.baseball.needs_enrich import needs_enrich
from helpers.strip_sr_only_value import strip_sr_only_value
from helpers.only_digits import only_digits
from helpers.baseball.extract_bats_throws_from_card import extract_bats_throws_from_card, BT_PAT



def _find_label(soup: BeautifulSoup, *labels) -> str | None:
    """
    Bio pages vary; search for DT/STRONG/SPAN/DIV that is exactly a label (case-insensitive),
    then read the next sibling text.
    """
    wanted = {lbl.lower() for lbl in labels}
    def is_label(tag):
        if tag.name not in ("dt", "strong", "span", "div"):
            return False
        t = (tag.get_text(" ", strip=True) or "").strip().rstrip(":").lower()
        return t in wanted

    lab = soup.find(is_label)
    if not lab:
        return None
    sib = lab.find_next_sibling()
    if sib:
        return sib.get_text(" ", strip=True) or None

    # fallback: sometimes label and value are in same node
    return lab.get_text(" ", strip=True) or None


def get_roster_baseball(sport_slug: str, year: int):
    sess = make_session()
    roster_url = f"{BASE}/sports/{sport_slug}/roster/{year}"
    soup = BeautifulSoup(sess.get(roster_url, timeout=12).text, "lxml")
    cards = soup.select('div[data-test-id="s-person-card-list__root"]')

    rows = []
    for c in cards:
        row = parse_player_row(c)
        if not row:
            continue

        # Normalize chips so labels don't leak into values
        pos_el  = c.select_one('[data-test-id="s-person-details__bio-stats-person-position-short"]')
        year_el = c.select_one('[data-test-id="s-person-details__bio-stats-person-title"]')
        hgt_el  = c.select_one('[data-test-id="s-person-details__bio-stats-person-season"]')
        wgt_el  = c.select_one('[data-test-id="s-person-details__bio-stats-person-weight"]')

        row["position"]   = strip_sr_only_value(pos_el)  or row.get("position")
        row["class_year"] = strip_sr_only_value(year_el) or row.get("class_year")
        row["height_raw"] = strip_sr_only_value(hgt_el)  or row.get("height_raw")

        wtxt = strip_sr_only_value(wgt_el)
        if wtxt:
            digits = only_digits(wtxt)
            row["weight_lbs"] = int(digits) if digits else row.get("weight_lbs")

        # Jersey: just the number
        stamp = c.select_one('[data-test-id="s-stamp__root"] .s-stamp__text')
        j = strip_sr_only_value(stamp)
        if j:
            row["jersey"] = j

        # NEW: B/T extraction
        if not row.get("bats_throws"):
            dbg = c.select_one('.s-person-details__bio-stats-item [data-html-wrapper]')
            if dbg:
                print("[DBG bt wrapper text]", row.get("full_name"), "=>", dbg.get_text(strip=True))

            bt = extract_bats_throws_from_card(c)
            if bt:
                row["bats_throws"] = bt

        rows.append(row)

    def enrich_task(p):
        if not needs_enrich(p):
            return p
        if not p.get("slug") or not p.get("mu_player_id"):
            return p

        url = urljoin(BASE, f"/sports/{sport_slug}/roster/{p['slug']}/{p['mu_player_id']}")
        try:
            r = sess.get(url, timeout=10)
            if r.status_code != 200:
                return p
            psoup = BeautifulSoup(r.text, "lxml")
            time.sleep(0.05 + random.random() * 0.05)  # polite jitter

            # ---- fill values ----
            bt = p.get("bats_throws")
            if not bt:
                # Try labeled detail blocks first
                bt = _find_label(psoup, "Bats/Throws", "B/T", "Bats / Throws", "Bats-Throws", "Custom Field 1", "Custom Field")
            if not bt:
                # Last resort: regex anywhere on the page
                m = BT_PAT.search(psoup.get_text(" ", strip=True))
                if m:
                    bt = m.group(0)

            if bt:
                bt = bt.upper().replace(" ", "")

            home = p.get("hometown") or _find_label(psoup, "Hometown")
            hs   = p.get("high_school") or _find_label(psoup, "High School", "Last School")

            # ---- return updated dict with the CORRECT variable names ----
            return {
                **p,
                "bats_throws": bt or p.get("bats_throws"),
                "hometown":    home or p.get("hometown"),
                "high_school": hs   or p.get("high_school"),
            }
        except Exception:
            return p


    if rows:
        with ThreadPoolExecutor(max_workers=6) as ex:
            futures = [ex.submit(enrich_task, p) for p in rows]
            for fut in as_completed(futures):
                yield fut.result()
    else:
        # Nothing found; still yield nothing to keep generator semantics
        return