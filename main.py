# main.py (sketch)
from roster.get_roster_baseball import get_roster_baseball
from roster.upsert_roster import upsert_roster
from helpers.core import get_db_connection
from schedule.schedule_helpers.ensure_team_season import ensure_team_season
from roster.get_roster_football import get_roster_from_api
from requests import Session 
from stats.baseball.parse_player_hitting import get_player_hitting_mu
from stats.baseball.upsert_player_hitting import upsert_player_batting_gamelog, upsert_player_hitting_season_highs
from stats.baseball.parse_player_pitching import get_player_pitching_mu
from stats.baseball.upsert_player_pitching import upsert_player_pitching_gamelog, upsert_player_pitching_season_highs
from stats.baseball.parse_player_fielding import get_player_fielding_mu
from stats.baseball.upsert_player_fielding import upsert_player_fielding_gamelog, upsert_player_fielding_season_highs
from schedule.get_schedule_from_api import upsert_games_from_schedule
from helpers.season_ids import FOOTBALL_SEASONS, MENS_BASKETBALL_SEASONS, WOMENS_BASKETBALL_SEASONS, SOFTBALL_SEASONS, VOLLEYBALL_SEASONS
from helpers.core import BASE






conn = get_db_connection()

# Basketball/Golf Years

'''
YEARS = {
    "2024-25",
    "2023-24",
    "2022-23",
    "2021-22",
    "2020-21",
    "2019-20",
    "2018-19",
    "2017-18",
    "2016-17",
    "2015-16",
    "2014-15",
    "2013-14",
    "2012-13",
    "2011-12",
    "2010-11",
    "2009-10",
    "2008-09",
    "2007-08",
    "2006-07",
    "2005-06",
    "2004-05",
    "2003-04",
    "2002-03",
    "2001-02",
    "2000-01"
}
'''


YEARS = {
    "2025",
    "2024",
    "2023",
    "2022",
    "2021",
    "2020",
    "2019",
    "2018",
    "2017",
    "2016",
    "2015",
    "2014",
    "2013",
    "2012",
    "2011",
    "2010",
    "2009",
    "2008",
    "2007",
    "2006",
    "2005",
    "2004",
    "2003",
    "2002",
    "2001",
    "2000"
}


def season_to_year(season_str: str, use="start") -> int:
    """
    Convert 'YYYY-YY' -> an integer year for DB.
    use='start' -> 2024
    use='end'   -> 2025 (assumes two-digit end and 2000s)
    """
    left, right = season_str.split("-")
    start = int(left)
    if use == "end":
        # handle '25' -> 2025; adjust if your data ever spans centuries
        end = int(right)
        end += 2000 if end < 100 else 0
        return end
    return start






# -------------------------------
# ROSTERS
# -------------------------------



# GET BASEBALL ROSTER BY SEASON 
'''
for year in YEARS:
    tsid = ensure_team_season(conn, school="Missouri", sport_key="baseball", sport_name="Baseball", year=year, sport_slug="baseball")
    for person in get_roster_baseball('baseball', year):
        upsert_roster(conn, tsid, [person]) 
'''

# GET FOOTBALL ROSTER BY SEASON 
'''
for year in YEARS:

    tsid = ensure_team_season(conn, school="Missouri", sport_key="football", sport_name="Football", year=year, sport_slug="football")
    for person in get_roster_from_api('football', year):
        upsert_roster(conn, tsid, [person])
'''

# GET BASKETBALL ROSTER BY SEASON
'''
for season in YEARS:

    api_season = season            
    db_year    = season_to_year(season, use="start")
    tsid = ensure_team_season(conn, school="Missouri", sport_key="mens-basketball", sport_name="Men's Basketball", year=db_year, sport_slug="mens-basketball")
    for person in get_roster_from_api('mens-basketball', api_season):
        upsert_roster(conn, tsid, [person])
'''

# GET BASKETBALL ROSTER BY SEASON (Womens)
'''
for season in YEARS:

    api_season = season            
    db_year    = season_to_year(season, use="start")
    tsid = ensure_team_season(conn, school="Missouri", sport_key="womens-basketball", sport_name="Women's Basketball", year=db_year, sport_slug="womens-basketball")
    for person in get_roster_from_api('womens-basketball', api_season):
        upsert_roster(conn, tsid, [person])
'''

