# Video feed working well. Refer colour detection video

import cv2
from pathFinder import *
from colorDetection import *

# Everything that follows is the original main.py code. Call functions from the other two .py files for reference here
# Code for video feed
# All cv2.imshow commands are commented by default (In main and referred .py files). Only to be used for testing purposes

video = cv2.VideoCapture('path_test_1.mp4')
video.set(cv2.CAP_PROP_FRAME_WIDTH,320)
video.set(cv2.CAP_PROP_FRAME_HEIGHT,240)

while True:
    ret,frame = video.read()
    #frame = cv2.flip(frame,-1)

    # Calling the functions
    hsv = convert_to_HSV(frame)
    edges = detect_edges(hsv)
    roi = region_of_interest(edges)
    line_segments = detect_line_segments(edges) # Changed roi to edges. Change back to crop image feed
    lane_lines = average_slope_intercept(frame,line_segments)
    lane_lines_image = display_lines(frame,lane_lines)
    steering_angle = get_steering_angle(frame, lane_lines)
    heading_image = display_heading_line(lane_lines_image,steering_angle)

    deviation = steering_angle - 90 # equivalent to angle_to_mid_deg variable
    print(deviation)
    if deviation < 5 and deviation > -5: # do not steer if there is a 10-degree error range
        print('Go straight')

    elif deviation > 5: # steer right if the deviation is positive
        print('Go right')

    elif deviation < -5: # steer left if deviation is negative
        print('Go left')
        
    if checkStop(frame, *getColorCode(getSpreadsheetColour())) :
        print('Stop')
        break
    
    cv2.imshow('Heading Image', heading_image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()

'''
# Code for image feed

frame = cv2.imread(r'resources/Capture2.JPG')

# frame = cv2.flip(frame,-1)

# Calling the functions
hsv = convert_to_HSV(frame)
edges = detect_edges(hsv)
roi = region_of_interest(edges)
line_segments = detect_line_segments(roi)
lane_lines = average_slope_intercept(frame, line_segments)
lane_lines_image = display_lines(frame, lane_lines)
steering_angle = get_steering_angle(frame, lane_lines)
heading_image = display_heading_line(lane_lines_image, steering_angle)

deviation = steering_angle - 90  # equivalent to angle_to_mid_deg variable
print(deviation)
if deviation < 5 and deviation > -5:  # do not steer if there is a 10-degree error range
    print('Go straight')

elif deviation > 5:  # steer right if the deviation is positive
    print('Go right')

elif deviation < -5:  # steer left if deviation is negative
    print('Go left')

#print(generateColorLimits(frame, getColorCode(getSpreadsheetColour())))

if checkStop(frame, *getColorCode(getSpreadsheetColour())) :
    print('Stop')

cv2.imshow('Heading Image', heading_image)

cv2.waitKey(0)
cv2.destroyAllWindows()
'''
