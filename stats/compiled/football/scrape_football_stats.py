from stats.football.parse_player_offense import get_player_football_offense_mu
from stats.football.upsert_player_offense import upsert_player_football_offense_gamelog, upsert_player_football_offense_season_highs
from stats.football.parse_player_defense import get_player_football_defense_mu
from stats.football.upsert_player_defense import upsert_player_football_defense_gamelog, upsert_player_football_defense_season_highs
from requests import Session 
from helpers.core import get_db_connection
from helpers.queries.football_offense import FOOTBALL_OFFENSE_SQL
from helpers.queries.football_defense import FOOTBALL_DEFENSE_SQL

conn = get_db_connection()
sess = Session()


def scrape_football_stats(year):

   

    with conn.cursor() as cur:

        cur.execute(FOOTBALL_OFFENSE_SQL, (year,))
        offensive_players = cur.fetchall()

        cur.execute(FOOTBALL_DEFENSE_SQL, (year,))
        defensive_players = cur.fetchall()



    print(f"Adding data for {len(offensive_players)} offensive players and {len(defensive_players)} defensive players")


    # Scrape all offensive stats
    for (player_id, roster_player_id) in offensive_players:
        print(f"Player ID: {player_id} - Roster Player ID: {roster_player_id}")

        parsed = get_player_football_offense_mu(sess, roster_player_id, year)
        print("first 2 rows:", parsed["gamelog"][:2])


        upsert_player_football_offense_gamelog(conn, player_id=player_id, rows=parsed["gamelog"])
        upsert_player_football_offense_season_highs(conn, player_id=player_id, highs=parsed["season_highs"])



    # Scrape all defensive stats
    for (player_id, roster_player_id) in defensive_players:
        print(f"Player ID: {player_id} - Roster Player ID: {roster_player_id}")

        parsed = get_player_football_defense_mu(sess, roster_player_id, year)
        print("first 2 rows:", parsed["gamelog"][:2])


        upsert_player_football_defense_gamelog(conn, player_id=player_id, rows=parsed["gamelog"])
        upsert_player_football_defense_season_highs(conn, player_id=player_id, highs=parsed["season_highs"])