# USAGE
# python ball_tracking.py --video ball_tracking_example.mp4
# python ball_tracking.py

# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
from networktables import NetworkTables
#import logging

#logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize(server = 'roborio-3637-frc.local')

sd = NetworkTables.getTable("SmartDashboard")

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the
# ball in the HSV color space, then initialize the
# list of tracked points
lowerBound = (30, 100, 150)
upperBound = (50, 215, 255)
#pts = deque(maxlen=args["buffer"])

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
	vs = VideoStream(src=0).start()

# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])
    vs.set(cv2.CAP_PROP_AUTO_WB, 0)
    vs.set(cv2.CAP_PROP_WB_TEMPERATURE, 2800)
    vs.set(cv2.CAP_PROP_BRIGHTNESS, 20)
    vs.set(cv2.CAP_PROP_CONTRAST, 0)
    vs.set(cv2.CAP_PROP_HUE, 0)
    vs.set(cv2.CAP_PROP_SATURATION, 128)
    vs.set(cv2.CAP_PROP_SHARPNESS, 0)
    vs.set(cv2.CAP_PROP_GAMMA, 126)
    vs.set(cv2.CAP_PROP_BACKLIGHT, 1)
    vs.set(cv2.CAP_PROP_GAIN, 0)
    vs.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    
# allow the camera or video file to warm up
time.sleep(2.0)

# keep looping
while True:
	# grab the current frame
	frame = vs.read()

	# handle the frame from VideoCapture or VideoStream
	frame = frame[1] if args.get("video", False) else frame

	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
	if frame is None:
		break

	# resize the frame, blur it, and convert it to the HSV
	# color space
	frame = imutils.resize(frame, width=600)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, lowerBound, upperBound)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	center = None
	
	xOffset = 0

	# only proceed if at least one contour was found
	for c in cnts:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		# c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		#print(center)

		# only proceed if the radius meets a minimum size
		if radius > 1:
                    xOffset = 300 - x
                    
                    #if x < 66:
                    #    xOffset = -4
                    #elif x < 132:
                    #    xOffset = -3
                    #elif x < 198:
                    #    xOffset = -2
                    #elif x < 264:
                    #    xOffset = -1
                    #elif x < 336:
                    #    xOffset = 0
                    #elif x < 402:
                    #    xOffset = 1
                    #elif x < 468:
                    #    xOffset = 2
                    #elif x < 534:
                    #    xOffset = 3
                    #else:
                    #    xOffset = 4
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
                    cv2.circle(frame, (int(x), int(y)), int(radius), (255, 0, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)
                    sd.putNumber("Distance", 103 * radius ** -0.933)
                    sd.putNumber("X Offset", xOffset)
			#print(103 * radius ** -0.933)
			#print(120 * radius **-0.981)
			#print(radius)

	# update the points queue
	#pts.appendleft(center)

	# loop over the set of tracked points
	#for i in range(1, len(pts)):
		# if either of the tracked points are None, ignore
		# them
	#	if pts[i - 1] is None or pts[i] is None:
	#		continue

		# otherwise, compute the thickness of the line and
		# draw the connecting lines
	#	thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
	#	cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

	# show the frame to our screen
	#cv2.imshow("Frame", frame)
	#key = cv2.waitKey(1) & 0xFF

	# if the 'q' key is pressed, stop the loop
	#if key == ord("q"):
		#break

# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
	vs.stop()

# otherwise, release the camera
else:
	vs.release()

# close all windows
cv2.destroyAllWindows()
