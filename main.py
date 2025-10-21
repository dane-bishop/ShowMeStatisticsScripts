# main.py (sketch)
from roster.get_roster_baseball import get_roster_baseball
from roster.upsert_roster_baseball import upsert_roster_baseball
from helpers.core import get_db_connection
from schedule.schedule_helpers.ensure_team_season import ensure_team_season
from requests import Session 
from stats.parse_player_hitting import get_player_hitting_mu
from stats.upsert_player_hitting import upsert_player_batting_gamelog, upsert_player_hitting_season_highs
from helpers.core import BASE

conn = get_db_connection()
tsid = ensure_team_season(conn, school="Missouri", sport_key="baseball", sport_name="Baseball", year=2025, sport_slug="baseball")


# Stream roster straight into DB


YEARS = {
    2025
}

'''
# GET BASEBALL ROSTER BY SEASON
for year in YEARS:
    tsid = ensure_team_season(conn, school="Missouri", sport_key="baseball", sport_name="Baseball", year=year, sport_slug="baseball")
    for person in get_roster_baseball('baseball', year):
        upsert_roster_baseball(conn, tsid, [person]) 


# GET BASEBALL SCHEDULE BY SEASON
for game in get_schedule_baseball('baseball', 2025, debug=False):
    upsert_schedule_baseball(conn, tsid, [game])

'''



# GET BASEBALL PLAYER STATS BY PLAYER LINK
sess = Session()
player_id = 4                
roster_player_id = 26046      
year = 2025

parsed = get_player_hitting_mu(sess, roster_player_id, year)
print("first 2 rows:", parsed["gamelog"][:2])


upsert_player_batting_gamelog(conn, player_id=player_id, rows=parsed["gamelog"])
upsert_player_hitting_season_highs(conn, player_id=player_id, highs=parsed["season_highs"])
