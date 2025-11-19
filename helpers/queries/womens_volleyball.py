WOMENS_VOLLEYBALL_SQL = """
SELECT
    p.id,
    rm.roster_player_id
FROM players p
JOIN roster_memberships rm ON rm.player_id = p.id
JOIN team_seasons ts       ON ts.id = rm.team_season_id
JOIN teams t               ON t.id = ts.team_id
JOIN sports s              ON s.id = t.sport_id
CROSS JOIN LATERAL (
    SELECT regexp_split_to_array(upper(rm.position), '[^A-Z]+') AS pos_tokens
) pt
WHERE s.key = 'womens-volleyball'
AND ts.year = %s
AND rm.position IS NOT NULL
AND rm.roster_player_id IS NOT NULL
ORDER BY p.id, ts.year DESC;      
"""