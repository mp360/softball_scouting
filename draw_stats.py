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

if len(sys.argv) < 3:
    print('Please enter a filename for the blank scouting report and a data file.')
    exit(0)

filename = sys.argv[1].split('.')[0]
dataFile = sys.argv[2]
img = cv2.imread(filename + '.png')

# START OF MARKUP PROCESS
cv2.putText(img, 'INSERT TEXT HERE', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0))

line(img, (200, 200), (300, 300), (0, 0, 0))

line(img, (300, 200), (400, 300), (0, 0, 0), style='dotted')

cv2.ellipse(img, (500, 200), (100, 20), 0, 60, 220, (0, 0, 0))

cv2.ellipse(img, (700, 200), (100, 20), 72, -40, 120, (0, 0, 0))
# END OF MARKUP PROCESS

cv2.imwrite(filename + '_markedup.png', img)