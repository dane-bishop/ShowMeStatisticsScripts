# upsert_roster.py
def upsert_roster(conn, team_season_id: int, people):


    print(f"Upserting roster for Team Season ID: {team_season_id}")
    with conn, conn.cursor() as cur:
        for p in people:
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
                     height_raw, weight_lbs, bats_throws, hometown, high_school)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (player_id, team_season_id)
                DO UPDATE SET jersey = COALESCE(EXCLUDED.jersey, roster_memberships.jersey),
                              position = COALESCE(EXCLUDED.position, roster_memberships.position),
                              class_year = COALESCE(EXCLUDED.class_year, roster_memberships.class_year),
                              height_raw = COALESCE(EXCLUDED.height_raw, roster_memberships.height_raw),
                              weight_lbs = COALESCE(EXCLUDED.weight_lbs, roster_memberships.weight_lbs),
                              bats_throws = COALESCE(EXCLUDED.bats_throws, roster_memberships.bats_throws),
                              hometown = COALESCE(EXCLUDED.hometown, roster_memberships.hometown),
                              high_school = COALESCE(EXCLUDED.high_school, roster_memberships.high_school)
            """, (player_id, team_season_id, p["jersey"], p["position"], p["class_year"],
                  p["height_raw"], p["weight_lbs"], p["bats_throws"], p["hometown"], p["high_school"]))
