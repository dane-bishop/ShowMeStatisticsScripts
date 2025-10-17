from __future__ import annotations
from typing import Iterable, Dict, Any, Optional
from helpers.find_game_id_by_source import _find_game_id_by_source



def upsert_player_batting_gamelog(conn, player_id: int, rows: Iterable[Dict[str, Any]]):
    """
    Expects rows from parse_gamelog_hitting().
    - First tries to map to games.id via games.source_game_id
    - If not found, you can add a fallback (date/opponent match) later if you like.
    """
    with conn, conn.cursor() as cur:
        for g in rows:
            sgid = g.get("source_game_id")
            game_id = _find_game_id_by_source(cur, sgid) if sgid else None
            if game_id is None:
                # no matching game yet—skip but keep the raw source id for later backfill
                # (Optional) log:
                # print(f"[WARN] No games.source_game_id={sgid} found; skipping for player {player_id}")
                pass

            cur.execute("""
                INSERT INTO player_game_batting (
                    player_id, game_id, source_game_id, wl, gs, ab, r, h, rbi,
                    doubles, triples, hr, bb, ibb, sb, sba, cs, hbp, sh, sf, gdp, k, avg
                ) VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
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




def upsert_player_hitting_season_highs(conn, player_id: int, highs: Iterable[Dict[str, Any]]):
    """
    If you want to persist season highs separately, you can put them in a simple table.
    This part is optional—many teams derive highs via SELECT MAX(...) over player_game_batting.
    """
    with conn, conn.cursor() as cur:
        # example table:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS player_season_highs (
            id BIGSERIAL PRIMARY KEY,
            player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
            stat_name TEXT NOT NULL,
            value INTEGER,
            game_id INTEGER REFERENCES games(id) ON DELETE SET NULL,
            source_game_id INTEGER,
            game_datetime TIMESTAMP,
            opponent_text TEXT,
            UNIQUE(player_id, stat_name)
        )
        """)
        for h in highs:
            game_id = None
            sgid = h.get("source_game_id")
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
                    value         = GREATEST(COALESCE(player_season_highs.value, 0), COALESCE(EXCLUDED.value, 0)),
                    game_id       = COALESCE(EXCLUDED.game_id, player_season_highs.game_id),
                    source_game_id= COALESCE(EXCLUDED.source_game_id, player_season_highs.source_game_id),
                    game_datetime = COALESCE(EXCLUDED.game_datetime, player_season_highs.game_datetime),
                    opponent_text = COALESCE(EXCLUDED.opponent_text, player_season_highs.opponent_text)
            """, (
                player_id, h.get("stat_name"), h.get("value"), game_id, sgid,
                h.get("game_datetime"), h.get("opponent_text")
            ))
