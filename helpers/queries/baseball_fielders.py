BASEBALL_FIELDERS_SQL = """
SELECT DISTINCT p.id, p.player_id
    FROM players p
    JOIN roster_memberships rm
    ON rm.player_id = p.id
    WHERE rm.position IS NOT NULL;
"""