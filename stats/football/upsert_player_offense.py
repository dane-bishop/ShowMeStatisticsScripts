from __future__ import annotations
from typing import Iterable, Dict, Any, Optional
from helpers.find_game_id_by_source import _find_game_id_by_source
import re
from datetime import datetime
from stats.stats_helpers.parse_dt import _parse_dt 
from stats.stats_helpers.coerce_int import _coerce_int
from stats.stats_helpers.extract_sgid import _extract_sgid
from stats.stats_helpers.coerce_float import _coerce_float


def upsert_player_football_offense_gamelog(conn, player_id: int, rows: Iterable[Dict[str, Any]]):

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
                    pass_comp, pass_att, pass_int, pass_pct, pass_yds, pass_tds, pass_lng,
                    rush_att, rush_yds, rush_tds, rush_lng,
                    rec, rec_yds, rec_tds, rec_lng,
                    kr_ret, kr_yds, kr_tds, kr_lng,
                    pr_ret, pr_yds, pr_tds, pr_lng
                ) VALUES (
                    %s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,
                    %s,%s,%s,%s,
                    %s,%s,%s,%s,
                    %s,%s,%s,%s
                )
                ON CONFLICT (player_id, game_id)
                DO UPDATE SET
                    source_game_id = COALESCE(EXCLUDED.source_game_id, player_game_football_offense.source_game_id),

                    pass_comp = COALESCE(EXCLUDED.pass_comp, player_game_football_offense.pass_comp),
                    pass_att  = COALESCE(EXCLUDED.pass_att,  player_game_football_offense.pass_att),
                    pass_int  = COALESCE(EXCLUDED.pass_int,  player_game_football_offense.pass_int),
                    pass_pct  = COALESCE(EXCLUDED.pass_pct,  player_game_football_offense.pass_pct),
                    pass_yds  = COALESCE(EXCLUDED.pass_yds,  player_game_football_offense.pass_yds),
                    pass_tds   = COALESCE(EXCLUDED.pass_tds,   player_game_football_offense.pass_tds),
                    pass_lng = COALESCE(EXCLUDED.pass_lng, player_game_football_offense.pass_lng),

                    rush_att  = COALESCE(EXCLUDED.rush_att,  player_game_football_offense.rush_att),
                    rush_yds  = COALESCE(EXCLUDED.rush_yds,  player_game_football_offense.rush_yds),
                    rush_tds   = COALESCE(EXCLUDED.rush_tds,   player_game_football_offense.rush_tds),
                    rush_lng = COALESCE(EXCLUDED.rush_lng, player_game_football_offense.rush_lng),

                    rec_rec   = COALESCE(EXCLUDED.rec_rec,   player_game_football_offense.rec_rec),
                    rec_yds   = COALESCE(EXCLUDED.rec_yds,   player_game_football_offense.rec_yds),
                    rec_tds    = COALESCE(EXCLUDED.rec_tds,    player_game_football_offense.rec_tds),
                    rec_lng  = COALESCE(EXCLUDED.rec_lng,  player_game_football_offense.rec_lng),

                    kr_ret    = COALESCE(EXCLUDED.kr_ret,    player_game_football_offense.kr_ret),
                    kr_yds    = COALESCE(EXCLUDED.kr_yds,    player_game_football_offense.kr_yds),
                    kr_tds     = COALESCE(EXCLUDED.kr_tds,     player_game_football_offense.kr_tds),
                    kr_lng   = COALESCE(EXCLUDED.kr_lng,   player_game_football_offense.kr_lng),

                    pr_ret    = COALESCE(EXCLUDED.pr_ret,    player_game_football_offense.pr_ret),
                    pr_yds    = COALESCE(EXCLUDED.pr_yds,    player_game_football_offense.pr_yds),
                    pr_tds     = COALESCE(EXCLUDED.pr_tds,     player_game_football_offense.pr_tds),
                    pr_lng   = COALESCE(EXCLUDED.pr_lng,   player_game_football_offense.pr_lng)
            """, (
                player_id, game_id, sgid,
                g.get("pass_comp"), g.get("pass_att"), g.get("pass_int"), g.get("pass_pct"),
                g.get("pass_yds"), g.get("pass_tds"), g.get("pass_lng"),
                g.get("rush_att"), g.get("rush_yds"), g.get("rush_tds"), g.get("rush_lng"),
                g.get("rec_rec"), g.get("rec_yds"), g.get("rec_tds"), g.get("rec_lng"),
                g.get("kr_ret"), g.get("kr_yds"), g.get("kr_tds"), g.get("kr_lng"),
                g.get("pr_ret"), g.get("pr_yds"), g.get("pr_tds"), g.get("pr_lng"),
            ))

            print(f"Attributes: Pass Att. {g.get("pass_att")}, Rush Yds: {g.get("rush_yds")}")
            if cur.rowcount == 1:
                inserted += 1
            else:
                updated += 1
    print(f"[gamelog] inserted={inserted} updated={updated} skipped={skipped}")






def upsert_player_football_offense_season_highs(conn, player_id: int, highs):
    
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
