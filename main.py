import psycopg2
from helpers.core import get_db_connection
from schedule.ensure_team_season import ensure_team_season
from schedule.get_schedule_text import get_schedule_text
from schedule.upsert_schedule import upsert_schedule
from roster.get_roster import get_roster
from roster.upsert_roster import upsert_roster



conn = get_db_connection()
tsid = ensure_team_season(conn, year=2025)
upsert_roster(conn, tsid, get_roster('baseball', 2025))
upsert_schedule(conn, tsid, get_schedule_text('baseball', 2025))