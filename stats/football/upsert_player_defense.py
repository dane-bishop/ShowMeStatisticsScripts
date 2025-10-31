from __future__ import annotations
from typing import Iterable, Dict, Any, Optional
from helpers.find_game_id_by_source import _find_game_id_by_source
import re
from datetime import datetime
from stats.stats_helpers.parse_dt import _parse_dt 
from stats.stats_helpers.coerce_int import _coerce_int
from stats.stats_helpers.extract_sgid import _extract_sgid
from stats.stats_helpers.coerce_float import _coerce_float


def upsert_player_football_defense_gamelog(conn, player_id: int, rows: Iterable[Dict[str, Any]]):

    inserted = updated = skipped = 0
    with conn, conn.cursor() as cur:
        for g in rows:

            sgid = g.get("source_game_id")
            game_id = _find_game_id_by_source(cur, sgid) if sgid else None
    
            if not g.get("game_source_id") and not g.get("game_date"):
                skipped += 1
                continue

            cur.execute("""
                INSERT INTO player_game_football_offense (
                    player_id, game_id, source_game_id,
                    solo, ast, ttot, tfl, tyds,
                    stot, syds,
                    ff, fr, fyds,
                    ints, int_yds,
                    qbh, brk, kick, saf 
                ) VALUES (
                    %s,%s,%s,
                    %s,%s,%s,%s,%s,
                    %s,%s,
                    %s,%s,%s,
                    %s,%s,
                    %s,%s,%s,%s
                )
                ON CONFLICT (player_id, game_id)
                DO UPDATE SET
                    source_game_id = COALESCE(EXCLUDED.source_game_id, player_game_football_defense.source_game_id),

                    solo = COALESCE(EXCLUDED.solo, player_game_football_defense.solo),
                    ast = COALESCE(EXCLUDED.ast, player_game_football_defense.ast),
                    ttot = COALESCE(EXCLUDED.ttot, player_game_football_defense.ttot),
                    tfl = COALESCE(EXCLUDED.tfl, player_game_football_defense.tfl),
                    tyds = COALESCE(EXCLUDED.tyds, player_game_football_defense.tyds),
                    
                    stot = COALESCE(EXCLUDED.stot, player_game_football_defense.stot),
                    syds = COALESCE(EXCLUDED.syds, player_game_football_defense.syds),
                    ff = COALESCE(EXCLUDED.ff, player_game_football_defense.ff),
                    fr = COALESCE(EXCLUDED.fr, player_game_football_defense.fr),
                    fyds = COALESCE(EXCLUDED.fyds, player_game_football_defense.fyds),
                        
                    ints = COALESCE(EXCLUDED.ints, player_game_football_defense.ints),
                    int_yds = COALESCE(EXCLUDED.int_yds, player_game_football_defense.int_yds),
                    qbh = COALESCE(EXCLUDED.qbh, player_game_football_defense.qbh),
                    brk = COALESCE(EXCLUDED.brk, player_game_football_defense.brk),
                    kick = COALESCE(EXCLUDED.kick, player_game_football_defense.kick),
                    saf = COALESCE(EXCLUDED.saf, player_game_football_defense.saf),
            """, (
                player_id, game_id, sgid,
                g.get("solo"), g.get("ast"), g.get("ttot"), g.get("tfl"),
                g.get("tyds"), g.get("stot"), g.get("syds"),
                g.get("ff"), g.get("fr"), g.get("fyds"), g.get("ints"),
                g.get("int_yds"), g.get("qbh"), g.get("brk"), g.get("kick"),
                g.get("saf"), 
            ))

            print(f"Attributes: Tackles {g.get("ttot")}, Interceptions: {g.get("ints")}")
            if cur.rowcount == 1:
                inserted += 1
            else:
                updated += 1
    print(f"[gamelog] inserted={inserted} updated={updated} skipped={skipped}")






def upsert_player_football_defense_season_highs(conn, player_id: int, highs):
    
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
