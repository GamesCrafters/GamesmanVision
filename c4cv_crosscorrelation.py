import cv2
import cv2.cv as cv# here
import numpy as np
from scipy import signal
import random
import math
import urllib
import string

def lizMatchTemplate(a,b):
    """
    gotta rewrite to implement fft-based convolution.
    this is impossible at slow speeds
    """
    out = a.copy()
    for x in range(len(b)/2, len(a) - len(b)/2):
        print "finishedrow"
        for y in range(len(b[0])/2, len(a[0]) - len(b[0])/2):
            #have center pixel in (x,y)
            runningsum = [0,0,0]
            for i in range(len(b)):
                for j in range(len(b[0])):
                    xd = x + (i-len(b)/2)
                    yd = y + (j-len(b[0])/2)
                    color = a[xd][yd]
                    color2 = b[i,j]
                    runningsum[0] += abs((int)(color[0]) - (int)(color2[0]))
                    runningsum[1] += abs((int)(color[1]) - (int)(color2[1]))
                    runningsum[2] += abs((int)(color[2]) - (int)(color2[2]))
            runningsum[0] = runningsum[0] / (len(b)*len(b[0]))
            runningsum[1] = runningsum[1] / (len(b)*len(b[0]))
            runningsum[2] = runningsum[2] / (len(b)*len(b[0]))

            out[i,j] = runningsum
    return out



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
#image = 'img_1_big.jpg'
image = 'img_2_big.jpg'
img = cv2.imread(image,1)
img = cv2.resize(img, None, fx=1/50.0, fy =1/50.0)


redpiece = 'redpiece_template.png'
redpiece_template = cv2.imread(redpiece,1)
redpiece_template = cv2.resize(redpiece_template, None, fx=1/50.0, fy=1/50.0)

blackpiece = 'blackpiece_template.png'
blackpiece_template = cv2.imread(blackpiece,1)
blackpiece_template = cv2.resize(blackpiece_template, None, fx=1/4.0, fy=1/4.0)

emptypiece = 'emptypiece_template.png'
emptypiece_template = cv2.imread(emptypiece,1)
emptypiece_template = cv2.resize(emptypiece_template, None, fx=1/4.0, fy=1/4.0)


"""
perform fft-based cross correlation of redpiece_template and img
"""


out = lizMatchTemplate(img,redpiece_template)
out = cv2.resize(out, None, fx=10.0, fy =10.0)

cv2.imshow("redtemplate",out)
"""
out = cv2.matchTemplate(img,redpiece_template,cv.CV_TM_SQDIFF_NORMED)
cv2.imshow("redtemplate",out)


out = cv2.matchTemplate(img,blackpiece_template,cv.CV_TM_SQDIFF_NORMED)
cv2.imshow("blacktemplate",out)


out = cv2.matchTemplate(img,emptypiece_template,cv.CV_TM_SQDIFF_NORMED)
cv2.imshow("emptytemplate",out)
"""


found = 0
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
        


cv2.imshow('image',img)
cv2.waitKey(0)
cv2.destroyAllWindows()
