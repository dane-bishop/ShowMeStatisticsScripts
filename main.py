# main.py (sketch)
from roster.get_roster_baseball import get_roster_baseball
from roster.upsert_roster_baseball import upsert_roster_baseball
from helpers.core import get_db_connection
from schedule.schedule_helpers.ensure_team_season import ensure_team_season
from requests import Session 
from stats.baseball.parse_player_hitting import get_player_hitting_mu
from stats.baseball.upsert_player_hitting import upsert_player_batting_gamelog, upsert_player_hitting_season_highs
from stats.baseball.parse_player_pitching import get_player_pitching_mu
from stats.baseball.upsert_player_pitching import upsert_player_pitching_gamelog, upsert_player_pitching_season_highs
from stats.baseball.parse_player_fielding import get_player_fielding_mu
from stats.baseball.upsert_player_fielding import upsert_player_fielding_gamelog, upsert_player_fielding_season_highs
from helpers.core import BASE

conn = get_db_connection()
tsid = ensure_team_season(conn, school="Missouri", sport_key="baseball", sport_name="Baseball", year=2025, sport_slug="baseball")


YEARS = {
    2025
}




# GET BASEBALL ROSTER BY SEASON
'''
for year in YEARS:
    tsid = ensure_team_season(conn, school="Missouri", sport_key="baseball", sport_name="Baseball", year=year, sport_slug="baseball")
    for person in get_roster_baseball('baseball', year):
        upsert_roster_baseball(conn, tsid, [person]) 
'''

# GET BASEBALL SCHEDULE BY SEASON
'''
for game in get_schedule_baseball('baseball', 2025, debug=False):
    upsert_schedule_baseball(conn, tsid, [game])

'''



# GET BASEBALL PLAYER HITTING STATS BY PLAYER LINK

'''
sess = Session()
#player_id = 4  
#roster_player_id = 26046      
year = 2025

with conn.cursor() as cur:
    cur.execute("""
    SELECT p.id, p.player_id 
    FROM players p
    JOIN roster_memberships rm 
    ON rm.player_id = p.id
    WHERE rm.position IS NOT NULL AND UPPER(rm.position) NOT IN ('RHP', 'LHP')
                
    """)
    batters = cur.fetchall()

print(f"Adding data for {len(batters)} batters")

for (player_id, roster_player_id) in batters:
    print(f"Player ID: {player_id} - Roster Player ID: {roster_player_id}")

    parsed = get_player_hitting_mu(sess, roster_player_id, year)
    print("first 2 rows:", parsed["gamelog"][:2])


    upsert_player_batting_gamelog(conn, player_id=player_id, rows=parsed["gamelog"])
    upsert_player_hitting_season_highs(conn, player_id=player_id, highs=parsed["season_highs"])
'''




# GET BASEBALL PLAYER PITCHING STATS BY PLAYER LINK
'''
sess = Session()
year = 2025

with conn.cursor() as cur:
    cur.execute("""
    SELECT DISTINCT p.id, p.player_id
    FROM players p
    JOIN roster_memberships rm
    ON rm.player_id = p.id
    WHERE rm.position IS NOT NULL AND UPPER(rm.position) LIKE ANY (ARRAY['%RHP%', '%LHP%'])
    """)
    pitchers = cur.fetchall()

print(f"Adding data for {len(pitchers)} pitchers")

for (player_id, roster_player_id) in pitchers:
    print(f"Player ID: {player_id} - Roster Player ID: {roster_player_id}")

    parsed = get_player_pitching_mu(sess, roster_player_id, year)
    print("first 2 rows: ", parsed["gamelog"][:2])

    upsert_player_pitching_gamelog(conn, player_id=player_id, rows=parsed["gamelog"])
    upsert_player_pitching_season_highs(conn, player_id=player_id, highs=parsed["season_highs"])

'''


# GET BASEBALL PLAYER FIELDING STATS BY PLAYER LINK
sess = Session()
year = 2025

with conn.cursor() as cur:
    cur.execute("""
    SELECT DISTINCT p.id, p.player_id
    FROM players p
    JOIN roster_memberships rm
    ON rm.player_id = p.id
    WHERE rm.position IS NOT NULL
    """)
    players = cur.fetchall()

print(f"Adding data for {len(players)} players")

for (player_id, roster_player_id) in players:
    print(f"Player ID: {player_id} - Roster Player ID: {roster_player_id}")

    parsed = get_player_fielding_mu(sess, roster_player_id, year)
    print("first 2 rows: ", parsed["gamelog"][:2])

    upsert_player_fielding_gamelog(conn, player_id=player_id, rows=parsed["gamelog"])
    upsert_player_fielding_season_highs(conn, player_id=player_id, highs=parsed["season_highs"])
