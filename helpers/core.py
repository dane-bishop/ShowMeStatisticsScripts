import psycopg2
from psycopg2.extras import RealDictCursor
import re

BASE = "https://mutigers.com"
HDRS = {"User-Agent": "Mozilla/5.0 (+data-ingest)"}

COACH_WORDS = re.compile(r"coach|director|ops|operations|trainer|analyst|staff", re.I)


API_TEMPLATE = "https://mutigers.com/api/v2/stats/bio?rosterPlayerId={pid}&sport={sport}&year={year}"


def get_db_connection():
    return psycopg2.connect(host="localhost", database="capstone_db", user="danebishop",password="Bayloreagles20")



TEAM_INFO = {

    "football": {
        "sport_key": "football",
        "sport_name": "Football",
        "sport_slug": "football",
        "season_id": 5121},

    "mens-basketball": {
        "sport_key": "mens-basketball",
        "sport_name": "Men's Basketball",
        "sport_slug": "mens-basketball",
        "season_id": 5143},

    "womens-basketball": {
        "sport_key": "womens-basketball",
        "sport_name": "Women's Basketball",
        "sport_slug": "womens-basketball",
        "season_id": 5144},

    "womens-volleyball": {
        "sport_key": "womens-volleyball",
        "sport_name": "Women's Volleyball",
        "sport_slug": "womens-volleyball",
        "season_id": 5124},

    "baseball": {
        "sport_key": "baseball",
        "sport_name": "Baseball",
        "sport_slug": "baseball",
        "season_id": 5116 
    },

    "softball": {
        "sport_key": "softball",
        "sport_name": "Softball",
        "sport_slug": "softball",
        "season_id": 5115
    }

 
}




YEARS_DUO = {
    "2025-26",
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