from __future__ import annotations
from typing import Iterable, Dict, Any, Optional
from helpers.find_game_id_by_source import _find_game_id_by_source











def upsert_player_batting_gamelog(conn, player_id: int, rows: Iterable[Dict[str, Any]]):
    """
    Expects rows from parse_gamelog_hitting().
    - First tries to map to games.id via games.source_game_id
    - If not found, you can add a fallback (date/opponent match) later if you like.
    """
    inserted = updated = skipped = 0
    with conn, conn.cursor() as cur:
        for g in rows:
            sgid = g.get("source_game_id")
            game_id = _find_game_id_by_source(cur, sgid) if sgid else None
    
            if not g.get("game_source_id") and not g.get("game_date"):
                skipped += 1
                continue

            cur.execute("""
                INSERT INTO player_game_batting (
                    player_id, game_id, source_game_id, wl, gs, ab, r, h, rbi,
                    doubles, triples, hr, bb, ibb, sb, sba, cs, hbp, sh, sf, gdp, k, avg
                ) VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                )
                ON CONFLICT (player_id, game_id)
                DO UPDATE SET
                    wl      = COALESCE(EXCLUDED.wl, player_game_batting.wl),
                    gs      = COALESCE(EXCLUDED.gs, player_game_batting.gs),
                    ab      = COALESCE(EXCLUDED.ab, player_game_batting.ab),
                    r       = COALESCE(EXCLUDED.r, player_game_batting.r),
                    h       = COALESCE(EXCLUDED.h, player_game_batting.h),
                    rbi     = COALESCE(EXCLUDED.rbi, player_game_batting.rbi),
                    doubles = COALESCE(EXCLUDED.doubles, player_game_batting.doubles),
                    triples = COALESCE(EXCLUDED.triples, player_game_batting.triples),
                    hr      = COALESCE(EXCLUDED.hr, player_game_batting.hr),
                    bb      = COALESCE(EXCLUDED.bb, player_game_batting.bb),
                    ibb     = COALESCE(EXCLUDED.ibb, player_game_batting.ibb),
                    sb      = COALESCE(EXCLUDED.sb, player_game_batting.sb),
                    sba     = COALESCE(EXCLUDED.sba, player_game_batting.sba),
                    cs      = COALESCE(EXCLUDED.cs, player_game_batting.cs),
                    hbp     = COALESCE(EXCLUDED.hbp, player_game_batting.hbp),
                    sh      = COALESCE(EXCLUDED.sh, player_game_batting.sh),
                    sf      = COALESCE(EXCLUDED.sf, player_game_batting.sf),
                    gdp     = COALESCE(EXCLUDED.gdp, player_game_batting.gdp),
                    k       = COALESCE(EXCLUDED.k, player_game_batting.k),
                    avg     = COALESCE(EXCLUDED.avg, player_game_batting.avg)
            """, (
                player_id, game_id, sgid, g.get("wl"), g.get("gs"),
                g.get("ab"), g.get("r"), g.get("h"), g.get("rbi"),
                g.get("doubles"), g.get("triples"), g.get("hr"), g.get("bb"), g.get("ibb"),
                g.get("sb"), g.get("sba"), g.get("cs"), g.get("hbp"), g.get("sh"),
                g.get("sf"), g.get("gdp"), g.get("k"), g.get("avg")
            ))
            print(f"Attributes: AB {g.get("ab")}, H: {g.get("h")}")
            if cur.rowcount == 1:
                inserted += 1
            else:
                updated += 1
    print(f"[gamelog] inserted={inserted} updated={updated} skipped={skipped}")
















def upsert_player_hitting_season_highs(conn, player_id: int, highs):
    import re
    from datetime import datetime

    def _coerce_int(x):
        if x is None:
            return None
        if isinstance(x, int):
            return x
        s = str(x).strip()
        if s == "":
            return None
        m = re.match(r"^\d+", s)
        return int(m.group(0)) if m else None

    def _extract_sgid(h):
        sgid = h.get("source_game_id") or h.get("game_source_id")
        if sgid:
            try:
                return int(sgid)
            except Exception:
                return None
        url = h.get("boxscoreUrl") or h.get("boxscore_url")
        if url:
            m = re.search(r"/boxscore/(\d+)", url)
            if m:
                return int(m.group(1))
        return None

    def _parse_dt(h):
        dt = h.get("game_datetime")
        if isinstance(dt, datetime):
            return dt
        s = (h.get("date") or "").replace("\u202f", " ").strip()
        if not s:
            return None
        # Try ISO first (your data): 2025-05-11
        for fmt in ("%Y-%m-%d", "%m/%d/%Y %I:%M:%S %p", "%-m/%-d/%Y %I:%M:%S %p",
                    "%m/%d/%Y %I:%M %p", "%-m/%-d/%Y %I:%M %p"):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                pass
        return None

    inserted = updated = skipped = 0

    with conn, conn.cursor() as cur:
        for raw in highs or []:
            # Accept stat_name, name, or label
            stat_name = (raw.get("stat_name")
                         or raw.get("name")
                         or raw.get("label")
                         or "").strip()
            if not stat_name:
                print("skip: missing stat_name", raw)
                skipped += 1
                continue

            value = _coerce_int(raw.get("value") or raw.get("stat_value"))
            sgid = _extract_sgid(raw)
            game_dt = _parse_dt(raw)
            opponent_text = raw.get("opponent_text") or raw.get("opponent")

            game_id = None
            if sgid:
                cur.execute("SELECT id FROM games WHERE source_game_id = %s", (sgid,))
                r = cur.fetchone()
                game_id = r[0] if r else None

            cur.execute("""
                INSERT INTO player_season_highs
                    (player_id, stat_name, value, game_id, source_game_id, game_datetime, opponent_text)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (player_id, stat_name)
                DO UPDATE SET
                    value          = GREATEST(COALESCE(player_season_highs.value, 0), COALESCE(EXCLUDED.value, 0)),
                    game_id        = COALESCE(EXCLUDED.game_id, player_season_highs.game_id),
                    source_game_id = COALESCE(EXCLUDED.source_game_id, player_season_highs.source_game_id),
                    game_datetime  = COALESCE(EXCLUDED.game_datetime, player_season_highs.game_datetime),
                    opponent_text  = COALESCE(EXCLUDED.opponent_text, player_season_highs.opponent_text)
            """, (player_id, stat_name, value, game_id, sgid, game_dt, opponent_text))

            inserted += 1  # treat upsert as success
            print(f"season-high row → stat_name={stat_name!r}, value={value}, sgid={sgid}, game_id={game_id}, date={game_dt}, opp={opponent_text!r}")

    print(f"[season_highs] inserted/updated={inserted} skipped={skipped}")
