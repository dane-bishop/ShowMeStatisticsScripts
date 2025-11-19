from roster.get_roster_baseball import get_roster_baseball
from roster.upsert_roster import upsert_roster
from helpers.core import get_db_connection
from schedule.schedule_helpers.ensure_team_season import ensure_team_season
from roster.get_roster_football import get_roster_from_api
from requests import Session 
from schedule.get_schedule_from_api import upsert_games_from_schedule
from helpers.core import TEAM_INFO
from helpers.etc.season_to_year import season_to_year
from stats.scrape_sports_stats import scrape_sports_stats




# Main parameters
conn = get_db_connection()
selected_sports = ["football"]
year = 2025
year_basketball = "2025-26"
sess = Session()




# -------------------------------
# ROSTERS
# -------------------------------


for team in selected_sports:

    team_info = TEAM_INFO[team]
    


    
    # BASEBALL ROSTER
    if team_info["sport_name"] == "Baseball":

        tsid = ensure_team_season(conn, 
                              school="Missouri", 
                              sport_key=team_info["sport_key"], 
                              sport_name=team_info["sport_name"],
                              year=year,
                              sport_slug=team_info["sport_slug"])

        for person in get_roster_baseball('baseball', year):
            upsert_roster(conn, tsid, [person]) 





    # BASKETBALL ROSTERS
    elif team_info["sport_name"] == "Men's Basketball" or team_info["sport_name"] == "Women's Basketball":

        api_season = year_basketball           
        db_year    = season_to_year(year_basketball, use="start")
        tsid = ensure_team_season(conn, 
                              school="Missouri", 
                              sport_key=team_info["sport_key"], 
                              sport_name=team_info["sport_name"],
                              year=db_year,
                              sport_slug=team_info["sport_slug"])
        
        for person in get_roster_from_api(team_info["sport_key"], api_season):
            upsert_roster(conn, tsid, [person])



    # ALL OTHER SPORTS
    else:

        tsid = ensure_team_season(conn, 
                              school="Missouri", 
                              sport_key=team_info["sport_key"], 
                              sport_name=team_info["sport_name"],
                              year=year,
                              sport_slug=team_info["sport_slug"])
        
        for person in get_roster_from_api(team_info["sport_key"], year):
            upsert_roster(conn, tsid, [person])












# -------------------------------
# SCHEDULES
# -------------------------------


for team in selected_sports:

    team_info = TEAM_INFO[team]

    tsid = ensure_team_season(conn, 
                              school="Missouri", 
                              sport_key=team_info["sport_key"], 
                              sport_name=team_info["sport_name"],
                              year=year,
                              sport_slug=team_info["sport_slug"])
    
    upsert_games_from_schedule(conn, tsid, season_id=team_info["season_id"])










# -------------------------------
# STATS
# -------------------------------

    
for sport in selected_sports:

    scrape_sports_stats(sport, year)







# GET FOOTBALL PLAYER SPECIAL TEAMS STATS
# GET SOFTBALL STATS









