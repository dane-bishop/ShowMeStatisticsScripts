FOOTBALL_DEFENSE_SQL = """
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
        WHERE s.name = 'Football'
        AND ts.year = %s
        AND rm.position IS NOT NULL
        AND rm.roster_player_id IS NOT NULL

        -- DEFENSE: include if any defensive indicators are present
        AND (
            -- single-token roles
            pt.pos_tokens && ARRAY[
                'DB','CB','S','SS','FS',
                'DL','DE','DT','NT',
                'LB','ILB','MLB','OLB',
                'EDGE','DEFENSE','DEFENSIVE',
                'CORNERBACK','SAFETY','LINEBACKER',
                'LINEMAN','LINEMEN','DEFENSIVEBACK','DEFENSIVELINE'
            ]
            -- multi-word / composed roles
            OR ('CORNER'    = ANY(pt.pos_tokens) AND 'BACK'   = ANY(pt.pos_tokens)) -- cornerback
            OR ('LINE'      = ANY(pt.pos_tokens) AND ('BACKER' = ANY(pt.pos_tokens) OR 'BACKERS' = ANY(pt.pos_tokens))) -- linebacker
            OR ('DEFENSIVE' = ANY(pt.pos_tokens) AND ('END' = ANY(pt.pos_tokens) OR 'TACKLE' = ANY(pt.pos_tokens) OR 'LINE' = ANY(pt.pos_tokens) OR 'BACK' = ANY(pt.pos_tokens)))
        )

        -- Optional: EXCLUDE obvious special-teams roles even if mixed (WR/DB won’t be excluded)
        AND NOT (
            pt.pos_tokens && ARRAY['K','P','PK','PUNTER','KICKER','PLACEKICKER','LS']
            OR ('LONG' = ANY(pt.pos_tokens) AND 'SNAPPER' = ANY(pt.pos_tokens))
        )
        ORDER BY p.id, ts.year DESC;

"""