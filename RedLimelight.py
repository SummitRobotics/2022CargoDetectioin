import cv2
import numpy as np
import math
def gc(cnts):
    # if the length the contours tuple returned by cv2.findContours
    # is '2' then we are using either OpenCV v2.4, v4-beta, or
    # v4-official
    if len(cnts) == 2:
        cnts = cnts[0]

    # if the length of the contours tuple is '3' then we are using
    # either OpenCV v3, v4-pre, or v4-alpha
    elif len(cnts) == 3:
        cnts = cnts[1]

    # otherwise OpenCV has changed their cv2.findContours return
    # signature yet again and I have no idea WTH is going on
    else:
        raise Exception(("Contours tuple must have length 2 or 3, "
            "otherwise OpenCV changed their cv2.findContours return "
            "signature yet again. Refer to OpenCV's documentation "
            "in that case"))

    # return the actual contours array
    return cnts
# To change a global variable inside a function,
# re-declare it the global keyword

blue = False
# runPipeline() is called every frame by Limelight's backend.
def runPipeline(image, llrobot):
    ballNum = 0
    largestContour = np.array([[]])
    largestContourMeasure = np.array([[]])
    llpython = [1,1,1,1,1,1,1,1]

    frame_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) 

        #Create Color Threshold Mask for Analysis (Range of Color in Image to Analyze)
    frame_threshold = cv2.inRange(frame_HSV, (0, 200, 0), (10, 255, 255))
    thresh2 = cv2.inRange(frame_HSV, (170, 200, 0), (180, 255, 255))
    frame_threshold  = cv2.bitwise_or(frame_threshold, thresh2)
        #Erode Color Threshold Mask to remove noise
    frame_threshold_eroded = cv2.erode(frame_threshold, None, iterations=3)

        #Dialate Color Threshold Mask after Eroding to Beef Up detected areas for analysis
    frame_threshold_dilated = cv2.dilate(frame_threshold_eroded, None, iterations=3)

        #Find contours in eroded and dialated color threshold mask used for finding circles
    cnts = cv2.findContours(frame_threshold_dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnts = gc(cnts)
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
                    # centroid
        for c in cnts:
            yNeg = False
            xNeg = False
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            xCoord = (x-160)*.3725
            yCoord = (y-120)*.3808
            xCoord = round(xCoord, 1)
            yCoord = round(yCoord, 1)
            mask1 = np.zeros_like(frame_threshold)
            mask1 = cv2.circle(mask1, (int(x),int(y)), int(radius), (255,255,255), -1)
            contourMask = np.zeros_like(frame_threshold)
            contourMask = cv2.drawContours(contourMask, c, -1, (255),1)
            cv2.fillPoly(contourMask, pts =[c], color=(255))
                            # draw the circle and centroid on the frame,
                            # then update the list of tracked points
            x,y,w,h = cv2.boundingRect(c)
            if radius > 10:
                if cv2.countNonZero(mask1) > 0:
                    if (cv2.countNonZero(contourMask)/cv2.countNonZero(mask1) > .8):
                        mainNum = 0
                        if xCoord < 0:
                          xCoord *= -1
                          mainNum += 100000000
                        mainNum += xCoord*1000000
                        if yCoord < 0:
                          yCoord *= -1
                          mainNum += 1000
                        mainNum += yCoord*100
                        if blue: 
                          mainNum += 2000000000
                        else: 
                          mainNum += 1000000000
                        mainNum += 2
                        if ballNum < 8:
                            llpython[ballNum] = mainNum
                            ballNum +=1
                        cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
                        if cv2.countNonZero(contourMask) > cv2.countNonZero(largestContour):
                            largestContourMeasure = contourMask
                            largestContour = c
  
       
    # make sure to return a contour,
    # an image to stream,
    # and optionally an array of up to 8 values for the "llpython"
    # networktables array
    # encoding: csxxxsyyyv
    # Key: c = color(1 = red, 2 = blue), s = sign (0 = +, 1 = -), x = x degrees, y = y degrees, v = validity(use mod, if odd then invalid)
    #Blue: (100, 200, 0), (110, 255, 200)
    return largestContour, image, llpython
