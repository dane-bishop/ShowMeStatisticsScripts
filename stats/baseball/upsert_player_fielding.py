from __future__ import annotations
from typing import Iterable, Dict, Any, Optional
from helpers.find_game_id_by_source import _find_game_id_by_source
import re
from datetime import datetime
from stats.stats_helpers.parse_dt import _parse_dt 
from stats.stats_helpers.coerce_int import _coerce_int
from stats.stats_helpers.extract_sgid import _extract_sgid
from stats.stats_helpers.coerce_float import _coerce_float


def upsert_player_fielding_gamelog(conn, player_id: int, rows: Iterable[Dict[str, Any]]):

    inserted = updated = skipped = 0
    with conn, conn.cursor() as cur:
        for g in rows:

            sgid = g.get("source_game_id")
            game_id = _find_game_id_by_source(cur, sgid) if sgid else None
    
            if not g.get("game_source_id") and not g.get("game_date"):
                skipped += 1
                continue

            cur.execute("""
                INSERT INTO player_game_fielding (
                    player_id, game_id, source_game_id, wl, c, po, a, e, fld,
                    dp, sba, csb, pb, ci
                ) VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s
                )
                ON CONFLICT (player_id, game_id)
                DO UPDATE SET
                    wl      = COALESCE(EXCLUDED.wl, player_game_fielding.wl),
                    c      = COALESCE(EXCLUDED.c, player_game_fielding.c),
                    po      = COALESCE(EXCLUDED.po, player_game_fielding.po),
                    a       = COALESCE(EXCLUDED.a, player_game_fielding.a),
                    e       = COALESCE(EXCLUDED.e, player_game_fielding.e),
                    fld     = COALESCE(EXCLUDED.fld, player_game_fielding.fld),
                    dp = COALESCE(EXCLUDED.dp, player_game_fielding.dp),
                    sba = COALESCE(EXCLUDED.sba, player_game_fielding.sba),
                    csb      = COALESCE(EXCLUDED.csb, player_game_fielding.csb),
                    pb      = COALESCE(EXCLUDED.pb, player_game_fielding.pb),
                    ci     = COALESCE(EXCLUDED.ci, player_game_fielding.ci)
            """, (
                player_id, game_id, sgid, g.get("wl"), g.get("c"),
                g.get("po"), g.get("a"), g.get("e"), g.get("fld"),
                g.get("dp"), g.get("sba"), g.get("csb"), g.get("pb"), g.get("ci")
            ))
            print(f"Attributes: c {g.get("c")}, fld%: {g.get("fld")}")
            if cur.rowcount == 1:
                inserted += 1
            else:
                updated += 1
    print(f"[gamelog] inserted={inserted} updated={updated} skipped={skipped}")






def upsert_player_fielding_season_highs(conn, player_id: int, highs):
    
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

            value = _coerce_float(raw.get("value") or raw.get("stat_value"))
            sgid = _extract_sgid(raw)
            raw_dt = raw.get("game_datetime") or raw.get("date")
            game_dt = _parse_dt(raw_dt)
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
                    value          = GREATEST(COALESCE(player_season_highs.value, 0.0), COALESCE(EXCLUDED.value, 0.0)),
                    game_id        = COALESCE(EXCLUDED.game_id, player_season_highs.game_id),
                    source_game_id = COALESCE(EXCLUDED.source_game_id, player_season_highs.source_game_id),
                    game_datetime  = COALESCE(EXCLUDED.game_datetime, player_season_highs.game_datetime),
                    opponent_text  = COALESCE(EXCLUDED.opponent_text, player_season_highs.opponent_text)
            """, (player_id, stat_name, value, game_id, sgid, game_dt, opponent_text))

            inserted += 1  # treat upsert as success
            print(f"season-high row → stat_name={stat_name!r}, value={value}, sgid={sgid}, game_id={game_id}, date={game_dt}, opp={opponent_text!r}")

    print(f"[season_highs] inserted/updated={inserted} skipped={skipped}")
