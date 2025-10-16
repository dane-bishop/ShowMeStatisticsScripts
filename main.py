# main.py (sketch)
from roster.get_roster import get_roster
from schedule.upsert_schedule import upsert_schedule
from schedule.get_schedule_html import get_schedule_html
from roster.upsert_roster import upsert_roster
from helpers.core import get_db_connection
from schedule.ensure_team_season import ensure_team_season

conn = get_db_connection()
tsid = ensure_team_season(conn, school="Missouri", sport_key="baseball", sport_name="Baseball", year=2025, sport_slug="baseball")


# Stream roster straight into DB


YEARS = {
    2025
}

#for year in range(2024, 2026):  # includes 2025
for year in YEARS:
    tsid = ensure_team_season(conn, school="Missouri", sport_key="baseball", sport_name="Baseball", year=year, sport_slug="baseball")
    for person in get_roster('baseball', year):
        upsert_roster(conn, tsid, [person]) 


# Same for games (HTML schedule is usually quick)

for game in get_schedule_html('baseball', 2025, debug=False):
    upsert_schedule(conn, tsid, [game])
