# main.py (sketch)
from roster import get_roster
from schedule.upsert_schedule import upsert_schedule
from schedule import get_schedule_html
from roster.upsert_roster import upsert_roster
from helpers.core import get_db_connection
from schedule.ensure_team_season import ensure_team_season

conn = get_db_connection()
tsid = ensure_team_season()

# tsid already exists (team_season 2025)
people = list(get_roster('baseball', 2025))
upsert_roster(conn, tsid, people)

games = list(get_schedule_html('baseball', 2025, debug=True))
upsert_schedule(conn, tsid, games)