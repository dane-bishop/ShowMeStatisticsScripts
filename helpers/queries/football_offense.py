FOOTBALL_OFFENSE_SQL = """
SELECT 
            p.id,
            rm.roster_player_id
        FROM players p
        JOIN roster_memberships rm ON rm.player_id = p.id
        JOIN team_seasons ts       ON ts.id = rm.team_season_id
        JOIN teams t               ON t.id = ts.team_id
        JOIN sports s              ON s.id = t.sport_id
        CROSS JOIN LATERAL regexp_split_to_array(upper(rm.position), '[^A-Z]+') AS pos_tokens
        WHERE s.name = 'Football' 
        AND ts.year = %s
        AND rm.position IS NOT NULL
        AND rm.roster_player_id IS NOT NULL

        -- OFFENSE: include if any of these are present
        AND (
            -- single-token roles
            pos_tokens && ARRAY[
                'QB','QUARTERBACK',
                'RB','TB','FB',             -- Running/Tail/Full back
                'WR',                       -- Wide Receiver
                'TE',                       -- Tight End
                'OL',                       -- Offensive Line (abbr)
                'OT','OG','G','C'           -- Tackle, Guard, Center
            ]
            -- multi-word roles (pairs)
            OR ( 'WIDE' = ANY(pos_tokens)      AND 'RECEIVER' = ANY(pos_tokens) )
            OR ( 'TIGHT' = ANY(pos_tokens)     AND 'END'      = ANY(pos_tokens) )
            OR (
                'OFFENSIVE' = ANY(pos_tokens)
            AND ( 'LINE' = ANY(pos_tokens) OR 'LINEMAN' = ANY(pos_tokens) OR 'LINEMEN' = ANY(pos_tokens) )
            )
            OR ( 'RUNNING' = ANY(pos_tokens)   AND 'BACK'     = ANY(pos_tokens) )
            OR ( 'TAILBACK' = ANY(pos_tokens) )
        )

        -- keep the most recent season per player id
        ORDER BY p.id, ts.year DESC
"""