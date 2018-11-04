import cv2
import numpy as np
import sys
import os
import random
from genStats import *
from fpdf import FPDF
import re
import nltk
import math

def randomize(pt):
  offsetX = random.random() * 2 - 1
  offsetY = random.random() * 2 - 1
  pt = tuple(map(sum,zip(pt, (offsetX * 30, offsetY * 30))))
  pt = (int(pt[0]), int(pt[1]))
  return pt
def unit_vector(vector):
    return vector / np.linalg.norm(vector)
def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    print(math.pi)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)) * 180 / math.pi
def line(img, pt1, pt2, style='solid', weight=1):
  if style is 'solid':
    cv2.line(img, pt1, pt2, (0, 0, 0), weight)
  elif style is 'dotted':
    dist =((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2)**.5
    pts= []
    gap = 10
    for i in  np.arange(0,dist,gap):
        r=i/dist
        x=int((pt1[0]*(1-r)+pt2[0]*r)+.5)
        y=int((pt1[1]*(1-r)+pt2[1]*r)+.5)
        p = (x,y)
        pts.append(p)
    s=pts[0]
    e=pts[0]
    i=0
    for p in pts:
        s=e
        e=p
        if i%2==1:
            cv2.line(img,s,e,(0, 0, 0))
        i+=1
def text(img, string, pos):
    cv2.putText(img, string, pos, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
def flyballLeft(img, pt1, pt2):
    pt1 = np.array(pt1)
    pt2 = np.array(pt2)
    average = tuple((pt1 + pt2) / 2)
    distance = np.linalg.norm(np.array(pt2) - np.array(pt1))
    average = (int(average[0]), int(average[1]))
    print(angle_between(pt1, pt2))
    cv2.ellipse(img, average, (int(distance), 20), int(angle_between(pt1, pt2)), 60, 220, (0, 0, 0))
def flyballRight(img, pos, rot, length=100):
    cv2.ellipse(img, pos, (length, 20), rot, -40, 120, (0, 0, 0))

# calculates the WOBA
def calculateWoba(slugPerc, obp):
    return str(round((slugPerc + (obp*2))/3, 2))

def number_from_name(name):
    with open('2018_all_teams.json') as handle:
        team_dict = json.loads(handle.read())

    team_number = team_dict.get(name)

    if not team_number:
        print("Team not found, double check text document for team name.")
        return

    return team_number

# constants
origin = (1150, 1000)
fb = (1150, 725)
sb = (900, 725)
tb = (900, 1000)
p = (1025, 850)
c = (1200, 1050)
ss = (800, 850)
lf = (550, 800)
cf = (700, 500)
rf = (950, 350)

# img = cv2.imread('blankScouting.png')
# flyballLeft(img, origin, sb)
# cv2.namedWindow('image',cv2.WINDOW_NORMAL)
# cv2.imshow('image', img)
# cv2.resizeWindow('image', 1000, 1000)
# cv2.waitKey()
# cv2.destroyAllWindows()

def main(team, markup):
    counter = 0;
    jerseys = []
    players = get_roster(team)
    colleges, plays = get_plays(team)
    player_dict = match_plays(players, colleges, plays)

    if not os.path.exists('export_' + team):
        os.makedirs('export_' + team)

    for entry in players:
        counter += 1;
        img = cv2.imread('blankScouting.png')

        # START OF MARKUP PROCESS
        try:
            text(img, entry['Player'], (150, 80))
            text(img, entry['Jersey'], (700, 80))
            text(img, entry['Pos'], (1420, 80))
            text(img, calculateWoba(float(entry['SlgPct']), float(entry['OBPct'])), (150, 253))
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

        if markup:
            for play in player_dict[entry['Jersey']]:
                play = play.split("\nPlay: ")[1]

                words = nltk.word_tokenize(play)
                if '3b' in words or 'third' in words:
                    final = tb
                elif 'ss' in words:
                    final = ss
                elif '2b' in words:
                    final = sb
                elif '1b' in words:
                    final = fb
                elif 'lf' in words:
                    final = lf
                elif 'rf' in words:
                    final = rf
                elif 'rf' in words:
                    final = rf
                elif 'p' in words:
                    final = p
                elif 'c' in words:
                    flyballRight(img, origin, 90)
                    continue
                
                if 'popped' in words or 'flied' in words or 'fouled' in words:
                    line(img, randomize(origin), randomize(final), weight=2)
                elif 'lined' in words:
                    line(img, randomize(origin), randomize(final))
                elif 'grounded' in words:
                    line(img, randomize(origin), randomize(final), style="dotted")
        # END OF MARKUP PROCESS

        jerseys.append((entry['Player'], entry['Jersey']))
        cv2.imwrite('export_' + team + '/markedup_' + entry['Jersey'] + '.png', img)

    pdf = FPDF()
    file = open('plays.txt', 'w+')
    for (player, jersey) in jerseys:
        filename = 'export_' + team + '/markedup_' + str(jersey) + '.png'

        pdf.add_page(orientation="L")
        pdf.image(filename, h=175)

        file.write('Player: ' + player + '\n\n')
        for play in player_dict[jersey]:
            file.write(play + '\n\n')
        
        file.write('\n\n')

    file.close()
    pdf.output('markedUpScouting.pdf', 'F')
