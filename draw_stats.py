import cv2
import numpy as np
import sys

def line(img, pt1, pt2, color, style='solid'):
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
            cv2.line(img,s,e,color)
        i+=1
def text(img, string, pos):
    cv2.putText(img, string, pos, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
def flyballLeft(img, pos, rot, length=100):
    cv2.ellipse(img, pos, (length, 20), rot, 60, 220, (0, 0, 0))
def flyballRight(img, pos, rot, length=100):
    cv2.ellipse(img, pos, (length, 20), rot, -40, 120, (0, 0, 0))

if len(sys.argv) < 3:
    print('Please enter a filename for the blank scouting report and a data file.')
    exit(0)

filename = sys.argv[1].split('.')[0]
dataFile = sys.argv[2]
img = cv2.imread(filename + '.png')

# START OF MARKUP PROCESS
text(img, 'Enoch Kumala', (150, 80))
text(img, 'WOOBAAII', (150, 253))
text(img, '99', (145, 323))
text(img, '99', (220, 323))
text(img, '123', (100, 370))
text(img, '456', (240, 370))
text(img, 'run', (120, 429))
text(img, 'run', (270, 429))
text(img, '2b', (140, 488))
text(img, '3b', (250, 488))
text(img, 'hr', (100, 547))
text(img, 'rbi', (240, 547))
text(img, '50', (140, 606))
text(img, '50', (300, 606))
text(img, 'bb', (130, 665))
text(img, 'k', (240, 665))
text(img, 'hbp', (130, 724))
text(img, 'sf', (130, 783))
text(img, 'sh', (240, 783))

line(img, (200, 200), (300, 300), (0, 0, 0))

line(img, (300, 200), (400, 300), (0, 0, 0), style='dotted')

flyballLeft(img, (500, 200), 0)

flyballRight(img, (800, 200), 0)

flyballRight(img, (1200, 200), 0, 300)
# END OF MARKUP PROCESS

cv2.imwrite(filename + '_markedup.png', img)