BASEBALL_PITCHERS_SQL = """
SELECT DISTINCT p.id, p.player_id
    FROM players p
    JOIN roster_memberships rm
    ON rm.player_id = p.id
    WHERE rm.position IS NOT NULL AND UPPER(rm.position) LIKE ANY (ARRAY['%RHP%', '%LHP%'])
"""