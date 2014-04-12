import cv2
import cv2.cv as cv

cv.NamedWindow("w1", cv.CV_WINDOW_AUTOSIZE)
capture = cv.CaptureFromCAM(0)

def repeat():

    frame = cv.QueryFrame(capture)

    
    cv.ShowImage("w1", frame)

    c = cv.WaitKey(100)
    if(c != -1):
        while True:
            c = cv.WaitKey(100)
            if(c != -1):
                break


repeat()
cv2.destroyAllWindows()
del(capture)
