import cv2
import cv2.cv as cv# here
import numpy as np
import random
import math
import urllib
import string



def board_to_response(board):
    board = string.replace(board, " ", "%20")
    global MEMOIZED_TABLE
    if board in MEMOIZED_TABLE:
        return MEMOIZED_TABLE[board]
    else:
        url = urllib.urlopen(BASEURL + board)
        html = url.read()
        url.close()
        ans = eval(html)['response']
        MEMOIZED_TABLE[board] = ans
        return ans
    
MEMOIZED_TABLE = {}
BASEURL = "http://nyc.cs.berkeley.edu:8080/gcweb/service/gamesman/puzzles/connect4/getNextMoveValues;width=7;height=6;pieces=4;board="

#image = 'cropped_image2.png'
image = './images/img_1_big.jpg'
img = cv2.imread(image,1)
img = cv2.resize(img, None, fx=1/4.0, fy =1/4.0)

edges = cv2.Canny(img,100,200)
w,h, c = img.shape



#make_circles_image
#cimg = cv2.cvtColor(edges,cv2.COLOR_BGR2GRAY)
cimg = edges.copy()
circles = cv2.HoughCircles(cimg,cv.CV_HOUGH_GRADIENT,10,25, param1=50,param2=30,minRadius=20,maxRadius=500)
circles = np.uint16(np.around(circles))
#do a pass and remove ones massively larger and smaller than median size
rads = []
for i in circles[0,:]:
    rads.append(i[2])
rads.sort()
avgrad = rads[len(rads)/2]
for i in circles[0,:]:
    if(i[2] > avgrad*2 or i[2] < avgrad/2):
        continue
    # draw the outer circle
    cv2.circle(cimg,(i[0],i[1]),i[2],(255,255,255),2)
    # draw the center of the circle
    cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)
cv2.imshow('detected circles',cimg)
print "done"

"""
make image of all circles in image on black background, high contrast
then try running findCirclesGrid on this
"""


#find circles grid
"""
find all circles that fit in any kind of linear grid pattern
identify all other possible circles or semicircles
make best guesses to gather 42, 6x7 grid, and their center points
"""


#built in, doesn't work very well on real images
[found, centers] = cv2.findCirclesGrid(edges, (7,6), flags=cv2.CALIB_CB_SYMMETRIC_GRID)


BOARD = ""
#generate board string if found!
if(found):
    #generate sampling distance
    sd = (centers[1][0][0] - centers[0][0][0])/4.0
    print sd
    for item in centers:
        #circles will be in order.
        runningsum = (0,0,0)
        cy = item[0][0]
        cx = item[0][1]
        for i in range(0,25):
            #sample 25 points and get their colors
            dist = random.random()*sd
            angle = random.random()*3.14
            x = math.cos(angle)*dist
            y = math.sin(angle)*dist
            color = img[cx+x,cy+y]
            runningsum += color
        runningsum = runningsum / 25
        #classify color
        color = "blank"
        if(runningsum[0] < 50  and runningsum[1] < 50 and runningsum[2] < 50):
            color = "black"
            BOARD = BOARD + "O"
        elif(runningsum[0] < 200 and runningsum[1] < 200 and runningsum[2] > 200):
            color = "red"
            BOARD = BOARD + "X"
        else:
            BOARD = BOARD + " "

if(len(BOARD) == 42):
    #need to fix board first
    newboard = BOARD[35:42]  + BOARD[28:35] + BOARD[21:28] + BOARD[14:21] + BOARD[7:14] + BOARD[0:7]
    print "Pinging server with board:  ;", newboard, ";"
    print BOARD[0:7]
    print BOARD[7:14]
    print BOARD[14:21]
    print BOARD[21:28]
    print BOARD[28:35]
    print BOARD[35:42]
    #ans = board_to_response(newboard)
        


#cv2.imshow('image',edges)
cv2.waitKey(0)
cv2.destroyAllWindows()
