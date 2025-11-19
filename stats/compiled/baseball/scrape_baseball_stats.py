from helpers.core import get_db_connection
from helpers.queries import BASEBALL_HITTERS_SQL
from requests import Session 
from stats.baseball.parse_player_hitting import get_player_hitting_mu
from stats.baseball.upsert_player_hitting import upsert_player_batting_gamelog, upsert_player_hitting_season_highs
from helpers.queries.baseball_hitters import BASEBALL_HITTERS_SQL
from helpers.queries.baseball_pitchers import BASEBALL_PITCHERS_SQL
from helpers.queries.baseball_fielders import BASEBALL_FIELDERS_SQL
from stats.baseball.parse_player_pitching import get_player_pitching_mu
from stats.baseball.upsert_player_pitching import upsert_player_pitching_gamelog, upsert_player_pitching_season_highs
from stats.baseball.parse_player_fielding import get_player_fielding_mu
from stats.baseball.upsert_player_fielding import upsert_player_fielding_gamelog, upsert_player_fielding_season_highs




conn = get_db_connection()
sess = Session()



def scrape_baseball_stats(year):


    # Query all players
    with conn.cursor() as cur:
                cur.execute(BASEBALL_HITTERS_SQL)
                batters = cur.fetchall()

                cur.execute(BASEBALL_PITCHERS_SQL)
                pitchers = cur.fetchall()

                cur.execute(BASEBALL_FIELDERS_SQL)
                fielders = cur.fetchall()


    print(f"Adding data for {len(batters)} batters, {len(pitchers)}, and {len(fielders)}")



    # Scrape Hitter Stats
    for (player_id, roster_player_id) in batters:
        print(f"Player ID: {player_id} - Roster Player ID: {roster_player_id}")

        parsed = get_player_hitting_mu(sess, roster_player_id, year)
        print("first 2 rows:", parsed["gamelog"][:2])


        upsert_player_batting_gamelog(conn, player_id=player_id, rows=parsed["gamelog"])
        upsert_player_hitting_season_highs(conn, player_id=player_id, highs=parsed["season_highs"])



    # Scrape Pitching Stats
    for (player_id, roster_player_id) in pitchers:
        print(f"Player ID: {player_id} - Roster Player ID: {roster_player_id}")

        parsed = get_player_pitching_mu(sess, roster_player_id, year)
        print("first 2 rows: ", parsed["gamelog"][:2])

        upsert_player_pitching_gamelog(conn, player_id=player_id, rows=parsed["gamelog"])
        upsert_player_pitching_season_highs(conn, player_id=player_id, highs=parsed["season_highs"])




    # Scrape fielding stats
    for (player_id, roster_player_id) in fielders:
        print(f"Player ID: {player_id} - Roster Player ID: {roster_player_id}")

        parsed = get_player_fielding_mu(sess, roster_player_id, year)
        print("first 2 rows: ", parsed["gamelog"][:2])

        upsert_player_fielding_gamelog(conn, player_id=player_id, rows=parsed["gamelog"])
        upsert_player_fielding_season_highs(conn, player_id=player_id, highs=parsed["season_highs"])




