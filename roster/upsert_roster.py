# upsert_roster.py
def upsert_roster(conn, team_season_id: int, people):


    print(f"Upserting roster for Team Season ID: {team_season_id}")
    with conn, conn.cursor() as cur:
        for p in people:


            cur.execute("""
                SELECT id FROM players
                WHERE player_slug = %s AND player_id = %s
            """, (p["slug"], p["mu_player_id"]))
            row = cur.fetchone()

            if row:
                player_id = row[0]
                # keep names fresh (safe, no unique issues)
                cur.execute("UPDATE players SET full_name = %s WHERE id = %s",
                            (p["full_name"], player_id))
            else:
                # 3) otherwise, update one existing row for this slug to the new id
                #    (pick a deterministic one; below uses the newest by updated_at/id)
                cur.execute("""
                    UPDATE players
                    SET full_name = %s, player_id = %s
                    WHERE id = (
                        SELECT id FROM players
                        WHERE player_slug = %s
                        ORDER BY id DESC
                        LIMIT 1
                    )
                    RETURNING id
                """, (p["full_name"], p["mu_player_id"], p["slug"]))
                row = cur.fetchone()

                if row:
                    player_id = row[0]
                else:
                    # 4) no row for this slug at all -> fall back to your original INSERT
                    cur.execute("""
                        INSERT INTO players (full_name, player_slug, player_id)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (player_slug, player_id)
                        DO UPDATE SET full_name = EXCLUDED.full_name
                        RETURNING id
                    """, (p["full_name"], p["slug"], p["mu_player_id"]))
                    player_id = cur.fetchone()[0]



            cur.execute("""
                INSERT INTO roster_memberships
                    (player_id, team_season_id, jersey, position, class_year,
                     height_raw, weight_lbs, bats_throws, hometown, high_school,
                    roster_player_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (player_id, team_season_id)
                DO UPDATE SET jersey = COALESCE(EXCLUDED.jersey, roster_memberships.jersey),
                    position = COALESCE(EXCLUDED.position, roster_memberships.position),
                    class_year = COALESCE(EXCLUDED.class_year, roster_memberships.class_year),
                    height_raw = COALESCE(EXCLUDED.height_raw, roster_memberships.height_raw),
                    weight_lbs = COALESCE(EXCLUDED.weight_lbs, roster_memberships.weight_lbs),
                    bats_throws = COALESCE(EXCLUDED.bats_throws, roster_memberships.bats_throws),
                    hometown = COALESCE(EXCLUDED.hometown, roster_memberships.hometown),
                    high_school = COALESCE(EXCLUDED.high_school, roster_memberships.high_school),
                    roster_player_id = COALESCE(EXCLUDED.roster_player_id, roster_memberships.roster_player_id)
                """, (player_id, team_season_id, p["jersey"], p["position"], p["class_year"],
                  p["height_raw"], p["weight_lbs"], p["bats_throws"], p["hometown"], p["high_school"], p["roster_player_id"]))
