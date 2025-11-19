from stats.compiled.baseball.scrape_baseball_stats import scrape_baseball_stats
from stats.compiled.football.scrape_football_stats import scrape_football_stats
from stats.compiled.basketball.scrape_basketball_stats import scrape_basketball_stats
from stats.compiled.volleyball.scrape_volleyball_stats import scrape_volleyball_stats


def scrape_sports_stats(sport, year):

    if sport == "baseball":

     
        scrape_baseball_stats(year)


    if sport == "football":

        scrape_football_stats(year)


    if sport == "mens-basketball":

        scrape_basketball_stats("mens", year)

    if sport == "womens-basketball":

        scrape_basketball_stats("womens", year)

    if sport == "womens-volleyball":

        scrape_volleyball_stats(year)



    return