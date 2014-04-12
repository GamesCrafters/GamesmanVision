import cv2
import cv2.cv as cv
import numpy as np
import random
import math
import urllib2
import string
import time
import socket
import thread

default_timeout = 12
socket.setdefaulttimeout(default_timeout)



#global parameter of piece size.  in future need to learn this actively.
piecesize = 20
color_threshold = 8000
RED_SIGN = "X" #determined by first color
BLACK_SIGN = "O"  #determined by first color
MEMOIZED_TABLE = {}
BASEURL = "http://nyc.cs.berkeley.edu:8080/gcweb/service/gamesman/puzzles/connect4/getNextMoveValues;width=7;height=6;pieces=4;board="

def board_to_response(board):
    """
    Passed in board string
    Memoize / ping Berkeley server and return evaluated answer
    """
    global MEMOIZED_TABLE
    if board in MEMOIZED_TABLE:
        if MEMOIZED_TABLE[board] != "failed":
            return MEMOIZED_TABLE[board]
    ans = "failed"
    try:
        board = board.replace(" ","%20")
        url = urllib2.urlopen(BASEURL + board, timeout=.25)
        html = url.read()
        url.close()
        ans = eval(html)['response']
    except:
        print "Bad URL or timeout or response"
    MEMOIZED_TABLE[board] = ans
    return ans



def determineTemplateColor(template, rad):
    runningsum = (0,0,0)
    cx = template.shape[0]/2
    cy = template.shape[1]/2
    for i in range(0,25):
        #sample 25 points and get their colors
        dist = random.random()*rad
        angle = random.random()*3.14
        x = math.cos(angle)*dist
        y = math.sin(angle)*dist
        color = template[cx+x,cy+y]
        runningsum += color
    runningsum = runningsum / 25
    return runningsum

def lizFindCirclesGrid(circles):
    """
    Passed in array of circles with no false positives, return array of most likely 6x7 grid centers
    in raste
    """
    #generate row and column delimiting values
    cxs = []
    cys = []
    for i in circles:
        cxs.append(i[0])
        cys.append(i[1])

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,10,1.0)
    retval_x, bestlabels_x, centers_kmeans_x = cv2.kmeans(np.array(np.float32(cxs)),7,criteria,10,cv2.KMEANS_PP_CENTERS)
    retval_y, bestlabels_y, centers_kmeans_y = cv2.kmeans(np.array(np.float32(cys)),6,criteria,10,cv2.KMEANS_PP_CENTERS)

    #we should see 7 groups of in x, and 6 groups in y
    #delimited by a jump of one piece size in width (~30-50 pixels)
    centers_kmeans_x = np.msort(centers_kmeans_x)
    centers_kmeans_y = np.msort(centers_kmeans_y)
    
    fullrow = []
    fullcol = []
    for i in centers_kmeans_x:
        fullcol.append(int(i))
    for j in centers_kmeans_y:
        fullrow.append(int(j))

        
    finalout = []
    #finalout is 42 possible pairs
    for i in range(5,-1,-1):
        for j in range(7):
            finalout.append( [fullrow[i],fullcol[j] ] )
      
    return finalout, centers_kmeans_x, centers_kmeans_y

def drawBoardOverlay(image):
    upperleft = (int(image.shape[1] * 1/4.0), int(image.shape[0]   * 1/4.0))
    lowerright = (int(image.shape[1] * 3/4.0), int(image.shape[0] * 3/4.0))
    cv2.rectangle(image,upperleft,lowerright,(1,1,1),thickness=5)
    return image

def captureImage(capture):
    """-
    Grabs image from webcam, draws rectangle on it, and returns the image
    """
    image =  None
    while(not image):
        image = cv.QueryFrame(capture)
    image = np.asarray(image[:,:])
    return image


