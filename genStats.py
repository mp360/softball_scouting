import urllib.request
from bs4 import BeautifulSoup
import json
import sys
import re


def get_roster(team_code):
    roster_url = "http://stats.ncaa.org/team/{}/stats/13430".format(team_code)
    req = urllib.request.Request(roster_url, headers={'User-Agent': "Scraper"})
    html = urllib.request.urlopen(req)
    soup = BeautifulSoup(html, 'html.parser')

    headers = [x.getText(strip=True) for x in soup.findAll("th")]

    players = soup.find("tbody").findAll("tr")

    to_return = []

    for player in players:
        player_dict = {}
        player_fields = player.findAll("td")

        for i in range(len(headers)):
            player_dict[headers[i]] = player_fields[i].getText(strip=True)

        to_return.append(player_dict)

    return to_return


def get_plays(team_code, num_games):
    gbg_url = "http://stats.ncaa.org/player/game_by_game?" \
              "game_sport_year_ctl_id=13430&org_id={}&stats_player_seq=-100".format(team_code)
    pbp_url = "http://stats.ncaa.org/game/play_by_play/{}"  # from above url

    return []


def main():
    if len(sys.argv) is not 2:
        print("Input error: follow format \'genStatistics.py \"Georgia Tech\"\'")
        return

    with open('2018_all_teams.json') as handle:
        team_dict = json.loads(handle.read())

    team_name = sys.argv[1]
    team_url = team_dict.get(team_name)

    if not team_url:
        print("Team not found, double check text document for team name.")
        return

    team_code = re.search("(?<=\/team\/)(.*)(?=\/13430)", team_url).group(1)

    # base_url = "http://stats.ncaa.org/team/{}/13430".format(team_code)

    players = get_roster(team_code)

    print(players)

    # play_by_plays = get_plays(team_code, 10)


if __name__ == "__main__":
    main()
