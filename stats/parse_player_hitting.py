from bs4 import BeautifulSoup
from typing import List, Dict, Any
from stats.stats_helpers.clean_dec import _clean_dec
from stats.stats_helpers.clean_int import _clean_int
from stats.stats_helpers.parse_dt import _parse_dt
from helpers.fetch import _fetch
from helpers.extract_box_id import extract_box_id



# ---- Season highs (Hitting)
def parse_season_highs_hitting(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    root = soup.select_one('[data-test-id="player-stats-season-highs-table__root"]')
    if not root:
        return out

    # first <table> inside the wrapper
    table = root.select_one("table")
    if not table:
        return out

    for tr in table.select("tbody tr"):
        tds = tr.find_all("td")
        if len(tds) < 4:
            continue
        stat_name = tds[0].get_text(strip=True) or None
        value_txt = tds[1].get_text(strip=True)
        date_txt  = tds[2].get_text(strip=True)
        opp_el    = tds[3].select_one("a")
        opp_txt   = opp_el.get_text(strip=True) if opp_el else tds[3].get_text(strip=True)
        href      = opp_el.get("href") if opp_el else None
        box_id    = extract_box_id(href)

        out.append({
            "stat_name": stat_name,       # e.g., "Runs Batted In"
            "value": _clean_int(value_txt),
            "game_datetime": _parse_dt(date_txt),
            "opponent_text": opp_txt,
            "source_game_id": box_id,
            "box_href": href,
        })
    return out

def parse_gamelog_hitting(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Returns one dict per game with the columns you showed.
    We locate the table by its header set (Date, Opponent, W/L, GS, AB, R, ... AVG).
    """
    out: List[Dict[str, Any]] = []

    # Heuristic: find a table whose first header cell is "Date" and last is "AVG"
    tables = soup.select("table")
    target = None
    for tbl in tables:
        headers = [th.get_text(strip=True).upper() for th in tbl.select("thead th") if th.get_text(strip=True)]
        if not headers:
            continue
        if headers[0] == "DATE" and headers[-1] == "AVG" and "OPPONENT" in headers:
            target = tbl
            break
    if not target:
        return out

    for tr in target.select("tbody tr"):
        tds = tr.find_all("td")
        if len(tds) < 23:
            continue

        # columns (based on your sample):
        # 0 Date | 1 Opponent(link) | 2 W/L | 3 GS | 4 AB | 5 R | 6 H | 7 RBI | 8 2B | 9 3B
        # 10 HR | 11 BB | 12 IBB | 13 SB | 14 SBA | 15 CS | 16 HBP | 17 SH | 18 SF | 19 GDP
        # 20 K | 21 AVG
        date_txt = tds[0].get_text(strip=True)
        opp_a    = tds[1].select_one("a")
        opp_txt  = opp_a.get_text(strip=True) if opp_a else tds[1].get_text(strip=True)
        href     = opp_a.get("href") if opp_a else None
        box_id   = extract_box_id(href)
        wl       = tds[2].get_text(strip=True) or None

        row = {
            "game_datetime": _parse_dt(date_txt),
            "opponent_text": opp_txt,
            "wl": wl,
            "gs": _clean_int(tds[3].get_text(strip=True)),
            "ab": _clean_int(tds[4].get_text(strip=True)),
            "r":  _clean_int(tds[5].get_text(strip=True)),
            "h":  _clean_int(tds[6].get_text(strip=True)),
            "rbi":_clean_int(tds[7].get_text(strip=True)),
            "doubles": _clean_int(tds[8].get_text(strip=True)),
            "triples": _clean_int(tds[9].get_text(strip=True)),
            "hr": _clean_int(tds[10].get_text(strip=True)),
            "bb": _clean_int(tds[11].get_text(strip=True)),
            "ibb": _clean_int(tds[12].get_text(strip=True)),
            "sb": _clean_int(tds[13].get_text(strip=True)),
            "sba": _clean_int(tds[14].get_text(strip=True)),
            "cs": _clean_int(tds[15].get_text(strip=True)),
            "hbp": _clean_int(tds[16].get_text(strip=True)),
            "sh": _clean_int(tds[17].get_text(strip=True)),
            "sf": _clean_int(tds[18].get_text(strip=True)),
            "gdp": _clean_int(tds[19].get_text(strip=True)),
            "k": _clean_int(tds[20].get_text(strip=True)),
            "avg": _clean_dec(tds[21].get_text(strip=True)),  # Decimal('.286') style
            "source_game_id": box_id,
            "box_href": href,
        }
        out.append(row)
    return out

# ---- One-stop fetcher you can call with a requests.Session
def get_player_hitting(sess, player_url: str) -> dict[str, Any]:
    html = _fetch(sess, player_url)
    soup = BeautifulSoup(html, "lxml")
    return {
        "season_highs": parse_season_highs_hitting(soup),
        "gamelog": parse_gamelog_hitting(soup),
    }