def gamesmanVision(capture):
    """
    main function.  recursively calls until escape command.
    """
    testimage = 0
    img = None    #this is the image for analysis, cropped from original
    image = None  #this is the original image

    blacktemp = './templates/blackpiece_template.png'
    redtemp = './templates/redpiece_template.png'
    
    blackcolor = determineTemplateColor(cv2.imread(blacktemp),25)
    redcolor = determineTemplateColor(cv2.imread(redtemp),25)

    width = 0
    height = 0
    if(not testimage):
        #capture image from webcam, add rectangle
        image = captureImage(capture)

        #grabs center 50% for processing
        height = image.shape[1]
        width = image.shape[0]
        img = image[.25*width:.75*width, .25*height:.75*height]

    while(cv2.waitKey(1) <= 0):                    
        if(not testimage):
            #capture image from webcam, add rectangle
            image = captureImage(capture)

            #grabs center 50% for processing
            height = image.shape[1]
            width = image.shape[0]
            img = image[.25*width:.75*width, .25*height:.75*height]

        #test images
        if(testimage):
            #image = './images/c4_template.png'
            image = './images/cropped_image1.png'
            #image = './images/cropped_image2.png'
            #image = './images/cropped_image3.png'
            #image = './images/img_2_big.jpg'
            img = cv2.imread(image,1)
            img = cv2.resize(img, None, fx=1/4.0, fy =1/4.0)
            #img = cv2.resize(img, None, fx=1/1.5, fy =1/1.5)
        edges = cv2.Canny(img,100,200)
        w,h, c = img.shape



        #make_circles_image
        cimg = edges.copy()
        circles = cv2.HoughCircles(cimg,cv.CV_HOUGH_GRADIENT,10,piecesize, param1=200,param2=100,minRadius=int(0.5*piecesize),maxRadius=int(2.0*piecesize))
        try:
            if(not circles):
                cv2.imshow("GamesmanVision",image)
                continue
        except:
            a = 2+2
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
        cv2.imshow('cricles?',cimg)


        dogrid = 1
        centers = None
        centers_kmeans_x = None
        centers_kmeans_y = None
        (centers, centers_kmeans_x, centers_kmeans_y) = lizFindCirclesGrid(circles_culled)

        try:
            (centers, centers_kmeans_x, centers_kmeans_y) = lizFindCirclesGrid(circles_culled)
        except:
            dogrid = 0
        if(not centers):
            dogrid = 0
            
            
        if(dogrid):
            #generate board string if found!
            #generate sampling distance
            sd =  piecesize / 3
            index = 0
            colors_km = []  #building array for kmeans clustering of colors
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
                runningsum = np.float32(runningsum)
                colors_km.append(list(runningsum))
                index += 1
            #now we've got each center associated with its color
            #generate groupings for red / black / empty!
            colors_km = np.array(colors_km)
            
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,10,1.0)
            retval, bestlabels, centers_kmeans = cv2.kmeans(colors_km,3,criteria,10,cv2.KMEANS_PP_CENTERS)

            #separate these out by ENERGY, not  by index.
            #sometimes opencv changes up the indicies

            #find index of highest overall energy (1,1,1)
            #find index of highest energy according to (-1,-1,1)
            #find lowest overall energy (-1,-1,-1)

            black_energy = (-1,-1,-1)
            white_energy = (1,1,1)
            b_max_energy = -1000000
            w_max_energy = -1000000
            b_ind = 0
            w_ind = 0
            for i in range(len(centers_kmeans)):
                current_center = centers_kmeans[i]
                tot_b = 0
                tot_w = 0
                for j in range(len(current_center)):
                    tot_b = black_energy[j]*pow(current_center[j],2)
                    tot_w = white_energy[j]*pow(current_center[j],2)
                if tot_b > b_max_energy:
                    b_max_energy = tot_b
                    b_ind = i
                if tot_w > w_max_energy:
                    w_max_energy = tot_w
                    w_ind = i
            colors_in_order = []
            for i in centers:
                # draw the center of the circle
                cv2.circle(img, (i[1],i[0]), 15,(255,255,255),3)
                color = "shit"
                color_choice = (255,0,0)
                #if within threshold of blackcolor or redcolor, classify as those
                #otherwise, is background
                distr = pow(redcolor[0] - i[2][0],2) + pow(redcolor[1]-i[2][1],2) + pow(redcolor[2]-i[2][2],2)
                distb = pow(blackcolor[0] - i[2][0],2) + pow(blackcolor[1]-i[2][1],2) + pow(blackcolor[2]-i[2][2],2)
                if distr < color_threshold:
                    color_choice = (0,0,255)
                    color = "red"
                elif distb < color_threshold:
                    color_choice = (0,0,0)
                    color = "black"
                else:
                    color_choice = (255,255,255)
                    color = "empty"
                colors_in_order.append(color)
                cv2.circle(img,(i[1],i[0]),10,color_choice,3)


            
            #from these, generate a board!
            BOARD = ""
            for i in colors_in_order:
                if(i == "red"):
                    BOARD = BOARD+RED_SIGN
                elif (i == "black"):
                    BOARD = BOARD+BLACK_SIGN
                elif (i == "empty"):
                    BOARD = BOARD+" "
                else:
                    BOARD = BOARD+"$" #this is debugging sign for problem

                    
            if(not testimage):
                image[.25*width:.75*width, .25*height:.75*height] = img
                img = drawBoardOverlay(image)
                
            ans = board_to_response(BOARD)
            moves = {}
            if ans != "failed":
                #generate list of moves and their associated color
                for i in ans:
                    if i['value'] == "lose":
                        moves[i["move"]] = (0,0,255)
                    elif i['value'] == "win":
                        moves[i["move"]] = (0,255,0)
                    else:
                        moves[i["move"]] = (0,255,255)
            #there will be seven valid moves (tops)
            if(not testimage and ans != "failed"):
                for i in range(7):
                    #paste them on to the full image above the board with appropriate coloring and opacity for move values!
                    color = (100,100,100)
                    if str(i) in moves:
                        color = moves[str(i)]
                    #figure out position of this rectangle
                    #centered at
                    cent = (centers_kmeans_x[i],centers_kmeans_y[5]+piecesize)
                    bottom_left = (cent[0]-piecesize/2, cent[1]-piecesize/2)
                    top_right = (cent[0]+piecesize/2, cent[1]+piecesize/2)
                    #these two locations relative from bottom left of sub-image
                    pt1 = bottom_left 
                    pt2 = top_right 
                    pt1 = (int(pt1[0]+height*.25), int(pt1[1]-width*.25))
                    pt2 = (int(pt2[0]+height*.25), int(pt2[1]-width*.25))
                    print pt1, pt2
                    cv2.rectangle(img,pt1,pt2,color,-1)
            cv2.imshow('GamesmanVision',img) 
    #clean up
    cv2.destroyAllWindows()
    del(capture)
 


capture = cv.CaptureFromCAM(1)
gamesmanVision(capture)
