from __future__ import annotations
from typing import Iterable, Dict, Any, Optional
from helpers.find_game_id_by_source import _find_game_id_by_source
import re
from datetime import datetime
from stats.stats_helpers.parse_dt import _parse_dt 
from stats.stats_helpers.coerce_int import _coerce_int
from stats.stats_helpers.extract_sgid import _extract_sgid


def upsert_player_pitching_gamelog(conn, player_id: int, rows: Iterable[Dict[str, Any]]):

    inserted = updated = skipped = 0
    with conn, conn.cursor() as cur:
        for g in rows:

            sgid = g.get("source_game_id")
            game_id = _find_game_id_by_source(cur, sgid) if sgid else None
    
            if not g.get("game_source_id") and not g.get("game_date"):
                skipped += 1
                continue

            cur.execute("""
                INSERT INTO player_game_pitching (
                    player_id, game_id, source_game_id, wl, ip, h, r, er, bb,
                    so, doubles, triples, hr, wp, bk, hbp, ibb, np, w, l, sv, gera, sera
                ) VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                )
                ON CONFLICT (player_id, game_id)
                DO UPDATE SET
                    wl      = COALESCE(EXCLUDED.wl, player_game_batting.wl),
                    ip      = COALESCE(EXCLUDED.ip, player_game_batting.ip),
                    h      = COALESCE(EXCLUDED.h, player_game_batting.h),
                    r       = COALESCE(EXCLUDED.r, player_game_batting.r),
                    er       = COALESCE(EXCLUDED.er, player_game_batting.er),
                    bb     = COALESCE(EXCLUDED.bb, player_game_batting.bb),
                    so = COALESCE(EXCLUDED.so, player_game_batting.so),
                    doubles = COALESCE(EXCLUDED.doubles, player_game_batting.doubles),
                    triples      = COALESCE(EXCLUDED.triples, player_game_batting.triples),
                    hr      = COALESCE(EXCLUDED.hr, player_game_batting.hr),
                    wp     = COALESCE(EXCLUDED.wp, player_game_batting.wp),
                    bk      = COALESCE(EXCLUDED.bk, player_game_batting.bk),
                    hbp     = COALESCE(EXCLUDED.hbp, player_game_batting.hbp),
                    ibb      = COALESCE(EXCLUDED.ibb, player_game_batting.ibb),
                    np     = COALESCE(EXCLUDED.np, player_game_batting.np),
                    w      = COALESCE(EXCLUDED.w, player_game_batting.w),
                    l      = COALESCE(EXCLUDED.l, player_game_batting.l),
                    sv     = COALESCE(EXCLUDED.sv, player_game_batting.sv),
                    gera       = COALESCE(EXCLUDED.gera, player_game_batting.gera),
                    sera     = COALESCE(EXCLUDED.sera, player_game_batting.sera)
            """, (
                player_id, game_id, sgid, g.get("wl"), g.get("ip"),
                g.get("h"), g.get("r"), g.get("er"), g.get("bb"),
                g.get("so"), g.get("doubles"), g.get("triples"), g.get("hr"), g.get("wp"),
                g.get("bk"), g.get("hbp"), g.get("ibb"), g.get("np"), g.get("w"),
                g.get("l"), g.get("sv"), g.get("gera"), g.get("sera")
            ))
            print(f"Attributes: IP {g.get("ip")}, ERA: {g.get("sera")}")
            if cur.rowcount == 1:
                inserted += 1
            else:
                updated += 1
    print(f"[gamelog] inserted={inserted} updated={updated} skipped={skipped}")






def upsert_player_pitching_season_highs(conn, player_id: int, highs):
    
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
