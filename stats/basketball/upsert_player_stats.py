from __future__ import annotations
from typing import Iterable, Dict, Any, Optional
from helpers.etc.find_game_id_by_source import _find_game_id_by_source
import re
from datetime import datetime
from stats.stats_helpers.parse_dt import _parse_dt 
from stats.stats_helpers.coerce_int import _coerce_int
from stats.stats_helpers.extract_sgid import _extract_sgid
from stats.stats_helpers.coerce_float import _coerce_float


def upsert_player_basketball_gamelog(conn, player_id: int, rows: Iterable[Dict[str, Any]]):

    inserted = updated = skipped = 0
    with conn, conn.cursor() as cur:
        for g in rows:

            sgid = g.get("source_game_id")
            game_id = _find_game_id_by_source(cur, sgid) if sgid else None
    
            if not sgid and not g.get("game_date"):
                skipped += 1
                continue

            cur.execute("""
                INSERT INTO player_game_basketball (
                    player_id, game_id, source_game_id,
                    minutes, fg_made, fg_att, fg_pct, 
                    three_made, three_att, three_pct,
                    ft_made, ft_att, ft_pct,
                    off_r, dr, tr, r_avg,
                    pf, ast, turnovers,
                    blk, stl, pts, pts_avg
                ) VALUES (
                    %s,%s,%s,
                    %s,%s,%s,%s,
                    %s,%s,%s,
                    %s,%s,%s,
                    %s,%s,%s,%s,
                    %s,%s,%s,
                    %s,%s,%s,%s
                )
                ON CONFLICT (player_id, game_id)
                DO UPDATE SET
                    source_game_id = COALESCE(EXCLUDED.source_game_id, player_game_basketball.source_game_id),

                    minutes = COALESCE(EXCLUDED.minutes, player_game_basketball.minutes),
                    fg_made = COALESCE(EXCLUDED.fg_made, player_game_basketball.fg_made),
                    fg_att = COALESCE(EXCLUDED.fg_att, player_game_basketball.fg_att),
                    fg_pct = COALESCE(EXCLUDED.fg_pct, player_game_basketball.fg_pct),

                    three_made = COALESCE(EXCLUDED.three_made, player_game_basketball.three_made),
                    three_att = COALESCE(EXCLUDED.three_att, player_game_basketball.three_att),
                    three_pct = COALESCE(EXCLUDED.three_pct, player_game_basketball.three_pct),

                    ft_made = COALESCE(EXCLUDED.ft_made, player_game_basketball.ft_made),
                    ft_att = COALESCE(EXCLUDED.ft_att, player_game_basketball.ft_att),
                    ft_pct = COALESCE(EXCLUDED.ft_pct, player_game_basketball.ft_pct),

                    off_r = COALESCE(EXCLUDED.off_r, player_game_basketball.off_r),
                    dr = COALESCE(EXCLUDED.dr, player_game_basketball.dr),
                    tr = COALESCE(EXCLUDED.tr, player_game_basketball.tr),
                    r_avg = COALESCE(EXCLUDED.r_avg, player_game_basketball.r_avg),
                        
                    pf = COALESCE(EXCLUDED.pf, player_game_basketball.pf),
                    ast = COALESCE(EXCLUDED.ast, player_game_basketball.ast),
                    turnovers = COALESCE(EXCLUDED.turnovers, player_game_basketball.turnovers),

                    blk = COALESCE(EXCLUDED.blk, player_game_basketball.blk),
                    stl = COALESCE(EXCLUDED.stl, player_game_basketball.stl),
                    pts = COALESCE(EXCLUDED.pts, player_game_basketball.pts),
                    pts_avg = COALESCE(EXCLUDED.pts_avg, player_game_basketball.pts_avg)

            """, (
                player_id, game_id, sgid,
                g.get("minutes"), g.get("fg_made"), g.get("fg_att"), g.get("fg_pct"),
                g.get("three_made"), g.get("three_att"), g.get("three_pct"),
                g.get("ft_made"), g.get("ft_att"), g.get("ft_pct"),
                g.get("off_r"), g.get("dr"), g.get("tr"), g.get("r_avg"),
                g.get("pf"), g.get("ast"), g.get("turnovers"),
                g.get("blk"), g.get("stl"), g.get("pts"), g.get("pts_avg"),
            ))

            print(f"Attributes: Points {g.get("pts")}, Assists: {g.get("ast")}")
            if cur.rowcount == 1:
                inserted += 1
            else:
                updated += 1
    print(f"[gamelog] inserted={inserted} updated={updated} skipped={skipped}")






def upsert_player_basketball_season_highs(conn, player_id: int, highs):
    
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
