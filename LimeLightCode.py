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

    
# runPipeline() is called every frame by Limelight's backend.
def runPipeline(image, llrobot):
   
  
    largestContour = np.array([[]])
    llpython = [0,0,0,0,0,0,0,0]

    frame_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) 

        #Create Color Threshold Mask for Analysis (Range of Color in Image to Analyze)
    frame_threshold = cv2.inRange(frame_HSV, (0, 200, 0), (5, 255, 255))
            
        #Erode Color Threshold Mask to remove noise
    frame_threshold_eroded = cv2.erode(frame_threshold, None, iterations=3)

        #Dialate Color Threshold Mask after Eroding to Beef Up detected areas for analysis
    frame_threshold_dilated = cv2.dilate(frame_threshold_eroded, None, iterations=3)


        #Find contours in eroded and dialated color threshold mask used for finding circles
    cnts = cv2.findContours(frame_threshold_dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = gc(cnts)
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
                    # centroid
        c = max(cnts, key=cv2.contourArea)
        
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                    # only proceed if the radius meets a minimum size
        if radius > 10:
                        # draw the circle and centroid on the frame,
                        # then update the list of tracked points
            x,y,w,h = cv2.boundingRect(c)
            if (abs((w-h)/w) < .2):
                cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
                llpython = [1, x, y, 2*radius, 2*radius, 9, 8, 7]
                largestContour = c
  
       
    # make sure to return a contour,
    # an image to stream,
    # and optionally an array of up to 8 values for the "llpython"
    # networktables array
    return largestContour, image, llpython