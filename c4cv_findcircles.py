import cv2
import cv2.cv as cv
import numpy as np
import random
import math
import urllib
import string


#global parameter of piece size.  in future need to learn this actively.
piecesize = 50

    
MEMOIZED_TABLE = {}
BASEURL = "http://nyc.cs.berkeley.edu:8080/gcweb/service/gamesman/puzzles/connect4/getNextMoveValues;width=7;height=6;pieces=4;board="
def board_to_response(board):
    """
    Passed in board string
    Memoize / ping Berkeley server and return evaluated answer
    """
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



def lizRemoveFalsePositives(circles):
    """
    Passed in an array of circles, some false positives, most of them conforming to a 6x7 grid
    Return set culled of any likely false positives
    """
    return circles


def lizFindCirclesGrid(circles):
    """
    Passed in array of circles with no false positives, return array of most likely 6x7 grid centers    
    """
    if(len(circles) > 42):
        return

    #generate row and column delimiting values
    cxs = []
    cys = []
    for i in circles:
        cxs.append(i[0])
        cys.append(i[1])
    cxs.sort()
    cys.sort()
    #we should see 6 groups of in x, and 7 groups in y
    #delimited by a jump of one piece size in width (~30-50 pixels)
    
    xdelimits = []
    ydelimits = []
    iold = cxs[0]
    for i in cxs[1:]:
        if(i-iold > piecesize / 1.25):
            #this is a delimiting case
            #avg of i and iold will be the delimiting value
            xdelimits.append( (i+iold) / 2)
        iold = i
    iold = cys[0]
    for i in cys[1:]:
        if(i-iold > piecesize / 1.5):
            #this is a delimiting case
            #avg of i and iold will be the delimiting value
            ydelimits.append( (i+iold) / 2)
        iold = i

    #finally we have our delimiters
    rows = [[],[],[],[],[],[]]
    cols = [[],[],[],[],[],[],[]]
    for i in cxs:
        if i < xdelimits[0]:
            cols[0].append(i)
            continue
        if i < xdelimits[1]:
            cols[1].append(i)
            continue
        if i < xdelimits[2]:
            cols[2].append(i)
            continue
        if i < xdelimits[3]:
            cols[3].append(i)
            continue
        if i < xdelimits[4]:
            cols[4].append(i)
            continue
        if i < xdelimits[5]:
            cols[5].append(i)
            continue
        else:
            cols[6].append(i)
            continue
        
    for i in cys:
        if i < ydelimits[0]:
            rows[0].append(i)
            continue
        if i < ydelimits[1]:
            rows[1].append(i)
            continue
        if i < ydelimits[2]:
            rows[2].append(i)
            continue
        if i < ydelimits[3]:
            rows[3].append(i)
            continue
        if i < ydelimits[4]:
            rows[4].append(i)
            continue
        else:
            rows[5].append(i)
            continue

    #now average together every value in every row and column to generate a master row/column numbers
    fullrow = []
    fullcol = []
    for i in rows:
        avg = 0
        for j in i:
            avg += j
        avg = avg / len(i)
        fullrow.append(avg)
    
    for i in cols:
        avg = 0
        for j in i:
            avg += j
        avg = avg / len(i)
        fullcol.append(avg)


    finalout = []
    #finalout is 42 possible pairs
    for i in range(6):
        for j in range(7):
            finalout.append( [fullrow[i],fullcol[j] ] )
            
    return finalout


#image = 'cropped_image2.png'
#image = './images/img_1_big.jpg'
#image = './images/c4_template.png'
#image = './images/cropped_image1.png'
#image = './images/cropped_image2.png'
image = './images/img_2_big.jpg'
img = cv2.imread(image,1)
img = cv2.resize(img, None, fx=1/4.0, fy =1/4.0)

edges = cv2.Canny(img,100,200)
w,h, c = img.shape



#make_circles_image
#cimg = cv2.cvtColor(edges,cv2.COLOR_BGR2GRAY)
cimg = edges.copy()
circles = cv2.HoughCircles(cimg,cv.CV_HOUGH_GRADIENT,10,piecesize, param1=200,param2=100,minRadius=20,maxRadius=40)
circles = np.uint16(np.around(circles))
#do a pass and remove ones massively larger and smaller than median size
rads = []
for i in circles[0,:]:
    rads.append(i[2])
rads.sort()
avgrad = float(rads[len(rads)/2])
circles_culled = []
for i in circles[0,:]:
    if(i[2] > avgrad*1.5 or i[2] < avgrad/1.5):
        continue
    circles_culled.append(i)
    # draw the outer circle
    cv2.circle(cimg,(i[0],i[1]),i[2],(255,255,255),2)
    # draw the center of the circle
    cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)
cv2.imshow('detected circles',cimg)



dogrid = 0
if(dogrid):
    centers = lizFindCirclesGrid(circles_culled)
    found = 1
    found = 0
    BOARD = ""
    #generate board string if found!
    if(found):
        #generate sampling distance
        sd =  piecesize / 3
        index = 0
        for item in centers:
            #circles will be in order.
            runningsum = (0,0,0)
            cy = item[1]
            cx = item[0]
            for i in range(0,25):
                #sample 25 points and get their colors
                dist = random.random()*sd
                angle = random.random()*3.14
                x = math.cos(angle)*dist
                y = math.sin(angle)*dist
                color = img[cx+x,cy+y]
                runningsum += color
            runningsum = runningsum / 25
            centers[index].append(runningsum)
            index += 1
        #now we've got each center associated with its color
        #generate groupings for red / black / empty!
        
        """
        #classify colors
        color = "blank"
        if(runningsum[0] < 50  and runningsum[1] < 50 and runningsum[2] < 50):
            color = "black"
            BOARD = BOARD + "O"
        elif(runningsum[0] < 200 and runningsum[1] < 200 and runningsum[2] > 200):
            color = "red"
            BOARD = BOARD + "X"
        else:
            BOARD = BOARD + " "
        """


    for i in centers:
        # draw the center of the circle
        cv2.circle(img, (i[1],i[0]), 15,(255,255,255),3)
        cv2.circle(img,(i[1],i[0]),10,i[2],3)
    cv2.imshow('detected circles',img)


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
            


#cv2.imshow('image',img)
cv2.waitKey(0)
cv2.destroyAllWindows()
