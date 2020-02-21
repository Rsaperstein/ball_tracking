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
import base64

NetworkTables.initialize(server = 'roborio-3637-frc.local')

sd = NetworkTables.getTable("SmartDashboard")

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the
# ball in the HSV color space, then initialize the
# list of tracked points

lowerBound = (30, 50, 0)
upperBound = (50, 255, 255)

def pick_color(event,x,y,flags,param):
	if event == cv2.EVENT_LBUTTONDOWN:
		pixel = image_hsv[y,x]
		upper =  np.array([pixel[0] + 10, pixel[1] + 10, pixel[2] + 40])
		lower =  np.array([pixel[0] - 10, pixel[1] - 10, pixel[2] - 40])
		print(pixel, lower, upper)


# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
	vs = VideoStream(src=0).start()

# otherwise, grab a reference to the video file
else:
	vs = cv2.VideoCapture(args["video"])
	vs.set(cv2.CAP_PROP_AUTO_WB, 0)
	vs.set(cv2.CAP_PROP_WB_TEMPERATURE, 2800)
	vs.set(cv2.CAP_PROP_BRIGHTNESS, 0)
	vs.set(cv2.CAP_PROP_CONTRAST, 32)
	vs.set(cv2.CAP_PROP_HUE, 0)
	vs.set(cv2.CAP_PROP_SATURATION, 150)
	vs.set(cv2.CAP_PROP_SHARPNESS, 2)
	vs.set(cv2.CAP_PROP_GAMMA, 100)
	vs.set(cv2.CAP_PROP_BACKLIGHT, 1)
	vs.set(cv2.CAP_PROP_GAIN, 0)
	vs.set(cv2.CAP_PROP_AUTO_EXPOSURE, .75)
	vs.set(cv2.CAP_PROP_EXPOSURE, 37)
	#print(vs.get(cv2.CAP_PROP_FRAME_WIDTH))
	#print(vs.get(cv2.CAP_PROP_FRAME_HEIGHT))


    
# allow the camera or video file to warm up
time.sleep(2.0)

count = -1

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
	sentToDashboard = 0

	# only proceed if at least one contour was found
	for c in cnts:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		# c = max(cnts, key=cv2.contourArea)
		distance = 0
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		#print(center)
		a,b,w,h = cv2.boundingRect(c)
		aspect_ratio = float(w)/h
		calc_area = 3.1415 * radius * radius
		area_ratio = calc_area / (float(w)*float(h))
		centerPointColor = (0, 0, 255) #Red
		Distance = (103 * radius ** -.933)
		
		approx = cv2.approxPolyDP(c, .03 * cv2.arcLength(c, True), True)
		if len(approx)==8:
			area = cv2.contourArea(c)
			circleArea = radius * radius * np.pi
			#print("circle area: "+str(circleArea))
			#print("area:" + str(area))
			#if circleArea == area:
				#cv2.drawContours(frame, [c], 0, (255, 255, 0), -1)
		
		# only proceed if the radius meets a minimum size
		#if radius > 5 and aspect_ratio > .9 and aspect_ratio < 1.1 and area_ratio > .7 and area_ratio < .93:
			#centerPointColor = (0, 255, 0)
		#if radius > 5 and aspect_ratio > .9 and aspect_ratio < 1.1:
		#if aspect_ratio > .9 and aspect_ratio < 1.1:
			#centerPointColor = (255, 0, 0)  #Blue
			#if area_ratio > .7 and area_ratio < .93:
					#centerPointColor = (0, 255, 0) #Green
		#if Distance < 6:
			#if aspect_ratio > .9 and aspect_ratio < 1.1:
				#centerPointColor = (255, 0, 0)  #Blue
				#if area_ratio > .62 and area_ratio < .93:
					#centerPointColor = (0, 255, 0) #Green
		#elif Distance > 6: 
			#if aspect_ratio > .5 and aspect_ratio < 1.5:
				#centerPointColor = (255, 0, 0) #blue
				#if area_ratio > .25 and area_ratio < 1.75:
					#centerPointColor = (0, 255, 0) #Green
		if radius > 5 and  aspect_ratio > .9 and aspect_ratio < 1.1 and area_ratio > .7 and area_ratio < .93:
			xOffset = 300 - x
			print("Distance :" + str(103 * radius ** -.933))
			print( "aspect_ratio = " + str(aspect_ratio))
			print( "area_ratio = " + str(area_ratio))
			#print("radius = " + str(radius))
			#print("area using radius = " + str(np.pi * radius * radius))
			#print(str(area_ratio) + " = " + str(calc_area) + " / " + str(w) + " * " + str(h) )

			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius), centerPointColor, 2)
			cv2.circle(frame, center, 3, centerPointColor, -1)
			distance = 103 * radius ** -0.933
			sd.putNumber("Distance", distance)
			sd.putNumber("X Offset", xOffset)
			sentToDashboard = 1
			count = 0
	if sentToDashboard == 0:
                count += 1
                print(count)
                if count >= 8:
                    sd.putNumber("Distance", -1)
                    sd.putNumber("X Offset", 100000)
                    print(-1)
                    print(100000)
			#cv2.drawContours(frame, [c], 0, (255, 255, 0), -1)


#	cv2.namedWindow('Frame')
#	cv2.setMouseCallback('Frame', pick_color)
#	image_hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
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
