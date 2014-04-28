import cv2
import cv2.cv as cv# here
import numpy as np
from scipy import signal
import random
import math
import urllib
import string




#image = 'cropped_image2.png'
#image = 'img_1_big.jpg'
image = './images/img_2_big.jpg'
img = cv2.imread(image,1)
img = cv2.resize(img, None, fx=1/4.0, fy =1/4.0)



boardtem = './templates/board_template.png'
board_template = cv2.imread(boardtem,1)
board_template = cv2.resize(board_template,None,fx=1/4.0,fy=1/4.0)

redpiece = './templates/redpiece_template.png'
redpiece_template = cv2.imread(redpiece,1)
redpiece_template = cv2.resize(redpiece_template, None, fx=1/4.0, fy=1/4.0)

blackpiece = './templates/blackpiece_template.png'
blackpiece_template = cv2.imread(blackpiece,1)
blackpiece_template = cv2.resize(blackpiece_template, None, fx=1/4.0, fy=1/4.0)

emptypiece = './templates/emptypiece_template.png'
emptypiece_template = cv2.imread(emptypiece,1)
emptypiece_template = cv2.resize(emptypiece_template, None, fx=1/4.0, fy=1/4.0)

threshold1 = './templates/threshold_template1.png'
threshold1_template = cv2.imread(threshold1,0)
threshold1_template = cv2.resize(threshold1_template, None, fx=1/4.0, fy=1/4.0)



#built-in matchTemplate
#works for black out of box, not empty or red
"""
outr = cv2.matchTemplate(img[:,:,0],redpiece_template[:,:,0],cv.CV_TM_SQDIFF_NORMED)
outg = cv2.matchTemplate(img[:,:,1],redpiece_template[:,:,1],cv.CV_TM_SQDIFF_NORMED)
outb = cv2.matchTemplate(img[:,:,2],redpiece_template[:,:,2],cv.CV_TM_SQDIFF_NORMED)
cv2.imshow("redtemplater",outr)
cv2.imshow("redtempg",outg)
cv2.imshow("redtemplateb",outb)
    
"""

outr = cv2.matchTemplate(img[:,:,0],board_template[:,:,0],cv.CV_TM_SQDIFF_NORMED)
cv2.imshow("bredtemplater",outr)

"""
#try thresholding red
red = img[:,:,2]
blue = img[:,:,1]
green = img[:,:,0]
thresholdedr = cv2.adaptiveThreshold(red,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 77, 15)
cv2.imshow("threshold result", thresholdedr)

thresholdedg = cv2.adaptiveThreshold(green,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 111, 2)
cv2.imshow("lolthresholdg",thresholdedg)

thresholdedb = cv2.adaptiveThreshold(blue,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 111, 2)
cv2.imshow("lolthresholdb",thresholdedb)
"""


"""
#find circles in thresholded image
circles = cv2.HoughCircles(thresholdedr,cv.CV_HOUGH_GRADIENT,1.0,50,param1=50,param2=20,minRadius=5,maxRadius=50)
circles = np.uint16(np.around(circles))
for i in circles[0,:]:
    # draw the outer circle
    cv2.circle(img,(i[0],i[1]),i[2],(255,255,255),2)
    # draw the center of the circle
    cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)
""" 

#try doing red - green - blue


"""
out = cv2.matchTemplate(img,blackpiece_template,cv.CV_TM_SQDIFF_NORMED)
cv2.imshow("blacktemplate",out)


out = cv2.matchTemplate(img,emptypiece_template,cv.CV_TM_SQDIFF_NORMED)
cv2.imshow("emptytemplate",out)
"""



"""
perform fft-based cross correlation of redpiece_template and img
"""
#out = lizMatchTemplate(img,redpiece_template)

#cv2.imshow("redtemplate",out)



cv2.imshow('image',img)
cv2.waitKey(0)
cv2.destroyAllWindows()
