import urllib.request
from bs4 import BeautifulSoup
import json
import sys
import re
import unidecode


def get_soup(url):
    """
    Helper method for generating searchable soup from url
    :param url: target url
    :return: soup object
    """
    req = urllib.request.Request(url, headers={'User-Agent': "Scraper"})
    html = urllib.request.urlopen(req)
    return BeautifulSoup(html, 'html.parser')


def get_roster(team_code):
    """
    Gets team roster for desired team
    :param team_code: code from json corresponding to desired team
    :return: list of dicts, each corresponding to a player
    """
    soup = get_soup("http://stats.ncaa.org/team/{}/stats/13430".format(team_code))

    headers = [x.getText(strip=True) for x in soup.findAll("th")]

    players = soup.find("tbody").findAll("tr")

    to_return = []

    for player in players:
        player_dict = {}
        player_fields = player.findAll("td")

        for i in range(len(headers)):
            to_add = unidecode.unidecode(player_fields[i].getText(strip=True))
            player_dict[headers[i]] = to_add if to_add else "0"

        to_return.append(player_dict)

    return to_return


def get_plays(team_code, num_games):
    """
    Gets plays for desired team
    :param team_code: code from json corresponding to desired team
    :param num_games: number of games from which to sample
    :return: List of games, list of list of lists - in order:
        Game from most to least recent
        Inning in game
        Plays in inning
    """
    soup = get_soup("http://stats.ncaa.org/player/game_by_game?" +
                    "game_sport_year_ctl_id=13430&org_id={}&stats_player_seq=-100".format(team_code))

    reversed_count = -2 * num_games - 1

    game_urls = [x["href"] for x in soup.findAll("a", {"class": "skipMask"})[-1:reversed_count:-2]]

    colleges = []
    games = []

    # List of games
    for game_url in game_urls:
        game_num = re.search("(?<=\/game\/index\/)(.*)(?=\?org_id=)", game_url).group(1)
        game_code = game_url[-3:]
        soup = get_soup("http://stats.ncaa.org/game/play_by_play/{}".format(game_num))

        all_tables = soup.findAll("table", {"class": "mytable"})
        colleges.append((all_tables[0].findAll("a")[0].getText(strip=True),
                         all_tables[0].findAll("a")[1].getText(strip=True)))

        start_index = 3 if team_code is game_code else 5
        plays = []

        # List of innings
        for i, table in enumerate(all_tables[1:]):
            table_entries = table.findAll("td")

            # List of plays
            individual_plays = [entry.getText(strip=True) for entry in table_entries[start_index:-3:3]
                                if entry.getText(strip=True)]
            if individual_plays:
                plays.append(individual_plays)

        games.append(plays)

    return colleges, games


def match_plays(players, colleges, plays):
    """
    Matches plays to players by last name, includes unidentified plays in key "UNIDENTIFIED PLAYS"
    :param players: list of players
    :param colleges: list of colleges
    :param plays: list of list of lists corresponding to plays
    :return: dict(player name: list of plays)
    """

    player_list = [player["Player"] for player in players]

    player_dict = {name: [] for name in player_list}
    player_dict["UNIDENTIFIED PLAYS"] = []

    for game_index, game in enumerate(plays):
        for inning_index, inning in enumerate(game):
            prefix = "Game {}: {} vs. {} - Inning Number: {} - Play: ".format(game_index + 1,
                                                                              colleges[game_index][0],
                                                                              colleges[game_index][1],
                                                                              inning_index + 1)
            for play in inning:
                found_name = False

                for name in player_list:
                    if re.search(name[:name.index(",")], play, re.IGNORECASE):
                        found_name = True
                        player_dict[name] = player_dict[name] + [prefix + play]

                if not found_name:
                    player_dict["UNIDENTIFIED PLAYS"] = player_dict["UNIDENTIFIED PLAYS"] + [prefix + play]

    name_to_jersey = {player["Jersey"]: player_dict[player["Player"]] for player in players}
    name_to_jersey["UNIDENTIFIED PLAYS"] = player_dict["UNIDENTIFIED PLAYS"]

    return name_to_jersey


def main():
    if len(sys.argv) is not 2:
        print("Input error: follow format \'genStats.py \"Georgia Tech\"\'")
        return

    with open('2018_all_teams.json') as handle:
        team_dict = json.loads(handle.read())

    team_name = sys.argv[1]
    team_url = team_dict.get(team_name)

    if not team_url:
        print("Team not found, double check text document for team name.")
        return

    team_code = re.search("(?<=\/team\/)(.*)(?=\/13430)", team_url).group(1)

    # team_code = "457"
    
    players = get_roster(team_code)

    colleges, plays = get_plays(team_code, 10)

    player_dict = match_plays(players, colleges, plays)

    print(player_dict)


if __name__ == "__main__":
    main()
