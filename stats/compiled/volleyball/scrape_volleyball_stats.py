from stats.volleyball.parse_player_stats import parse_player_volleyball_stats, get_player_volleyball_mu
from stats.volleyball.upsert_player_stats import upsert_player_volleyball_gamelog, upsert_player_volleyball_season_highs
from requests import Session 
from helpers.core import get_db_connection
from helpers.queries.womens_volleyball import WOMENS_VOLLEYBALL_SQL

conn = get_db_connection()
sess = Session()

def scrape_volleyball_stats(year):

    with conn.cursor() as cur:
        
        cur.execute(WOMENS_VOLLEYBALL_SQL, (year,))
        players = cur.fetchall()

        

        print(f"Adding data for {len(players)} Women's Volleyball players")


    for (player_id, roster_player_id) in players:
        print(f"Player ID: {player_id} - Roster Player ID: {roster_player_id}")

        parsed = get_player_volleyball_mu(sess, roster_player_id, year)
        print("first 2 rows:", parsed["gamelog"][:2])

        upsert_player_volleyball_gamelog(conn, player_id=player_id, rows=parsed["gamelog"])
        upsert_player_volleyball_season_highs(conn, player_id=player_id, highs=parsed["season_highs"])
