import urllib.request
from bs4 import BeautifulSoup
import datetime
import os
import errno
import json
import re


def get_teams_by_division(division):
    teams = []
    year = datetime.datetime.now().year

    team_url = "http://stats.ncaa.org/team/inst_team_list" + \
               "?academic_year={}&conf_id=-1&division={}&sport_code=WSB".format(year, division)
    req = urllib.request.Request(team_url, headers={'User-Agent': "Scraper"})
    html = urllib.request.urlopen(req)
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find("table").findAll("a")
    for link in links:
        name = link.contents[0]
        url_suffix = link.attrs["href"]
        teams.append((name, url_suffix))

    return teams


def silent_remove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred


def generate_text_file(filename, teams):
    text_filename = filename + ".txt"
    silent_remove(text_filename)
    file = open(text_filename, "w")
    sorted_teams = sorted(teams, key=lambda tup: tup[0])
    for team in sorted_teams:
        file.write(team[0] + "\n")
    file.close()


def generate_json_file(filename, teams):
    json_filename = filename + ".json"
    silent_remove(json_filename)
    data = {}
    for name, url_suffix in teams:
        data[name] = re.search("(?<=\/team\/)(.*)(?=\/13430)", url_suffix).group(1)
    with open(json_filename, 'w') as outfile:
        json.dump(data, outfile)


def main():
    teams_1 = get_teams_by_division(1)
    teams_2 = get_teams_by_division(2)
    teams_3 = get_teams_by_division(3)

    teams = teams_1 + teams_2 + teams_3

    generate_text_file("2018_all_teams", teams)
    generate_text_file("2018_div1_teams", teams_1)
    generate_text_file("2018_div2_teams", teams_2)
    generate_text_file("2018_div3_teams", teams_3)

    generate_json_file("2018_all_teams", teams)


if __name__ == "__main__":
    main()
