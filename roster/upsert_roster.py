def upsert_roster(conn, team_season_id: int, people):
    with conn, conn.cursor() as cur:
        for p in people:
            # players
            cur.execute("""
                INSERT INTO players (full_name, player_slug, player_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (player_slug, player_id)
                DO UPDATE SET full_name = EXCLUDED.full_name
                RETURNING id
            """, (p["full_name"], p["slug"], p["mu_player_id"]))
            player_id = cur.fetchone()[0]

            # roster_memberships
            cur.execute("""
                INSERT INTO roster_memberships
                    (player_id, team_season_id, jersey, position, class_year,
                     height_raw, weight_lbs, bats_throws, hometown, high_school)
                VALUES (%s,%s,NULL,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (player_id, team_season_id)
                DO UPDATE SET position=EXCLUDED.position,
                              class_year=EXCLUDED.class_year,
                              height_raw=EXCLUDED.height_raw,
                              weight_lbs=EXCLUDED.weight_lbs,
                              bats_throws=EXCLUDED.bats_throws,
                              hometown=EXCLUDED.hometown,
                              high_school=EXCLUDED.high_school
            """, (player_id, team_season_id, p["position"], p["class_year"],
                  p["height_raw"], p["weight_lbs"], p["bats_throws"],
                  p["hometown"], p["high_school"]))