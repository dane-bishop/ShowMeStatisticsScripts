from helpers.core import BASE

def upsert_schedule(conn, team_season_id: int, games_iter):
    with conn, conn.cursor() as cur:
        for g in games_iter:
            if not g.get("game_date"):
                continue

            # ---- Opponent
            opp_name = g.get("opponent_name")
            if not opp_name:
                continue

            cur.execute("""
                INSERT INTO opponents (name)
                VALUES (%s)
                ON CONFLICT (name_norm) DO NOTHING
                RETURNING id
            """, (opp_name,))
            row = cur.fetchone()
            if row is None:
                cur.execute(
                    "SELECT id FROM opponents WHERE name_norm = lower(regexp_replace(%s,'\\s+',' ','g'))",
                    (opp_name,)
                )
                opp_id = cur.fetchone()[0]
            else:
                opp_id = row[0]

            # ---- Venue
            venue_id = None
            if g.get("venue_city") or g.get("venue_state") or g.get("venue_name"):
                cur.execute("""
                    INSERT INTO venues (name, city, state)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING
                    RETURNING id
                """, (g.get("venue_name"), g.get("venue_city"), g.get("venue_state")))
                r2 = cur.fetchone()
                if r2 is None:
                    cur.execute("""
                        SELECT id FROM venues
                        WHERE (name  IS NOT DISTINCT FROM %s)
                          AND (city  IS NOT DISTINCT FROM %s)
                          AND (state IS NOT DISTINCT FROM %s)
                    """, (g.get("venue_name"), g.get("venue_city"), g.get("venue_state")))
                    v = cur.fetchone()
                    venue_id = v[0] if v else None
                else:
                    venue_id = r2[0]

            # ---- Prefer stable key: source_game_id (boxscore id)
            source_id   = g.get("source_game_id")
            game_time   = g.get("game_time")     # 'HH:MM' or None
            game_number = g.get("game_number")   # 1/2 or None

            if source_id is not None:
                cur.execute("""
                    INSERT INTO games
                      (team_season_id, game_date, location, opponent_id,
                       venue_id, source_url, result, score_for, score_against, notes,
                       source_game_id, game_time, game_number)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT ON CONSTRAINT uniq_games_source
                    DO UPDATE SET
                       venue_id      = COALESCE(EXCLUDED.venue_id, games.venue_id),
                       result        = COALESCE(EXCLUDED.result, games.result),
                       score_for     = COALESCE(EXCLUDED.score_for, games.score_for),
                       score_against = COALESCE(EXCLUDED.score_against, games.score_against),
                       notes         = CASE
                                          WHEN games.notes IS NULL OR games.notes = '' THEN EXCLUDED.notes
                                          ELSE games.notes
                                       END,
                       game_time     = COALESCE(EXCLUDED.game_time, games.game_time),
                       game_number   = COALESCE(EXCLUDED.game_number, games.game_number)
                """, (
                    team_season_id, g["game_date"], g.get("location"), opp_id,
                    venue_id, f"{BASE}/sports/baseball/schedule/{g['game_date'].year}",
                    g.get("result"), g.get("score_for"), g.get("score_against"), g.get("notes"),
                    source_id, game_time, game_number
                ))
                continue

            # ---- No source id → do a NULL-safe UPDATE first, then INSERT if needed
            cur.execute("""
                UPDATE games SET
                   venue_id      = COALESCE(%s, venue_id),
                   result        = COALESCE(%s, result),
                   score_for     = COALESCE(%s, score_for),
                   score_against = COALESCE(%s, score_against),
                   notes         = CASE WHEN notes IS NULL OR notes = '' THEN %s ELSE notes END,
                   source_url    = COALESCE(%s, source_url),
                   game_time     = COALESCE(%s, game_time),
                   game_number   = COALESCE(%s, game_number)
                WHERE team_season_id = %s
                  AND game_date      = %s
                  AND opponent_id    = %s
                  AND location  IS NOT DISTINCT FROM %s
                  AND game_time IS NOT DISTINCT FROM %s
                  AND game_number IS NOT DISTINCT FROM %s
            """, (
                venue_id, g.get("result"), g.get("score_for"), g.get("score_against"),
                g.get("notes"), f"{BASE}/sports/baseball/schedule/{g['game_date'].year}",
                game_time, game_number,
                team_season_id, g["game_date"], opp_id, g.get("location"),
                game_time, game_number
            ))

            if cur.rowcount == 0:
                # Not found → insert new
                cur.execute("""
                    INSERT INTO games
                      (team_season_id, game_date, location, opponent_id,
                       venue_id, source_url, result, score_for, score_against, notes,
                       game_time, game_number)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    team_season_id, g["game_date"], g.get("location"), opp_id,
                    venue_id, f"{BASE}/sports/baseball/schedule/{g['game_date'].year}",
                    g.get("result"), g.get("score_for"), g.get("score_against"), g.get("notes"),
                    game_time, game_number
                ))