# GET GOLF ROSTER BY SEASON
'''
for season in YEARS:

    api_season = season            
    db_year    = season_to_year(season, use="start")
    tsid = ensure_team_season(conn, school="Missouri", sport_key="mens-golf", sport_name="Men's Golf", year=db_year, sport_slug="mens-golf")
    for person in get_roster_from_api('mens-golf', api_season):
        upsert_roster(conn, tsid, [person])
'''

# GET GOLF ROSTER BY SEASON (WOMENS)    
'''
for season in YEARS:

    api_season = season            
    db_year    = season_to_year(season, use="start")
    tsid = ensure_team_season(conn, school="Missouri", sport_key="womens-golf", sport_name="Women's Golf", year=db_year, sport_slug="womens-golf")
    for person in get_roster_from_api('womens-golf', api_season):
        upsert_roster(conn, tsid, [person])
'''
        

# GET WOMENS SOCCER ROSTER
'''
for year in YEARS:
    tsid = ensure_team_season(conn, school="Missouri", sport_key="womens-soccer", sport_name="Women's Soccer", year=year, sport_slug="womens-soccer")
    for person in get_roster_from_api('womens-soccer', year):
        upsert_roster(conn, tsid, [person])
'''

# GET SOFTBALL ROSTER
'''
for year in YEARS:
    tsid = ensure_team_season(conn, school="Missouri", sport_key="softball", sport_name="Softball", year=year, sport_slug="softball")
    for person in get_roster_from_api('softball', year):
        upsert_roster(conn, tsid, [person])
'''


# GET VOLLEYBALL ROSTER
'''
for year in YEARS:
    tsid = ensure_team_season(conn, school="Missouri", sport_key="womens-volleyball", sport_name="Women's Volleyball", year=year, sport_slug="womens-volleyball")
    for person in get_roster_from_api('womens-volleyball', year):
        upsert_roster(conn, tsid, [person])
'''































# -------------------------------
# SCHEDULES
# -------------------------------





# GET BASEBALL SCHEDULE BY SEASON
'''
for game in get_schedule_baseball('baseball', 2025, debug=False):
    upsert_schedule_baseball(conn, tsid, [game])

'''

# GET FOOTBALL SCHEDULE BY API ID's - DONE
'''

for season_id, year in FOOTBALL_SEASONS.items():
    tsid = ensure_team_season(conn, school="Missouri", sport_key="football", sport_name="Football", year=year, sport_slug="football")
    upsert_games_from_schedule(conn, tsid, season_id)
'''

# GET MENS BASKETBALL SCHEDULE BY ID's - DONE
'''

for season_id, year in MENS_BASKETBALL_SEASONS.items():
    tsid = ensure_team_season(conn, school="Missouri", sport_key="mens-basketball", sport_name="Men's Basketball", year=year, sport_slug="mens-basketball")
    upsert_games_from_schedule(conn, tsid, season_id)
'''

# GET WOMENS BASKETBALL SCHEDULE BY ID's - DONE
'''

for season_id, year in WOMENS_BASKETBALL_SEASONS.items():
    tsid = ensure_team_season(conn, school="Missouri", sport_key="womens-basketball", sport_name="Women's Basketball", year=year, sport_slug="womens-basketball")
    upsert_games_from_schedule(conn, tsid, season_id)
'''

# GET SOFTBALL SCHEDULE BY ID's - DONE
'''

for season_id, year in SOFTBALL_SEASONS.items():
    tsid = ensure_team_season(conn, school="Missouri", sport_key="softball", sport_name="Softball", year=year, sport_slug="softball")
    upsert_games_from_schedule(conn, tsid, season_id)
'''

# GET VOLLEYBALL SCHEDULE BY ID's - DONE
'''
for season_id, year in VOLLEYBALL_SEASONS.items():
    tsid = ensure_team_season(conn, school="Missouri", sport_key="womens-volleyball", sport_name="Women's Volleyball", year=year, sport_slug="womens-volleyball")
    upsert_games_from_schedule(conn, tsid, season_id)
'''








# -------------------------------
# STATS
# -------------------------------


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
'''

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
'''




# GET FOOTBALL PLAYER OFFENSE STATS

# GET FOOTBALL PLAYER DEFENSE STATS

# GET FOOTBALL PLAYER SPECIAL TEAMS STATS



# GET BASKETBALL PLAYER STATS (Men's and Women's)






