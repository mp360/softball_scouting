import errno
import shutil
import cv2
import os
from fpdf import FPDF
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
    return BeautifulSoup(html, "html.parser", from_encoding="utf-8")


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

    print("Preparing to collect plays.")

    reversed_count = -2 * num_games - 1

    game_urls = [x["href"] for x in soup.findAll("a", {"class": "skipMask"})[-1:reversed_count:-2]]

    colleges = []
    games = []

    # List of games
    for index, game_url in enumerate(game_urls):
        game_num = re.search("(?<=\/game\/index\/)(.*)(?=\?org_id=)", game_url).group(1)
        game_code = game_url[-3:]
        soup = get_soup("http://stats.ncaa.org/game/play_by_play/{}".format(game_num))

        print("Progress: " + str(100 * index // len(game_urls)))

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


def text(img, string, pos):
    cv2.putText(img, string, pos, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))


# calculates the WOBA
def calculate_woba(slug_perc, obp):
    return str(round((slug_perc + (obp*2))/3, 2))


def main():
    if len(sys.argv) < 2:
        print("Input error: follow format \'make_report.py \"Georgia Tech\" (# games, 10 default)\'")
        return

    with open('resources/2018_all_teams.json') as handle:
        team_dict = json.loads(handle.read())

    team_name = sys.argv[1]
    num_games = int(sys.argv[2]) if sys.argv[2] else 10

    team_url = team_dict.get(team_name)

    if not team_url:
        print("Team not found, double check text document for team name.")
        return

    team_code = re.search("(?<=\/team\/)(.*)(?=\/13430)", team_url).group(1)

    players = get_roster(team_code)
    print("Gathered player data")
    colleges, plays = get_plays(team_code, num_games)
    print("Gathered play-by-play data")
    jerseys = []
    player_dict = match_plays(players, colleges, plays)

    export_directory = "export " + team_name + '/'

    try:
        shutil.rmtree(export_directory)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise

    os.makedirs(export_directory)
    image_directory = export_directory + '/images/'
    os.makedirs(image_directory)

    for entry in players:
        img = cv2.imread("resources/blankScouting.png")

        try:
            text(img, entry['Player'], (150, 80))
            text(img, entry['Jersey'], (700, 80))
            text(img, entry['Pos'], (1420, 80))
            text(img, calculate_woba(float(entry['SlgPct']), float(entry['OBPct'])), (150, 253))
            text(img, entry['SB'], (145, 323))
            text(img, entry['CS'], (220, 323))
            text(img, entry['BA'][1:], (100, 370))
            text(img, entry['AB'], (240, 370))
            text(img, entry['R'], (120, 429))
            text(img, entry['H'], (270, 429))
            text(img, entry['2B'], (140, 488))
            text(img, entry['3B'], (250, 488))
            text(img, entry['HR'], (100, 547))
            text(img, entry['RBI'], (240, 547))
            text(img, entry['SlgPct'][1:], (140, 606))
            text(img, entry['OBPct'][1:], (300, 606))
            text(img, entry['BB'], (130, 665))
            text(img, entry['K'], (240, 665))
            text(img, entry['HBP'], (130, 724))
            text(img, entry['SF'], (130, 783))
            text(img, entry['SH'], (240, 783))
        except ValueError:
            print("invalid entry")

        jerseys.append((entry['Player'], entry['Jersey']))
        cv2.imwrite(image_directory + 'markedup_' + entry['Jersey'] + '.png', img)

    pdf = FPDF()
    file = open(export_directory + team_name + ' plays.txt', 'w+')
    for (player, jersey) in jerseys:
        filename = image_directory + 'markedup_' + str(jersey) + '.png'

        pdf.add_page(orientation="L")
        pdf.image(filename, h=175)

        file.write('Player: ' + player + '\n\n')
        for play in player_dict[jersey]:
            file.write(play + '\n\n')

        file.write('\n\n')

    file.close()
    pdf.output(export_directory + team_name + ' report.pdf', 'F')
    print("Generation complete")


if __name__ == "__main__":
    main()
