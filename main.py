# main.py (sketch)
from roster.get_roster_baseball import get_roster_baseball
from schedule.upsert_schedule_baseball import upsert_schedule_baseball
from schedule.get_schedule_baseball import get_schedule_baseball
from roster.upsert_roster_baseball import upsert_roster_baseball
from helpers.core import get_db_connection
from schedule.schedule_helpers.ensure_team_season import ensure_team_season

conn = get_db_connection()
tsid = ensure_team_season(conn, school="Missouri", sport_key="baseball", sport_name="Baseball", year=2025, sport_slug="baseball")


# Stream roster straight into DB


YEARS = {
    2025
}

#for year in range(2024, 2026):  # includes 2025
for year in YEARS:
    tsid = ensure_team_season(conn, school="Missouri", sport_key="baseball", sport_name="Baseball", year=year, sport_slug="baseball")
    for person in get_roster_baseball('baseball', year):
        upsert_roster_baseball(conn, tsid, [person]) 


# Same for games (HTML schedule is usually quick)

for game in get_schedule_baseball('baseball', 2025, debug=False):
    upsert_schedule_baseball(conn, tsid, [game])
