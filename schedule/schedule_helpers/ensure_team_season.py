def ensure_team_season(conn, school, sport_key, sport_name, year, sport_slug):
    with conn, conn.cursor() as cur:
        cur.execute("INSERT INTO sports(key,name) VALUES(%s,%s) ON CONFLICT (key) DO UPDATE SET name=EXCLUDED.name RETURNING id",
                    (sport_key, sport_name))
        sport_id = cur.fetchone()[0]
        cur.execute("""
            INSERT INTO teams (school_name, sport_id, site_slug)
            VALUES (%s,%s,%s)
            ON CONFLICT (school_name, sport_id) DO UPDATE SET site_slug=EXCLUDED.site_slug
            RETURNING id
        """, (school, sport_id, sport_slug))
        team_id = cur.fetchone()[0]
        cur.execute("""
            INSERT INTO team_seasons (team_id, year)
            VALUES (%s,%s)
            ON CONFLICT (team_id, year) DO NOTHING
            RETURNING id
        """, (team_id, year))
        row = cur.fetchone()
        if row: return row[0]
        cur.execute("SELECT id FROM team_seasons WHERE team_id=%s AND year=%s", (team_id, year))
        return cur.fetchone()[0]