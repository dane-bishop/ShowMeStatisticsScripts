from stats.basketball.parse_player_stats import parse_player_basketball_stats, get_player_basketball_mu
from stats.basketball.upsert_player_stats import upsert_player_basketball_gamelog, upsert_player_basketball_season_highs
from helpers.queries.mens_basketball import MENS_BASKETBALL_SQL
from helpers.queries.womens_basketball import WOMENS_BASKETBALL_SQL
from requests import Session 
from helpers.core import get_db_connection

conn = get_db_connection()
sess = Session()


def scrape_basketball_stats(gender, year):


    with conn.cursor() as cur:
        
        cur.execute(MENS_BASKETBALL_SQL, (year,))
        mens_players = cur.fetchall()

        cur.execute(WOMENS_BASKETBALL_SQL, (year,))
        womens_players = cur.fetchall()

        print(f"Adding data for {len(mens_players)} Men's basketball players")
        

    # Get all mens stats
    for (player_id, roster_player_id) in mens_players:
        print(f"Player ID: {player_id} - Roster Player ID: {roster_player_id}")

        

        parsed = get_player_basketball_mu(sess, roster_player_id, year, 'mbball')
        print("first 2 rows:", parsed["gamelog"][:2])

        upsert_player_basketball_gamelog(conn, player_id=player_id, rows=parsed["gamelog"])
        upsert_player_basketball_season_highs(conn, player_id=player_id, highs=parsed["season_highs"])


    # Get all womens stats
    for (player_id, roster_player_id) in womens_players:
        print(f"Player ID: {player_id} - Roster Player ID: {roster_player_id}")

        

        parsed = get_player_basketball_mu(sess, roster_player_id, year, 'wbball')
        print("first 2 rows:", parsed["gamelog"][:2])

        upsert_player_basketball_gamelog(conn, player_id=player_id, rows=parsed["gamelog"])
        upsert_player_basketball_season_highs(conn, player_id=player_id, highs=parsed["season_highs"])