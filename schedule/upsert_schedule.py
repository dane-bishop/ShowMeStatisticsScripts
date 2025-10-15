def upsert_schedule(conn, team_season_id: int, games_iter):
    with conn, conn.cursor() as cur:
        for g in games_iter:
            # opponent
            cur.execute("""
                INSERT INTO opponents (name) VALUES (%s)
                ON CONFLICT (name_norm) DO NOTHING
                RETURNING id
            """, (g["opponent_name"],))
            row = cur.fetchone()
            if row is None:
                cur.execute("SELECT id FROM opponents WHERE name_norm = lower(regexp_replace(%s,'\\s+',' ','g'))",
                            (g["opponent_name"],))
                opp_id = cur.fetchone()[0]
            else:
                opp_id = row[0]

            # venue (optional)
            venue_id = None
            if g["venue_city"] or g["venue_state"]:
                cur.execute("""
                    INSERT INTO venues (name, city, state)
                    VALUES (NULL, %s, %s)
                    ON CONFLICT DO NOTHING
                    RETURNING id
                """, (g["venue_city"], g["venue_state"]))
                r2 = cur.fetchone()
                if r2 is None:
                    cur.execute("SELECT id FROM venues WHERE city IS NOT DISTINCT FROM %s AND state IS NOT DISTINCT FROM %s",
                                (g["venue_city"], g["venue_state"]))
                    v = cur.fetchone()
                    venue_id = v[0] if v else None
                else:
                    venue_id = r2[0]

            # game
            cur.execute("""
                INSERT INTO games
                  (team_season_id, game_date, location, opponent_id, venue_id, result, score_for, score_against, source_url)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (team_season_id, game_date, opponent_id, location)
                DO UPDATE SET result=EXCLUDED.result,
                              score_for=EXCLUDED.score_for,
                              score_against=EXCLUDED.score_against,
                              venue_id = COALESCE(EXCLUDED.venue_id, games.venue_id),
                              source_url = EXCLUDED.source_url
            """, (team_season_id, g["game_date"], g["location"], opp_id, venue_id,
                  g["result"], g["score_for"], g["score_against"], g["source"]))