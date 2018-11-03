import cv2
import numpy as np
import sys
from genStats import get_roster

def line(img, pt1, pt2, style='solid'):
  if style is 'solid':
    cv2.line(img, (200, 200), (300, 300), (0, 0, 0))
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
def flyballLeft(img, pos, rot, length=100):
    cv2.ellipse(img, pos, (length, 20), rot, 60, 220, (0, 0, 0))
def flyballRight(img, pos, rot, length=100):
    cv2.ellipse(img, pos, (length, 20), rot, -40, 120, (0, 0, 0))

# calculates the WOBA
def calculateWoba(slugPerc, obp):
    return str(round((slugPerc + (obp*2))/3, 2))

if len(sys.argv) < 2:
    print('Please enter a filename for the blank scouting report and a data file.')
    exit(0)

filename = sys.argv[1].split('.')[0]
counter = 0;

for entry in get_roster('457'):
    counter += 1;
    img = cv2.imread(filename + '.png')
    # START OF MARKUP PROCESS
    # choice = 1, 2, 3, or 4
    choice = 4

    if choice is 1:
        cv2.ellipse(img, ((70, 195), (75, 50), 0), (0, 0, 0))
    elif choice is 2:
        cv2.ellipse(img, ((145, 195), (75, 50), 0), (0, 0, 0))
    elif choice is 3:
        cv2.ellipse(img, ((265, 195), (160, 50), 0), (0, 0, 0))
    elif choice is 4:
        cv2.ellipse(img, ((400, 195), (120, 50), 0), (0, 0, 0))

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

    # line(img, (200, 200), (300, 300))

    # line(img, (300, 200), (400, 300), style='dotted')

    # flyballLeft(img, (500, 200), 0)

    # flyballRight(img, (800, 200), 0)

    # flyballRight(img, (1200, 200), 0, 300)
    # END OF MARKUP PROCESS

    cv2.imwrite('export/' + filename + '_markedup' + str(counter) + '.png', img)